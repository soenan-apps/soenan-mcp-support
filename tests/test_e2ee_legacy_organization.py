from __future__ import annotations

import json
from copy import deepcopy

import pytest
from test_e2ee import new_session
from test_e2ee_recovery_transfer import RecoveryAndObjectAPI

from soenan_arteligo_support.e2ee import (
    DeviceSession,
    E2eeCrypto,
    E2eeError,
    EncryptedRecords,
)
from soenan_arteligo_support.e2ee._crypto import decode, encode


class OrganizationAPI(RecoveryAndObjectAPI):
    def __init__(self, crypto):
        super().__init__(crypto)
        self.reads = []

    def call(self, operation, *, body=None, **params):
        if body is None:
            self.reads.append((operation, deepcopy(params)))
            if operation == "e2eeListOrganizations":
                return {"projects": [deepcopy(self.projects["org-test"])]}
            if operation == "e2eeListProjects":
                return {
                    "projects": deepcopy(
                        [
                            value
                            for key, value in self.projects.items()
                            if key != "org-test"
                        ]
                    )
                }
        result = super().call(operation, body=body, **params)
        if operation == "e2eeGetRecipients" and params["scope_id"] != "org-test":
            result.update(
                organization_id="org-test",
                organization_epoch=self.projects["org-test"]["key_epoch"],
            )
        if operation == "e2eeRotateScope":
            value = json.loads(decode(body["body_bytes"]))
            if value["scope_id"] == "org-test":
                for project in self.projects.values():
                    if project["project_id"] != "org-test":
                        project["lifecycle"] = "rekey_required"
        return result


@pytest.fixture
def legacy_project():
    api = OrganizationAPI(E2eeCrypto())
    owner, store, code = new_session(api, setup=True)
    organization = {
        "project_id": "org-test",
        "owner_org": "org-test",
        "participation_policy": "organization",
        "key_epoch": 1,
        "role": "owner",
        "lifecycle": "active",
    }
    api.projects["org-test"] = organization
    org_key = api.crypto.key()
    org_public = api.crypto.execute(
        {
            "op": "public_keys",
            "encryption_secret_key": encode(org_key),
            "signing_secret_key": encode(bytes(32)),
        }
    )["encryption_public_key"]
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
                org_key,
                recipient=recipient,
                kind=kind,
                public_key=public,
            )
        )
    project = EncryptedRecords(owner).create_project(
        owner_org="org-test",
        value={"title": "旧組織鍵で暗号化したプロジェクト"},
    )
    api.projects[project]["participation_policy"] = "organization"
    project_key = owner.scope_key(project, 1)
    api.envelopes = [item for item in api.envelopes if item["scope_id"] != project]
    fields = {
        "scope_id": project,
        "key_epoch": 1,
        "recipient_id": "org-test",
        "recipient_kind": "organization",
        "sender_device_id": owner.device_id,
    }
    context = api.crypto.canonical({"v": 1, "domain": "arteligo.scope-key", **fields})
    sealed = api.crypto.execute(
        {
            "op": "hpke_auth_seal",
            "sender_secret_key": owner._device["encryption_secret_key"],
            "recipient_public_key": org_public,
            "plaintext": encode(project_key),
            "info": encode(context),
            "aad": encode(context),
        }
    )
    legacy = {
        **fields,
        "encapsulated_key": sealed["enc"],
        "ciphertext": sealed["ciphertext"],
    }
    api.envelopes.append(legacy)
    owner.rotate_scope(organization)
    owner.lock()
    api.reads.clear()
    return api, store, code, project, legacy


def reopen(api, store):
    session = DeviceSession(
        api,
        api.crypto,
        store,
        origin="https://arteligo.test",
        subject="account-subject",
    )
    assert session.refresh() == "approved"
    return session


def historical_queries(api):
    return [
        params
        for operation, params in api.reads
        if operation == "e2eeGetEnvelopes" and "epoch" not in params
    ]


def test_cold_org_only_admin_rekeys_legacy_project_using_own_saved_device_envelope(
    legacy_project,
):
    api, store, _, project, legacy = legacy_project
    previous = deepcopy(legacy)
    assert api.projects[project]["lifecycle"] == "rekey_required"
    session = reopen(api, store)
    session.reconcile_keys()
    assert api.projects[project]["lifecycle"] == "active"
    assert api.projects[project]["key_epoch"] == 2
    assert legacy == previous
    assert historical_queries(api) == [
        {
            "scope_id": "org-test",
            "recipient_id": session.device_id,
            "recipient_kind": "device",
        }
    ]
    current = next(
        item
        for item in api.envelopes
        if (
            item["scope_id"] == project
            and item["key_epoch"] == 2
            and item["recipient_kind"] == "organization"
        )
    )
    assert current["organization_epoch"] == 2
    session.lock()
    restarted = reopen(api, store)
    assert (
        EncryptedRecords(restarted).page(project)["records"][0]["value"]["title"]
        == "旧組織鍵で暗号化したプロジェクト"
    )
    EncryptedRecords(restarted).write(
        project,
        key_epoch=2,
        records=[
            {
                "record_id": "after-legacy-repair",
                "kind": "chat",
                "expected_revision": 0,
                "value": {"text": "更新後の鍵で書き込める"},
            }
        ],
    )


