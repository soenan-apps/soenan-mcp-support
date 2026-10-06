from copy import deepcopy
import json
import time
from types import SimpleNamespace

import httpx

import pytest

from test_e2ee import MemoryAPI, new_session
from soenan_arteligo_support.e2ee import (
    E2eeCrypto,
    E2eeError,
    EncryptedDirectory,
    EncryptedRecords,
    abort_directory_migration,
    migrate_directory,
)
from soenan_arteligo_support.e2ee._crypto import decode, encode
from soenan_arteligo_support.e2ee._api import GeneratedAPI


def test_generated_transport_uses_bounded_read_and_kind_contracts():
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "POST":
            assert request.url.path == "/api/e2ee/records/read"
            assert json.loads(request.content) == {
                "scopes": [{"scope_id": "scope", "record_ids": ["record"]}],
                "include_keys": True,
            }
            return httpx.Response(
                200,
                json={"scopes": [], "commands": {}, "key_scopes": [], "server_time": 1},
            )
        if request.url.path.endswith("/devices"):
            assert request.url.params["device_id"] == "author"
            return httpx.Response(200, json={"devices": []})
        assert request.url.path == "/api/e2ee/scopes/scope/current"
        assert request.url.params["kind"] == "directory"
        return httpx.Response(
            200,
            json={
                "records": [],
                "commands": {},
                "cursor": 0,
                "has_more": False,
                "server_time": 1,
            },
        )

    api = GeneratedAPI(
        SimpleNamespace(
            arteligo_origin="https://arteligo.test", access_token=lambda: "access"
        ),
        transport=httpx.MockTransport(respond),
    )
    api.call(
        "e2eeReadRecords",
        body={
            "scopes": [{"scope_id": "scope", "record_ids": ["record"]}],
            "include_keys": True,
        },
    )
    assert (
        api.call("e2eeGetCurrent", scope_id="scope", kind="directory")["records"] == []
    )
    assert api.call("e2eeGetMemberDevices", scope_id="scope", device_id="author") == {
        "devices": []
    }
    assert len(requests) == 3


@pytest.fixture
def workspace():
    api = MemoryAPI(E2eeCrypto())
    session, _, _ = new_session(api, setup=True)
    records = EncryptedRecords(session)
    scope = records.create_project(value={"title": "bounded"}, owner_org="org-test")
    return api, session, records, scope


def test_selected_records_verify_shared_proof_once_without_global_reads(
    workspace, monkeypatch
):
    api, session, records, scope = workspace
    records.write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": f"chat-{index}",
                "kind": "chat",
                "expected_revision": 0,
                "value": {"message": str(index)},
            }
            for index in range(64)
        ],
    )
    verified, calls = [], []
    verify, call = session.crypto.verify, api.call

    def track_verify(key, operation, signed):
        verified.append(operation)
        return verify(key, operation, signed)

    def track_call(operation, **arguments):
        calls.append(operation)
        return call(operation, **arguments)

    monkeypatch.setattr(session.crypto, "verify", track_verify)
    monkeypatch.setattr(api, "call", track_call)
    session._clear_keys()
    opened = records.read(scope, ["chat-1", "chat-20", "chat-63"])
    assert [item["value"]["message"] for item in opened.values()] == ["1", "20", "63"]
    assert verified.count("records_write") == 1
    assert calls == ["e2eeReadRecords"]


@pytest.mark.parametrize(
    "mutation", ["ordinal", "record_id", "kind", "revision", "deleted"]
)
def test_compact_record_rejects_mismatched_signed_reference(
    workspace, monkeypatch, mutation
):
    api, _, records, scope = workspace
    call = api.call

    def tamper(operation, **arguments):
        result = call(operation, **arguments)
        if operation == "e2eeReadRecords":
            wire = result["scopes"][0]["records"][0]
            wire[mutation] = {
                "ordinal": 999,
                "record_id": "wrong",
                "kind": "file",
                "revision": 99,
                "deleted": True,
            }[mutation]
        return result

    monkeypatch.setattr(api, "call", tamper)
    with pytest.raises(E2eeError, match="invalid_record_signature|invalid_response"):
        records.read(scope, [scope])


def test_one_scope_verification_failure_keeps_other_scopes_readable(
    workspace, monkeypatch
):
    api, _, records, scope = workspace
    other = records.create_project(value={"title": "other"}, owner_org="org-test")
    call = api.call

    def tamper(operation, **arguments):
        result = call(operation, **arguments)
        if operation == "e2eeReadRecords":
            result["scopes"][0]["records"][0]["ordinal"] = 999
        return result

    monkeypatch.setattr(api, "call", tamper)
    result = records.read_many({scope: [scope], other: [other]})
    assert result[scope] == {"error": "invalid_record_signature"}
    assert result[other]["records"][0]["value"]["title"] == "other"


