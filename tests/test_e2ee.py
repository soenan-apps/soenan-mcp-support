from __future__ import annotations

from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time
from hashlib import sha256

import httpx
import pytest

from soenan_arteligo_support.e2ee import (
    DeviceSession,
    E2eeCrypto,
    E2eeError,
    EncryptedRecords,
)
from soenan_arteligo_support.e2ee._crypto import decode, encode
from soenan_arteligo_support.e2ee._oauth import OAuthSession
from soenan_arteligo_support.transfer import upload_file, download_file


class MemoryStore:
    def __init__(self):
        self.values: dict[str, str] = {}

    def read(self, name):
        return self.values.get(name)

    def write(self, name, value):
        self.values[name] = value

    def delete(self, name):
        self.values.pop(name, None)


class MemoryAPI:
    def __init__(self, crypto):
        self.crypto = crypto
        self.devices = {}
        self.recovery = None
        self.projects = {}
        self.envelopes = []
        self.records = {}
        self.objects = {}
        self.epoch_links = {}
        self.commands = []
        self.trust_statements = []
        self.base_url = ""

    def call(self, operation, *, body=None, **params):
        if operation == "e2eeReadRecords":
            scopes, commands = [], {}
            for request in body["scopes"]:
                scope = request["scope_id"]
                records = self.records.get(scope, {})
                values = [
                    records[identifier]
                    for identifier in request["record_ids"]
                    if identifier in records
                ]
                page = self._compact(values)
                commands.update(page["commands"])
                scopes.append(
                    {
                        "scope_id": scope,
                        "metadata": deepcopy(self.projects[scope]),
                        "records": page["records"],
                        "remaining_record_ids": [],
                        "missing_record_ids": [
                            identifier
                            for identifier in request["record_ids"]
                            if identifier not in records
                        ],
                        "devices": deepcopy(list(self.devices.values())),
                        "envelopes": deepcopy(
                            [
                                value
                                for value in self.envelopes
                                if value["scope_id"] == scope
                            ]
                        ),
                        "recoveries": [],
                        "epochs": [],
                    }
                )
            return {
                "scopes": scopes,
                "commands": commands,
                "key_scopes": [],
                "server_time": int(time.time()),
            }
        if body is None:
            if operation == "e2eeGetScope":
                return deepcopy(self.projects[params["scope_id"]])
            if operation == "e2eeGetTrust":
                return {"statements": deepcopy(self.trust_statements)}
            if operation == "e2eeGetRecovery":
                if self.recovery is None:
                    raise E2eeError("not_found")
                return deepcopy(self.recovery)
            if operation == "e2eeListDevices" or operation == "e2eeGetMemberDevices":
                return {"devices": deepcopy(list(self.devices.values()))}
            if operation == "e2eeListProjects":
                return {"projects": deepcopy(list(self.projects.values()))}
            if operation == "e2eeListOrganizations":
                return {"projects": []}
            if operation == "e2eeGetRecipients":
                return {
                    "devices": deepcopy(
                        [
                            device
                            for device in self.devices.values()
                            if device["state"] == "approved"
                        ]
                    ),
                    "recoveries": [deepcopy(self.recovery)],
                    "organization_id": None,
                }
            if operation == "e2eeGetEnvelopes":
                return {
                    "envelopes": deepcopy(
                        [
                            item
                            for item in self.envelopes
                            if item["scope_id"] == params["scope_id"]
                            and item["key_epoch"] == params["epoch"]
                            and item["recipient_id"] == params["recipient_id"]
                            and item["recipient_kind"] == params["recipient_kind"]
                        ]
                    )
                }
            if operation in {"e2eeGetSnapshot", "e2eeGetRecords", "e2eeGetCurrent"}:
                values = list(self.records.get(params["scope_id"], {}).values())
                values.sort(
                    key=lambda item: (
                        item["record_id"]
                        if operation in {"e2eeGetSnapshot", "e2eeGetCurrent"}
                        else item["cursor"]
                    )
                )
                if operation in {"e2eeGetSnapshot", "e2eeGetCurrent"}:
                    values = [
                        item
                        for item in values
                        if item["record_id"] > params.get("after_record_id", "")
                        and (
                            params.get("kind") is None or params["kind"] == item["kind"]
                        )
                    ]
                else:
                    values = [
                        item
                        for item in values
                        if item["cursor"] > params.get("after", 0)
                    ]
                count = params.get("limit", 256)
                result = {
                    "records": deepcopy(values[:count]),
                    "cursor": max(
                        [item["cursor"] for item in values] + [params.get("after", 0)]
                    ),
                    "has_more": len(values) > count,
                }
                if operation == "e2eeGetCurrent":
                    result.update(self._compact(values[:count]))
                    result["next_record_id"] = (
                        values[count - 1]["record_id"] if len(values) > count else None
                    )
                return result
            if operation == "e2eeGetEpochs":
                return {
                    "epochs": deepcopy(
                        [
                            item
                            for item in self.epoch_links.get(params["scope_id"], [])
                            if item["key_epoch"] > params["after_epoch"]
                        ][: params["limit"]]
                    )
                }
            if operation == "e2eeGetObject":
                return deepcopy(self.objects[params["object_id"]])
            if operation == "e2eeGetObjectCapability":
                chunk = self.objects[params["object_id"]]["manifest"]["chunks"][
                    params["index"]
                ]
                return {
                    "method": "GET",
                    "url": self.base_url
                    + "/"
                    + params["object_id"]
                    + "/"
                    + str(params["index"]),
                    "headers": {},
                    "content_length": chunk["ciphertext_size"],
                    "expires_at": int(time.time()) + 60,
                }
            raise AssertionError(operation)
        self.commands.append(deepcopy((operation, body, params)))
        value = json.loads(decode(body["body_bytes"]))
        commands = {
            "e2eeBootstrap": "bootstrap",
            "e2eeEnrollDevice": "device_enroll",
            "e2eeApproveDevice": "device_approve",
            "e2eeRestoreRecovery": "recovery_restore",
            "e2eeCreateProject": "project_create",
            "e2eeWriteRecords": "records_write",
            "e2eeSaveEnvelopes": "envelopes_save",
            "e2eeBeginObject": "object_begin",
            "e2eePutObjectCapability": "object_put",
            "e2eeFinalizeObject": "object_finalize",
            "e2eeDeleteObject": "object_delete",
            "e2eeRotateRecovery": "recovery_rotate",
            "e2eeRotateScope": "rotate_scope",
            "e2eeSaveTrust": "peer_trust",
        }
        if operation == "e2eeBootstrap":
            signer = value["device"]["signing_public_key"]
        elif operation == "e2eeEnrollDevice":
            signer = value["signing_public_key"]
        elif operation == "e2eeRestoreRecovery":
            signer = self.recovery["signing_public_key"]
        else:
            signer = self.devices[body["device_id"]]["signing_public_key"]
            if self.devices[body["device_id"]]["state"] != "approved":
                raise E2eeError("access_denied")
        self.crypto.verify(signer, commands[operation], body)
        if operation == "e2eeSaveTrust":
            self.trust_statements.append(deepcopy(body))
            return {}
        if operation == "e2eeBootstrap":
            root = value["recovery"]
            self.crypto.verify(signer, "recovery_public", root["public_command"])
            self.devices[value["device"]["device_id"]] = {
                **value["device"],
                "certificates": [
                    {
                        "operation": "bootstrap",
                        "public_device": value["device"],
                        "recovery_root": {
                            field: root[field]
                            for field in (
                                "recovery_id",
                                "encryption_public_key",
                                "signing_public_key",
                                "generation",
                            )
                        },
                        "root_signature": value["root_signature"],
                    }
                ],
            }
            self.recovery = {
                **value["recovery"],
                "account_subject": "account-subject",
                "certificates": [
                    {
                        "operation": "recovery_public",
                        "signed_command": root["public_command"],
                    }
                ],
            }
            return deepcopy(self.devices[value["device"]["device_id"]])
        if operation == "e2eeRotateRecovery":
            self.crypto.verify(signer, "recovery_public", value["public_command"])
            for root in value["device_roots"]:
                device = root["public_device"]
                assert self.devices[device["device_id"]]["state"] in {
                    "approved",
                    "revoked",
                }
                self.crypto.execute(
                    {
                        "op": "verify_bytes",
                        "public_key": value["signing_public_key"],
                        "bytes": encode(
                            b"arteligo-e2ee-device-root-v1\n"
                            + self.crypto.canonical(device)
                        ),
                        "signature": root["root_signature"],
                    }
                )
                self.devices[device["device_id"]]["certificates"].append(
                    {
                        "operation": "bootstrap",
                        "public_device": device,
                        "root_signature": root["root_signature"],
                        "recovery_root": {
                            field: value[field]
                            for field in (
                                "recovery_id",
                                "encryption_public_key",
                                "signing_public_key",
                                "generation",
                            )
                        },
                    }
                )
            self.recovery = {
                **value,
                "account_subject": "account-subject",
                "certificates": [
                    {
                        "operation": "recovery_public",
                        "signed_command": value["public_command"],
                    }
                ],
            }
            for project in self.projects.values():
                project["lifecycle"] = "rekey_required"
            return deepcopy(self.recovery)
        if operation == "e2eeRotateScope":
            scope = value["scope_id"]
            project = self.projects[scope]
            if project["key_epoch"] != value["expected_epoch"]:
                raise E2eeError("revision_conflict")
            project.update(key_epoch=project["key_epoch"] + 1, lifecycle="active")
            self.envelopes.extend(value["envelopes"])
            if "previous_key_ciphertext" in value:
                self.epoch_links.setdefault(scope, []).append(
                    {
                        "key_epoch": project["key_epoch"],
                        "previous_key_ciphertext": value["previous_key_ciphertext"],
                        "signed_command": body,
                    }
                )
            return deepcopy(project)
        if operation == "e2eeEnrollDevice":
            self.devices[value["device_id"]] = {
                key: value[key]
                for key in (
                    "device_id",
                    "account_subject",
                    "encryption_public_key",
                    "signing_public_key",
                )
            }
            self.devices[value["device_id"]].update(state="pending", certificates=[])
            return deepcopy(self.devices[value["device_id"]])
        if operation == "e2eeApproveDevice":
            target = self.devices[value["device_id"]]
            target.update(
                state="approved",
                certificates=[{"operation": "device_approve", "signed_command": body}],
            )
            self.envelopes.extend(value["envelopes"])
            return deepcopy(target)
        if operation == "e2eeRestoreRecovery":
            target = {
                **value["device"],
                "certificates": [
                    {"operation": "recovery_restore", "signed_command": body}
                ],
            }
            self.devices[target["device_id"]] = target
            return deepcopy(target)
        if operation == "e2eeSaveEnvelopes":
            self.envelopes.extend(value["envelopes"])
            return {}
        if operation == "e2eeCreateProject":
            scope = value["project_id"]
            self.projects[scope] = {
                "project_id": scope,
                "owner_org": value["owner_org"],
                "participation_policy": value["participation_policy"],
                "role": "owner",
                "lifecycle": "active",
                "key_epoch": 1,
                "revision": 1,
            }
            self.envelopes.extend(value["envelopes"])
            self._write(scope, value["records"], body)
            return deepcopy(self.projects[scope])
        if operation == "e2eeWriteRecords":
            assert value["format_version"] == 2
            assert (
                int(time.time()) <= value["expires_at"] <= int(time.time()) + 30 * 86400
            )
            for condition in value.get("preconditions", []):
                record = self.records.get(value["scope_id"], {}).get(
                    condition["record_id"]
                )
                if (
                    record is None
                    or record["revision"] != condition["expected_revision"]
                    or (condition.get("require_live") and record["deleted"])
                ):
                    raise E2eeError("revision_conflict")
            return self._write(value["scope_id"], value["records"], body)
        if operation == "e2eeBeginObject":
            self.objects.setdefault(
                value["object_id"],
                {
                    "manifest": value,
                    "state": "uploading",
                    "expires_at": int(time.time()) + 3600,
                },
            )
            return deepcopy(self.objects[value["object_id"]])
        if operation == "e2eePutObjectCapability":
            return {
                "method": "PUT",
                "url": self.base_url
                + "/"
                + value["object_id"]
                + "/"
                + str(value["index"]),
                "headers": {},
                "expires_at": int(time.time()) + 60,
                "content_length": self.objects[value["object_id"]]["manifest"][
                    "chunks"
                ][value["index"]]["ciphertext_size"],
            }
        if operation == "e2eeFinalizeObject":
            self.objects[value["object_id"]]["state"] = "ready"
            return deepcopy(self.objects[value["object_id"]])
        if operation == "e2eeDeleteObject":
            del self.objects[value["object_id"]]
            return {}
        raise AssertionError(operation)

    @staticmethod
    def _compact(values):
        commands, records = {}, []
        for value in values:
            command = value["signed_command"]
            body = json.loads(decode(command["body_bytes"]))
            operation = "project_create" if "project_id" in body else "records_write"
            identifier = sha256(
                json.dumps(command, sort_keys=True).encode()
            ).hexdigest()
            commands[identifier] = {
                "operation": operation,
                "command": deepcopy(command),
            }
            ordinal = next(
                index
                for index, record in enumerate(body["records"])
                if record["record_id"] == value["record_id"]
            )
            records.append(
                {
                    **{
                        key: item
                        for key, item in value.items()
                        if key not in {"ciphertext", "signed_command"}
                    },
                    "command_id": identifier,
                    "ordinal": ordinal,
                }
            )
        return {"records": records, "commands": commands}

    def _write(self, scope, writes, signed):
        current = self.records.setdefault(scope, {})
        for value in writes:
            if (
                current.get(value["record_id"], {}).get("revision", 0)
                != value["expected_revision"]
            ):
                raise E2eeError("revision_conflict")
        result = []
        cursor = max([item["cursor"] for item in current.values()] + [0])
        for value in writes:
            cursor += 1
            result.append(
                {
                    key: value[key]
                    for key in (
                        "record_id",
                        "kind",
                        "key_epoch",
                        "ciphertext",
                        "deleted",
                    )
                }
            )
            result[-1].update(
                revision=value["expected_revision"] + 1,
                cursor=cursor,
                author_device_id=signed["device_id"],
                signed_command=signed,
            )
        for value in result:
            current[value["record_id"]] = value
        return {"records": deepcopy(result), "cursor": cursor, "has_more": False}


