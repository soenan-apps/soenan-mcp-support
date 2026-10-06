from __future__ import annotations

import json
import sys
from copy import deepcopy

import pytest
from test_e2ee import new_session
from test_e2ee_recovery_transfer import RecoveryAndObjectAPI

from soenan_arteligo_support.e2ee import (
    DeviceSession,
    E2eeCrypto,
    E2eeError,
    EncryptedRecords,
    _cli,
)
from soenan_arteligo_support.e2ee._crypto import decode


class RecoveryReplacementAPI(RecoveryAndObjectAPI):
    def call(self, operation, *, body=None, **parameters):
        value = (
            json.loads(decode(body["body_bytes"]))
            if body and "body_bytes" in body
            else None
        )
        if operation != "e2eeRotateRecovery":
            return super().call(operation, body=body, **parameters)
        expected = {
            (project["project_id"], project["key_epoch"])
            for project in self.projects.values()
        }
        envelopes = value["envelopes"]
        if (
            value["generation"] != self.recovery["generation"] + 1
            or {(item["scope_id"], item["key_epoch"]) for item in envelopes} != expected
            or len(envelopes) != len(expected)
            or any(
                item["recipient_kind"] != "recovery"
                or item["recipient_id"] != value["recovery_id"]
                for item in envelopes
            )
        ):
            raise E2eeError("revision_conflict")
        archived = {
            project["project_id"]
            for project in self.projects.values()
            if project["lifecycle"] == "archived"
        }
        result = super().call(operation, body=body, **parameters)
        self.envelopes.extend(deepcopy(envelopes))
        for identifier in archived:
            self.projects[identifier]["lifecycle"] = "archived"
        return result


@pytest.fixture
def recovery_workspace():
    api = RecoveryReplacementAPI(E2eeCrypto())
    owner, store, old_code = new_session(api, setup=True)
    scopes = {}
    for role, lifecycle in (
        ("owner", "active"),
        ("viewer", "active"),
        ("owner", "archived"),
    ):
        scope = EncryptedRecords(owner).create_project(
            value={"title": f"{role} {lifecycle}"}, owner_org="org-test"
        )
        api.projects[scope].update(role=role, lifecycle=lifecycle)
        scopes[(role, lifecycle)] = scope
    return api, owner, store, old_code, scopes


@pytest.mark.parametrize("failure", ["request", "response", "rekey"])
def test_recovery_replacement_resumes_the_confirmed_code_after_restart(
    recovery_workspace, monkeypatch, failure
):
    api, owner, store, old_code, scopes = recovery_workspace
    draft = owner.prepare_recovery_replacement()
    identifier = draft["recovery"]["recovery_id"]
    original = api.call
    failed = False

    def interrupt(operation, **parameters):
        nonlocal failed
        if not failed and (
            (failure == "request" and operation == "e2eeRotateRecovery")
            or (failure == "rekey" and operation == "e2eeRotateScope")
        ):
            failed = True
            raise E2eeError("service_unavailable")
        result = original(operation, **parameters)
        if not failed and failure == "response" and operation == "e2eeRotateRecovery":
            failed = True
            raise E2eeError("service_unavailable")
        return result

    monkeypatch.setattr(api, "call", interrupt)
    with pytest.raises(E2eeError, match="service_unavailable"):
        owner.replace_recovery(draft)
    assert owner.recovery_replacement_pending
    saved = json.dumps(store.values)
    assert draft["code"] not in saved and old_code not in saved
    pending = json.loads(store.read(owner._storage_key))["recovery_replacement"]
    assert "envelopes" not in pending and "device_roots" not in pending
    with pytest.raises(E2eeError, match="recovery_replacement_pending"):
        owner.prepare_recovery_replacement()
    owner.lock()

    resumed = DeviceSession(
        api,
        api.crypto,
        store,
        origin="https://arteligo.test",
        subject="account-subject",
    )
    assert resumed.refresh() == "approved"
    assert resumed.recovery_replacement_pending
    with pytest.raises(E2eeError, match="authentication_failed"):
        resumed.resume_recovery_replacement(old_code)
    resumed.resume_recovery_replacement(draft["code"])
    assert not resumed.recovery_replacement_pending
    assert api.recovery["recovery_id"] == identifier
    assert api.recovery["generation"] == 2
    assert (
        sum(operation == "e2eeRotateRecovery" for operation, _, _ in api.commands) == 1
    )
    assert api.projects[scopes[("owner", "active")]]["key_epoch"] == 2
    assert api.projects[scopes[("viewer", "active")]]["key_epoch"] == 1
    assert api.projects[scopes[("owner", "archived")]]["key_epoch"] == 1
    for scope in scopes.values():
        assert EncryptedRecords(resumed).read(scope, [scope])[scope]["value"]["title"]


