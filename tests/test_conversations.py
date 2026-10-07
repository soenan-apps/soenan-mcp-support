import json
from copy import deepcopy

import pytest
from soenan_arteligo_support.e2ee import (
    E2eeCrypto,
    E2eeError,
    EncryptedConversations,
    EncryptedRecords,
)
from soenan_arteligo_support.e2ee._conversation_context import (
    CHAT_HEADER,
    COMMENT_HEADER,
)
from soenan_arteligo_support.e2ee._crypto import decode
from test_e2ee import MemoryAPI, new_session


class ConversationAPI(MemoryAPI):
    def __init__(self):
        super().__init__(E2eeCrypto())
        self.calls = []
        self.lose_response = False
        self.conflicts = 0
        self.after_snapshot = None

    def call(self, operation, *, body=None, **params):
        self.calls.append((operation, deepcopy(params), deepcopy(body)))
        if operation == "e2eeWriteRecords" and self.conflicts:
            self.conflicts -= 1
            raise E2eeError("revision_conflict")
        if operation == "e2eeGetImmutable":
            scope = params["scope_id"]
            all_records = self.records[scope]
            cutoff = params.get(
                "snapshot_cursor", max(item["cursor"] for item in all_records.values())
            )
            values = [
                item
                for item in all_records.values()
                if item["kind"] == params["kind"]
                and params["after"] < item["cursor"] <= cutoff
                and any(
                    write.get("immutable", False)
                    for write in json.loads(
                        decode(item["signed_command"]["body_bytes"])
                    )["records"]
                    if write["record_id"] == item["record_id"]
                )
            ]
            values.sort(key=lambda item: item["cursor"])
            limit = params["limit"]
            selected = values[:limit]
            result = {
                **self._compact(selected),
                "cursor": selected[-1]["cursor"] if selected else params["after"],
                "snapshot_cursor": cutoff,
                "has_more": len(values) > limit,
            }
            callback, self.after_snapshot = self.after_snapshot, None
            if callback:
                callback()
            return result
        result = super().call(operation, body=body, **params)
        if operation == "e2eeWriteRecords" and self.lose_response:
            self.lose_response = False
            raise E2eeError("network_error")
        return result

    def _write(self, scope, writes, signed):
        for value in writes:
            current = self.records.get(scope, {}).get(value["record_id"])
            if current:
                prior = json.loads(decode(current["signed_command"]["body_bytes"]))
                immutable = next(
                    item.get("immutable", False)
                    for item in prior["records"]
                    if item["record_id"] == value["record_id"]
                )
                if immutable or value.get("immutable", False):
                    raise E2eeError("revision_conflict")
        return super()._write(scope, writes, signed)


@pytest.fixture
def conversations():
    api = ConversationAPI()
    session, _, _ = new_session(api, setup=True)
    records = EncryptedRecords(session)
    scope = records.create_project(
        owner_org="org_test", value={"title": "conversation test"}
    )
    return api, records, EncryptedConversations(records, scope)


def send(
    client,
    identifier="cmsg_11111111111111111111111111111111",
    operation="fixture_operation_send",
    body="hello",
):
    return client.write_chat(
        type="sent",
        message_id=identifier,
        operation_id=operation,
        body=body,
        references=[{"kind": "file", "fileId": "file"}],
        committed_at="2026-10-07T00:00:00Z",
    )


@pytest.mark.parametrize(
    "body,references",
    [
        (42, []),
        ("x" * 8001, []),
        ("bad\x00body", []),
        ("bad\x7fbody", []),
        ("", []),
        ("text", [{"fileId": "file"}]),
        ("text", [{"kind": "file", "fileId": "file"}] * 2),
        ("text", [{"kind": "file", "fileId": str(index)} for index in range(11)]),
    ],
)
def test_chat_writer_rejects_content_the_browser_cannot_display(
    conversations, body, references
):
    api, _, client = conversations
    api.calls.clear()
    with pytest.raises(E2eeError, match="invalid_request"):
        client.write_chat(
            type="sent",
            message_id="cmsg_33333333333333333333333333333333",
            operation_id="fixture_operation_invalid",
            body=body,
            references=references,
            committed_at="2026-10-07T00:00:00Z",
        )
    assert api.calls == []


