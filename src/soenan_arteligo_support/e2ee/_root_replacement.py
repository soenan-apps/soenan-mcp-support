from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError, decode, encode, wipe
from ._key_operation_proof import OperationProofContext
from ._owner_protocol import ROOT_FIELDS, OwnerBinding, OwnerManifest, OwnerOperation, SignedEvidence, authority_head, canonical_digest, custody, object_value
from ._owner_root_history import ScopeGenerationReference
from ._owner_sources import OriginalIssuerAdmission, OwnerIssuerEvidence
from ._owner_state import CandidateSecret, OwnerKey, PreparationStamp, SavedManifest
from ._root_admission import RootAdmissionProof, open_recovery_code
from ._root_operation import ProtectedRootDependencies, ProposedRootReplacement
from ._root_plan import RootReplacementPlan
from ._root_read_set import RootReadSet
from ._root_wire import root_request_digest
from ._signed_commands import AcceptedCommand, RejectedCommand, SavedCommand, UncertainCommand
from ._trust import _DEVICE_ROOT_DOMAIN, _RootIdentity, public_device

if TYPE_CHECKING:
    from ._session import DeviceSession


@dataclass
class RootReplacementIntent:
    saved: SavedCommand
    admission: RootAdmissionProof
    generations: tuple[ScopeGenerationReference, ...]
    operation: dict[str, Any] | None = None

    @classmethod
    def parse(cls, session: DeviceSession, value: Any) -> RootReplacementIntent:
        value = object_value(value)
        if set(value) - {"operation"} != {"saved_command", "root_admission", "scope_generations"}:
            raise E2eeError("unsupported_recovery_replacement_proof")
        saved = SavedCommand.parse(value["saved_command"], "recovery_rotate")
        admission = RootAdmissionProof.parse(session.crypto, value["root_admission"], session.public)
        if any(saved.command.body.get(name) != admission.root[name] for name in ROOT_FIELDS):
            raise E2eeError("invalid_recovery_replacement")
        saved.command.verify(session.crypto, session.public["signing_public_key"], "recovery_rotate")
        generations = tuple(ScopeGenerationReference.parse(item) for item in value["scope_generations"])
        if len({(item.scope, item.epoch) for item in generations}) != len(generations):
            raise E2eeError("invalid_recovery_replacement")
        operation = object_value(value["operation"]) if "operation" in value else None
        if operation is not None:
            if set(operation) - {"result", "legacy_root_receipts"} != {"operation_id", "read_set", "request", "local"}:
                raise E2eeError("invalid_recovery_replacement")
            request = object_value(operation["request"])
            if (request.get("root_command") != saved.command.document()
                    or request.get("companion_admission") != admission.command.document()):
                raise E2eeError("invalid_recovery_replacement")
        return cls(saved, admission, generations, operation)

    def document(self) -> dict[str, Any]:
        value = {"saved_command": self.saved.document(), "root_admission": self.admission.document(),
                 "scope_generations": [item.document() for item in self.generations]}
        if self.operation is not None:
            value["operation"] = self.operation
        return value


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

    def _archive(self, intent: RootReplacementIntent, history: dict[str, Any]) -> None:
        identity = ("operation:" + intent.operation["operation_id"] if intent.operation is not None
                    else intent.saved.command.digest(self.crypto, "recovery_rotate"))
        self.session._device.setdefault(self.HISTORY_COLLECTION, {})[identity] = history

    def _capture(self) -> tuple[RootReadSet, OperationProofContext]:
        session = self.session
        observed = session.owner_access.verifier.root(session.recovery, session.subject)
        pending = session._device.get("root_replacement_preparation")
        if pending is None or observed.generation > pending["expected_root"]["generation"]:
            pending = {"operation_id": secrets.token_urlsafe(24), "issuer_device_id": session.device_id,
                       "expected_root": observed.document(), "dependency_manifest": ProtectedRootDependencies.for_session(session)}
            session._device["root_replacement_preparation"] = pending
            session._persist()
        snapshot = RootReadSet.receive(pending["operation_id"], session._api.stream("e2eePrepareRootReplacement", body=pending))
        for name, values in pending["dependency_manifest"].items():
            if any(value not in snapshot.dependency_manifest.get(name, []) for value in values):
                raise E2eeError("root_replacement_dependency_missing")
        proof = OperationProofContext.from_wire(session, snapshot.proof_context)
        proof.require_identity(session, snapshot.operation_id)
        if (proof.digest != snapshot.preparation_digest
                or proof.context["key_state_digest"] != snapshot.key_state_digest
                or proof.context["manifest_digest"] != canonical_digest(self.crypto, snapshot.dependency_manifest)):
            raise E2eeError("invalid_key_operation_proof")
        self._require_closure(snapshot, proof)
        snapshot.remember(session, proof)
        for organization in self.session.owner_access.store.organizations():
            for saved in self.session.owner_access.store.get(organization).journal.values():
                if saved.operation == OwnerOperation.INVALIDATE and isinstance(saved.outcome, AcceptedCommand):
                    original = self._original_custody_receipt(proof, organization, saved.command)
                    if original is None or original["head"] != saved.outcome.result:
                        raise E2eeError("owner_receipt_missing")
        return snapshot, proof

    @staticmethod
    def _require_closure(snapshot: RootReadSet, proof: OperationProofContext) -> None:
        for reference in snapshot.dependency_manifest["references"]:
            if not any(all(result["target"].get(target, "") == reference.get(source, "") for source, target in (
                ("account_subject", "account_subject"), ("organization_id", "organization_id"),
                ("scope_id", "scope_id"), ("kind", "purpose"), ("origin_reference", "origin_reference"),
            )) for result in proof.targets):
                raise E2eeError("root_replacement_dependency_missing")
            for field, kind in (("root_evidence_digest", "custody_evidence"),
                                ("certificate_digest", "certificate_projection"),
                                ("transfer_operation_id", "transfer_decision")):
                if field in reference and not any(result["reference"]["kind"] == kind
                    and result["reference"]["account_subject"] == reference["account_subject"]
                    and result["reference"]["digest"] == reference[field] for result in proof.references):
                    raise E2eeError("root_replacement_dependency_missing")
        for reference in snapshot.dependency_manifest["retained_bindings"]:
            proof.selected(reference["organization_id"], reference["binding_digest"])

    def _original_custody_receipt(self, proof: OperationProofContext, organization: str,
                                  command: SignedEvidence) -> dict[str, Any] | None:
        body = command.body
        for value in proof.references:
            reference = value["reference"]
            if (reference["kind"] != "custody_receipt" or reference["account_subject"] != self.session.subject
                    or reference["organization_id"] != organization or reference["digest"] != body["request_id"]
                    or value["outcome"] != "available"):
                continue
            receipt = value["custody_receipt"]
            if (receipt["actor_subject"] != self.session.subject or receipt["organization_id"] != organization
                    or receipt["request_id"] != body["request_id"]
                    or receipt["requested_custody_revision"] != body["custody_revision"]):
                raise E2eeError("owner_receipt_mismatch")
            return receipt
        return None

    def _resolve_predecessor_registrations(self, snapshot: RootReadSet,
                                          proof: OperationProofContext) -> dict[str, Any]:
        owner, resolved = self.session.owner_access, {}
        for organization in owner.store.organizations():
            state = owner.store.get(organization)
            pending = state.registration
            if pending is None:
                continue
            command = pending.command
            if not any(value["operation"] == OwnerOperation.REGISTER_KEY
                       and value["signed_command"] == command.document()
                       for value in snapshot.dependency_manifest["pending_commands"]):
                raise E2eeError("root_replacement_dependency_missing")
            digest = command.digest(self.crypto, OwnerOperation.REGISTER_KEY)
            outcome = proof.reference_outcome("selected_binding", self.session.subject, organization, digest)
            if outcome["outcome"] == "denied":
                raise E2eeError("recovery_replacement_pending")
            if outcome["outcome"] == "available":
                selected = proof.selected(organization, digest).head
                binding = OwnerBinding.parse(command.document())
                binding_proof = snapshot.read("e2eeGetOwnerBinding", organization_id=organization, binding_digest=digest)
                if (binding_proof.get("signed_binding") != command.document() or pending.key is None
                        or selected.key_id != binding.body.key_id or selected.public_key != binding.body.public_key
                        or selected.public_key != owner.capsules.public_key(pending.key)):
                    raise E2eeError("owner_binding_mismatch")
                owner.verifier.binding(organization, binding_proof, selected)
                owner.keyring.merge(organization, [OwnerKey(selected.key_id, selected.key_epoch, selected.public_key,
                    selected.binding_digest, pending.key, binding)])
            elif outcome["outcome"] != "missing" or isinstance(pending.outcome, AcceptedCommand):
                raise E2eeError("recovery_replacement_pending")
            resolved[organization] = {"saved_command": pending.document(), "outcome": outcome["outcome"]}
        return resolved

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
            message = bytearray(_DEVICE_ROOT_DOMAIN) + self.crypto.canonical(checked)
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

    def _plan(self, intent: RootReplacementIntent, snapshot: RootReadSet,
              proof: OperationProofContext) -> None:
        session = self.session
        public = SignedEvidence.parse(intent.saved.command.body["public_command"])
        old = OriginalIssuerAdmission.parse(public.body["issuer_admission"]).root
        state = proof.subject(session.subject)
        revision = state["custody_revision"]
        legacy_receipts = None
        if all(snapshot.recovery.get(name) == intent.saved.command.body[name] for name in ROOT_FIELDS):
            legacy_receipts = self._legacy_receipts(intent, proof)
            session.trust.confirm_recovery(session.subject, snapshot.recovery)
            session.recovery = dict(snapshot.recovery)
            revision -= 1
        proposed = ProposedRootReplacement.create(self.crypto, old, intent.saved.command.body,
            public, intent.admission, session.public, revision)
        predecessors = self._resolve_predecessor_registrations(snapshot, proof)
        request, local = RootReplacementPlan(session, snapshot, proof, proposed,
            previous_admission=OriginalIssuerAdmission.parse(public.body["issuer_admission"])).build(
                intent.saved.command, intent.admission.command)
        local["predecessor_registrations"] = predecessors
        local["owner_journals"] = {
            organization: {slot: saved.document() for slot, saved in session.owner_access.store.get(organization).journal.items()}
            for organization in session.owner_access.store.organizations()
        }
        local["scope_journals"] = {
            collection: {scope: dict(value) for scope, value in session._device.get(collection, {}).items()}
            for collection in ("scope_rotations", "root_device_history")
        }
        intent.operation = {"operation_id": snapshot.operation_id, "read_set": snapshot.document(),
                            "request": request, "local": local}
        if legacy_receipts is not None:
            intent.operation["legacy_root_receipts"] = legacy_receipts
        session._device.pop("root_replacement_preparation", None)
        self._save(intent)

    def prepare(self) -> dict[str, Any]:
        session = self.session
        session.require_approved()
        if session.recovery_replacement_pending:
            raise E2eeError("recovery_replacement_pending")
        if session.recovery is None:
            raise E2eeError("recovery_missing")
        if session.recovery["generation"] >= 2**63 - 1:
            raise E2eeError("revision_conflict")
        snapshot, proof = self._capture()
        with snapshot.use(session, proof):
            if session.owner_access.verifier.root(snapshot.recovery, session.subject) != session.owner_access.verifier.root(session.recovery, session.subject):
                raise E2eeError("owner_custody_changed")
            self._resolve_predecessor_registrations(snapshot, proof)
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
                history = session.owner_access.recovery.root_history.seal(body, keys, admission, references, qualified)
                body["owner_access_snapshot"] = history.envelope
                body["public_command"] = session.sign("recovery_public", {**root, "account_subject": session.subject,
                    "issuer_admission": admission.document(), "owner_access_snapshot_digest": canonical_digest(self.crypto, history.envelope),
                    "owner_bindings_digest": history.owner_bindings_digest})
                companion = RootAdmissionProof.create(self.crypto, root, session.public,
                    session._device["signing_secret_key"], keys["signing_secret_key"])
                intent = RootReplacementIntent(SavedCommand("recovery_rotate",
                    UncertainCommand(SignedEvidence.parse(session.sign("recovery_rotate", body)))), companion, tuple(references))
                self._plan(intent, snapshot, proof)
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
        self.session._check_current()
        value = (self.session._device or {}).get("recovery_replacement")
        if value is None:
            raise E2eeError("recovery_replacement_not_pending")
        self._apply(RootReplacementIntent.parse(self.session, value), code)

    def _supersede(self, intent: RootReplacementIntent, current: Mapping[str, Any],
                   proof: OperationProofContext, applied: OperationProofContext | None = None) -> None:
        session, owner = self.session, self.session.owner_access
        root = owner.verifier.root(current, session.subject)
        if (root.generation < intent.saved.command.body["generation"]
                or root.generation == intent.saved.command.body["generation"] and (
                    applied is not None or isinstance(intent.saved.outcome, AcceptedCommand)
                    or intent.operation is not None and "legacy_root_receipts" in intent.operation)):
            raise E2eeError("recovery_key_changed")
        latest = proof.subject(session.subject).get("latest_root_transition")
        if latest is None or owner.verifier.root(latest["target"], session.subject) != root:
            raise E2eeError("owner_root_proof_missing")
        public = next((SignedEvidence.parse(value["signed_command"]) for value in current.get("certificates", [])
                       if value.get("operation") == "recovery_public"
                       and SignedEvidence.parse(value["signed_command"]).digest(self.crypto, "recovery_public") == latest["evidence_digest"]), None)
        if public is None:
            raise E2eeError("owner_root_proof_missing")
        admission = OriginalIssuerAdmission.parse(latest["issuer_admission"])
        owner.current.historical_event("recovery_public", public,
            {"account_subject": session.subject, **{name: current[name] for name in ROOT_FIELDS}}, admission.root)
        if applied is not None:
            for organization, planned in intent.operation["local"]["keys"].items():
                selected = applied.selected(organization, planned["head"]["binding_digest"]).head
                if selected.to_dict() != planned["head"]:
                    raise E2eeError("owner_binding_mismatch")
                owner.keyring.merge(organization, [OwnerKey(selected.key_id, selected.key_epoch, selected.public_key,
                    selected.binding_digest, planned["secret"], OwnerBinding.parse(planned["command"]))])
            for organization, planned in intent.operation["local"]["candidates"].items():
                binding = OwnerBinding.parse(planned["command"])
                candidate = CandidateSecret(planned["secret"], custody({
                    "recovery_id": binding.body.recovery_id, "recovery_generation": binding.body.recovery_generation,
                    "root_revision": binding.body.root_revision, "custody_revision": binding.body.custody_revision,
                }), binding, True)
                state = owner.store.get(organization)
                if candidate not in state.retired_candidates:
                    state.retired_candidates.append(candidate)
                    owner.store.save(organization)
        session.trust.confirm_recovery(session.subject, current)
        session.recovery = dict(current)
        history = RootReplacementSupersession(intent, root).document()
        self._archive(intent, history)
        if session._device.get("root_admission") == intent.admission.document():
            session._device.pop("root_admission")
        session._device.pop("recovery_replacement")
        session._device.pop("root_replacement_preparation", None)
        session._persist()

    def _settle(self, intent: RootReplacementIntent, snapshot: RootReadSet,
                receipt: OperationProofContext, result: Mapping[str, Any], keys: Mapping[str, str],
                current_snapshot: RootReadSet, current_proof: OperationProofContext) -> None:
        session, owner = self.session, self.session.owner_access
        requested = intent.saved.command.body
        acknowledged = object_value(result.get("recovery"))
        current = current_snapshot.recovery
        if any(acknowledged.get(name) != requested[name] or current.get(name) != requested[name]
               for name in (*ROOT_FIELDS, "encrypted_bundle")):
            raise E2eeError("recovery_key_changed")
        public = SignedEvidence.parse(requested["public_command"])
        witness = receipt.witness(session.subject, public.digest(self.crypto, "recovery_public"))
        if witness.target.to_dict() != {"kind": "recovery_root", "account_subject": session.subject,
                                       **{name: requested[name] for name in ROOT_FIELDS}}:
            raise E2eeError("owner_custody_evidence_mismatch")
        original = OriginalIssuerAdmission.parse(public.body["issuer_admission"])
        owner.current.historical_event("recovery_public", public,
            {"account_subject": session.subject, **{name: requested[name] for name in ROOT_FIELDS}}, original.root)
        material = object_value(result.get("issuer_device"))
        if (public_device(material) != session.public or material.get("state") != "approved"
                or not any(value.get("operation") == "device_add_by_key"
                           and value.get("signed_command") == intent.admission.command.document()
                           for value in material.get("certificates", []))):
            raise E2eeError("root_admission_unconfirmed")
        material = current_snapshot.device(None, session.device_id)
        if public_device(material) != session.public or material.get("state") != "approved":
            raise E2eeError("device_revoked")
        owner.current._require_nonnegative(material)
        session.trust.confirm_private_recovery(current, keys)
        session.trust.confirm_recovery(session.subject, current)
        session.recovery = dict(current)
        session._devices[session.device_id] = material
        session._device["root_scope_generations"] = {"root": {"origin": session.trust.origin,
            "account_subject": session.subject, **intent.admission.root}, "operation": "recovery_rotate",
            "evidence_digest": intent.saved.command.digest(self.crypto, "recovery_rotate"),
            "references": [item.document() for item in intent.generations]}
        session._persist()
        local = intent.operation["local"]
        for organization, planned in local["keys"].items():
            selected = receipt.selected(organization, planned["head"]["binding_digest"])
            if selected.head.to_dict() != planned["head"]:
                raise E2eeError("owner_binding_mismatch")
            binding = OwnerBinding.parse(planned["command"])
            proof = snapshot.read("e2eeGetOwnerBinding", organization_id=organization,
                                  binding_digest=selected.head.binding_digest)
            owner.verifier.binding(organization, proof, selected.head)
            owner.keyring.merge(organization, [OwnerKey(selected.head.key_id, selected.head.key_epoch,
                selected.head.public_key, selected.head.binding_digest, planned["secret"], binding)])
        live = current_proof
        actual_custody = custody({"recovery_id": current["recovery_id"], "recovery_generation": current["generation"],
                                 "root_revision": current["generation"], "custody_revision": live.subject(session.subject)["custody_revision"]})
        invalidations = self._settle_custody_invalidations(intent, snapshot, receipt, result, actual_custody)
        for organization, planned in local["candidates"].items():
            binding = OwnerBinding.parse(planned["command"])
            candidates = receipt.organizations[organization]["candidates"]
            if not any(value["offer_digest"] == binding.command.digest(self.crypto, OwnerOperation.OFFER) for value in candidates):
                raise E2eeError("owner_candidate_invalidated")
            owner.verifier.candidate(organization, {"offer": planned["command"],
                "offer_digest": binding.command.digest(self.crypto, OwnerOperation.OFFER)})
            state = owner.store.get(organization)
            qualified = {value["offer_digest"] for value in live.organizations.get(organization, {}).get("candidates", [])}
            if state.candidate is not None and (
                state.candidate.custody != actual_custody
                or state.candidate.binding.command.digest(self.crypto, OwnerOperation.OFFER) not in qualified
            ):
                if state.candidate not in state.retired_candidates:
                    state.retired_candidates.append(state.candidate)
                state.candidate = None
            candidate = CandidateSecret(planned["secret"], custody({
                "recovery_id": binding.body.recovery_id, "recovery_generation": binding.body.recovery_generation,
                "root_revision": binding.body.root_revision, "custody_revision": binding.body.custody_revision,
            }), binding, True)
            if (candidate.custody == actual_custody
                    and candidate.binding.command.digest(self.crypto, OwnerOperation.OFFER) in qualified
                    and (state.candidate is None or state.candidate.binding == binding)):
                state.candidate = candidate
            elif candidate not in state.retired_candidates:
                state.retired_candidates.append(candidate)
            state.custody = actual_custody
            head, previous_head = receipt.authority(organization).head, state.observed_head
            if (previous_head is not None and head.key_epoch == previous_head.key_epoch
                    and head.binding_digest != previous_head.binding_digest):
                raise E2eeError("owner_authority_rollback")
            if (previous_head is None or head.key_epoch >= previous_head.key_epoch
                    and head.ownership_revision >= previous_head.ownership_revision):
                state.observed_head = head
            state.prepared.clear()
            owner.store.save(organization)
        settled = {value["scope"]["project_id"]: value for value in result.get("settled_scopes", [])}
        for entry in intent.operation["request"]["scope_commands"]:
            command = SignedEvidence.parse(entry["signed_command"])
            scope = command.body["scope_id"]
            actual = settled.get(scope)
            if actual is None or any(not any(
                candidate.get("signed_command") == command.document()
                and all(candidate.get(name) == value for name, value in envelope.items())
                for candidate in actual["envelopes"]) for envelope in command.body.get("envelopes", [])):
                raise E2eeError("recovery_replacement_pending")
        for envelope in requested["envelopes"]:
            actual = settled.get(envelope["scope_id"])
            if actual is None or not any(candidate.get("signed_command") == intent.saved.command.document()
                and all(candidate.get(name) == value for name, value in envelope.items())
                for candidate in actual["envelopes"]):
                raise E2eeError("recovery_replacement_pending")
        for scope, planned in local["rotations"].items():
            actual = settled.get(scope)
            if actual is None or not any(value.get("signed_command") == planned["command"]
                                        for value in actual["generations"]):
                raise E2eeError("recovery_replacement_pending")
            current_scope = current_snapshot.scopes.get(scope)
            if current_scope is not None and current_proof.scope_authorized(
                    session.subject, current_scope["scope"]["owner_org"], scope,
                    current_scope["authorization_basis"], "interactive_read"):
                key = decode(planned["key"])
                try:
                    session._remember(scope, planned["epoch"], key, owner=session._scope_owner(scope))
                finally:
                    wipe(key)
        for submission in intent.operation["request"]["source_submissions"]:
            manifest = OwnerManifest.parse(self.crypto, submission["signed_command"], submission["documents"])
            organization = manifest.body.organization_id
            state = owner.store.get(organization)
            artifact = snapshot.read("e2eeGetOwnerManifestDocuments", organization_id=organization,
                                     manifest_id=manifest.body.manifest_id)
            if artifact["signed_command"] != submission["signed_command"] or artifact["documents"] != submission["documents"]:
                raise E2eeError("owner_source_manifest_mismatch")
            proof = snapshot.read("e2eeGetOwnerBinding", organization_id=organization,
                                  binding_digest=manifest.body.owner_authority.binding_digest)
            source = owner.verifier.binding(organization, proof, receipt.authority(organization).head)
            issuer = OwnerIssuerEvidence.parse(artifact["issuer_evidence"])
            evidence = owner.verifier.manifest(organization, manifest, source, issuer)
            state.manifests[manifest.body.manifest_id] = SavedManifest(manifest, issuer_evidence=evidence)
            owner.store.save(organization)
        for command in intent.operation["request"]["keyring_commands"]:
            organization = SignedEvidence.parse(command).body["organization_id"]
            if snapshot.owner(organization)["keyring"]["signed_command"] != command:
                raise E2eeError("owner_keyring_mismatch")
        for command in intent.operation["request"]["preparation_commands"]:
            body = SignedEvidence.parse(command).body
            if not any(value["signed_command"] == command for value in snapshot.owner(body["organization_id"])["preparations"]):
                raise E2eeError("owner_preparation_missing")
            if receipt.gate(body["organization_id"], body["gate_descriptor"]["gate_id"]).to_dict() != body["gate_descriptor"]:
                raise E2eeError("owner_gate_mismatch")
            state = owner.store.get(body["organization_id"])
            state.prepared[body["candidate_id"]] = PreparationStamp(receipt.authority(body["organization_id"]).head,
                                                                  body["offer_digest"], body["source_manifest_digest"])
            owner.store.save(body["organization_id"])
        self._finish_journals(intent, invalidations)
        owner.store.retain_roots(tuple(owner.verifier.root(value, session.subject) for value in owner.recovery.root_history.roots()))
        if session._device.get("root_admission") == intent.admission.document():
            session._device.pop("root_admission")
        if "legacy_root_receipts" not in intent.operation:
            intent.saved.outcome = AcceptedCommand(intent.saved.command, intent.operation["result"])
        self._save(intent)
        session._device.pop("recovery_replacement")
        session._device.pop("root_replacement_preparation", None)
        session._persist()

    def _settle_custody_invalidations(self, intent: RootReplacementIntent, snapshot: RootReadSet,
                                     receipt: OperationProofContext, result: Mapping[str, Any],
                                     actual_custody: Any) -> list[dict[str, Any]]:
        confirmed = []
        for pending in snapshot.dependency_manifest["pending_commands"]:
            if pending["operation"] != OwnerOperation.INVALIDATE:
                continue
            command = SignedEvidence.parse(pending["signed_command"])
            body = command.body
            organization = body["organization_id"]
            matches = [value for value in result.get("settled_custody_invalidations", [])
                       if value["signed_command"] == command.document()]
            if len(matches) != 1:
                raise E2eeError("recovery_replacement_pending")
            head = authority_head(matches[0]["owner_authority"], organization)
            state = self.session.owner_access.store.get(organization)
            journals = [(slot, saved) for slot, saved in state.journal.items() if saved.command == command]
            original = self._original_custody_receipt(receipt, organization, command)
            for _, saved in journals:
                if isinstance(saved.outcome, AcceptedCommand) and (
                    original is None or original["head"] != saved.outcome.result
                ):
                    raise E2eeError("owner_receipt_missing")
            allowed = [original["head"]] if original is not None else []
            transition = receipt.receipt["root_transition"]
            if transition["custody_revision"] >= body["custody_revision"]:
                allowed.extend(value for value in receipt.receipt.get("root_invalidation_heads", [])
                               if value["organization_id"] == organization)
            if head.to_dict() not in allowed:
                raise E2eeError("owner_invalidation_unconfirmed")
            retired = intent.operation["local"].setdefault("custody_journals", [])
            for slot, saved in journals:
                item = {"organization_id": organization, "slot": slot, "saved_command": saved.document(),
                        "disposition": "accepted" if original is not None else "superseded_by_root"}
                if original is not None:
                    item["original_receipt"] = original
                if item not in retired:
                    retired.append(item)
            if state.candidate is not None and state.candidate.custody != actual_custody:
                state.retired_candidates.append(state.candidate)
                state.candidate = None
            state.custody = actual_custody
            state.prepared.clear()
            self.session.owner_access.store.save(organization)
            confirmed.append(command.document())
        return confirmed

    def _finish_journals(self, intent: RootReplacementIntent, invalidations: list[dict[str, Any]]) -> None:
        request, local, session = intent.operation["request"], intent.operation["local"], self.session
        committed = [request["root_command"], request["companion_admission"], *invalidations]
        for name in ("owner_key_commands", "owner_candidate_commands", "keyring_commands", "gate_commands", "preparation_commands"):
            committed.extend(request[name])
        committed.extend(item["signed_command"] for item in request["scope_commands"])
        committed.extend(item["signed_command"] for item in request["source_submissions"])
        self._archive(intent, {"intent": intent.document(), "state": "accepted"})
        self._save(intent)
        for organization in session.owner_access.store.organizations():
            state = session.owner_access.store.get(organization)
            retired = local["owner_journals"].get(organization, {})
            state.journal = {
                slot: saved for slot, saved in state.journal.items()
                if saved.command.document() not in committed
                and (saved.document() != retired.get(slot)
                     or not isinstance(saved.outcome, (AcceptedCommand, RejectedCommand)))
            }
            predecessor = local["predecessor_registrations"].get(organization)
            if (state.registration is not None and predecessor is not None
                    and state.registration.document() == predecessor["saved_command"]):
                state.registration = None
            session.owner_access.store.save(organization)
        for collection, retired in local["scope_journals"].items():
            pending = session._device.get(collection, {})
            for scope, saved in retired.items():
                if pending.get(scope) != saved:
                    continue
                journal = SavedCommand.parse(saved)
                rotation = local["rotations"].get(scope) if collection == "scope_rotations" else None
                if (journal.command.document() in committed or (rotation is not None
                        and journal.command.body.get("expected_epoch", rotation["epoch"]) < rotation["epoch"])):
                    pending.pop(scope)
        session._persist()

    def _legacy_receipts(self, intent: RootReplacementIntent, proof: OperationProofContext) -> list[dict[str, Any]]:
        session, owner = self.session, self.session.owner_access
        requested = intent.saved.command.body
        if any(session._root_read_set.recovery.get(name) != requested[name] for name in (*ROOT_FIELDS, "encrypted_bundle")):
            raise E2eeError("recovery_key_changed")
        public = SignedEvidence.parse(requested["public_command"])
        evidence_digest = public.digest(self.crypto, "recovery_public")
        evidence = proof.witness(session.subject, evidence_digest)
        receipt_id = "custody_" + intent.saved.command.digest(self.crypto, "recovery_rotate")
        receipts = [value["custody_receipt"] for value in proof.references
                    if value["reference"]["kind"] == "custody_receipt"
                    and value["reference"]["account_subject"] == session.subject
                    and value["reference"]["digest"] == receipt_id and value["outcome"] == "available"]
        current_revision = proof.subject(session.subject)["custody_revision"]
        receipts = [receipt for receipt in receipts
                    if receipt["actor_subject"] == session.subject and receipt["request_id"] == receipt_id
                    and evidence.accepted_custody_revision <= receipt["custody_revision"] <= current_revision
                    and any(item == evidence.to_dict() for item in receipt["custody_evidence"])]
        if not receipts:
            raise E2eeError("owner_receipt_missing")
        original = OriginalIssuerAdmission.parse(public.body["issuer_admission"])
        owner.current.historical_event("recovery_public", public,
            {"account_subject": session.subject, **{name: requested[name] for name in ROOT_FIELDS}}, original.root)
        return receipts


    def _current_context(self, result: Mapping[str, Any]) -> tuple[RootReadSet, OperationProofContext] | None:
        outcome = result.get("current_proof_context_outcome")
        wire = result.get("current_proof_context")
        if outcome not in {"available", "unavailable"}:
            raise E2eeError("invalid_key_operation_proof")
        if outcome == "unavailable":
            if wire is not None:
                raise E2eeError("invalid_key_operation_proof")
            return None
        if not isinstance(wire, str):
            raise E2eeError("invalid_key_operation_proof")
        raw = decode(wire)
        try:
            current = RootReadSet.from_context(self.session, object_value(json.loads(raw)))
        finally:
            wipe(raw)
        if current.operation_id != result["operation_id"]:
            raise E2eeError("operation_proof_context_mismatch")
        proof = OperationProofContext.from_wire(self.session, current.proof_context)
        return current, proof

    def _apply(self, intent: RootReplacementIntent, code: str) -> None:
        session, requested = self.session, intent.saved.command.body
        keys = open_recovery_code(self.crypto, session.subject, requested, code)
        try:
            if intent.operation is None:
                if isinstance(intent.saved.outcome, RejectedCommand):
                    raise E2eeError(intent.saved.outcome.code)
                session.require_approved()
                snapshot, proof = self._capture()
                with snapshot.use(session, proof):
                    current = snapshot.recovery
                    if (current["recovery_id"] != requested["recovery_id"]
                            and current["generation"] >= requested["generation"]):
                        self._supersede(intent, current, proof)
                        raise E2eeError("recovery_replacement_superseded")
                    self._plan(intent, snapshot, proof)
            operation = intent.operation
            snapshot = RootReadSet.parse(operation["read_set"])
            preparation = OperationProofContext.from_wire(session, snapshot.proof_context)
            expected_digest = root_request_digest(operation["operation_id"], operation["request"])
            stored = operation.get("result")
            try:
                result = session.call("e2eeApplyRootReplacement",
                    operation_id=operation["operation_id"], body=operation["request"])
            except E2eeError as error:
                if error.code in {"authentication_superseded", "device_session_superseded"} or error.code.startswith("authorization_"):
                    raise
                if stored is not None and stored.get("phase") == "locally_applied":
                    raise E2eeError("root_current_state_unavailable") from None
                raise E2eeError("recovery_replacement_pending") from None
            if (result.get("operation_id") != operation["operation_id"]
                    or result.get("phase") not in {"locally_applied", "rejected"}
                    or result.get("request_digest") != expected_digest):
                raise E2eeError("invalid_key_operation_proof")
            proof = OperationProofContext.from_wire(session, result["proof_context"])
            proof.require_identity(session, operation["operation_id"], preparation, request_digest=expected_digest)
            rejection = result["phase"] == "rejected"
            if (rejection and (proof.rejection is None or proof.digest != result.get("rejection_digest"))
                    or not rejection and (proof.receipt is None or proof.digest != result.get("receipt_digest"))):
                raise E2eeError("invalid_key_operation_proof")
            original = {name: value for name, value in result.items()
                        if name not in {"current_proof_context", "current_proof_context_outcome"}}
            if stored is not None and stored != original:
                raise E2eeError("invalid_key_operation_proof")
            operation["result"] = original
            if not rejection and "legacy_root_receipts" not in operation:
                intent.saved.outcome = AcceptedCommand(intent.saved.command, original)
            self._save(intent)
            if rejection:
                current = self._current_context(result)
                if current is not None:
                    current_snapshot, current_proof = current
                    current_snapshot.remember(session, current_proof)
                    with current_snapshot.use(session, current_proof):
                        if (current_snapshot.recovery["recovery_id"] != requested["recovery_id"]
                                and current_snapshot.recovery["generation"] >= requested["generation"]):
                            self._supersede(intent, current_snapshot.recovery, current_proof)
                            raise E2eeError("recovery_replacement_superseded")
                error_code = "access_denied" if proof.rejection["reason"] == "access_denied" else "revision_conflict"
                if "legacy_root_receipts" not in operation:
                    intent.saved.outcome = RejectedCommand(intent.saved.command, error_code)
                self._archive(intent, {"intent": intent.document(), "state": "rejected"})
                if "legacy_root_receipts" in operation:
                    intent.operation = None
                    self._save(intent)
                else:
                    session._device.pop("recovery_replacement")
                session._device.pop("root_replacement_preparation", None)
                session._persist()
                raise E2eeError(error_code)
            self._archive(intent, {"intent": intent.document(), "state": "accepted"})
            session._persist()
            current = self._current_context(result)
            if current is None:
                raise E2eeError("root_current_state_unavailable")
            current_snapshot, current_proof = current
            current_snapshot.remember(session, current_proof)
            with current_snapshot.use(session, current_proof):
                if any(current_snapshot.recovery.get(name) != requested[name] for name in ROOT_FIELDS):
                    if current_snapshot.recovery.get("generation", 0) >= requested["generation"]:
                        self._supersede(intent, current_snapshot.recovery, current_proof, applied=proof)
                        raise E2eeError("recovery_replacement_superseded")
                    raise E2eeError("recovery_key_changed")
                material = current_snapshot.device(None, session.device_id)
                session.owner_access.current._require_nonnegative(material)
                if material.get("state") != "approved":
                    raise E2eeError("device_revoked")
            settled = snapshot.settled(result)
            with settled.use(session, proof):
                self._settle(intent, settled, proof, result, keys, current_snapshot, current_proof)
            session._proof_read_set = current_snapshot
            session.owner_access.reads._operation = current_proof
        finally:
            keys.clear()