def new_session(api, *, setup=False):
    store = MemoryStore()
    session = DeviceSession(
        api,
        api.crypto,
        store,
        origin="https://arteligo.test",
        subject="account-subject",
    )
    session.refresh()
    code = None
    if setup:
        draft = session.prepare_setup()
        code = draft["code"]
        session.finish_setup(draft)
    return session, store, code


@pytest.fixture
def initialized():
    crypto = E2eeCrypto()
    api = MemoryAPI(crypto)
    session, store, code = new_session(api, setup=True)
    scope = EncryptedRecords(session).create_project(
        owner_org="org_test", value={"title": "秘密の制作", "deadline": "2027-01-01"}
    )
    return api, session, store, code, scope


def test_python_uses_packaged_shared_rust_nist_aes_vector():
    crypto = E2eeCrypto()
    envelope = crypto.execute(
        {
            "op": "aead_seal_with_nonce",
            "key": encode(bytes(32)),
            "nonce": encode(bytes(12)),
            "plaintext": "",
            "aad": "",
        }
    )
    assert decode(envelope["ciphertext"]).hex() == "530f8afbc74536b9a963b4f1c4cb738b"
    assert crypto.open(bytes(32), envelope, b"") == b""


def test_records_never_send_names_or_plain_keys_and_reject_tampering(initialized):
    api, session, store, code, scope = initialized
    records = EncryptedRecords(session)
    result = records.write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": "chat_1",
                "kind": "chat",
                "expected_revision": 0,
                "value": {"body": "機密メッセージ"},
            }
        ],
    )
    assert result[0]["value"] == {"body": "機密メッセージ"}
    assert "機密メッセージ" not in json.dumps(api.commands, ensure_ascii=False)
    assert "秘密の制作" not in json.dumps(api.commands, ensure_ascii=False)
    assert code not in json.dumps(api.commands)
    for _, signed, _ in api.commands:
        payload = json.loads(decode(signed["body_bytes"]))
        assert "signing_secret_key" not in json.dumps(payload)
        assert "encryption_secret_key" not in json.dumps(payload)
    tampered = deepcopy(api.records[scope]["chat_1"])
    tampered["revision"] += 1
    with pytest.raises(E2eeError, match="invalid_record_signature"):
        records.open(scope, tampered)
    with pytest.raises(E2eeError, match="revision_conflict"):
        records.write(
            scope,
            key_epoch=1,
            records=[
                {
                    "record_id": "chat_1",
                    "kind": "chat",
                    "expected_revision": 0,
                    "value": {"body": "new"},
                }
            ],
        )


