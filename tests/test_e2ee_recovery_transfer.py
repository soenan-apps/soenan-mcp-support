from __future__ import annotations

import json
from copy import deepcopy
from types import SimpleNamespace

import httpx
import pytest
from test_e2ee import MemoryAPI, new_session

from soenan_arteligo_support.e2ee import (
    DeviceSession,
    E2eeCrypto,
    E2eeError,
    EncryptedRecords,
)
from soenan_arteligo_support.e2ee._api import GeneratedAPI
from soenan_arteligo_support.e2ee._crypto import decode, encode
from soenan_arteligo_support.transfer import upload_file
from soenan_arteligo_support.transfer._workflow import snapshot


class RecoveryAndObjectAPI(MemoryAPI):
    def call(self, operation, *, body=None, **params):
        if operation == "e2eeGetEnvelopes" and "epoch" not in params:
            return {
                "envelopes": deepcopy(
                    [
                        item
                        for item in self.envelopes
                        if item["scope_id"] == params["scope_id"]
                        and item["recipient_id"] == params["recipient_id"]
                        and item["recipient_kind"] == params["recipient_kind"]
                    ]
                )
            }
        value = json.loads(decode(body["body_bytes"])) if body else None
        if (
            operation == "e2eeWriteRecords"
            and self.projects[value["scope_id"]]["lifecycle"] == "rekey_required"
        ):
            raise E2eeError("rekey_required")
        if (
            operation == "e2eePutObjectCapability"
            and self.objects[value["object_id"]]["state"] != "uploading"
        ):
            raise E2eeError("revision_conflict")
        result = super().call(operation, body=body, **params)
        if operation == "e2eeRestoreRecovery":
            for device in self.devices.values():
                if device["device_id"] != value["device"]["device_id"]:
                    device["state"] = "revoked"
            for project in self.projects.values():
                project["lifecycle"] = "rekey_required"
        return result


@pytest.fixture
def workspace():
    api = RecoveryAndObjectAPI(E2eeCrypto())
    owner, _, code = new_session(api, setup=True)
    scope = EncryptedRecords(owner).create_project(
        value={"title": "復旧と再開"}, owner_org="org-test"
    )
    return api, owner, code, scope


@pytest.mark.parametrize(
    "failure", ["restore_request", "restore_response", "envelope", "rotation"]
)
def test_restore_resumes_same_device_and_finishes_authorized_rekey(
    workspace, monkeypatch, failure
):
    api, owner, code, first = workspace
    second = EncryptedRecords(owner).create_project(
        value={"title": "第二のプロジェクト"}, owner_org="org-test"
    )
    restored, store, _ = new_session(api)
    call = api.call
    failed = False

    def interrupt(operation, *, body=None, **params):
        nonlocal failed
        value = json.loads(decode(body["body_bytes"])) if body else {}
        if not failed and (
            (failure == "restore_request" and operation == "e2eeRestoreRecovery")
            or (failure == "envelope" and operation == "e2eeSaveEnvelopes")
            or (
                failure == "rotation"
                and operation == "e2eeRotateScope"
                and value["scope_id"] == second
            )
        ):
            failed = True
            raise E2eeError("service_unavailable")
        result = call(operation, body=body, **params)
        if (
            not failed
            and failure == "restore_response"
            and operation == "e2eeRestoreRecovery"
        ):
            failed = True
            raise E2eeError("service_unavailable")
        return result

    monkeypatch.setattr(api, "call", interrupt)
    with pytest.raises(E2eeError, match="service_unavailable"):
        restored.restore(code)
    new_device = restored.device_id
    assert restored.state == "recovery_pending"
    assert code not in json.dumps(store.values)
    assert "recovery_restore" in json.loads(store.read(restored._storage_key))
    with pytest.raises(E2eeError, match="device_approval_required"):
        restored.require_approved()
    restored.lock()

    resumed = DeviceSession(
        api,
        api.crypto,
        store,
        origin="https://arteligo.test",
        subject="account-subject",
    )
    assert resumed.refresh() == "recovery_pending"
    resumed.restore(code)
    assert resumed.state == "approved"
    assert resumed.device_id == new_device
    assert api.devices[owner.device_id]["state"] == "revoked"
    assert "recovery_restore" not in json.loads(store.read(resumed._storage_key))
    assert sum(name == "e2eeRestoreRecovery" for name, _, _ in api.commands) == 1
    for scope in (first, second):
        assert api.projects[scope]["lifecycle"] == "active"
        assert api.projects[scope]["key_epoch"] == 2
        assert EncryptedRecords(resumed).page(scope)["records"][0]["value"]["title"]
        EncryptedRecords(resumed).write(
            scope,
            key_epoch=2,
            records=[
                {
                    "record_id": "after-recovery",
                    "kind": "chat",
                    "expected_revision": 0,
                    "value": {"text": "書き込みを再開"},
                }
            ],
        )