def test_recovery_can_rekey_org_only_legacy_project_from_saved_recovery_envelope(
    legacy_project,
):
    api, _, code, project, _ = legacy_project
    restored, store, _ = new_session(api)
    restored.restore(code)
    assert restored.state == "approved"
    assert api.projects["org-test"]["key_epoch"] == 3
    assert api.projects[project]["key_epoch"] == 2
    assert api.projects[project]["lifecycle"] == "active"
    assert {item["recipient_kind"] for item in historical_queries(api)} == {
        "device",
        "recovery",
    }
    assert all(item["scope_id"] == "org-test" for item in historical_queries(api))
    assert len(historical_queries(api)) == 2
    assert code not in json.dumps(store.values)
    assert (
        EncryptedRecords(restored).page(project)["records"][0]["value"]["title"]
        == "旧組織鍵で暗号化したプロジェクト"
    )
    current = next(
        item
        for item in api.envelopes
        if (
            item["scope_id"] == project
            and item["key_epoch"] == 2
            and item["recipient_kind"] == "organization"
        )
    )
    assert current["organization_epoch"] == 3


@pytest.mark.parametrize("access", ["device", "recovery"])
def test_missing_historical_keys_fail_without_rotating_project_or_guessing_epochs(
    legacy_project,
    access,
):
    api, store, code, project, _ = legacy_project
    api.envelopes = [
        item
        for item in api.envelopes
        if not (item["scope_id"] == "org-test" and item["key_epoch"] == 1)
    ]
    session = reopen(api, store) if access == "device" else new_session(api)[0]
    commands = len(api.commands)
    with pytest.raises(E2eeError, match="key_redistribution_required"):
        if access == "device":
            session.reconcile_keys()
        else:
            session.restore(code)
    if access == "device":
        assert len(api.commands) == commands
    else:
        assert session.state == "recovery_pending"
    assert not any(name == "e2eeRotateScope" for name, _, _ in api.commands[commands:])
    assert api.projects[project]["key_epoch"] == 1
    assert api.projects[project]["lifecycle"] == "rekey_required"
    assert len(historical_queries(api)) == (1 if access == "device" else 2)
    assert not any(operation == "e2eeGetEpochs" for operation, _ in api.reads)


def test_bound_epoch_authentication_failure_does_not_try_historical_keys(
    legacy_project,
):
    api, store, _, project, envelope = legacy_project
    envelope["organization_epoch"] = 2
    session = reopen(api, store)
    with pytest.raises(E2eeError, match="authentication_failed"):
        session.scope_key(project, 1)
    assert not historical_queries(api)


def test_legacy_repair_tolerates_new_org_rotation_while_loading_saved_envelopes(
    legacy_project,
    monkeypatch,
):
    api, store, _, project, _ = legacy_project
    session = reopen(api, store)
    other_device_session = reopen(api, store)
    call = api.call
    rotated = False

    def concurrent_rotation(operation, **params):
        nonlocal rotated
        if operation == "e2eeGetEnvelopes" and "epoch" not in params and not rotated:
            rotated = True
            other_device_session.rotate_scope(deepcopy(api.projects["org-test"]))
        return call(operation, **params)

    monkeypatch.setattr(api, "call", concurrent_rotation)
    session.reconcile_keys()
    assert rotated
    assert api.projects["org-test"]["key_epoch"] == 3
    assert api.projects[project]["key_epoch"] == 2
    assert api.projects[project]["lifecycle"] == "active"
    assert len(historical_queries(api)) == 1
    assert any(
        item["scope_id"] == project
        and item["key_epoch"] == 2
        and item.get("organization_epoch") == 3
        for item in api.envelopes
    )


def test_legacy_key_search_rejects_more_than_1024_saved_envelopes(legacy_project):
    api, store, _, project, _ = legacy_project
    old = next(
        item
        for item in api.envelopes
        if (
            item["scope_id"] == "org-test"
            and item["key_epoch"] == 1
            and item["recipient_kind"] == "device"
        )
    )
    api.envelopes.extend(deepcopy(old) for _ in range(1024))
    session = reopen(api, store)
    with pytest.raises(E2eeError, match="limit_exceeded"):
        session.scope_key(project, 1)
    assert len(historical_queries(api)) == 1


@pytest.mark.parametrize(
    "field,value", [("key_epoch", 2**63), ("recipient_id", "other-device")]
)
def test_legacy_search_rejects_misbound_saved_envelopes(
    legacy_project, monkeypatch, field, value
):
    api, store, _, project, _ = legacy_project
    call = api.call

    def corrupted(operation, **params):
        result = call(operation, **params)
        if operation == "e2eeGetEnvelopes" and "epoch" not in params:
            previous = next(
                item for item in result["envelopes"] if item["key_epoch"] == 1
            )
            previous[field] = value
        return result

    monkeypatch.setattr(api, "call", corrupted)
    session = reopen(api, store)
    with pytest.raises(E2eeError, match="invalid_envelope"):
        session.scope_key(project, 1)
