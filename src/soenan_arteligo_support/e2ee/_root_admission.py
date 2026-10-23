from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from ._admission import admission_message
from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe
from ._owner_protocol import ROOT_FIELDS, SignedEvidence, bytes32, object_value
from ._trust import public_device
from ._owner_sources import OriginalIssuerAdmission
from ._signed_commands import SavedCommand, UncertainCommand

if TYPE_CHECKING:
    from ._session import DeviceSession


def open_recovery_code(crypto: E2eeCrypto, subject: str, root: Mapping[str, Any], code: str) -> dict[str, str]:
    aad = crypto.canonical({"v": 1, "domain": "arteligo.recovery", "account_subject": subject,
                            "recovery_id": root["recovery_id"], "generation": root["generation"]})
    plaintext, keys = bytearray(), {}
    try:
        sealed = json.loads(decode(root["encrypted_bundle"]))
        plaintext = decode(crypto.execute({"op": "recovery_open", "code": code, "envelope": sealed,
                                          "aad": encode(aad)})["plaintext"])
        keys = json.loads(plaintext)
        if not isinstance(keys, dict) or any(not isinstance(keys.get(name), str)
            for name in ("encryption_secret_key", "signing_secret_key")):
            raise E2eeError("invalid_recovery")
        derived = crypto.execute({"op": "public_keys", "encryption_secret_key": keys["encryption_secret_key"],
                                  "signing_secret_key": keys["signing_secret_key"]})
        if any(derived[name] != root[name] for name in ("encryption_public_key", "signing_public_key")):
            raise E2eeError("recovery_key_changed")
        return keys
    except (ValueError, TypeError, KeyError):
        if isinstance(keys, dict):
            keys.clear()
        raise E2eeError("invalid_recovery") from None
    finally:
        wipe(aad)
        wipe(plaintext)


@dataclass(frozen=True)
class RootAdmissionProof:
    root: dict[str, Any]
    command: SignedEvidence

    @classmethod
    def create(cls, crypto: E2eeCrypto, root: Mapping[str, Any], device: Mapping[str, Any],
               device_secret: str, root_secret: str, challenge: str | None = None) -> RootAdmissionProof:
        public = public_device(device)
        body = {"recovery_id": root["recovery_id"], "generation": root["generation"],
                "device": public, "challenge": challenge or secrets.token_urlsafe(32)}
        message = admission_message(crypto, body)
        try:
            signature = crypto.execute({"op": "sign_bytes", "secret_key": device_secret, "bytes": encode(message)})["signature"]
        finally:
            wipe(message)
        command = SignedEvidence.parse(crypto.sign(root_secret, "device_add_by_key",
            {**body, "device_signature": signature}, public["device_id"]))
        return cls({name: root[name] for name in ROOT_FIELDS}, command)

    @classmethod
    def parse(cls, crypto: E2eeCrypto, value: Any, device: Mapping[str, Any]) -> RootAdmissionProof:
        value = object_value(value)
        root = object_value(value.get("root"))
        if (set(value) != {"root", "signed_command"} or set(root) != set(ROOT_FIELDS)
                or type(root["generation"]) is not int or root["generation"] < 1
                or not isinstance(root["recovery_id"], str) or not root["recovery_id"]):
            raise E2eeError("invalid_key_admission")
        bytes32(root["encryption_public_key"])
        bytes32(root["signing_public_key"])
        command = SignedEvidence.parse(value["signed_command"])
        command.verify(crypto, root["signing_public_key"], "device_add_by_key")
        body, public = command.body, public_device(device)
        if (set(body) != {"recovery_id", "generation", "device", "challenge", "device_signature"}
                or body["recovery_id"] != root["recovery_id"] or body["generation"] != root["generation"]
                or body["device"] != public or command.device_id != public["device_id"]):
            raise E2eeError("invalid_key_admission")
        nonce = decode(body["challenge"])
        try:
            if len(nonce) != 32:
                raise E2eeError("invalid_key_admission")
        finally:
            wipe(nonce)
        message = admission_message(crypto, {name: body[name] for name in ("recovery_id", "generation", "device", "challenge")})
        try:
            crypto.execute({"op": "verify_bytes", "public_key": public["signing_public_key"],
                            "bytes": encode(message), "signature": body["device_signature"]})
        finally:
            wipe(message)
        return cls(dict(root), command)

    def document(self) -> dict[str, Any]:
        return {"root": self.root, "signed_command": self.command.document()}


