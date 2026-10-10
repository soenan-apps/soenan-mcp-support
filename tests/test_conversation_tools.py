import asyncio
from copy import deepcopy

import pytest
from mcp.server.fastmcp.exceptions import ToolError
from soenan_arteligo_support.e2ee import (
    DeviceSession,
    EncryptedConversations,
    EncryptedRecords,
)
from soenan_arteligo_support.e2ee._mcp import create_local_mcp
from test_conversations import ConversationAPI
from test_e2ee import new_session


@pytest.fixture
def tools():
    api = ConversationAPI()
    session, store, _ = new_session(api, setup=True)
    records = EncryptedRecords(session)
    scope = records.create_project(owner_org="org_test", value={"title": "local tools"})
    created = []

    def factory():
        current = DeviceSession(
            api,
            api.crypto,
            store,
            origin="https://arteligo.test",
            subject="account-subject",
        )
        current.refresh()
        created.append(current)
        return current

    server = create_local_mcp(factory)

    def invoke(name, **values):
        # FastMCP validates its advertised typed schema before invoking the tool.
        return asyncio.run(server._tool_manager.call_tool(name, values))

    return api, scope, server, invoke, factory, created


def test_generic_tools_preserve_files_and_reject_conversation_index_bypass(tools):
    api, scope, _, invoke, _, created = tools
    before = deepcopy(api.records[scope])
    for kind in ("chat", "comment"):
        with pytest.raises(ToolError, match="conversation_operation_required"):
            invoke(
                "arteligo_write_record",
                project_id=scope,
                record_id="bare",
                kind=kind,
                expected_revision=0,
                key_epoch=1,
                value={"body": "unindexed"},
            )
    assert api.records[scope] == before
    assert created == []
    invoke(
        "arteligo_write_record",
        project_id=scope,
        record_id="file",
        kind="file",
        expected_revision=0,
        key_epoch=1,
        value={"name": "example"},
    )
    assert api.records[scope]["file"]["revision"] == 1
    assert created[-1].state == "locked"


def test_chat_tools_commit_the_same_signed_index_and_reuse_operations(tools):
    api, scope, _, invoke, factory, created = tools
    arguments = {
        "project_id": scope,
        "message_id": "cmsg_11111111111111111111111111111111",
        "operation_id": "fixture_operation_send",
        "body": "hello",
        "committed_at": "2026-10-07T00:00:00Z",
    }
    sent = invoke("arteligo_chat_send", **arguments)
    before = deepcopy(api.records[scope])
    assert invoke("arteligo_chat_send", **arguments) == sent
    assert api.records[scope] == before
    edited = invoke(
        "arteligo_chat_edit",
        project_id=scope,
        message_id="cmsg_11111111111111111111111111111111",
        operation_id="fixture_operation_edit",
        expected_revision=1,
        body="updated",
        committed_at="2026-10-07T01:00:00Z",
    )
    assert (
        invoke("arteligo_chat_messages", project_id=scope)["messages"][0]["body"]
        == "updated"
    )
    assert (
        invoke(
            "arteligo_chat_message_history",
            project_id=scope,
            message_id="cmsg_11111111111111111111111111111111",
        )["revision"]
        == 2
    )
    assert (
        invoke(
            "arteligo_chat_operation",
            project_id=scope,
            operation_id="fixture_operation_edit",
        )["event"]
        == edited
    )
    current = factory()
    try:
        assert EncryptedConversations(EncryptedRecords(current), scope).chat_events()[
            "events"
        ] == [sent, edited]
    finally:
        current.lock()
    deleted = invoke(
        "arteligo_chat_delete",
        project_id=scope,
        message_id="cmsg_11111111111111111111111111111111",
        operation_id="fixture_operation_delete",
        expected_revision=2,
        committed_at="2026-10-07T02:00:00Z",
    )
    assert deleted["type"] == "deleted"
    assert all(session.state == "locked" for session in created)


def test_comment_tools_bind_the_signed_author_and_support_edits_and_resolution(tools):
    _, scope, _, invoke, _, _ = tools
    comment = invoke(
        "arteligo_comment_create",
        project_id=scope,
        comment_id="comment",
        body="note",
        anchor={"kind": "file", "fileId": "file"},
        created_at="2026-10-07T00:00:00Z",
        display_name="Maker",
    )
    assert comment["author"]["member"]["membershipId"] == "account-subject"
    reply = invoke(
        "arteligo_comment_reply_create",
        project_id=scope,
        reply_id="reply",
        comment_id="comment",
        body="reply",
        created_at="2026-10-07T00:00:00Z",
    )
    assert invoke("arteligo_comment_replies", project_id=scope, comment_id="comment")[
        "replies"
    ] == [reply]
    invoke(
        "arteligo_comment_edit",
        project_id=scope,
        comment_id="comment",
        operation_id="editcomment",
        expected_revision=1,
        body="changed",
        committed_at="2026-10-07T01:00:00Z",
    )
    invoke(
        "arteligo_comment_reply_edit",
        project_id=scope,
        reply_id="reply",
        comment_id="comment",
        operation_id="editreply",
        expected_revision=1,
        body="changed reply",
        committed_at="2026-10-07T01:00:00Z",
    )
    invoke(
        "arteligo_comment_resolution",
        project_id=scope,
        comment_id="comment",
        operation_id="resolve",
        resolved=True,
    )
    thread = invoke("arteligo_comment_thread", project_id=scope, comment_id="comment")[
        "comment"
    ]
    assert thread["resolved"] is True and thread["revision"] == 2
    assert (
        invoke("arteligo_comment_reply", project_id=scope, reply_id="reply")["reply"][
            "body"
        ]
        == "changed reply"
    )


