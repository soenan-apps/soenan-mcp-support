from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError, encode, wipe
from ._owner_protocol import ROOT_FIELDS, SignedEvidence, canonical_digest, object_value
from ._owner_root_history import ScopeGenerationReference
from ._owner_sources import OriginalIssuerAdmission
from ._root_admission import RootAdmissionProof, open_recovery_code
from ._signed_commands import RejectedCommand, SavedCommand, UncertainCommand
from ._trust import _RootIdentity

if TYPE_CHECKING:
    from ._session import DeviceSession


@dataclass
class RootReplacementIntent:
    saved: SavedCommand
    admission: RootAdmissionProof
    generations: tuple[ScopeGenerationReference, ...]

    @classmethod
    def parse(cls, session: DeviceSession, value: Any) -> RootReplacementIntent:
        value = object_value(value)
        if set(value) != {"saved_command", "root_admission", "scope_generations"}:
            raise E2eeError("unsupported_recovery_replacement_proof")
        saved = SavedCommand.parse(value["saved_command"], "recovery_rotate")
        admission = RootAdmissionProof.parse(session.crypto, value["root_admission"], session.public)
        if any(saved.command.body.get(name) != admission.root[name] for name in ROOT_FIELDS):
            raise E2eeError("invalid_recovery_replacement")
        saved.command.verify(session.crypto, session.public["signing_public_key"], "recovery_rotate")
        generations = tuple(ScopeGenerationReference.parse(item) for item in value["scope_generations"])
        if len({(item.scope, item.epoch) for item in generations}) != len(generations):
            raise E2eeError("invalid_recovery_replacement")
        return cls(saved, admission, generations)

    def document(self) -> dict[str, Any]:
        return {"saved_command": self.saved.document(), "root_admission": self.admission.document(),
                "scope_generations": [item.document() for item in self.generations]}


@dataclass(frozen=True)
class RootReplacementSupersession:
    intent: RootReplacementIntent
    root: _RootIdentity

    def document(self) -> dict[str, Any]:
        return {"intent": self.intent.document(), "superseding_root": self.root.document()}