def test_omitted_optional_key_assistance_falls_back_to_exact_scope(
    workspace, monkeypatch
):
    api, session, records, scope = workspace
    call, calls = api.call, []

    def without_assistance(operation, **arguments):
        calls.append(operation)
        result = call(operation, **arguments)
        if operation == "e2eeReadRecords":
            result["scopes"][0]["envelopes"] = []
            result["scopes"][0]["devices"] = []
        return result

    monkeypatch.setattr(api, "call", without_assistance)
    session._clear_keys()
    assert records.read(scope, [scope])[scope]["value"]["title"] == "bounded"
    assert calls == ["e2eeReadRecords", "e2eeGetEnvelopes"]


def test_one_signed_malformed_payload_keeps_other_scopes_readable(workspace):
    _, session, records, scope = workspace
    other = records.create_project(value={"title": "other"}, owner_org="org-test")
    session.command(
        "e2eeWriteRecords",
        "records_write",
        {
            "scope_id": scope,
            "format_version": 2,
            "expires_at": int(time.time()) + 86400,
            "preconditions": [],
            "records": [
                {
                    "record_id": "malformed",
                    "kind": "chat",
                    "key_epoch": 1,
                    "expected_revision": 0,
                    "deleted": False,
                    "ciphertext": encode(b"not-json"),
                }
            ],
        },
        scope_id=scope,
    )
    result = records.read_many({scope: ["malformed"], other: [other]})
    assert result[scope] == {"error": "invalid_record"}
    assert result[other]["records"][0]["value"]["title"] == "other"


def test_cold_organization_batch_uses_all_bundled_keys_without_per_scope_reads(
    workspace, monkeypatch
):
    api, session, records, _ = workspace
    organizations = []
    projects = []
    for index in range(32):
        organization = records.create_project(
            value={"title": "org"}, owner_org="org-test"
        )
        organizations.append(organization)
        project = records.create_project(
            value={"title": str(index)},
            owner_org=organization,
            participation_policy="organization",
        )
        projects.append(project)
    api.envelopes = [
        value
        for value in api.envelopes
        if value["scope_id"] not in projects
        or value["recipient_kind"] == "organization"
    ]
    call, calls = api.call, []

    def bundled(operation, **arguments):
        calls.append(operation)
        result = call(operation, **arguments)
        if operation == "e2eeReadRecords":
            result["key_scopes"] = call(
                operation,
                body={
                    "scopes": [
                        {"scope_id": identifier, "record_ids": []}
                        for identifier in organizations
                    ]
                },
            )["scopes"]
        return result

    session._clear_keys()
    monkeypatch.setattr(api, "call", bundled)
    opened = records.read_many({identifier: [identifier] for identifier in projects})
    assert [
        opened[identifier]["records"][0]["value"]["title"] for identifier in projects
    ] == [str(index) for index in range(32)]
    assert calls == ["e2eeReadRecords"]


def test_missing_author_certificate_fetches_only_that_device(workspace, monkeypatch):
    api, session, records, scope = workspace
    added, _, _ = new_session(api)
    added.accept_approval(session.approve(added.enroll()))
    EncryptedRecords(added).write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": "from-new-device",
                "kind": "chat",
                "expected_revision": 0,
                "value": {"message": "hello"},
            }
        ],
    )
    identifier = added.device_id
    session._devices.pop(identifier, None)
    session.trust._state["devices"].pop(identifier, None)
    session.store.delete(f"{session.trust.name}:devices:{identifier}")
    call, fetched = api.call, []

    def limited(operation, **arguments):
        if operation == "e2eeGetMemberDevices":
            fetched.append(arguments)
            assert arguments == {"scope_id": scope, "device_id": identifier}
            return {"devices": [deepcopy(api.devices[identifier])]}
        response = call(operation, **arguments)
        if operation == "e2eeReadRecords":
            response["scopes"][0]["devices"] = []
        return response

    monkeypatch.setattr(api, "call", limited)
    assert records.read(scope, ["from-new-device"])["from-new-device"]["value"] == {
        "message": "hello"
    }
    assert len(fetched) == 1


def test_epoch_history_continues_until_target_when_byte_budget_shortens_pages(
    workspace, monkeypatch
):
    api, session, records, scope = workspace
    for _ in range(20):
        session.rotate_scope(api.projects[scope])
    api.envelopes = [value for value in api.envelopes if value["key_epoch"] == 21]
    session._clear_keys()
    session.scope_metadata(scope, refresh=True)
    call, epoch_pages = api.call, []

    def shortened(operation, **arguments):
        response = call(operation, **arguments)
        if operation == "e2eeGetEpochs":
            assert arguments["limit"] == 16
            epoch_pages.append(arguments["after_epoch"])
            response["epochs"] = response["epochs"][:1]
        return response

    monkeypatch.setattr(api, "call", shortened)
    assert records.read(scope, [scope])[scope]["value"]["title"] == "bounded"
    assert epoch_pages == list(range(1, 21))