def test_tool_schema_rejects_unbounded_reads_and_invalid_revisions_before_session(
    tools,
):
    api, scope, _, invoke, _, created = tools
    before = deepcopy(api.records[scope])
    for arguments in ({"limit": 101}, {"limit": 0}, {"before_sequence": -1}):
        with pytest.raises(ToolError):
            invoke("arteligo_chat_messages", project_id=scope, **arguments)
    with pytest.raises(ToolError):
        invoke(
            "arteligo_chat_edit",
            project_id=scope,
            message_id="cmsg_11111111111111111111111111111111",
            operation_id="fixture_operation_edit",
            expected_revision=0,
            body="updated",
            committed_at="2026-10-07T00:00:00Z",
        )
    with pytest.raises(ToolError):
        invoke(
            "arteligo_chat_send",
            project_id=scope,
            message_id="cmsg_11111111111111111111111111111111",
            operation_id="fixture_operation_send",
            body="text",
            committed_at="not-a-date",
        )
    for values in (
        {"body": "x" * 8001},
        {
            "body": "text",
            "references": [
                {"kind": "file", "fileId": str(index)} for index in range(11)
            ],
        },
    ):
        with pytest.raises(ToolError):
            invoke(
                "arteligo_chat_send",
                project_id=scope,
                message_id="cmsg_33333333333333333333333333333333",
                operation_id="fixture_operation_invalid",
                committed_at="2026-10-07T00:00:00Z",
                **values,
            )
    assert api.records[scope] == before
    assert created == []


def test_chat_tool_accepts_the_same_8000_character_limit_as_the_browser(tools):
    _, scope, _, invoke, _, _ = tools
    body = "🙂" * 8000
    invoke(
        "arteligo_chat_send",
        project_id=scope,
        message_id="cmsg_44444444444444444444444444444444",
        operation_id="fixture_operation_long",
        body=body,
        committed_at="2026-10-07T00:00:00Z",
    )
    assert (
        invoke("arteligo_chat_messages", project_id=scope)["messages"][0]["body"]
        == body
    )


def test_mcp_cursor_can_be_passed_back_without_reformatting(tools):
    _, scope, _, invoke, _, _ = tools
    for index in range(3):
        invoke(
            "arteligo_comment_create",
            project_id=scope,
            comment_id=f"comment{index}",
            body="note",
            anchor={"kind": "file", "fileId": "file"},
            created_at="2026-10-07T00:00:00Z",
        )
    first = invoke("arteligo_comment_threads", project_id=scope, limit=1)
    second = invoke(
        "arteligo_comment_threads", project_id=scope, limit=1, after=first["next_key"]
    )
    assert first["threads"][0]["id"] == "comment2"
    assert second["threads"][0]["id"] == "comment1"


def test_independent_work_completes_and_cancellation_locks_its_own_session(
    tools, monkeypatch
):
    import threading

    import anyio

    _api, scope, server, invoke, _, created = tools
    invoke(
        "arteligo_chat_send",
        project_id=scope,
        message_id="cmsg_11111111111111111111111111111111",
        operation_id="fixture_operation_send",
        body="hello",
        committed_at="2026-10-07T00:00:00Z",
    )
    started = threading.Event()
    released = threading.Event()
    lock = threading.Lock()
    scopes, results, paused = [], [], []
    original = EncryptedRecords.read

    def slow_read(self, project, ids):
        with lock:
            should_pause = not paused
            if should_pause:
                paused.append(self.session)
        if should_pause:
            started.set()
            released.wait()
        return original(self, project, ids)

    monkeypatch.setattr(EncryptedRecords, "read", slow_read)

    async def history():
        with anyio.CancelScope() as scope:
            scopes.append(scope)
            results.append(
                await server._tool_manager.call_tool(
                    "arteligo_chat_message_history",
                    {
                        "project_id": project,
                        "message_id": "cmsg_11111111111111111111111111111111",
                    },
                )
            )

    project = scope

    async def exercise():
        async with anyio.create_task_group() as group:
            group.start_soon(history)
            await anyio.to_thread.run_sync(started.wait)
            try:
                page = await server._tool_manager.call_tool(
                    "arteligo_chat_messages", {"project_id": project}
                )
                assert page["messages"][0]["body"] == "hello"
                assert created[-1] is not paused[0]
                assert created[-1].state == "locked"
                assert paused[0].state == "approved"
                scopes[0].cancel()
            finally:
                released.set()

    anyio.run(exercise)
    assert results == []
    assert paused[0].state == "locked"
    assert (
        invoke("arteligo_chat_messages", project_id=scope)["messages"][0]["body"]
        == "hello"
    )