class RootReplacements:
    HISTORY_COLLECTION = "recovery_replacement_history"

    def __init__(self, session: DeviceSession):
        self.session, self.crypto = session, session.crypto

    def _save(self, intent: RootReplacementIntent) -> None:
        self.session._device["recovery_replacement"] = intent.document()
        self.session._persist()

    def _associations(self, keys: Mapping[str, str]) -> list[dict[str, Any]]:
        session = self.session
        devices = session.call("e2eeListDevices")["devices"]
        lookup = session._current_device_lookup(None, devices)
        roots = []
        for device in devices:
            historical = device["state"] == "revoked" and any(
                item.get("operation") in {"bootstrap", "device_approve", "device_add_by_key"}
                for item in device.get("certificates", []))
            if device["state"] != "approved" and not historical:
                continue
            if device["account_subject"] != session.subject:
                raise E2eeError("account_mismatch")
            checked = session.trust.verify_device(device, lookup,
                recovery_lookup=lambda identifier: session._recovery_material(None, identifier))
            message = bytearray(b"arteligo-e2ee-device-root-v1\n") + self.crypto.canonical(checked)
            try:
                signature = self.crypto.execute({"op": "sign_bytes", "secret_key": keys["signing_secret_key"],
                                                 "bytes": encode(message)})["signature"]
            finally:
                wipe(message)
            roots.append({"public_device": checked, "root_signature": signature})
        return roots

    def _envelopes(self, root: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[ScopeGenerationReference]]:
        session = self.session
        envelopes, references = [], []
        for scope in session.scopes():
            identifier, current, organization = scope["project_id"], scope["key_epoch"], scope.get("owner_org")
            if current == 0 and scope["key_state"] == "uninitialized":
                continue
            head = session.owner_access.authority(organization, active=False) if organization else None
            if head is not None and head.owner_subject == session.subject:
                continue
            epochs = session.root_admissions.recovery_epochs(scope, session.recovery)
            if head is not None and epochs:
                qualified = session.owner_access.current.qualify(organization, session.public,
                    session.owner_access.current.independent_root(identifier, session.public), head, proof_scope=identifier)
                if identifier == organization and not qualified.custody.can_receive_organization_keys:
                    raise E2eeError("organization_key_recipient_ineligible")
            for epoch in epochs:
                if epoch == current:
                    with session.owner_access.publications.key(identifier, epoch, head) as publication:
                        envelopes.append(self._seal_envelope(root, identifier, epoch, publication.key))
                        if publication.generation is not None:
                            generation = publication.generation
                            references.append(ScopeGenerationReference(identifier, epoch, canonical_digest(self.crypto,
                                {"operation": generation.operation, "signed_command": generation.command.document()})))
                else:
                    key = session.scope_key(identifier, epoch)
                    try:
                        envelopes.append(self._seal_envelope(root, identifier, epoch, key))
                    finally:
                        wipe(key)
        return envelopes, references

    def _seal_envelope(self, root: Mapping[str, Any], scope: str, epoch: int, key: bytearray) -> dict[str, Any]:
        fields = {"scope_id": scope, "key_epoch": epoch, "sender_device_id": self.session.device_id,
                  "recipient_id": root["recovery_id"], "recipient_kind": "recovery"}
        context = self.crypto.canonical({"v": 1, "domain": "arteligo.scope-key", **fields})
        try:
            sealed = self.crypto.execute({"op": "hpke_auth_seal",
                "sender_secret_key": self.session._device["encryption_secret_key"],
                "recipient_public_key": root["encryption_public_key"], "plaintext": encode(key),
                "info": encode(context), "aad": encode(context)})
            return {**fields, "encapsulated_key": sealed["enc"], "ciphertext": sealed["ciphertext"]}
        finally:
            wipe(context)

    def prepare(self) -> dict[str, Any]:
        session = self.session
        session.require_approved()
        if session.recovery_replacement_pending:
            raise E2eeError("recovery_replacement_pending")
        if session.recovery is None:
            raise E2eeError("recovery_missing")
        session.owner_access.recovery.require_selected_history()
        qualified = session.owner_access.recovery.root_history.qualified()
        admission = qualified.original_admission if qualified is not None else session.root_admissions.original_current()
        keys = self.crypto.keypair()
        code = self.crypto.execute({"op": "recovery_generate"})["code"]
        root = {"recovery_id": secrets.token_urlsafe(24), "generation": session.recovery["generation"] + 1,
                "encryption_public_key": keys["encryption_public_key"], "signing_public_key": keys["signing_public_key"]}
        aad = self.crypto.canonical({"v": 1, "domain": "arteligo.recovery", "account_subject": session.subject,
                                     "recovery_id": root["recovery_id"], "generation": root["generation"]})
        plaintext = self.crypto.canonical(keys)
        try:
            sealed = self.crypto.execute({"op": "recovery_seal", "code": code, "plaintext": encode(plaintext), "aad": encode(aad)})
            envelopes, references = self._envelopes(root)
            body = {**root, "encrypted_bundle": encode(json.dumps(sealed, separators=(",", ":")).encode()),
                    "device_roots": self._associations(keys), "envelopes": envelopes}
            snapshot = session.owner_access.recovery.root_history.seal(body, keys, admission, references, qualified)
            body["owner_access_snapshot"] = snapshot.envelope
            body["public_command"] = session.sign("recovery_public", {**root, "account_subject": session.subject,
                "issuer_admission": admission.document(), "owner_access_snapshot_digest": canonical_digest(self.crypto, snapshot.envelope),
                "owner_bindings_digest": snapshot.owner_bindings_digest})
            companion = RootAdmissionProof.create(self.crypto, root, session.public,
                session._device["signing_secret_key"], keys["signing_secret_key"])
            intent = RootReplacementIntent(SavedCommand("recovery_rotate",
                UncertainCommand(SignedEvidence.parse(session.sign("recovery_rotate", body)))), companion, tuple(references))
            self._save(intent)
            return {"code": code, "recovery": body}
        finally:
            keys.clear()
            wipe(plaintext)
            wipe(aad)

    def apply(self, draft: Mapping[str, Any]) -> None:
        session = self.session
        session.require_approved()
        value = session._device.get("recovery_replacement")
        if value is None:
            raise E2eeError("recovery_replacement_not_pending")
        intent = RootReplacementIntent.parse(session, value)
        if draft.get("recovery") != intent.saved.command.body or not isinstance(draft.get("code"), str):
            raise E2eeError("recovery_replacement_pending")
        self._apply(intent, draft["code"])

    def resume(self, code: str) -> None:
        self.session.require_approved()
        value = self.session._device.get("recovery_replacement")
        if value is None:
            raise E2eeError("recovery_replacement_not_pending")
        self._apply(RootReplacementIntent.parse(self.session, value), code)

    def _supersede(self, intent: RootReplacementIntent, current: Mapping[str, Any]) -> None:
        session, owner = self.session, self.session.owner_access
        root = owner.verifier.root(current, session.subject)
        for certificate in current.get("certificates", []):
            if certificate.get("operation") != "recovery_public":
                continue
            command = SignedEvidence.parse(certificate["signed_command"])
            if (command.body.get("account_subject") != session.subject
                    or any(command.body.get(name) != current[name] for name in ROOT_FIELDS)):
                continue
            fact = owner.account.witness(session.subject, command.digest(self.crypto, "recovery_public"))
            admission = OriginalIssuerAdmission.parse(fact.issuer_admission.to_dict())
            owner.current.historical_event("recovery_public", command, {
                "account_subject": session.subject, **{name: current[name] for name in ROOT_FIELDS}},
                admission.root, known_roots=tuple(owner.verifier.root(value, session.subject)
                    for value in owner.recovery.root_history.roots()))
            break
        else:
            raise E2eeError("owner_root_proof_missing")
        try:
            intent.saved.submit(lambda command: session.call("e2eeRotateRecovery", body=command),
                lambda: self._save(intent), rejections=frozenset({"revision_conflict"}))
        except E2eeError as error:
            if error.code != "revision_conflict" or not isinstance(intent.saved.outcome, RejectedCommand):
                raise
        session.trust.confirm_recovery(session.subject, current)
        session.recovery = dict(current)
        digest = intent.saved.command.digest(self.crypto, "recovery_rotate")
        session._device.setdefault(self.HISTORY_COLLECTION, {})[digest] = RootReplacementSupersession(intent, root).document()
        session._device.pop("recovery_replacement")
        session._persist()

    def _apply(self, intent: RootReplacementIntent, code: str) -> None:
        session, requested = self.session, intent.saved.command.body
        current = session.call("e2eeGetRecovery")
        if current["recovery_id"] != requested["recovery_id"] and current["generation"] >= requested["generation"]:
            self._supersede(intent, current)
            raise E2eeError("recovery_replacement_superseded")
        keys = open_recovery_code(self.crypto, session.subject, requested, code)
        try:
            if current["recovery_id"] == requested["recovery_id"]:
                if any(current.get(name) != requested[name] for name in (*ROOT_FIELDS, "encrypted_bundle")):
                    raise E2eeError("recovery_key_changed")
            elif current["generation"] + 1 != requested["generation"]:
                raise E2eeError("revision_conflict")
            intent.saved.submit(lambda command: session.call("e2eeRotateRecovery", body=command),
                                lambda: self._save(intent), rejections=frozenset())
            session.recovery = session.call("e2eeGetRecovery")
            if any(session.recovery.get(name) != requested[name] for name in (*ROOT_FIELDS, "encrypted_bundle")):
                raise E2eeError("recovery_key_changed")
            session.trust.confirm_private_recovery(session.recovery, keys)
            session.trust.confirm_recovery(session.subject, session.recovery)
            session.root_admissions.complete(intent.admission)
            session.owner_access.store.retain_roots(tuple(session.owner_access.verifier.root(item, session.subject)
                for item in session.owner_access.recovery.root_history.roots()))
            session._device["root_scope_generations"] = {"root": {"origin": session.trust.origin,
                "account_subject": session.subject, **intent.admission.root}, "operation": "recovery_rotate",
                "evidence_digest": intent.saved.command.digest(self.crypto, "recovery_rotate"),
                "references": [item.document() for item in intent.generations]}
            session._persist()
            session.owner_access.after_custody_change()
            session.reconcile_keys()
            session._device.pop("recovery_replacement")
            session._persist()
        finally:
            keys.clear()
