from __future__ import annotations

import json
import secrets
from typing import TYPE_CHECKING, Any, Callable
from urllib.parse import urlsplit

from ._crypto import E2eeError, decode, wipe
from ._oauth import origin
from ._owner_authority import OwnerAuthorityReads
from ._owner_commands import OwnerCommands
from ._owner_keyring import OwnerKeyring
from ._owner_protocol import (
    OwnerAuthorityHead, OwnerCapsuleCrypto, OwnerDomain, OwnerManifest, OwnerOperation,
    OwnerPreparation, authority_head, bytes32, canonical_digest, committed_decision,
    custody, object_value,
)
from ._owner_state import (
    CandidateSecret, ManifestSelection, OwnerKey, OwnerStateStore, PreparationStamp, SavedManifest,
)
from ._owner_verifier import OwnerEvidenceVerifier
from ._owner_sources import OriginalIssuerAdmission, OwnerIssuerEvidence

if TYPE_CHECKING:
    from ._session import DeviceSession


class OwnerHandoffs:
    def __init__(self, session: DeviceSession, store: OwnerStateStore,
                 account: OwnerAuthorityReads, commands: OwnerCommands,
                 verifier: OwnerEvidenceVerifier, capsules: OwnerCapsuleCrypto, keyring: OwnerKeyring):
        self.session, self.store, self.reads = session, store, account
        self.commands, self.verifier, self.capsules = commands, verifier, capsules
        self.crypto = session.crypto
        self.keyring = keyring

    @staticmethod
    def consume_link(link: str, arteligo_origin: str) -> dict[str, str]:
        try:
            parsed = urlsplit(link)
            if (parsed.scheme + "://" + parsed.netloc != origin(arteligo_origin)
                    or parsed.path not in {"", "/"} or parsed.query
                    or not parsed.fragment.startswith("owner-handoff=")):
                raise E2eeError("invalid_owner_handoff_link")
            raw = decode(parsed.fragment[len("owner-handoff="):])
            try:
                action = object_value(json.loads(raw))
            finally:
                wipe(raw)
            if set(action) != {"organization_id", "operation_id", "gate_id", "gate_private_key", "read_capability"} or any(
                not isinstance(value, str) or not value for value in action.values()
            ):
                raise E2eeError("invalid_owner_handoff_link")
            bytes32(action["gate_private_key"])
            return action
        except (ValueError, TypeError):
            raise E2eeError("invalid_owner_handoff_link") from None

    def prepare(self, organization: str, head: OwnerAuthorityHead,
                entry: dict[str, Any], manifest: OwnerManifest) -> None:
        binding = self.verifier.candidate(organization, entry)
        candidate = binding.body
        state = self.store.get(organization)
        desired = PreparationStamp(head, entry["offer_digest"], manifest.digest)
        slot, gate_slot = "prepare:" + candidate.candidate_id, "gate:" + candidate.candidate_id
        pending = state.journal.get(slot)
        if pending is not None:
            self.commands.submit(organization, slot, OwnerOperation.PREPARE)
            prepared = OwnerPreparation.parse(pending.command.document())
            state.prepared[candidate.candidate_id] = PreparationStamp(
                authority_head(prepared.body.owner_authority.to_dict(), organization),
                prepared.body.offer_digest, prepared.body.source_manifest_digest,
            )
            self.store.finish(organization, slot)
            self.store.finish(organization, gate_slot)
        if state.prepared.get(candidate.candidate_id) == desired:
            return
        keys = [key.document() for key in state.keys]
        keyring = [key.public_binding() for key in state.keys]
        expected_gate = {
            "organization_id": organization, "candidate_id": candidate.candidate_id,
            "ownership_revision": head.ownership_revision, "source_key_epoch": head.key_epoch,
            "source_binding_digest": head.binding_digest, "offer_digest": entry["offer_digest"],
            "source_manifest_id": manifest.body.manifest_id, "source_manifest_digest": manifest.digest,
            "history_manifest_digest": canonical_digest(self.crypto, keyring),
        }
        qualified = self.session.owner_access._qualify_local(organization, head)
        issuer_admission = qualified.original_admission.document()
        previous_gate = state.journal.get(gate_slot)
        if previous_gate is not None:
            self.commands.submit(organization, gate_slot, OwnerOperation.GATE)
            if any(previous_gate.command.body.get(field) != value for field, value in expected_gate.items()):
                self.store.finish(organization, gate_slot)
        gate_response = self.commands.submit(organization, gate_slot, OwnerOperation.GATE, {
            **expected_gate, "preparation_id": secrets.token_urlsafe(24), "issuer_admission": issuer_admission,
        })
        gate_request = state.journal[gate_slot].command.body
        issuer_admission = OriginalIssuerAdmission.parse(gate_request.get("issuer_admission")).document()
        suggested = object_value(gate_response.get("gate", gate_response))
        gate = self.reads.gate(organization, suggested.get("gate_id"))
        gate_document = gate.to_dict()
        if any(gate_document.get(field) != value for field, value in gate_request.items() if field != "issuer_admission"):
            raise E2eeError("owner_gate_mismatch")
        prepared = {
            "organization_id": organization, "preparation_id": gate.preparation_id,
            "owner_authority": head.to_dict(), "candidate_id": candidate.candidate_id,
            "offer_digest": entry["offer_digest"], "source_manifest_id": manifest.body.manifest_id,
            "source_manifest_digest": manifest.digest, "keyring_manifest": keyring,
            "gate_descriptor": gate_document,
            "issuer_admission": issuer_admission,
        }
        plaintext = self.crypto.canonical({"v": 1, "organization_id": organization, "keys": keys})
        inner_raw = bytearray()
        try:
            sender_secret = self.session._device["encryption_secret_key"]
            inner = self.capsules.seal(sender_secret, candidate.public_key, plaintext, prepared, OwnerDomain.INNER)
            inner_raw = self.crypto.canonical(inner)
            capsule = self.capsules.seal(sender_secret, gate.public_key, inner_raw, prepared, OwnerDomain.OUTER)
        finally:
            wipe(plaintext)
            wipe(inner_raw)
        self.commands.submit(organization, slot, OwnerOperation.PREPARE, {
            **prepared, "capsule": capsule, "capsule_digest": canonical_digest(self.crypto, capsule),
        })
        state.prepared[candidate.candidate_id] = desired
        self.store.finish(organization, slot)
        self.store.finish(organization, gate_slot)

    def _select_action(self, action: dict[str, str] | None) -> tuple[str, dict[str, str]]:
        if action is not None:
            if set(action) != {"organization_id", "operation_id", "gate_id", "gate_private_key", "read_capability"} or any(
                not isinstance(value, str) or not value for value in action.values()
            ):
                raise E2eeError("invalid_owner_handoff_link")
            bytes32(action["gate_private_key"])
            organization = action["organization_id"]
            state = self.store.get(organization)
            if state.pending_import is not None and state.pending_import != action:
                raise E2eeError("owner_handoff_import_pending")
            state.pending_import = dict(action)
            self.store.save(organization)
            return organization, action
        pending = [(organization, self.store.get(organization).pending_import)
                   for organization in self.store.organizations()
                   if self.store.get(organization).pending_import is not None]
        if len(pending) != 1:
            raise E2eeError("owner_handoff_import_not_selected")
        return pending[0]

    def import_action(self, action: dict[str, str] | None,
                      authority: Callable[[str], OwnerAuthorityHead]) -> dict[str, str]:
        organization, action = self._select_action(action)
        self.session.load_owner_context(organization=organization, gate_ids=[action["gate_id"]],
                                        operation_ids=[action["operation_id"]])
        state = self.store.get(organization)
        if state.source_anchor is None:
            raise E2eeError("owner_source_anchor_missing")
        decision = committed_decision(self.reads.decision(organization, action["operation_id"]), organization)
        selected_head = authority_head(decision.head.to_dict(), organization)
        candidates = [*state.retired_candidates, *([state.candidate] if state.candidate is not None else [])]
        for key in state.keys:
            if key.binding.operation == OwnerOperation.OFFER:
                body = key.binding.body
                candidates.append(CandidateSecret(key.secret_key, custody({
                    "recovery_id": body.recovery_id, "recovery_generation": body.recovery_generation,
                    "root_revision": body.root_revision, "custody_revision": body.custody_revision,
                }), key.binding, True))
        candidate = next((item for item in candidates if item.binding.body.candidate_id == decision.candidate_id), None)
        if (candidate is None or candidate.binding.body.account_subject != self.session.subject
                or self.capsules.public_key(candidate.secret_key) != candidate.binding.body.public_key):
            raise E2eeError("owner_candidate_secret_missing")
        offered = candidate.binding.body
        if (offered.organization_id != organization or decision.target_subject != self.session.subject
                or decision.candidate_offer_digest != candidate.binding.command.digest(self.crypto, OwnerOperation.OFFER)
                or decision.gate_id != action["gate_id"] or selected_head.key_id != offered.key_id
                or selected_head.public_key != offered.public_key
                or selected_head.binding_digest != decision.candidate_offer_digest):
            raise E2eeError("owner_receipt_mismatch")
        gate = self.reads.gate(organization, action["gate_id"])
        if self.capsules.public_key(action["gate_private_key"]) != gate.public_key:
            raise E2eeError("owner_gate_mismatch")
        saved = self.session.call("e2eeGetOwnerPreparation", organization_id=organization,
                                  preparation_id=decision.preparation_id)
        preparation = OwnerPreparation.parse(saved.get("signed_command"))
        body = preparation.body
        source_head = authority_head(body.owner_authority.to_dict(), organization)
        proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization,
                                  binding_digest=source_head.binding_digest)
        source = self.verifier.binding(organization, proof, source_head)
        target_proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization,
                                         binding_digest=selected_head.binding_digest)
        selected_binding = self.verifier.binding(organization, target_proof, selected_head)
        if selected_binding.binding.command != candidate.binding.command:
            raise E2eeError("owner_receipt_mismatch")
        sender = self.verifier.preparation_issuer(organization, preparation, source,
            OwnerIssuerEvidence.parse(target_proof.get("issuer_evidence")))
        if (body.gate_descriptor.to_dict() != gate.to_dict()
                or body.capsule_digest != canonical_digest(self.crypto, body.capsule.to_dict())
                or gate.organization_id != organization or gate.candidate_id != offered.candidate_id
                or gate.preparation_id != body.preparation_id
                or gate.source_manifest_id != body.source_manifest_id
                or gate.source_manifest_digest != body.source_manifest_digest
                or gate.source_binding_digest != source_head.binding_digest
                or gate.source_key_epoch != source_head.key_epoch
                or gate.ownership_revision != source_head.ownership_revision
                or gate.offer_digest != decision.candidate_offer_digest
                or gate.history_manifest_digest != canonical_digest(self.crypto, [item.to_dict() for item in body.keyring_manifest])):
            raise E2eeError("owner_gate_mismatch")
        decision = self.verifier.verify_decision(organization, decision, preparation, offered, selected_head)
        saved_manifest = self.session.call("e2eeGetOwnerManifestDocuments", organization_id=organization,
                                           manifest_id=body.source_manifest_id)
        manifest = OwnerManifest.parse(self.crypto, saved_manifest.get("signed_command"), saved_manifest.get("documents"))
        if manifest.digest != body.source_manifest_digest or manifest.body.manifest_id != body.source_manifest_id:
            raise E2eeError("owner_source_manifest_mismatch")
        outer = self.capsules.open(action["gate_private_key"], sender, body.capsule.to_dict(),
                                   preparation.context(), OwnerDomain.OUTER)
        inner = bytearray()
        try:
            inner = self.capsules.open(candidate.secret_key, sender, object_value(json.loads(outer)),
                                       preparation.context(), OwnerDomain.INNER)
            payload = object_value(json.loads(inner))
            if payload.get("v") != 1 or payload.get("organization_id") != organization or not isinstance(payload.get("keys"), list):
                raise E2eeError("owner_keyring_mismatch")
            keys = self.keyring.verify_history(organization, payload["keys"],
                [item.to_dict() for item in body.keyring_manifest], source_head)
            if any(key.key_id == offered.key_id or key.public_key == offered.public_key for key in keys):
                raise E2eeError("owner_keyring_mismatch")
            evidence = self.verifier.manifest(organization, manifest, source, OwnerIssuerEvidence.parse(saved_manifest.get("issuer_evidence")))
            active = OwnerKey(selected_head.key_id, selected_head.key_epoch, selected_head.public_key,
                              selected_head.binding_digest, candidate.secret_key, candidate.binding)
            self.keyring.merge(organization, [*keys, active])
        except (ValueError, KeyError, TypeError):
            raise E2eeError("invalid_owner_handoff") from None
        finally:
            wipe(outer)
            wipe(inner)
        state.manifests[manifest.body.manifest_id] = SavedManifest(
            manifest, ManifestSelection(proof, preparation.command, decision), issuer_evidence=evidence)
        state.receipts[decision.operation_id] = decision
        self.store.save(organization)
        current = authority(organization)
        if current.owner_subject == self.session.subject:
            self.keyring.backup(organization, current)
        state.completed_imports.add(decision.operation_id)
        state.pending_import = None
        self.store.save(organization)
        return {"organization_id": organization, "operation_id": decision.operation_id, "state": "ready"}