@pytest.mark.parametrize("failure", ["response", "rekey"])
def test_new_code_recovers_all_existing_scopes_when_the_last_device_is_lost(
    recovery_workspace, monkeypatch, failure
):
    api, owner, _, _, scopes = recovery_workspace
    draft = owner.prepare_recovery_replacement()
    original = api.call
    failed = False

    def interrupt(operation, **parameters):
        nonlocal failed
        if not failed and failure == "rekey" and operation == "e2eeRotateScope":
            failed = True
            raise E2eeError("service_unavailable")
        result = original(operation, **parameters)
        if not failed and failure == "response" and operation == "e2eeRotateRecovery":
            failed = True
            raise E2eeError("service_unavailable")
        return result

    monkeypatch.setattr(api, "call", interrupt)
    with pytest.raises(E2eeError, match="service_unavailable"):
        owner.replace_recovery(draft)
    owner.lock()
    recovered, _, _ = new_session(api)
    recovered.restore(draft["code"])
    assert recovered.state == "approved"
    for (role, lifecycle), scope in scopes.items():
        assert (
            EncryptedRecords(recovered).read(scope, [scope])[scope]["value"]["title"]
            == f"{role} {lifecycle}"
        )


def test_epoch_conflict_keeps_the_old_root_and_can_resume_the_same_new_code(
    recovery_workspace,
):
    api, owner, _, _, scopes = recovery_workspace
    draft = owner.prepare_recovery_replacement()
    previous_root = api.recovery["recovery_id"]
    scope = scopes[("owner", "active")]
    owner.rotate_scope(deepcopy(api.projects[scope]))
    with pytest.raises(E2eeError, match="revision_conflict"):
        owner.replace_recovery(draft)
    assert api.recovery["recovery_id"] == previous_root
    assert owner.recovery_replacement_pending
    owner.resume_recovery_replacement(draft["code"])
    assert api.recovery["recovery_id"] == draft["recovery"]["recovery_id"]
    assert not owner.recovery_replacement_pending


@pytest.mark.parametrize("tampered", [False, True])
def test_superseded_replacement_checks_the_latest_root_before_clearing_pending(
    recovery_workspace, monkeypatch, tampered
):
    api, owner, _, _, _ = recovery_workspace
    peer, _, _ = new_session(api)
    peer.accept_approval(owner.approve(peer.enroll()))
    first = owner.prepare_recovery_replacement()
    original = api.call
    failed = False

    def lose_response(operation, **parameters):
        nonlocal failed
        result = original(operation, **parameters)
        if operation == "e2eeRotateRecovery" and not failed:
            failed = True
            raise E2eeError("service_unavailable")
        return result

    monkeypatch.setattr(api, "call", lose_response)
    with pytest.raises(E2eeError, match="service_unavailable"):
        owner.replace_recovery(first)
    peer.refresh()
    second = peer.prepare_recovery_replacement()
    peer.replace_recovery(second)
    assert api.recovery["generation"] == 3
    old_root = deepcopy(owner.recovery)
    authentic = deepcopy(api.recovery)
    if tampered:
        api.recovery["encryption_public_key"] = first["recovery"][
            "encryption_public_key"
        ]
        with pytest.raises(E2eeError, match="untrusted_recovery"):
            owner.resume_recovery_replacement(first["code"])
        assert owner.recovery_replacement_pending
        assert owner.recovery == old_root
        api.recovery = authentic
    with pytest.raises(E2eeError, match="recovery_replacement_superseded"):
        owner.resume_recovery_replacement(first["code"])
    assert not owner.recovery_replacement_pending
    assert owner.recovery["recovery_id"] == second["recovery"]["recovery_id"]
    assert owner.prepare_recovery_replacement()["recovery"]["generation"] == 4
    assert (
        sum(operation == "e2eeRotateRecovery" for operation, _, _ in api.commands) == 2
    )


def test_new_recovery_root_opens_old_records_through_a_cold_project_key_chain():
    api = RecoveryReplacementAPI(E2eeCrypto())
    owner, _, _ = new_session(api, setup=True)
    scope = EncryptedRecords(owner).create_project(
        value={"title": "初期 epoch の記録"}, owner_org="org-test"
    )
    owner.rotate_scope(deepcopy(api.projects[scope]))
    api.projects[scope]["role"] = "viewer"
    draft = owner.prepare_recovery_replacement()
    owner.replace_recovery(draft)
    owner.lock()
    recovered, _, _ = new_session(api)
    recovered.restore(draft["code"])
    assert api.projects[scope]["key_epoch"] == 2
    assert api.records[scope][scope]["key_epoch"] == 1
    current_recipients = {draft["recovery"]["recovery_id"], recovered.device_id}
    assert all(
        envelope["key_epoch"] == 2
        for envelope in api.envelopes
        if envelope["scope_id"] == scope
        and envelope["recipient_id"] in current_recipients
    )
    assert (
        EncryptedRecords(recovered).read(scope, [scope])[scope]["value"]["title"]
        == "初期 epoch の記録"
    )