def test_independent_device_requires_returned_approval_and_decrypts(initialized):
    api, original, store, code, scope = initialized
    added, added_store, _ = new_session(api)
    pairing = added.enroll()
    assert (
        added.public["encryption_public_key"]
        != original.public["encryption_public_key"]
    )
    receipt = original.approve(pairing)
    assert added.refresh() == "pending_approval"
    with pytest.raises(E2eeError, match="device_approval_required"):
        EncryptedRecords(added).page(scope)
    bad_receipt = deepcopy(receipt)
    bad_receipt["challenge"] = "other"
    with pytest.raises(E2eeError, match="pairing_mismatch"):
        added.accept_approval(bad_receipt)
    added.accept_approval(receipt)
    result = EncryptedRecords(added).page(scope)
    assert result["records"][0]["value"]["title"] == "秘密の制作"
    assert "recovery" not in json.loads(added_store.read(added._storage_key))
    original_key = original.scope_key(scope, 1)
    assert added.scope_key(scope, 1) == original_key


def test_recovery_code_restores_new_device_without_copying_recovery_secret(initialized):
    api, original, store, code, scope = initialized
    restored, restored_store, _ = new_session(api)
    with pytest.raises(E2eeError):
        restored.restore(api.crypto.execute({"op": "recovery_generate"})["code"])
    restored.restore(code)
    assert (
        restored.public["encryption_public_key"]
        != original.public["encryption_public_key"]
    )
    assert (
        EncryptedRecords(restored).page(scope)["records"][0]["value"]["title"]
        == "秘密の制作"
    )
    assert code not in json.dumps(restored_store.values)
    assert (
        len([name for name in restored_store.values if name.startswith("device:")]) == 1
    )