def test_restore_does_not_rotate_a_viewer_scope(workspace):
    api, _, code, scope = workspace
    api.projects[scope]["role"] = "viewer"
    restored, _, _ = new_session(api)
    restored.restore(code)
    assert restored.state == "approved"
    assert api.projects[scope]["key_epoch"] == 1
    assert api.projects[scope]["lifecycle"] == "rekey_required"
    assert not any(name == "e2eeRotateScope" for name, _, _ in api.commands)
    assert EncryptedRecords(restored).page(scope)["records"]


@pytest.mark.parametrize("initialized", [False, True])
def test_restore_handles_initialized_and_uninitialized_organization_scopes(
    workspace, monkeypatch, initialized
):
    api, owner, code, project = workspace
    organization = {
        "project_id": "org-test",
        "owner_org": "org-test",
        "role": "owner",
        "lifecycle": "active" if initialized else "uninitialized",
        "key_epoch": 1 if initialized else 0,
    }
    if initialized:
        api.projects["org-test"] = organization
        key = api.crypto.key()
        for recipient, kind, public in (
            (owner.device_id, "device", owner.public["encryption_public_key"]),
            (
                api.recovery["recovery_id"],
                "recovery",
                api.recovery["encryption_public_key"],
            ),
        ):
            api.envelopes.append(
                owner.wrap_key(
                    "org-test",
                    1,
                    key,
                    recipient=recipient,
                    kind=kind,
                    public_key=public,
                )
            )
    call = api.call

    def scopes(operation, **kwargs):
        if operation == "e2eeListOrganizations":
            return {"projects": [deepcopy(organization)]}
        if operation == "e2eeListProjects":
            return {"projects": [deepcopy(api.projects[project])]}
        return call(operation, **kwargs)

    monkeypatch.setattr(api, "call", scopes)
    restored, _, _ = new_session(api)
    restored.restore(code)
    assert restored.state == "approved"
    assert api.projects[project]["key_epoch"] == 2
    assert organization["key_epoch"] == (2 if initialized else 0)
    assert organization["lifecycle"] == ("active" if initialized else "uninitialized")


def test_restore_keeps_pending_when_conflicts_leave_scope_unrekeyed(
    workspace, monkeypatch
):
    api, _, code, _ = workspace
    restored, _, _ = new_session(api)
    call = api.call
    attempts = 0

    def conflict(operation, **kwargs):
        nonlocal attempts
        if operation == "e2eeRotateScope":
            attempts += 1
            raise E2eeError("revision_conflict")
        return call(operation, **kwargs)

    monkeypatch.setattr(api, "call", conflict)
    with pytest.raises(E2eeError, match="rekey_required"):
        restored.restore(code)
    assert attempts == 3
    assert restored.state == "recovery_pending"