def test_directory_pages_seek_and_invalidate_after_concurrent_insertion(
    workspace, monkeypatch
):
    api, _, records, scope = workspace
    directory = EncryptedDirectory(records, scope)
    entries = [
        {
            "id": f"entry-{index:04}",
            "name": f"name-{index:04}",
            "kind": "file",
            "fileId": f"file-{index}",
            "parentFolderId": None,
        }
        for index in range(512)
    ]
    for start in range(0, len(entries), 64):
        writes, conditions = directory.insertion(entries[start : start + 64])
        records.write(scope, key_epoch=1, records=writes, preconditions=conditions)
    call, requested = api.call, []

    def track(operation, **arguments):
        assert operation != "e2eeGetSnapshot"
        if operation == "e2eeReadRecords":
            requested.extend(
                identifier
                for request in arguments["body"]["scopes"]
                for identifier in request["record_ids"]
            )
        return call(operation, **arguments)

    monkeypatch.setattr(api, "call", track)
    first = directory.page(limit=100)
    assert first["entries"] == entries[:100]
    requested.clear()
    middle = directory.page(limit=100, cursor=first["cursor"])
    assert middle["entries"] == entries[100:200]
    assert len(requested) < 12
    assert not any(identifier.startswith("file-") for identifier in requested)
    with pytest.raises(E2eeError, match="entry_exists"):
        directory.insert(
            {**entries[32], "id": "different-id"}, key_epoch=1, additional_records=[]
        )
    directory.insert(
        {**entries[0], "id": "new", "name": "aaa"}, key_epoch=1, additional_records=[]
    )
    with pytest.raises(E2eeError, match="revision_conflict"):
        directory.page(cursor=middle["cursor"])


def test_directory_name_order_uses_utf16(workspace):
    _, _, records, scope = workspace
    entries = [
        {"id": f"entry-{index}", "name": name, "kind": "file", "parentFolderId": None}
        for index, name in enumerate(["\uff00", "\U00010000", "a", "A"])
    ]
    directory = EncryptedDirectory(records, scope)
    writes, conditions = directory.insertion(entries)
    records.write(scope, key_epoch=1, records=writes, preconditions=conditions)
    assert [entry["name"] for entry in directory.page()["entries"]] == [
        "A",
        "a",
        "\U00010000",
        "\uff00",
    ]


def test_first_directory_page_restarts_when_a_node_changes_during_read(
    workspace, monkeypatch
):
    api, _, records, scope = workspace
    project = records.read(scope, [scope])[scope]
    folder_id = project["value"]["directory"]["root"]
    folder = records.read(scope, [folder_id])[folder_id]
    node_id = folder["value"]["root"]["id"]
    call, changed = api.call, False

    def interleave(operation, **arguments):
        nonlocal changed
        if (
            operation == "e2eeReadRecords"
            and not changed
            and arguments["body"]["scopes"][0]["record_ids"] == [node_id]
        ):
            changed = True
            EncryptedDirectory(records, scope).insert(
                {
                    "id": "added",
                    "name": "added",
                    "kind": "file",
                    "parentFolderId": None,
                },
                key_epoch=1,
                additional_records=[],
            )
        return call(operation, **arguments)

    monkeypatch.setattr(api, "call", interleave)
    page = EncryptedDirectory(records, scope).page()
    assert changed
    assert [entry["id"] for entry in page["entries"]] == ["added"]


class MigrationAPI(MemoryAPI):
    def __init__(self, source_scan_batches=0):
        super().__init__(E2eeCrypto())
        self.migration = None
        self.source_scan_batches = source_scan_batches
        self.created = set()

    def call(self, operation, *, body=None, **parameters):
        if operation == "e2eeGetMigration":
            return {"migration": deepcopy(self.migration)}
        if operation == "e2eeGetMigrationCreated":
            ids = sorted(self.created)
            limit = parameters["limit"]
            return {"record_ids": ids[:limit], "has_more": len(ids) > limit}
        if operation == "e2eeWriteRecords":
            command = json.loads(decode(body["body_bytes"]))
            maintenance = command.get("maintenance")
            if (
                self.migration
                and self.migration["state"] in {"building", "aborting"}
                and maintenance is None
            ):
                raise E2eeError("revision_conflict")
            if maintenance is not None:
                checkpoint_revision = (
                    self.migration["checkpoint_revision"]
                    if self.migration and maintenance["action"] != "begin"
                    else 0
                )
                if maintenance["expected_checkpoint_revision"] != checkpoint_revision:
                    raise E2eeError("revision_conflict")
                if maintenance["action"] == "complete":
                    assert self.migration["source_scan_complete"]
                result = super().call(operation, body=body, **parameters)
                if maintenance["action"] == "begin":
                    self.created.clear()
                self.created.update(maintenance["created_record_ids"])
                self.created.difference_update(
                    record["record_id"]
                    for record in command["records"]
                    if record["deleted"]
                )
                checkpoint_deleted = next(
                    record["deleted"]
                    for record in command["records"]
                    if record["record_id"] == maintenance["checkpoint_record_id"]
                )
                state = {
                    "complete": "complete",
                    "abort": "aborted" if checkpoint_deleted else "aborting",
                }.get(maintenance["action"], "building")
                self.migration = {
                    "migration_id": maintenance["migration_id"],
                    "state": state,
                    "created_record_count": len(self.created),
                    "checkpoint_record_id": maintenance["checkpoint_record_id"],
                    "checkpoint_revision": checkpoint_revision + 1,
                    "source_scan_complete": checkpoint_revision + 1
                    >= self.source_scan_batches,
                }
                return result
        return super().call(operation, body=body, **parameters)