def test_changed_recovery_encryption_key_is_rejected(initialized):
    api, session, store, code, scope = initialized
    api.recovery["encryption_public_key"] = api.crypto.keypair()[
        "encryption_public_key"
    ]
    with pytest.raises(E2eeError, match="recovery_key_changed"):
        session.refresh()
    with pytest.raises(E2eeError, match="device_approval_required"):
        session.require_approved()


def test_replaced_code_restores_history_and_keeps_revoked_author_revoked(initialized):
    api, owner, _, previous_code, scope = initialized
    additional, _, _ = new_session(api)
    additional.accept_approval(owner.approve(additional.enroll()))
    EncryptedRecords(additional).write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": "historical-message",
                "kind": "chat",
                "expected_revision": 0,
                "value": {"text": "revoked author history"},
            }
        ],
    )
    api.devices[additional.device_id]["state"] = "revoked"
    draft = owner.prepare_recovery_replacement()
    assert "encrypted_bundle" not in json.dumps(draft["recovery"]["device_roots"])
    assert (
        "encrypted_bundle"
        not in bytes(decode(draft["recovery"]["public_command"]["body_bytes"])).decode()
    )
    owner.replace_recovery(draft)
    assert api.projects[scope]["key_epoch"] == 2
    assert api.devices[additional.device_id]["state"] == "revoked"
    restored, store, _ = new_session(api)
    with pytest.raises(E2eeError):
        restored.restore(previous_code)
    restored.restore(draft["code"])
    values = EncryptedRecords(restored).page(scope)["records"]
    assert (
        next(item for item in values if item["record_id"] == "historical-message")[
            "value"
        ]["text"]
        == "revoked author history"
    )
    assert draft["code"] not in json.dumps(store.values)