class RootAdmissions:
    HISTORY_COLLECTION = "root_device_history"

    def __init__(self, session: DeviceSession):
        self.session = session

    def prepare(self, root: Mapping[str, Any], keys: Mapping[str, str]) -> RootAdmissionProof:
        session = self.session
        if session._device is None:
            raise E2eeError("device_approval_required")
        saved = session._device.get("root_admission")
        if saved is not None:
            pending = RootAdmissionProof.parse(session.crypto, saved, session.public)
            if pending.root == {name: root[name] for name in ROOT_FIELDS}:
                return pending
            session._device.setdefault("superseded_root_admissions", []).append(saved)
        proof = RootAdmissionProof.create(session.crypto, root, session.public,
            session._device["signing_secret_key"], keys["signing_secret_key"],
            session._device.get("challenge") if session.device_approval == "pending" else None)
        session._device["root_admission"] = proof.document()
        session._persist()
        return proof

    def original_current(self) -> OriginalIssuerAdmission:
        session = self.session
        if session.recovery is None:
            raise E2eeError("recovery_missing")
        root = session.owner_access.verifier.root(session.recovery, session.subject)
        if session.trust._confirmed_head(session.subject) != root:
            raise E2eeError("owner_root_requalification_required")
        recovery = session._recovery_material(None, root.identifier)
        if recovery is None or session.owner_access.verifier.root(recovery, session.subject) != root:
            raise E2eeError("owner_root_proof_missing")
        material = session._device_material(None, session.device_id, refresh=True)
        if material.get("state") != "approved" or public_device(material) != session.public:
            raise E2eeError("device_approval_required")
        for statement in recovery.get("certificates", []):
            if statement.get("operation") != "recovery_public":
                continue
            public = SignedEvidence.parse(statement["signed_command"])
            if (public.body.get("account_subject") != session.subject
                    or any(public.body.get(name) != session.recovery[name] for name in ROOT_FIELDS)):
                continue
            digest = public.digest(session.crypto, "recovery_public")
            try:
                session.owner_access.account.witness(session.subject, digest)
            except E2eeError as error:
                if (error.code != "owner_custody_evidence_missing"
                        or (root.generation != 1 and not session.trust.has_private_recovery(root))):
                    raise
                digest = None
            return session.owner_access.current.proposed_local_admission(material, root, digest)
        raise E2eeError("owner_root_proof_missing")

    def complete(self, proof: RootAdmissionProof | None = None) -> None:
        session = self.session
        value = (session._device or {}).get("root_admission")
        if proof is None:
            if value is None:
                return
            proof = RootAdmissionProof.parse(session.crypto, value, session.public)
        if session.recovery is None or proof.root != {name: session.recovery[name] for name in ROOT_FIELDS}:
            return
        original_error = None
        try:
            session.call("e2eeAddDeviceByKey", body=proof.command.document())
        except E2eeError as error:
            original_error = error
        values = session.call("e2eeListDevices")["devices"]
        material = next((item for item in values if item["device_id"] == session.device_id), None)
        if material is None or public_device(material) != session.public:
            raise E2eeError("device_key_changed")
        if material.get("state") == "revoked":
            raise E2eeError("device_revoked")
        if material.get("state") != "approved" or not any(
            item.get("operation") == "device_add_by_key" and item.get("signed_command") == proof.command.document()
            for item in material.get("certificates", [])
        ):
            if original_error is not None:
                raise original_error
            raise E2eeError("root_admission_unconfirmed")
        session._devices[session.device_id] = material
        if value == proof.document():
            session._device.pop("root_admission")
            session._persist()

    def recovery_epochs(self, scope: Mapping[str, Any], root: Mapping[str, Any]) -> tuple[int, ...]:
        session, identifier = self.session, scope["project_id"]
        retained = session.call("e2eeGetEnvelopes", scope_id=identifier,
            recipient_id=root["recovery_id"], recipient_kind="recovery")["envelopes"]
        epochs = set()
        for envelope in retained:
            epoch = envelope.get("key_epoch")
            if (envelope.get("scope_id") != identifier or envelope.get("recipient_kind") != "recovery"
                    or envelope.get("recipient_id") != root["recovery_id"]
                    or type(epoch) is not int or not 1 <= epoch <= scope["key_epoch"]):
                raise E2eeError("invalid_envelope")
            source = SignedEvidence.parse(envelope.get("signed_command"))
            if envelope.get("operation") == "recovery_rotate":
                if source.document() != root.get("owner_access_snapshot_command"):
                    raise E2eeError("invalid_owner_custody_backup")
                issuer = session._device_material(None, source.device_id)
                if issuer["account_subject"] != session.subject:
                    raise E2eeError("account_mismatch")
                source.verify(session.crypto, issuer["signing_public_key"], "recovery_rotate")
                selected = {name: value for name, value in envelope.items() if name not in {"operation", "signed_command"}}
                if sum(value == selected for value in source.body.get("envelopes", [])) != 1:
                    raise E2eeError("participant_envelope_mismatch")
            else:
                session.owner_access.envelopes.sender(identifier, epoch, envelope)
            epochs.add(epoch)
        return tuple(sorted(epochs))

    def _complete_history(self, scope: str, saved: SavedCommand) -> None:
        session, source = self.session, saved.command
        issuer = session._device_material(None, source.device_id)
        if issuer["account_subject"] != session.subject:
            raise E2eeError("account_mismatch")
        source.verify(session.crypto, issuer["signing_public_key"], "envelopes_save")
        body = source.body
        if (set(body) != {"scope_id", "key_epoch", "envelopes"} or body["scope_id"] != scope
                or type(body["key_epoch"]) is not int
                or body["key_epoch"] < 1 or not isinstance(body["envelopes"], list) or len(body["envelopes"]) != 1):
            raise E2eeError("invalid_key_admission")
        envelope = body["envelopes"][0]
        if (envelope.get("scope_id") != scope or envelope.get("key_epoch") != body["key_epoch"]
                or envelope.get("sender_device_id") != source.device_id
                or envelope.get("recipient_kind") != "device" or envelope.get("recipient_id") != source.device_id):
            raise E2eeError("invalid_key_admission")
        session.publications.submit(self.HISTORY_COLLECTION, scope, saved,
            lambda command: session.call("e2eeSaveEnvelopes", scope_id=scope, body=command))
        values = session.call("e2eeGetEnvelopes", scope_id=scope, epoch=body["key_epoch"],
            recipient_id=source.device_id, recipient_kind="device")["envelopes"]
        exact = {**envelope, "operation": "envelopes_save", "signed_command": source.document()}
        if exact not in values:
            raise E2eeError("key_redistribution_required")
        if source.device_id == session.device_id:
            key = session._open_key_envelope(scope, body["key_epoch"], exact, recipient=session.device_id,
                kind="device", secret_key=session._device["encryption_secret_key"])
            try:
                session._remember(scope, body["key_epoch"], key, owner=session._scope_owner(scope))
            finally:
                wipe(key)
        session.publications.finish(self.HISTORY_COLLECTION, scope, saved)

    def publish_history(self, scope: Mapping[str, Any], root: Mapping[str, Any], secret: str) -> None:
        session, identifier = self.session, scope["project_id"]
        saved = session.publications.pending(self.HISTORY_COLLECTION, identifier, "envelopes_save")
        if saved is not None:
            self._complete_history(identifier, saved)
        if scope["key_epoch"] <= 1:
            return
        organization = scope.get("owner_org")
        if organization and session.owner_access.authority(organization, active=False).owner_subject == session.subject:
            return
        self.original_current()
        for epoch in self.recovery_epochs(scope, root):
            if epoch == scope["key_epoch"]:
                continue
            try:
                key = session._read_key(identifier, epoch, recipient=session.device_id, kind="device",
                    secret_key=session._device["encryption_secret_key"])
            except E2eeError as error:
                if error.code != "key_redistribution_required":
                    raise
            else:
                wipe(key)
                continue
            key = session._read_key(identifier, epoch, recipient=root["recovery_id"], kind="recovery", secret_key=secret)
            try:
                envelope = session.wrap_key(identifier, epoch, key, recipient=session.device_id,
                    kind="device", public_key=session.public["encryption_public_key"])
                saved = SavedCommand("envelopes_save", UncertainCommand(SignedEvidence.parse(
                    session.sign("envelopes_save", {"scope_id": identifier, "key_epoch": epoch, "envelopes": [envelope]}))))
                session.publications.save(self.HISTORY_COLLECTION, identifier, saved)
            finally:
                wipe(key)
            self._complete_history(identifier, saved)