@pytest.mark.parametrize("source_scan_batches", [0, 12])
def test_directory_migration_resumes_from_encrypted_checkpoint_and_preserves_ids(
    source_scan_batches,
):
    api = MigrationAPI(source_scan_batches)
    session, _, _ = new_session(api, setup=True)
    records = EncryptedRecords(session)
    scope = records.create_project(value={"title": "legacy"}, owner_org="org-test")
    project = records.read(scope, [scope])[scope]
    project["value"].pop("directory")
    entries = [
        {
            "id": f"entry-{index}",
            "name": f"name-{index:03}",
            "kind": "file",
            "fileId": f"file-{index}",
            "parentFolderId": None,
        }
        for index in range(70)
    ]
    entries.extend(
        [
            {
                "id": "folder-a",
                "name": "folder",
                "kind": "folder",
                "parentFolderId": None,
            },
            {
                "id": "child",
                "name": "child",
                "kind": "file",
                "fileId": "existing-file",
                "parentFolderId": "folder-a",
            },
        ]
    )
    records.write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": scope,
                "kind": "project",
                "expected_revision": 1,
                "value": project["value"],
            },
            {
                "record_id": "old-directory",
                "kind": "directory",
                "expected_revision": 0,
                "value": {"entries": entries},
            },
        ],
    )
    for _ in range(30):
        result = migrate_directory(EncryptedRecords(session), scope, maximum_batches=1)
        if result["complete"]:
            break
    assert result["complete"]
    directory = EncryptedDirectory(records, scope)
    assert {entry["id"] for entry in directory.page()["entries"]} == {
        entry["id"] for entry in entries if entry["parentFolderId"] is None
    }
    assert directory.page(folder_id="folder-a")["entries"] == [entries[-1]]
    assert records.read(scope, ["old-directory"])["old-directory"]["deleted"]
    assert api.migration["state"] == "complete"


def test_migration_abort_resumes_without_deleting_legacy_and_can_restart():
    api = MigrationAPI()
    session, _, _ = new_session(api, setup=True)
    records = EncryptedRecords(session)
    scope = records.create_project(value={"title": "legacy"}, owner_org="org-test")
    project = records.read(scope, [scope])[scope]
    project["value"].pop("directory")
    entries = [
        {
            "id": f"folder-{index}",
            "name": f"folder-{index:03}",
            "kind": "folder",
            "parentFolderId": None,
        }
        for index in range(130)
    ]
    records.write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": scope,
                "kind": "project",
                "expected_revision": 1,
                "value": project["value"],
            },
            {
                "record_id": "old-directory",
                "kind": "directory",
                "expected_revision": 0,
                "value": {"entries": entries},
            },
        ],
    )
    migrate_directory(records, scope, maximum_batches=1)
    checkpoint_id = api.migration["checkpoint_record_id"]
    assert api.migration["created_record_count"] > 128
    result = abort_directory_migration(records, scope, maximum_batches=1)
    assert result == {"phase": "aborting", "complete": False}
    assert not records.read(scope, [checkpoint_id])[checkpoint_id]["deleted"]
    result = abort_directory_migration(records, scope, maximum_batches=1)
    assert result == {"phase": "aborted", "complete": True}
    checkpoint = records.read(scope, [checkpoint_id])[checkpoint_id]
    assert checkpoint["deleted"] and checkpoint["value"] == {}
    assert not records.read(scope, ["old-directory"])["old-directory"]["deleted"]
    assert "directory" not in records.read(scope, [scope])[scope]["value"]
    assert not api.created
    assert migrate_directory(records, scope)["complete"]
    page = EncryptedDirectory(records, scope).page(limit=200)
    assert len(page["entries"]) == 130
    with pytest.raises(E2eeError, match="migration_already_published"):
        abort_directory_migration(records, scope)