@pytest.mark.parametrize(
    "failure", ["finalize_response", "metadata_response", "directory_conflict"]
)
def test_ready_upload_resumes_metadata_without_reupload_or_duplicates(
    workspace, tmp_path, monkeypatch, failure
):
    api, session, _, scope = workspace
    source = tmp_path / "音声.wav"
    source.write_bytes(b"unchanged source" * 100)
    puts = []
    monkeypatch.setattr(
        "soenan_arteligo_support.transfer._workflow.put_ciphertext",
        lambda *args, **kwargs: puts.append(args[2]),
    )
    if failure == "directory_conflict":
        EncryptedRecords(session).write(
            scope,
            key_epoch=1,
            records=[
                {
                    "record_id": "directory-page",
                    "kind": "directory",
                    "expected_revision": 0,
                    "value": {"entries": []},
                }
            ],
        )
    call = api.call
    failed = False

    def interrupt(operation, *, body=None, **params):
        nonlocal failed
        value = json.loads(decode(body["body_bytes"])) if body else {}
        metadata_write = operation == "e2eeWriteRecords" and any(
            item["record_id"].startswith("fil_") for item in value["records"]
        )
        if not failed and failure == "directory_conflict" and metadata_write:
            failed = True
            EncryptedRecords(session).write(
                scope,
                key_epoch=1,
                records=[
                    {
                        "record_id": "directory-page",
                        "kind": "directory",
                        "expected_revision": 1,
                        "value": {"entries": [{"id": "other-entry", "kind": "folder"}]},
                    }
                ],
            )
        result = call(operation, body=body, **params)
        if not failed and (
            (failure == "finalize_response" and operation == "e2eeFinalizeObject")
            or (failure == "metadata_response" and metadata_write)
        ):
            failed = True
            raise E2eeError("service_unavailable")
        return result

    monkeypatch.setattr(api, "call", interrupt)
    with pytest.raises(E2eeError, match="revision_conflict|service_unavailable"):
        upload_file(session, project_id=scope, source=source)
    identifier = next(iter(api.objects))
    assert api.objects[identifier]["state"] == "ready"
    assert len(puts) == 1
    uploaded = upload_file(
        session, project_id=scope, source=source, upload_id=identifier
    )
    assert uploaded["object_id"] == identifier
    assert len(puts) == 1
    assert sum(name == "e2eeFinalizeObject" for name, _, _ in api.commands) == 1
    saved = deepcopy(api.records)
    assert (
        upload_file(session, project_id=scope, source=source, upload_id=identifier)
        == uploaded
    )
    assert api.records == saved
    current = snapshot(session, scope)
    assert current["upl_" + identifier]["deleted"]
    assert current[uploaded["file_id"]]["value"]["sourceState"] == "ready"
    entries = [
        entry
        for item in current.values()
        if item["kind"] == "directory"
        for entry in item["value"]["entries"]
    ]
    assert sum(entry.get("fileId") == uploaded["file_id"] for entry in entries) == 1
    if failure == "directory_conflict":
        assert any(entry["id"] == "other-entry" for entry in entries)
    source.write_bytes(b"X" * source.stat().st_size)
    with pytest.raises(E2eeError, match="source_changed"):
        upload_file(session, project_id=scope, source=source, upload_id=identifier)
    assert api.records == saved
    assert len(puts) == 1


def test_organization_envelope_binds_generation_to_authenticated_context(workspace):
    api, session, _, scope = workspace
    organization = api.crypto.keypair()
    key = session.scope_key(scope, 1)
    envelope = session.wrap_key(
        scope,
        1,
        key,
        recipient="org-test",
        kind="organization",
        public_key=organization["encryption_public_key"],
        organization_epoch=7,
    )
    assert envelope["organization_epoch"] == 7
    command = session.sign("envelopes_save", {"envelopes": [envelope]})
    assert (
        api.crypto.verify(
            session.public["signing_public_key"], "envelopes_save", command
        )["envelopes"][0]["organization_epoch"]
        == 7
    )
    api.envelopes.append(envelope)
    session._remember("org-test", 7, decode(organization["encryption_secret_key"]))
    session._remember("org-test", 8, api.crypto.key())

    def open_key(epoch):
        return session._read_key(
            scope,
            1,
            recipient="org-test",
            kind="organization",
            organization_epoch=epoch,
        )

    assert open_key(7) == key
    assert open_key(8) == key
    envelope["organization_epoch"] = 8
    with pytest.raises(E2eeError):
        open_key(8)
    session._remember("org-test", 8, decode(organization["encryption_secret_key"]))
    with pytest.raises(E2eeError):
        open_key(8)
    envelope.pop("organization_epoch")
    with pytest.raises(E2eeError):
        open_key(7)

    context = api.crypto.canonical(
        {
            "v": 1,
            "domain": "arteligo.scope-key",
            **{
                field: envelope[field]
                for field in (
                    "scope_id",
                    "key_epoch",
                    "sender_device_id",
                    "recipient_id",
                    "recipient_kind",
                )
            },
        }
    )
    legacy = api.crypto.execute(
        {
            "op": "hpke_auth_seal",
            "sender_secret_key": session._device["encryption_secret_key"],
            "recipient_public_key": organization["encryption_public_key"],
            "plaintext": encode(key),
            "info": encode(context),
            "aad": encode(context),
        }
    )
    envelope.update(encapsulated_key=legacy["enc"], ciphertext=legacy["ciphertext"])
    assert open_key(7) == key