def test_recovery_authenticates_foreign_sender_from_own_signed_peer_trust(initialized):
    api, owner, _, code, scope = initialized
    keys = api.crypto.keypair()
    foreign = {
        "device_id": "foreign-inviter",
        "account_subject": "foreign-account",
        "encryption_public_key": keys["encryption_public_key"],
        "signing_public_key": keys["signing_public_key"],
        "state": "approved",
        "certificates": [],
    }
    api.devices[foreign["device_id"]] = foreign
    recovery_id = api.recovery["recovery_id"]
    key = owner.scope_key(scope, 1)
    context = api.crypto.canonical(
        {
            "v": 1,
            "domain": "arteligo.scope-key",
            "scope_id": scope,
            "key_epoch": 1,
            "sender_device_id": foreign["device_id"],
            "recipient_id": recovery_id,
            "recipient_kind": "recovery",
        }
    )
    sealed = api.crypto.execute(
        {
            "op": "hpke_auth_seal",
            "sender_secret_key": keys["encryption_secret_key"],
            "recipient_public_key": api.recovery["encryption_public_key"],
            "plaintext": encode(key),
            "info": encode(context),
            "aad": encode(context),
        }
    )
    api.envelopes = [
        value for value in api.envelopes if value["recipient_kind"] != "recovery"
    ]
    api.envelopes.append(
        {
            "scope_id": scope,
            "key_epoch": 1,
            "sender_device_id": foreign["device_id"],
            "recipient_id": recovery_id,
            "recipient_kind": "recovery",
            "encapsulated_key": sealed["enc"],
            "ciphertext": sealed["ciphertext"],
        }
    )
    untrusted, _, _ = new_session(api)
    with pytest.raises(E2eeError, match="untrusted_device"):
        untrusted.restore(code)
    owner.endorse(foreign)
    restored, _, _ = new_session(api)
    restored.restore(code)
    assert restored.scope_key(scope, 1) == key
    assert EncryptedRecords(restored).page(scope)["records"]
    command = api.trust_statements[0]
    signature = bytearray(decode(command["signature"]))
    signature[0] ^= 1
    command["signature"] = encode(signature)
    tampered, _, _ = new_session(api)
    with pytest.raises(E2eeError):
        tampered.restore(code)


def test_historical_epoch_chain_verifies_rotation_signature(initialized):
    api, session, store, code, scope = initialized
    old_key = session.scope_key(scope, 1)
    new_key = api.crypto.key()
    aad = api.crypto.canonical(
        {
            "v": 1,
            "domain": "arteligo.previous-project-key",
            "scope_id": scope,
            "key_epoch": 2,
            "previous_epoch": 1,
        }
    )
    packed = encode(json.dumps(api.crypto.seal(new_key, old_key, aad)).encode())
    signed = session.sign(
        "rotate_scope",
        {
            "scope_id": scope,
            "expected_epoch": 1,
            "previous_key_ciphertext": packed,
            "envelopes": [],
        },
    )
    api.epoch_links[scope] = [
        {"key_epoch": 2, "previous_key_ciphertext": packed, "signed_command": signed}
    ]
    api.projects[scope]["key_epoch"] = 2
    api.envelopes = [
        session.wrap_key(
            scope,
            2,
            new_key,
            recipient=session.device_id,
            kind="device",
            public_key=session.public["encryption_public_key"],
        )
    ]
    session._clear_keys()
    assert session.scope_key(scope, 1) == old_key
    session._clear_keys()
    api.epoch_links[scope][0]["previous_key_ciphertext"] = encode(b"changed")
    with pytest.raises(E2eeError, match="invalid_epoch_chain"):
        session.scope_key(scope, 1)