def test_chat_body_limit_counts_unicode_characters_and_allows_text_whitespace(
    conversations,
):
    api, _, client = conversations
    body = "🙂" * 7997 + "\t\n\r"
    sent = send(client, body=body)
    assert sent["body"] == client.chat_messages()["messages"][0]["body"] == body
    api.calls.clear()
    for identifier, operation in (
        ("unreadable_message_id", "fixture_operation_invalid"),
        ("cmsg_33333333333333333333333333333333", "short"),
        ("cmsg_33333333333333333333333333333333", "operation with spaces"),
    ):
        with pytest.raises(E2eeError, match="invalid_request"):
            client.write_chat(
                type="sent",
                message_id=identifier,
                operation_id=operation,
                body="valid body",
                committed_at="2026-10-07T00:00:00Z",
            )
    assert api.calls == []


def member(subject="account-subject"):
    return {"kind": "member", "member": {"membershipId": subject, "userId": subject}}


def comment_value(body="comment"):
    return {
        "author": member(),
        "body": body,
        "anchor": {"kind": "file", "fileId": "file"},
        "createdAt": "2026-10-07T00:00:00Z",
        "references": [],
    }


def test_project_headers_are_atomic_and_stage_counter_is_initialized(conversations):
    api, records, client = conversations
    headers = records.read(client.scope, [CHAT_HEADER, COMMENT_HEADER, client.scope])
    assert headers[CHAT_HEADER]["value"] == {
        "format": 3,
        "recordType": "chat_header",
        "sequence": 0,
        "events": None,
        "messages": None,
    }
    assert headers[COMMENT_HEADER]["value"]["threads"] is None
    assert headers[client.scope]["value"]["lastStageVersion"] == 0
    assert (
        len(
            {
                json.dumps(api.records[client.scope][identifier]["signed_command"])
                for identifier in headers
            }
        )
        == 1
    )
    assert client.chat_messages()["messages"] == []
    assert client.comment_threads()["threads"] == []


def test_chat_sent_edit_delete_and_immutable_operation_retry(conversations):
    _api, _records, client = conversations
    sent = send(client)
    assert client.chat_messages()["messages"][0]["body"] == "hello"
    assert client.chat_operation("fixture_operation_send") == sent
    edited = client.write_chat(
        type="edited",
        message_id="cmsg_11111111111111111111111111111111",
        operation_id="fixture_operation_edit",
        expected_revision=1,
        body="updated",
        committed_at="2026-10-07T01:00:00Z",
    )
    assert send(client) == sent
    assert (
        client.chat_message("cmsg_11111111111111111111111111111111")["body"]
        == "updated"
    )
    assert (
        client.chat_message_history("cmsg_11111111111111111111111111111111") == edited
    )
    deleted = client.write_chat(
        type="deleted",
        message_id="cmsg_11111111111111111111111111111111",
        operation_id="fixture_operation_delete",
        expected_revision=2,
        committed_at="2026-10-07T02:00:00Z",
    )
    assert (
        client.chat_message("cmsg_11111111111111111111111111111111")["type"]
        == "deleted"
    )
    assert client.chat_events()["events"] == [sent, edited, deleted]
    with pytest.raises(E2eeError, match="message_state_changed"):
        client.write_chat(
            type="edited",
            message_id="cmsg_11111111111111111111111111111111",
            operation_id="fixture_operation_resurrect",
            expected_revision=3,
            body="resurrection",
            committed_at="2026-10-07T03:00:00Z",
        )
    with pytest.raises(E2eeError, match="idempotency_conflict"):
        send(client, body="different")
    archive = client.archive()
    assert archive["events"] == [sent, edited, deleted]