@pytest.mark.parametrize("action", ["create", "rotate"])
def test_organization_project_commands_wrap_with_observed_organization_epoch(
    workspace, monkeypatch, action
):
    api, session, _, existing = workspace
    org_key = api.crypto.key()
    session._remember("org-test", 5, org_key)
    call = api.call

    def with_organization(operation, **kwargs):
        if operation == "e2eeListOrganizations":
            return {
                "projects": [
                    {
                        "project_id": "org-test",
                        "owner_org": "org-test",
                        "key_epoch": 5,
                        "role": "owner",
                        "lifecycle": "active",
                    }
                ]
            }
        response = call(operation, **kwargs)
        if operation == "e2eeGetRecipients":
            response.update(organization_id="org-test", organization_epoch=5)
        return response

    monkeypatch.setattr(api, "call", with_organization)
    if action == "create":
        scope = EncryptedRecords(session).create_project(
            value={"title": "組織のプロジェクト"},
            owner_org="org-test",
            participation_policy="organization",
        )
        epoch = 1
    else:
        scope, epoch = existing, 2
        session.rotate_scope(api.projects[scope])
    envelope = next(
        item
        for item in api.envelopes
        if (
            item["scope_id"] == scope
            and item["key_epoch"] == epoch
            and item["recipient_kind"] == "organization"
        )
    )
    assert envelope["organization_epoch"] == 5
    assert session._read_key(
        scope,
        epoch,
        recipient="org-test",
        kind="organization",
        organization_epoch=6,
    ) == session.scope_key(scope, epoch)


@pytest.mark.parametrize(
    "kind,epoch",
    [
        ("organization", None),
        ("organization", 0),
        ("organization", True),
        ("device", 1),
        ("recovery", 1),
    ],
)
def test_envelope_rejects_missing_or_misplaced_organization_epoch(
    workspace, kind, epoch
):
    _, session, _, scope = workspace
    with pytest.raises(E2eeError, match="invalid_envelope"):
        session.wrap_key(
            scope,
            1,
            session.scope_key(scope, 1),
            recipient="recipient",
            kind=kind,
            public_key=session.public["encryption_public_key"],
            organization_epoch=epoch,
        )


def test_generated_transport_preserves_bound_organization_epoch(workspace):
    _, session, _, scope = workspace
    envelope = session.wrap_key(
        scope,
        1,
        session.scope_key(scope, 1),
        recipient="org-test",
        kind="organization",
        public_key=session.public["encryption_public_key"],
        organization_epoch=7,
    )
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"envelopes": [envelope]})
    )
    api = GeneratedAPI(
        SimpleNamespace(
            arteligo_origin="https://arteligo.test", access_token=lambda: "test-token"
        ),
        transport=transport,
    )
    assert api.call(
        "e2eeGetEnvelopes",
        scope_id=scope,
        epoch=1,
        recipient_id="org-test",
        recipient_kind="organization",
    )["envelopes"] == [envelope]