def test_oauth_credentials_are_bound_to_account_and_resource_origins():
    store = MemoryStore()
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "token_type": "Bearer",
                "scope": "arteligo:app",
                "access_token": "new-access",
                "refresh_token": "new-refresh",
                "access_expires_at": int(time.time()) + 300,
            },
        )

    first = OAuthSession(
        account_origin="https://account.test",
        arteligo_origin="https://arteligo.test",
        store=store,
        transport=httpx.MockTransport(handler),
    )
    other = OAuthSession(
        account_origin="https://account.test",
        arteligo_origin="https://another.test",
        store=store,
    )
    store.write(
        first._storage_key,
        json.dumps(
            {
                "access_token": "old-access",
                "refresh_token": "old-refresh",
                "access_expires_at": 0,
            }
        ),
    )
    with pytest.raises(E2eeError, match="authentication_required"):
        other.access_token()
    assert not calls
    assert first.access_token() == "new-access"
    assert len(calls) == 1
    assert first.access_token() == "new-access"
    assert len(calls) == 1


@pytest.mark.parametrize("legacy_copy", [False, True])
def test_direct_bucket_roundtrip_authenticates_before_destination_publish(
    initialized, tmp_path, legacy_copy
):
    api, session, store, code, scope = initialized
    ciphertexts = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_PUT(self):
            assert self.headers.get("Authorization") is None
            ciphertexts[self.path] = self.rfile.read(
                int(self.headers["Content-Length"])
            )
            self.send_response(200)
            self.end_headers()

        def do_GET(self):
            value = ciphertexts[self.path]
            self.send_response(200)
            self.send_header("Content-Length", str(len(value)))
            self.end_headers()
            self.wfile.write(value)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    api.base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        source = tmp_path / "秘密の音声.wav"
        payload = b"private media content" * 1000
        source.write_bytes(payload)
        result = upload_file(session, project_id=scope, source=source)
        from soenan_arteligo_support.e2ee import EncryptedDirectory

        records = EncryptedRecords(session)
        entry = EncryptedDirectory(records, scope).page()["entries"][0]
        assert entry["file"]["id"] == result["file_id"]
        assert entry["file"]["originalFilename"] == source.name
        assert entry["file"]["sizeBytes"] == len(payload)
        assert entry["file"]["sourceState"] == "available"
        assert entry["file"]["media"]["kind"] == "audio"
        assert entry["file"]["createdAt"]
        saved_file = records.read(scope, [result["file_id"]])[result["file_id"]]
        assert "directoryEntry" not in saved_file["value"]
        assert saved_file["value"]["entryIntent"] == {
            "name": source.name,
            "parentFolderId": None,
        }
        if legacy_copy:
            records.write(
                scope,
                key_epoch=1,
                records=[
                    {
                        "record_id": result["file_id"],
                        "kind": "file",
                        "expected_revision": saved_file["revision"],
                        "value": {**saved_file["value"], "directoryEntry": entry},
                    }
                ],
            )
        assert len(ciphertexts) == 1
        assert payload not in next(iter(ciphertexts.values()))
        remote_manifest = api.objects[result["object_id"]]["manifest"]
        assert source.name not in json.dumps(remote_manifest, ensure_ascii=False)
        assert "wrapped" not in json.dumps(remote_manifest)
        target = tmp_path / "output.wav"
        assert download_file(
            session, project_id=scope, file_id=result["file_id"], destination=target
        ) == len(payload)
        assert target.read_bytes() == payload
        with pytest.raises(E2eeError, match="destination_exists"):
            download_file(
                session, project_id=scope, file_id=result["file_id"], destination=target
            )
        path = next(iter(ciphertexts))
        ciphertexts[path] = bytes([ciphertexts[path][0] ^ 1]) + ciphertexts[path][1:]
        corrupt_target = tmp_path / "corrupt.wav"
        with pytest.raises(E2eeError, match="transfer_failed"):
            download_file(
                session,
                project_id=scope,
                file_id=result["file_id"],
                destination=corrupt_target,
            )
        assert not corrupt_target.exists()
        assert not list(tmp_path.glob(".arteligo-*"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_wav_preview_uses_encrypted_object_api_and_authenticates_local_source(
    initialized, tmp_path
):
    import io
    import shutil
    import struct
    import wave
    from hashlib import sha256
    from soenan_arteligo_support.transfer import upload_wav_preview
    from soenan_arteligo_support.transfer._crypto import preview_chunk_aad, chunk_nonce
    from soenan_arteligo_support.transfer._workflow import key_aad

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("local FFmpeg and FFprobe are required")
    api, session, _, _, scope = initialized
    encrypted = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_PUT(self):
            assert self.headers.get("Authorization") is None
            encrypted[self.path] = self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    api.base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wav = io.BytesIO()
        with wave.open(wav, "wb") as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(48000)
            stream.writeframes(struct.pack("<h", 8000) * 48000)
        source = tmp_path / "秘密のプレビュー.wav"
        source.write_bytes(wav.getvalue())
        uploaded = upload_file(session, project_id=scope, source=source)
        altered = tmp_path / "different.wav"
        altered.write_bytes(wav.getvalue()[:-2] + b"\0\0")
        with pytest.raises(E2eeError, match="source_changed"):
            upload_wav_preview(
                session, project_id=scope, file_id=uploaded["file_id"], source=altered
            )
        assert len(api.objects) == 1
        result = upload_wav_preview(
            session, project_id=scope, file_id=uploaded["file_id"], source=source
        )
        assert result["state"] == "ready"
        assert len(api.objects) == 2
        public = json.dumps(api.objects)
        assert (
            source.name not in public
            and "wrapped" not in public
            and "duration" not in public
        )
        private = EncryptedRecords(session).read(scope, [uploaded["file_id"]])[
            uploaded["file_id"]
        ]["value"]["preview"]
        assert private["media"]["codecs"] == "opus"
        assert (
            private["media"]["playbackLoudness"]["policyVersion"]
            == "ebu-r128-playback-v1"
        )
        manifest = private["manifest"]
        wrapped = private["wrappedDataKey"]
        dek = session.crypto.open(
            session.scope_key(scope, private["epoch"]),
            {
                "nonce": wrapped["nonceB64u"],
                "ciphertext": wrapped["ciphertextB64u"],
            },
            key_aad(scope, private["epoch"], result["preview_id"], 2),
        )
        clear = bytearray()
        for chunk in manifest["chunks"]:
            ciphertext = encrypted[
                "/" + result["preview_id"] + "/" + str(chunk["chunkIndex"])
            ]
            assert encode(sha256(ciphertext).digest()) == chunk["ciphertextSha256B64u"]
            clear.extend(
                session.crypto.open(
                    dek,
                    {
                        "nonce": encode(
                            chunk_nonce(
                                decode(private["nonceBaseB64u"]), chunk["chunkIndex"]
                            )
                        ),
                        "ciphertext": encode(ciphertext),
                    },
                    preview_chunk_aad(
                        project_id=scope,
                        source_object_id=uploaded["object_id"],
                        processing_id=result["preview_id"],
                        preview_id=result["preview_id"],
                        job_id=result["preview_id"],
                        total_plaintext_size=manifest["plaintextSize"],
                        chunk_count=len(manifest["chunks"]),
                        chunk_size=manifest["chunkSize"],
                        chunk_index=chunk["chunkIndex"],
                        plaintext_offset=chunk["plaintextOffset"],
                        plaintext_length=chunk["plaintextSize"],
                        final=chunk["finalChunk"],
                    ),
                )
            )
        assert clear.startswith(bytes.fromhex("1a45dfa3"))
        assert b"OpusHead" in clear
        before = len(api.objects)
        assert (
            upload_wav_preview(
                session, project_id=scope, file_id=uploaded["file_id"], source=source
            )
            == result
        )
        assert len(api.objects) == before
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_generated_transport_preserves_signed_bytes_and_selects_product_paths():
    from soenan_arteligo_support.e2ee._api import GeneratedAPI

    store = MemoryStore()
    oauth = OAuthSession(
        account_origin="https://account.test",
        arteligo_origin="https://arteligo.test",
        store=store,
    )
    store.write(
        oauth._storage_key,
        json.dumps(
            {
                "access_token": "access",
                "refresh_token": "refresh",
                "access_expires_at": int(time.time()) + 300,
            }
        ),
    )
    requests = []

    def handle(request):
        requests.append(request)
        assert request.headers["Authorization"] == "Bearer access"
        if request.method == "POST":
            assert json.loads(request.content) == {
                "device_id": "d",
                "body_bytes": "signed-exactly",
                "signature": "signature",
            }
            return httpx.Response(204)
        return httpx.Response(200, json={"envelopes": []})

    api = GeneratedAPI(oauth, transport=httpx.MockTransport(handle))
    assert api.call(
        "e2eeGetEnvelopes",
        scope_id="scope-1",
        epoch=7,
        recipient_id="d",
        recipient_kind="device",
    ) == {"envelopes": []}
    assert requests[-1].url.path == "/api/e2ee/scopes/scope-1/envelopes"
    assert requests[-1].url.params["epoch"] == "7"
    assert (
        api.call(
            "e2eeSaveEnvelopes",
            scope_id="scope-1",
            body={
                "device_id": "d",
                "body_bytes": "signed-exactly",
                "signature": "signature",
            },
        )
        == {}
    )


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (409, "limit_exceeded"),
        (409, "quota_exceeded"),
        (409, "rekey_required"),
        (403, "device_revoked"),
        (403, "service_terms_acceptance_required"),
    ],
)
def test_generated_transport_preserves_actionable_errors(status, code):
    from soenan_arteligo_support.e2ee._api import GeneratedAPI

    store = MemoryStore()
    oauth = OAuthSession(
        account_origin="https://account.test",
        arteligo_origin="https://arteligo.test",
        store=store,
    )
    store.write(
        oauth._storage_key,
        json.dumps(
            {
                "access_token": "access",
                "refresh_token": "refresh",
                "access_expires_at": int(time.time()) + 300,
            }
        ),
    )
    api = GeneratedAPI(
        oauth,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(status, json={"error": {"code": code}})
        ),
    )
    with pytest.raises(E2eeError, match=f"^{code}$"):
        api.call("e2eeGetRecipients", scope_id="scope-1")