def test_lost_response_converges_without_more_records_or_new_signed_bytes(
    conversations,
):
    api, _records, client = conversations
    api.lose_response = True
    with pytest.raises(E2eeError, match="network_error"):
        send(client)
    before = deepcopy(api.records[client.scope])
    api.calls.clear()
    assert send(client)["revision"] == 1
    assert api.records[client.scope] == before
    assert not any(operation == "e2eeWriteRecords" for operation, _, _ in api.calls)


def test_chat_page_crosses_node_boundaries_and_normal_read_skips_history(conversations):
    api, _records, client = conversations
    for index in range(130):
        send(
            client,
            identifier=f"cmsg_{index:032x}",
            operation=f"fixture_operation_send_{index}",
        )
    first = client.chat_messages(limit=100)
    second = client.chat_messages(
        before_sequence=first["next_before_sequence"], limit=100
    )
    assert [
        value["sentSequence"] for value in first["messages"] + second["messages"]
    ] == list(range(130, 0, -1))
    assert second["next_before_sequence"] is None
    events = client.chat_events(limit=100)
    assert events["has_more"] is True
    assert len(client.chat_events(after=100)["events"]) == 30
    for revision in range(1, 75):
        client.write_chat(
            type="edited",
            message_id="cmsg_00000000000000000000000000000000",
            operation_id=f"fixture_operation_edit_{revision}",
            expected_revision=revision,
            body=f"edit {revision}",
            committed_at="2026-10-07T01:00:00Z",
        )
    api.calls.clear()
    assert (
        client.chat_message("cmsg_00000000000000000000000000000000")["revision"] == 75
    )
    reads = [
        body["scopes"][0]["record_ids"]
        for operation, _, body in api.calls
        if operation == "e2eeReadRecords"
    ]
    assert len(reads) == 5
    assert sum(map(len, reads)) == 6
    assert not any(
        operation in {"e2eeGetRecords", "e2eeGetCurrent", "e2eeGetImmutable"}
        for operation, _, _ in api.calls
    )
    assert (
        client.chat_message_history("cmsg_00000000000000000000000000000000")["revision"]
        == 75
    )


def test_comment_reply_text_edits_resolution_and_archive(conversations):
    _api, _records, client = conversations
    comment = client.create_comment("comment", comment_value())
    assert comment["revision"] == 1
    assert client.create_comment("comment", comment_value())["id"] == "comment"
    reply = client.create_reply(
        "reply", parent_id="comment", value=comment_value("reply")
    )
    assert client.comment_thread("comment")["replyCount"] == 1
    assert client.comment_reply("reply") == reply
    assert client.comment_replies("comment")["replies"] == [reply]
    edited = client.edit_comment(
        "comment",
        operation_id="commentedit",
        expected_revision=1,
        body="updated comment",
        committed_at="2026-10-07T01:00:00Z",
    )
    assert edited["revision"] == 2
    assert (
        client.edit_comment(
            "comment",
            operation_id="commentedit",
            expected_revision=1,
            body="updated comment",
            committed_at="2026-10-07T01:00:00Z",
        )["revision"]
        == 2
    )
    client.edit_reply(
        "reply",
        parent_id="comment",
        operation_id="replyedit",
        expected_revision=1,
        body="updated reply",
        committed_at="2026-10-07T01:00:00Z",
    )
    assert (
        client.set_resolution(
            "comment", resolved=True, actor=member(), operation_id="resolve"
        )["resolved"]
        is True
    )
    assert (
        client.comment_threads(anchor=comment_value()["anchor"])["threads"][0][
            "resolved"
        ]
        is True
    )
    snapshot = client.archive()
    assert snapshot["comments"][0]["body"] == "updated comment"
    assert snapshot["comments"][0]["replies"][0]["body"] == "updated reply"
    assert snapshot["comments"][0]["resolved"] is True
    client.set_resolution(
        "comment", resolved=False, actor=member(), operation_id="reopen"
    )
    assert (
        client.archive(snapshot_cursor=snapshot["snapshot_cursor"])["comments"]
        == snapshot["comments"]
    )


