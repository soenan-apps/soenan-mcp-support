from __future__ import annotations

import json
import secrets
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_envelopes import OWNER_KEY_PROOF
from ._owner_protocol import OwnerBinding, OwnerDomain, OwnerManifest, OwnerOperation, ROOT_FIELDS, SignedEvidence, canonical_digest
from ._owner_recovery import _RootCustodyContext
from ._root_operation import ProposedRootReplacement
from ._owner_sources import OriginalIssuerAdmission
from ._signed_commands import RejectedCommand, SavedCommand
from ._trust import _DEVICE_ROOT_DOMAIN, public_device

if TYPE_CHECKING:
    from ._key_operation_proof import OperationProofContext
    from ._owner_current import VerifiedCurrentDevice
    from ._root_read_set import RootReadSet
    from ._session import DeviceSession


@dataclass(frozen=True)
class ProposedOwnerKey:
    command: SignedEvidence
    secret: str = field(repr=False)
    head: dict[str, Any]

    def document(self) -> dict[str, Any]:
        return {"command": self.command.document(), "secret": self.secret, "head": self.head}


class RootReplacementPlan:
    def __init__(self, session: DeviceSession, snapshot: RootReadSet, proof: OperationProofContext,
                 proposed: ProposedRootReplacement, *, previous_admission: OriginalIssuerAdmission):
        self.session, self.owner, self.crypto = session, session.owner_access, session.crypto
        self.snapshot, self.reads, self.proposed = snapshot, proof, proposed
        self.previous_admission = previous_admission
        self.root_is_current = all(snapshot.recovery.get(name) == proposed.root.document()[name] for name in ROOT_FIELDS)
        self.keys: dict[str, ProposedOwnerKey] = {}
        self.candidates: dict[str, dict[str, Any]] = {}
        self.rotations: dict[str, dict[str, Any]] = {}
        self.qualified: dict[str, VerifiedCurrentDevice] = {}
        self.request: dict[str, Any] = {
            "preparation_digest": snapshot.preparation_digest, "read_set_digest": snapshot.read_set_digest,
            "owner_key_commands": [], "owner_candidate_commands": [], "scope_commands": [],
            "source_submissions": [], "keyring_commands": [], "gate_commands": [], "preparation_commands": [],
        }

    def _identity(self) -> dict[str, Any]:
        return {"device": self.session.public,
                "recovery_root": {name: self.proposed.root.document()[name] for name in ROOT_FIELDS},
                "issuer_admission": self.proposed.admission.document()}

    def _seal_backup(self, body: dict[str, Any], operation: OwnerOperation, secret: str,
                     sources: dict[str, Any]) -> dict[str, str]:
        return self.owner.recovery._seal(_RootCustodyContext(body, operation), {
            "v": 1, "organization_id": body["organization_id"], "key_id": body["key_id"],
            "public_key": body["public_key"], "secret_key": secret, "source_evidence": sources,
        }, self.proposed.root.encryption_key)

    def _owner_bindings(self) -> None:
        for organization, captured in self.snapshot.owners.items():
            if captured.get("authority") is None:
                continue
            head = self.owner.authority(organization, active=False)
            eligible = any(value["outcome"] == "available" and value["can_receive_organization_keys"]
                           and value["target"]["account_subject"] == self.session.subject
                           and value["target"]["organization_id"] == organization
                           and value["target"]["scope_id"] in {"", organization}
                           for value in self.reads.targets)
            if not eligible:
                continue
            if self.root_is_current:
                sources = self.owner.recovery.source_evidence(
                    organization, historical_admission=self.previous_admission).document()
            else:
                qualified = self.owner._qualify_local(organization, head)
                self.qualified[organization] = qualified
                sources = self.owner.recovery.source_evidence(organization, qualified=qualified).document()
            sources["issuer_admission"] = self.proposed.admission.document()
            anchor = self.owner.verifier.anchor(organization, self.snapshot.read("e2eeGetOwnerAuthority", organization_id=organization))
            pair = self.crypto.keypair()
            try:
                candidate = {"organization_id": organization, "candidate_id": secrets.token_urlsafe(24),
                             "account_subject": self.session.subject, "key_id": secrets.token_urlsafe(24),
                             "public_key": pair["encryption_public_key"], **self.proposed.custody_fields(),
                             **self._identity(), "source_anchor": anchor.command.document()}
                candidate["custody_backup"] = self._seal_backup(candidate, OwnerOperation.OFFER,
                    pair["encryption_secret_key"], sources)
                signed = SignedEvidence.parse(self.session.sign(OwnerOperation.OFFER, candidate))
                self.candidates[organization] = {"command": signed.document(), "secret": pair["encryption_secret_key"]}
                self.request["owner_candidate_commands"].append(signed.document())
            finally:
                pair.clear()
            if (head.owner_subject != self.session.subject or not self.reads.scope_authorized(
                    self.session.subject, organization, organization, "product_entitlement", "interactive_mutation")):
                continue
            if head.key_epoch >= 2**63 - 1:
                raise E2eeError("owner_key_changed")
            pair = self.crypto.keypair()
            try:
                body = {"organization_id": organization, "request_id": secrets.token_urlsafe(24),
                        "expected_ownership_revision": head.ownership_revision, "expected_key_epoch": head.key_epoch,
                        "key_id": secrets.token_urlsafe(24), "public_key": pair["encryption_public_key"],
                        "recovery_id": self.proposed.root.identifier, "recovery_generation": self.proposed.root.generation,
                        "custody_revision": self.proposed.custody_revision, **self._identity(),
                        "source_anchor": anchor.command.document()}
                body["custody_backup"] = self._seal_backup(body, OwnerOperation.REGISTER_KEY,
                    pair["encryption_secret_key"], sources)
                signed = SignedEvidence.parse(self.session.sign(OwnerOperation.REGISTER_KEY, body))
                proposed_head = {**head.to_dict(), "key_id": body["key_id"], "public_key": body["public_key"],
                                 "key_epoch": head.key_epoch + 1, "binding_digest": signed.digest(self.crypto, OwnerOperation.REGISTER_KEY),
                                 "state": "active"}
                self.keys[organization] = ProposedOwnerKey(signed, pair["encryption_secret_key"], proposed_head)
                self.request["owner_key_commands"].append(signed.document())
            finally:
                pair.clear()

    def _wrap(self, scope: str, epoch: int, key: bytearray, recipient: str, kind: str, public_key: str,
              head: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
        fields = {"scope_id": scope, "key_epoch": epoch, "sender_device_id": self.session.device_id,
                  "recipient_id": recipient, "recipient_kind": kind, **extra}
        maintained = self.keys.get(head["organization_id"]) if head is not None else None
        if maintained is not None:
            context = {"v": 1, "domain": "arteligo.owner-scope-key", **fields,
                       "sender_owner": {"organization_id": head["organization_id"], "key_id": head["key_id"],
                                        "key_epoch": head["key_epoch"], "binding_digest": head["binding_digest"]}}
            secret = maintained.secret
        else:
            context = {"v": 1, "domain": "arteligo.scope-key", **fields}
            secret = self.session._device["encryption_secret_key"]
        aad = self.crypto.canonical(context)
        try:
            result = self.crypto.execute({"op": "hpke_auth_seal", "sender_secret_key": secret,
                "recipient_public_key": public_key, "plaintext": encode(key), "info": encode(aad), "aad": encode(aad)})
            return {**fields, "encapsulated_key": result["enc"], "ciphertext": result["ciphertext"]}
        finally:
            wipe(aad)

    def _head(self, organization: str | None) -> dict[str, Any] | None:
        if organization is None:
            return None
        proposed = self.keys.get(organization)
        return proposed.head if proposed is not None else self.reads.authority(organization).head.to_dict()


    def _proposed_self_devices(self, scope: str, devices: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = []
        associations = {}
        for value in self.snapshot.recovery["device_roots"]:
            device = public_device(value["public_device"])
            if device["device_id"] in associations:
                raise E2eeError("invalid_recovery_replacement")
            associations[device["device_id"]] = value
        for device in devices:
            material = self.session._device_material(None, device["device_id"])
            self.owner.current._require_nonnegative(material, scope)
            if material.get("state") != "approved" or public_device(material) != public_device(device):
                raise E2eeError("owner_device_requalification_required")
            association = associations.get(device["device_id"])
            if association is None:
                self.owner.current.proposed_local_admission(
                    material, self.proposed.root, self.proposed.admission.root_evidence_digest)
                result.append(public_device(material))
                continue
            if association["public_device"] != public_device(device):
                raise E2eeError("owner_device_requalification_required")
            message = bytearray(_DEVICE_ROOT_DOMAIN)
            message.extend(self.crypto.canonical(association["public_device"]))
            try:
                self.crypto.execute({"op": "verify_bytes", "public_key": self.proposed.root.signing_key,
                                     "bytes": encode(message), "signature": association["root_signature"]})
            finally:
                wipe(message)
            result.append(public_device(material))
        return result

    def _rotation(self, scope: str, captured: Mapping[str, Any]) -> None:
        self.reads.require_scope(self.session.subject, captured, "interactive_mutation")
        metadata = captured["scope"]
        epoch = metadata["key_epoch"]
        if epoch >= 2**63 - 1:
            raise E2eeError("revision_conflict")
        organization = metadata.get("owner_org")
        head = self._head(organization)
        previous_head = self.reads.authority(organization).head if organization else None
        audience = captured["recipients"]
        current_audience = audience
        own_devices = []
        if self.root_is_current:
            own_devices = [value for value in audience["devices"] if value["account_subject"] == self.session.subject]
            current_audience = {**audience,
                "devices": [value for value in audience["devices"] if value["account_subject"] != self.session.subject],
                "recoveries": [value for value in audience["recoveries"] if value["account_subject"] != self.session.subject]}
        recipients = self.session.trust.current_recipients(scope, current_audience,
            self.session._current_device_lookup(scope, current_audience["devices"]),
            lambda identifier: self.session._recovery_material(scope, identifier))
        if previous_head is not None and scope == organization:
            self.owner.organizations.qualify_recipients(organization, recipients, previous_head)
            if own_devices and not self.reads.custody(organization, self.session.subject).can_receive_organization_keys:
                raise E2eeError("organization_key_recipient_ineligible")
        planned_devices = [*recipients.devices, *self._proposed_self_devices(scope, own_devices)] if self.root_is_current else recipients.devices
        planned_roots = [self.proposed.root if item.identity.subject == self.session.subject else item.identity
                         for item in recipients.roots]
        if self.root_is_current and (own_devices or any(value["account_subject"] == self.session.subject for value in audience["recoveries"])):
            planned_roots.append(self.proposed.root)
        key, previous = self.crypto.key(), bytearray()
        try:
            body: dict[str, Any] = {"scope_id": scope, "expected_epoch": epoch}
            if scope != organization:
                previous = self.session.scope_key(scope, epoch)
                aad = self.crypto.canonical({"v": 1, "domain": "arteligo.previous-project-key",
                                            "scope_id": scope, "key_epoch": epoch + 1, "previous_epoch": epoch})
                try:
                    body["previous_key_ciphertext"] = encode(json.dumps(self.crypto.seal(key, previous, aad), separators=(",", ":")).encode())
                finally:
                    wipe(aad)
            envelopes = []
            for device in planned_devices:
                if head is not None and device["account_subject"] == head["owner_subject"]:
                    continue
                envelopes.append(self._wrap(scope, epoch + 1, key, device["device_id"], "device", device["encryption_public_key"], head))
            for root in planned_roots:
                if head is not None and root.subject == head["owner_subject"]:
                    continue
                envelopes.append(self._wrap(scope, epoch + 1, key, root.identifier, "recovery", root.encryption_key, head))
            inherited = audience.get("organization_id")
            if inherited is not None:
                rotation = self.rotations.get(inherited)
                if rotation is not None:
                    inherited_key = decode(rotation["key"])
                    inherited_epoch = rotation["epoch"]
                else:
                    inherited_epoch = audience["organization_epoch"]
                    inherited_key = self.session.scope_key(inherited, inherited_epoch)
                try:
                    public = self.crypto.execute({"op": "public_keys", "encryption_secret_key": encode(inherited_key),
                                                  "signing_secret_key": encode(bytes(32))})["encryption_public_key"]
                    envelopes.append(self._wrap(scope, epoch + 1, key, inherited, "organization", public, head,
                                                organization_epoch=inherited_epoch))
                finally:
                    wipe(inherited_key)
            if head is not None:
                body["owner_authority"] = head
                envelopes.append(self._wrap(scope, epoch + 1, key, head["key_id"], "owner", head["public_key"], head,
                                            owner_key_epoch=head["key_epoch"], owner_binding_digest=head["binding_digest"]))
            operation = "owner_rotate_scope" if organization in self.keys else "rotate_scope"
            if operation == "owner_rotate_scope":
                body["owner_key_proof"] = OWNER_KEY_PROOF
            body["envelopes"] = envelopes
            signed = self.session.sign(operation, body)
            self.request["scope_commands"].append({"operation": operation, "signed_command": signed})
            self.rotations[scope] = {"operation": operation, "command": signed, "key": encode(key), "epoch": epoch + 1}
        finally:
            wipe(key)
            wipe(previous)

    def _coverage(self, organization: str, selected_scopes: set[str] | None = None) -> None:
        proposed = self.keys[organization]
        inventory = self.snapshot.owners[organization]["inventory"]
        scopes = [(organization, inventory["organization"]["epochs"])]
        scopes.extend((project["project_id"], project["epochs"]) for project in inventory["projects"])
        for scope, epochs in scopes:
            if selected_scopes is not None and scope not in selected_scopes:
                continue
            self.reads.require_scope(self.session.subject, self.snapshot.scope(scope), "interactive_mutation")
            for epoch in epochs:
                key = self.session.scope_key(scope, epoch)
                try:
                    head = proposed.head
                    envelope = self._wrap(scope, epoch, key, head["key_id"], "owner", head["public_key"], head,
                                          owner_key_epoch=head["key_epoch"], owner_binding_digest=head["binding_digest"])
                    command = self.session.sign(OwnerOperation.ENVELOPES, {"scope_id": scope, "key_epoch": epoch,
                        "owner_authority": head, "owner_key_proof": OWNER_KEY_PROOF, "envelopes": [envelope]})
                    self.request["scope_commands"].append({"operation": OwnerOperation.ENVELOPES.value, "signed_command": command})
                finally:
                    wipe(key)

    def _history(self, organization: str, manifest: OwnerManifest) -> dict[str, Any]:
        history = (self.owner.recovery.history(organization, historical_admission=self.previous_admission)
                   if self.root_is_current else self.owner.recovery.history(organization, qualified=self.qualified[organization]))
        proposed = self.keys[organization]
        history["keys"].append({"key_id": proposed.head["key_id"], "key_epoch": proposed.head["key_epoch"],
                                "public_key": proposed.head["public_key"], "binding_digest": proposed.head["binding_digest"],
                                "secret_key": proposed.secret, "binding_command": proposed.command.document()})
        history["issuer_admission"] = self.proposed.admission.document()
        history["manifests"].append({"signed_command": manifest.command.document(), "manifest_digest": manifest.digest,
                                     "documents": [item.document() for item in manifest.require_documents()],
                                     "origin": "unqualified_history"})
        return history

    def _manifests_and_gates(self) -> None:
        for organization, proposed in self.keys.items():
            old = self.reads.authority(organization).head
            proof = self.snapshot.read("e2eeGetOwnerAuthority", organization_id=organization)
            source = self.owner.verifier.binding(organization, proof, old) if old.key_id else None
            documents = ({item.document.project_key: item.document for item in self.owner.verifier.project_origins(organization, source).values()}
                         if source is not None else {})
            for project in self.snapshot.owners[organization]["inventory"]["projects"]:
                document = self.owner._project_evidence(organization, project, self.proposed.admission,
                    previous_admission=self.previous_admission if self.root_is_current else self.qualified[organization].original_admission)
                previous = documents.get(document.project_key)
                if previous is not None and previous.document_bytes != document.document_bytes:
                    raise E2eeError("owner_project_source_mismatch")
                documents[document.project_key] = document
            ordered = tuple(documents[key] for key in sorted(documents, key=lambda value: bytes(decode(value))))
            command = self.session.sign(OwnerOperation.MANIFEST, {"format": "project_index_v1", "organization_id": organization,
                "manifest_id": secrets.token_urlsafe(24), "owner_authority": proposed.head,
                "issuer_admission": self.proposed.admission.document(), "entries": [item.entry() for item in ordered]})
            manifest = OwnerManifest.parse(self.crypto, command, [item.document() for item in ordered])
            self.request["source_submissions"].append(manifest.submission())
            history = self._history(organization, manifest)
            aad = self.crypto.canonical({"v": 1, "domain": OwnerDomain.KEYRING, "organization_id": organization,
                                         "owner_authority": proposed.head})
            raw, secret = self.crypto.canonical(history), decode(proposed.secret)
            try:
                encrypted = self.crypto.canonical(self.crypto.seal(secret, raw, aad))
                try:
                    self.request["keyring_commands"].append(self.session.sign(OwnerOperation.KEYRING, {
                        "organization_id": organization, "owner_authority": proposed.head, "ciphertext": encode(encrypted)}))
                finally:
                    wipe(encrypted)
            finally:
                wipe(raw)
                wipe(aad)
                wipe(secret)
            self._gates(organization, manifest, history["keys"])

    def _gates(self, organization: str, manifest: OwnerManifest, keys: list[dict[str, Any]]) -> None:
        head = self.keys[organization].head
        keyring = [{name: key[name] for name in ("key_id", "key_epoch", "public_key", "binding_digest")} for key in keys]
        candidates = list(self.snapshot.owners[organization]["candidates"])
        own = self.candidates.get(organization)
        if own is not None:
            signed = SignedEvidence.parse(own["command"])
            candidates.append({"state": "qualified", "offer": signed.document(),
                               "offer_digest": signed.digest(self.crypto, OwnerOperation.OFFER)})
        for entry in candidates:
            if entry.get("state") != "qualified":
                continue
            proposed = own is not None and entry.get("offer") == own["command"]
            candidate = OwnerBinding.parse(entry.get("offer"))
            body = candidate.body
            if not proposed and body.account_subject == self.session.subject:
                continue
            offer = self.reads.gate_offer(organization, body.account_subject, body.candidate_id, proposed)
            if offer is None:
                continue
            if (offer["operation_id"] != self.snapshot.operation_id
                    or offer["slot"]["ownership_revision"] != head["ownership_revision"]
                    or offer["slot"]["source_key_epoch"] != head["key_epoch"]
                    or offer["slot"]["expected_root"] != {"kind": "recovery_root", "account_subject": self.session.subject,
                        **{name: self.snapshot.recovery[name] for name in ROOT_FIELDS}}):
                raise E2eeError("invalid_key_operation_proof")
            if not proposed:
                candidate = self.owner.verifier.candidate(organization, entry)
            gate_request = {"organization_id": organization, "preparation_id": secrets.token_urlsafe(24),
                "candidate_id": body.candidate_id, "ownership_revision": head["ownership_revision"],
                "source_key_epoch": head["key_epoch"], "source_binding_digest": head["binding_digest"],
                "offer_digest": entry["offer_digest"], "source_manifest_id": manifest.body.manifest_id,
                "source_manifest_digest": manifest.digest, "history_manifest_digest": canonical_digest(self.crypto, keyring),
                "issuer_admission": self.proposed.admission.document()}
            descriptor = {name: value for name, value in gate_request.items() if name != "issuer_admission"}
            descriptor.update(gate_id=offer["gate_id"], public_key=offer["public_key"])
            prepared = {"organization_id": organization, "preparation_id": gate_request["preparation_id"],
                "owner_authority": head, "candidate_id": body.candidate_id, "offer_digest": entry["offer_digest"],
                "source_manifest_id": manifest.body.manifest_id, "source_manifest_digest": manifest.digest,
                "keyring_manifest": keyring, "gate_descriptor": descriptor,
                "issuer_admission": self.proposed.admission.document()}
            raw = self.crypto.canonical({"v": 1, "organization_id": organization, "keys": keys})
            inner = bytearray()
            try:
                sender = self.session._device["encryption_secret_key"]
                sealed = self.owner.capsules.seal(sender, body.public_key, raw, prepared, OwnerDomain.INNER)
                inner = self.crypto.canonical(sealed)
                capsule = self.owner.capsules.seal(sender, offer["public_key"], inner, prepared, OwnerDomain.OUTER)
            finally:
                wipe(raw)
                wipe(inner)
            self.request["gate_commands"].append(self.session.sign(OwnerOperation.GATE, gate_request))
            self.request["preparation_commands"].append(self.session.sign(OwnerOperation.PREPARE, {
                **prepared, "capsule": capsule, "capsule_digest": canonical_digest(self.crypto, capsule)}))

    def _pending_device_history(self) -> None:
        for scope, value in self.session._device.get("root_device_history", {}).items():
            captured = self.snapshot.scopes.get(scope)
            if captured is None or not self.reads.scope_authorized(
                    self.session.subject, captured["scope"]["owner_org"], scope,
                    captured["authorization_basis"], "interactive_read"):
                continue
            organization = captured["scope"].get("owner_org")
            if organization and self.reads.authority(organization).head.owner_subject == self.session.subject:
                continue
            saved = SavedCommand.parse(value, "envelopes_save")
            if isinstance(saved.outcome, RejectedCommand):
                continue
            epoch = saved.command.body.get("key_epoch")
            if saved.command.body.get("scope_id") != scope or type(epoch) is not int or epoch < 1:
                raise E2eeError("invalid_key_admission")
            if epoch != captured["scope"]["key_epoch"] and not any(
                    value.get("key_epoch") == epoch for name in ("envelopes", "epoch_links", "generations")
                    for value in captured[name]):
                continue
            self.request["scope_commands"].append({
                "operation": "envelopes_save", "signed_command": saved.command.document()})

    def build(self, root_command: SignedEvidence, admission: SignedEvidence) -> tuple[dict[str, Any], dict[str, Any]]:
        self.request.update(root_command=root_command.document(), companion_admission=admission.document())
        self._owner_bindings()
        self._pending_device_history()
        for scope, captured in sorted(self.snapshot.scopes.items(), key=lambda item: item[0] != item[1]["scope"].get("owner_org")):
            metadata = captured["scope"]
            organization = metadata.get("owner_org")
            if (organization is not None and self.reads.authority(organization).head.owner_subject == self.session.subject
                    and organization not in self.keys):
                continue
            if not self.reads.scope_authorized(self.session.subject, organization, scope,
                                                 captured["authorization_basis"], "interactive_mutation"):
                continue
            if (metadata["key_epoch"] > 0 and metadata.get("role") in {"owner", "editor", "admin"}
                    and metadata.get("lifecycle") in {"active", "archived"}):
                self._rotation(scope, captured)
        for organization in self.keys:
            self._coverage(organization)
        self._manifests_and_gates()
        return self.request, {"keys": {key: value.document() for key, value in self.keys.items()},
                              "candidates": self.candidates, "rotations": self.rotations}