def test_local_mcp_stdio_starts_without_reading_credentials():
    import asyncio
    import sys
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    script = "from soenan_arteligo_support.e2ee._mcp import create_local_mcp; create_local_mcp(lambda: None).run(transport='stdio')"

    async def inspect():
        async with stdio_client(
            StdioServerParameters(command=sys.executable, args=["-c", script])
        ) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                result = await client.list_tools()
                names = {tool.name for tool in result.tools}
                assert "arteligo_upload_file" in names
                assert "arteligo_write_record" in names
                assert not any(
                    "key" in name
                    or "recovery" in name
                    or "login" in name
                    or "approve" in name
                    for name in names
                )

    asyncio.run(inspect())


def test_maximum_source_and_preview_manifests_fit_bounded_record_commands(initialized):
    from soenan_arteligo_support.transfer._crypto import (
        ChunkMetadata,
        EncryptionPlan,
        CHUNK_SIZE,
    )

    api, session, _, _, scope = initialized
    chunks = tuple(
        ChunkMetadata(
            i,
            i * (CHUNK_SIZE + 16),
            bytes(range(32)),
            CHUNK_SIZE + 16,
            i == 1023,
            i * CHUNK_SIZE,
            CHUNK_SIZE,
        )
        for i in range(1024)
    )
    plan = EncryptionPlan(
        scope,
        "fil_" + "b" * 32,
        "a" * 36,
        1,
        CHUNK_SIZE * 1024,
        1024,
        bytes(8),
        bytes(32),
        bytes(12),
        bytes(48),
        chunks,
    )
    value = {
        "source": plan.manifest(),
        "preview": plan.manifest(),
        "filename": "音声" * 100,
    }
    sealed = EncryptedRecords(session).seal(
        scope,
        record_id="fil_limit",
        kind="file",
        expected_revision=0,
        key_epoch=1,
        value=value,
    )
    signed = session.sign("records_write", {"scope_id": scope, "records": [sealed]})
    assert len(session.crypto.canonical(value)) < 512 * 1024
    assert len(sealed["ciphertext"]) < 1024 * 1024
    assert len(decode(signed["body_bytes"])) < 1024 * 1024
    assert len(json.dumps(signed).encode()) < 2 * 1024 * 1024
    assert len(signed["body_bytes"]) < 2 * 1024 * 1024
    with pytest.raises(E2eeError, match="record_too_large"):
        EncryptedRecords(session).seal(
            scope,
            record_id="fil_limit",
            kind="file",
            expected_revision=0,
            key_epoch=1,
            value={"content": "x" * (512 * 1024)},
        )
    with pytest.raises(E2eeError, match="command_too_large"):
        session.sign("records_write", {"content": "x" * (1024 * 1024)})