def test_comments_and_replies_page_over_shared_tree_splits(conversations):
    _api, _records, client = conversations
    for index in range(70):
        client.create_comment(f"comment{index}", comment_value())
        client.create_reply(
            f"reply{index}", parent_id="comment0", value=comment_value("reply")
        )
    first = client.comment_threads(limit=40)
    second = client.comment_threads(after=first["next_key"], limit=40)
    assert len(first["threads"]) == 40 and len(second["threads"]) == 30
    replies = client.comment_replies("comment0", limit=40)
    final = client.comment_replies("comment0", after=replies["next_key"], limit=40)
    assert [
        value["sequence"] for value in replies["replies"] + final["replies"]
    ] == list(range(1, 71))
    assert final["next_key"] is None


def test_snapshot_excludes_writes_between_kind_pages_and_enforces_budget(conversations):
    api, _records, client = conversations
    send(client)
    api.after_snapshot = lambda: client.create_comment("later", comment_value())
    snapshot = client.archive()
    assert snapshot["comments"] == []
    assert client.archive()["comments"][0]["id"] == "later"
    with pytest.raises(E2eeError, match="conversation_archive_limit"):
        client.archive(max_records=1)
    with pytest.raises(E2eeError, match="conversation_archive_limit"):
        client.archive(max_bytes=1)


def test_conflicts_and_cancellation_have_finite_work(conversations):
    api, records, client = conversations
    api.conflicts = 3
    with pytest.raises(E2eeError, match="revision_conflict"):
        send(client)
    assert sum(operation == "e2eeWriteRecords" for operation, _, _ in api.calls) == 3
    assert client.chat_messages()["messages"] == []

    def cancelled():
        raise InterruptedError("cancelled")

    before = deepcopy(api.records[client.scope])
    with pytest.raises(InterruptedError):
        send(EncryptedConversations(records, client.scope, checkpoint=cancelled))
    assert api.records[client.scope] == before


def test_forged_actor_and_terminal_mismatch_are_rejected(conversations):
    _api, records, client = conversations
    with pytest.raises(E2eeError, match="invalid_conversation_author"):
        client.create_comment(
            "comment", {**comment_value(), "author": member("another-member")}
        )
    event = send(client)
    head = records.read(client.scope, [event["messageHeadId"]])[event["messageHeadId"]]
    records.write(
        client.scope,
        key_epoch=1,
        records=[
            {
                "record_id": head["record_id"],
                "kind": "chat",
                "expected_revision": head["revision"],
                "value": {**head["value"], "messageRevision": 2},
            }
        ],
    )
    with pytest.raises(E2eeError, match="invalid_conversation_origin"):
        client.chat_messages()


def test_public_shared_fixture_reads_current_views_and_complete_archive():
    from pathlib import Path
    from types import SimpleNamespace

    fixture = json.loads(
        (Path(__file__).parent / "fixtures/conversation_format3.json").read_text()
    )

    class FixtureRecords:
        session = SimpleNamespace(subject=fixture["subject"])

        def read(self, scope, ids):
            assert scope == fixture["scope"]
            return {
                identifier: deepcopy(fixture["records"][identifier])
                for identifier in ids
                if identifier in fixture["records"]
            }

    client = EncryptedConversations(FixtureRecords(), fixture["scope"])
    expected = fixture["expected"]
    assert client.chat_messages()["messages"] == expected["messages"]
    assert client.chat_events()["events"] == expected["events"]
    assert client.comment_threads()["threads"] == expected["threads"]
    assert client.comment_replies("comment")["replies"] == expected["replies"]
    immutable = {
        identifier: record
        for identifier, record in fixture["records"].items()
        if record["immutable"]
    }
    assert client.archive_snapshot(immutable) == expected["archive"]
    broken = deepcopy(immutable)
    del broken["cop_fixture_operation_edit"]
    with pytest.raises(E2eeError, match="invalid_conversation"):
        client.archive_snapshot(broken)