@pytest.mark.parametrize("revocation", ["explicit", "restore"])
def test_replacement_proves_only_previously_approved_revoked_devices(
    recovery_workspace, revocation
):
    api, owner, _, old_code, _ = recovery_workspace
    historical, _, _ = new_session(api)
    historical.accept_approval(owner.approve(historical.enroll()))
    pending, _, _ = new_session(api)
    pending.enroll()
    api.devices[pending.device_id]["certificates"] = [
        {
            "operation": "device_enroll",
            "signed_command": deepcopy(api.commands[-1][1]),
        }
    ]
    approved_ids = {owner.device_id, historical.device_id}
    if revocation == "explicit":
        for identifier in (historical.device_id, pending.device_id):
            api.devices[identifier]["state"] = "revoked"
    else:
        owner.lock()
        owner, _, _ = new_session(api)
        owner.restore(old_code)
        approved_ids.add(owner.device_id)
    assert api.devices[pending.device_id]["state"] == "revoked"
    changed = api.devices[historical.device_id]
    authentic = changed["encryption_public_key"]
    changed["encryption_public_key"] = pending.public["encryption_public_key"]
    with pytest.raises(E2eeError):
        owner.prepare_recovery_replacement()
    changed["encryption_public_key"] = authentic
    draft = owner.prepare_recovery_replacement()
    proof_ids = {
        proof["public_device"]["device_id"]
        for proof in draft["recovery"]["device_roots"]
    }
    assert proof_ids == approved_ids
    assert pending.device_id not in proof_ids
    owner.replace_recovery(draft)
    assert not owner.recovery_replacement_pending
    assert all(
        certificate["operation"] == "device_enroll"
        for certificate in api.devices[pending.device_id]["certificates"]
    )


def test_recovery_replacement_has_no_envelope_for_an_uninitialized_organization(
    monkeypatch,
):
    api = RecoveryReplacementAPI(E2eeCrypto())
    owner, _, _ = new_session(api, setup=True)
    original = api.call

    def organizations(operation, **parameters):
        if operation == "e2eeListOrganizations":
            return {
                "projects": [
                    {
                        "project_id": "org-unused",
                        "owner_org": "org-unused",
                        "key_epoch": 0,
                        "lifecycle": "uninitialized",
                        "role": "owner",
                    }
                ]
            }
        return original(operation, **parameters)

    monkeypatch.setattr(api, "call", organizations)
    draft = owner.prepare_recovery_replacement()
    assert draft["recovery"]["envelopes"] == []
    owner.replace_recovery(draft)
    assert not owner.recovery_replacement_pending


def test_cli_reports_pending_replacement_and_resumes_without_generating_a_code(
    recovery_workspace, monkeypatch, capsys
):
    api, owner, store, _, _ = recovery_workspace
    draft = owner.prepare_recovery_replacement()
    original = api.call

    def interrupted(operation, **parameters):
        result = original(operation, **parameters)
        if operation == "e2eeRotateRecovery":
            raise E2eeError("service_unavailable")
        return result

    monkeypatch.setattr(api, "call", interrupted)
    with pytest.raises(E2eeError, match="service_unavailable"):
        owner.replace_recovery(draft)
    monkeypatch.setattr(api, "call", original)
    owner.lock()

    def connect(**_kwargs):
        session = DeviceSession(
            api,
            api.crypto,
            store,
            origin="https://arteligo.test",
            subject="account-subject",
        )
        session.refresh()
        return session

    monkeypatch.setattr(_cli, "SystemSecureStore", lambda _profile: store)
    monkeypatch.setattr(_cli, "open_session", connect)
    arguments = [
        "arteligo",
        "--account-origin",
        "https://account.test",
        "--arteligo-origin",
        "https://arteligo.test",
    ]
    monkeypatch.setattr(sys, "argv", [*arguments, "status"])
    assert _cli.main() == 0
    assert json.loads(capsys.readouterr().out)["recovery_replacement_pending"] is True
    monkeypatch.setattr(sys, "argv", [*arguments, "replace-recovery"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(_cli.getpass, "getpass", lambda _prompt: draft["code"])
    assert _cli.main() == 0
    output = capsys.readouterr().out
    assert "交換を完了" in output
    assert draft["code"] not in output
    assert api.recovery["recovery_id"] == draft["recovery"]["recovery_id"]
    assert api.recovery["generation"] == 2