def test_write_recovers_all_committed_records_from_bounded_partial_response(
    initialized,
):
    api, session, _, _, scope = initialized
    call = api.call
    reads = []

    def bounded(operation, *, body=None, **parameters):
        result = call(operation, body=body, **parameters)
        if operation in {"e2eeWriteRecords", "e2eeGetRecords"}:
            if operation == "e2eeGetRecords":
                reads.append(parameters["after"])
            if len(result["records"]) > 1:
                result["records"] = result["records"][:1]
                result["cursor"] = result["records"][-1]["cursor"]
                result["has_more"] = True
        return result

    api.call = bounded
    records = EncryptedRecords(session).write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": f"chat_{index}",
                "kind": "chat",
                "expected_revision": 0,
                "value": {"text": f"large batch record {index}"},
            }
            for index in range(3)
        ],
    )
    assert [record["record_id"] for record in records] == ["chat_0", "chat_1", "chat_2"]
    assert [record["value"]["text"] for record in records] == [
        f"large batch record {index}" for index in range(3)
    ]
    assert all(record["author_subject"] == session.subject for record in records)
    assert len(reads) == 2 and reads[1] > reads[0]
    assert (
        len(
            [
                command
                for operation, command, _ in api.commands
                if operation == "e2eeWriteRecords"
            ]
        )
        == 1
    )


def test_write_does_not_report_success_for_an_incomplete_committed_response(
    initialized,
):
    api, session, _, _, scope = initialized
    call = api.call

    def missing(operation, *, body=None, **parameters):
        result = call(operation, body=body, **parameters)
        if operation == "e2eeWriteRecords":
            result["records"] = []
            result["has_more"] = False
        return result

    api.call = missing
    with pytest.raises(E2eeError, match="incomplete_write_response"):
        EncryptedRecords(session).write(
            scope,
            key_epoch=1,
            records=[
                {
                    "record_id": "chat_unconfirmed",
                    "kind": "chat",
                    "expected_revision": 0,
                    "value": {"text": "saved"},
                }
            ],
        )