def test_immutable_page_rejects_mutable_proofs_and_changed_snapshot(
    conversations, monkeypatch
):
    api, records, client = conversations
    send(client)
    original = api.call

    def mutable_page(operation, **parameters):
        if operation == "e2eeGetImmutable":
            current = api.records[client.scope][CHAT_HEADER]
            return {
                **api._compact([current]),
                "cursor": current["cursor"],
                "snapshot_cursor": current["cursor"],
                "has_more": False,
            }
        return original(operation, **parameters)

    monkeypatch.setattr(api, "call", mutable_page)
    with pytest.raises(E2eeError, match="invalid_cursor"):
        records.immutable_kind(client.scope, "chat")

    def changed_snapshot(operation, **parameters):
        page = original(operation, **parameters)
        if operation == "e2eeGetImmutable":
            page["snapshot_cursor"] += 1
        return page

    monkeypatch.setattr(api, "call", changed_snapshot)
    snapshot = max(record["cursor"] for record in api.records[client.scope].values())
    with pytest.raises(E2eeError, match="invalid_cursor"):
        records.immutable_kind(client.scope, "chat", snapshot_cursor=snapshot)


def test_chat_signed_terminal_blocks_a_later_forged_head(conversations):
    _api, records, client = conversations
    original = send(client)
    client.write_chat(
        type="deleted",
        message_id="cmsg_11111111111111111111111111111111",
        operation_id="fixture_operation_delete",
        expected_revision=1,
        committed_at="2026-10-07T01:00:00Z",
    )
    head = records.read(client.scope, [original["messageHeadId"]])[
        original["messageHeadId"]
    ]
    records.write(
        client.scope,
        key_epoch=1,
        records=[
            {
                "record_id": "cevt_resurrect",
                "kind": "chat",
                "expected_revision": 0,
                "immutable": True,
                "value": {
                    **original,
                    "type": "edited",
                    "revision": 3,
                    "sequence": 3,
                    "references": [],
                    "clientOperationId": "resurrect",
                    "body": "forged",
                },
            },
            {
                "record_id": head["record_id"],
                "kind": "chat",
                "expected_revision": head["revision"],
                "value": {
                    **head["value"],
                    "messageRevision": 3,
                    "lastEvent": {"id": "cevt_resurrect", "revision": 1},
                },
            },
        ],
    )
    with pytest.raises(E2eeError, match="invalid_conversation_terminal"):
        client.chat_message("cmsg_11111111111111111111111111111111")


def test_index_rejects_sibling_overlap_and_cyclic_or_malformed_nodes():
    from soenan_arteligo_support.e2ee._ordered_index import OrderedIndex

    def record(identifier, value):
        return {
            "record_id": identifier,
            "kind": "chat",
            "revision": 1,
            "deleted": False,
            "value": value,
        }

    root = {
        "format": 2,
        "type": "branch",
        "children": [
            {"first": {"name": "a", "id": "a"}, "node": {"id": "left", "revision": 1}},
            {"first": {"name": "b", "id": "b"}, "node": {"id": "right", "revision": 1}},
        ],
    }
    values = {
        "root": record("root", root),
        "left": record(
            "left",
            {
                "format": 2,
                "type": "leaf",
                "entries": [{"name": "a", "id": "a"}, {"name": "c", "id": "c"}],
            },
        ),
        "right": record(
            "right",
            {"format": 2, "type": "leaf", "entries": [{"name": "b", "id": "b"}]},
        ),
    }

    def index():
        return OrderedIndex(
            lambda ids: {identifier: values[identifier] for identifier in ids},
            lambda: "unused",
            "chat",
        )

    with pytest.raises(E2eeError, match="invalid_conversation_index"):
        index().page({"id": "root", "revision": 1})
    values["root"]["value"]["children"][0]["node"]["id"] = "root"
    with pytest.raises(E2eeError, match="invalid_conversation_index"):
        index().page({"id": "root", "revision": 1})
    values["root"]["value"] = {"format": 2, "type": "leaf", "entries": None}
    with pytest.raises(E2eeError, match="invalid_conversation_index"):
        index().page({"id": "root", "revision": 1})
