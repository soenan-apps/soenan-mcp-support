from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Iterator, Mapping, Protocol

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_protocol import (
    E2EeOwnerCommittedExportReference, OwnerBinding, OwnerOperation, ROOT_FIELDS, SignedEvidence, authority_head,
    canonical_digest, committed_decision, committed_export_references, custody, object_value,
)
from ._owner_state import CandidateSecret, ManifestOrigin, ManifestSelection, OwnerKey, RootProvenance, SavedManifest, SourceAnchor
from ._owner_sources import OwnerSourceEvidence, OwnerSourceManifestReference, OwnerStoredManifestReference, OwnerIssuerEvidence, OriginalIssuerAdmission
from ._signed_commands import SavedCommand, UncertainCommand
from ._owner_root_history import OwnerRootHistory, ScopeGenerationReference
from ._trust import _RootIdentity

if TYPE_CHECKING:
    from ._owner_access import OwnerAccess
    from ._owner_current import VerifiedCurrentDevice


class OwnerCustodyContext(Protocol):
    def document(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class _RootCustodyContext:
    body: Mapping[str, Any]
    operation: OwnerOperation

    def document(self) -> dict[str, Any]:
        return {"v": 1, "domain": "arteligo.owner-custody-backup",
                "operation": self.operation, "binding": dict(self.body)}


@dataclass(frozen=True)
class _DeviceCustodyContext:
    body: Mapping[str, Any]
    sender_device_id: str

    def document(self) -> dict[str, Any]:
        return {"v": 1, "domain": "arteligo.owner-device-custody",
                "sender_device_id": self.sender_device_id, "binding": dict(self.body)}


class OwnerRecovery:
    def __init__(self, owner: OwnerAccess):
        self.owner, self.session = owner, owner.session
        self.crypto = owner.crypto
        self.root_history = OwnerRootHistory(self)

    def _seal(self, context: OwnerCustodyContext, plaintext: dict[str, Any],
              recipient: str) -> dict[str, str]:
        raw, aad = self.crypto.canonical(plaintext), self.crypto.canonical(context.document())
        try:
            sealed = self.crypto.execute({
                "op": "hpke_auth_seal", "sender_secret_key": self.session._device["encryption_secret_key"],
                "recipient_public_key": recipient, "plaintext": encode(raw), "info": encode(aad), "aad": encode(aad),
            })
            return {"encapsulated_key": sealed["enc"], "ciphertext": sealed["ciphertext"]}
        finally:
            wipe(raw)
            wipe(aad)

    def open_custody(self, context: OwnerCustodyContext, envelope: Any,
              recipient_secret: str, sender_public: str) -> dict[str, Any]:
        envelope = object_value(envelope)
        if set(envelope) != {"encapsulated_key", "ciphertext"}:
            raise E2eeError("invalid_owner_custody_backup")
        aad, plaintext = self.crypto.canonical(context.document()), bytearray()
        try:
            plaintext = decode(self.crypto.execute({
                "op": "hpke_auth_open", "recipient_secret_key": recipient_secret,
                "sender_public_key": sender_public, "info": encode(aad), "aad": encode(aad),
                "envelope": {"v": 1, "suite": "HPKE-Auth-X25519-HKDF-SHA256-AES256GCM",
                             "enc": envelope["encapsulated_key"], "ciphertext": envelope["ciphertext"]},
            })["plaintext"])
            return object_value(json.loads(plaintext))
        except (ValueError, TypeError, KeyError):
            raise E2eeError("invalid_owner_custody_backup") from None
        finally:
            wipe(aad)
            wipe(plaintext)

    def remember_confirmation(self, scope: str, value: Mapping[str, Any]) -> None:
        command = SignedEvidence.parse(dict(value))
        command.verify(self.crypto, self.session.public["signing_public_key"], "peer_trust")
        organization = self.session.scope_metadata(scope).get("owner_org")
        if not organization:
            return
        anchor = SourceAnchor.parse({"command": command.document(),
            "device": command.body.get("trusted_device"), "root": command.body.get("recovery_root")},
            origin=self.session.trust.origin)
        state = self.owner.store.get(organization)
        if anchor not in state.confirmed_sources:
            state.confirmed_sources.append(anchor)
            self.owner.store.save(organization)

    def capture_confirmations(self, organization: str) -> None:
        scopes = {value["project_id"]: value.get("owner_org") for value in self.session.scopes()}
        head = self.owner.reads.authority(organization, self.owner.reads.capability(organization))
        qualified: set[str] = set()
        for value in self.session.trust._endorsements:
            statement = SignedEvidence.parse(value)
            selected_scope = statement.body.get("scope_id")
            if selected_scope != organization and scopes.get(selected_scope) != organization:
                continue
            issuer = self.session._device_material(None, statement.device_id)
            if issuer["account_subject"] != self.session.subject:
                continue
            if statement.device_id not in qualified:
                try:
                    anchor = self.owner.current.independent_root(organization, issuer)
                    self.owner.current.qualify(organization, issuer, anchor, head)
                except E2eeError as error:
                    if error.code in {"device_revoked", "owner_device_requalification_required", "owner_root_requalification_required", "owner_custody_evidence_missing"}:
                        continue
                    raise
                qualified.add(statement.device_id)
            statement.verify(self.crypto, issuer["signing_public_key"], "peer_trust")
            anchor = SourceAnchor.parse({"command": statement.document(), "device": statement.body.get("trusted_device"),
                                        "root": statement.body.get("recovery_root")}, origin=self.session.trust.origin)
            state = self.owner.store.get(organization)
            if anchor not in state.confirmed_sources:
                state.confirmed_sources.append(anchor)
                self.owner.store.save(organization)

    def source_evidence(self, organization: str, *, qualified: VerifiedCurrentDevice | None = None,
                        historical_admission: OriginalIssuerAdmission | None = None) -> OwnerSourceEvidence:
        from ._owner_protocol import OwnerPreparation

        self.capture_confirmations(organization)
        state = self.owner.store.get(organization)
        head = self.owner.reads.authority(organization, self.owner.reads.capability(organization))
        if self.session.recovery is None:
            raise E2eeError("recovery_missing")
        root = self.owner.verifier.root(self.session.recovery, self.session.subject)
        if historical_admission is None:
            anchor = self.owner.current.independent_root(organization, self.session.public)
            if qualified is None:
                qualified = self.owner.current.qualify(organization, self.session.public, anchor, head, expected_root=root)
            if qualified.root != root or qualified.device != self.session.public:
                raise E2eeError("owner_custody_changed")
            admission = qualified.original_admission
        else:
            admission = historical_admission
            if admission.root.subject != self.session.subject or admission.root.origin != self.session.trust.origin:
                raise E2eeError("owner_custody_changed")
        references = []
        covered: set[str] = set()
        for saved in state.manifests.values():
            if saved.selection is None:
                continue
            preparation = OwnerPreparation.parse(saved.selection.preparation.document())
            references.append(OwnerSourceManifestReference(saved.manifest.body.manifest_id, saved.manifest.digest,
                saved.selection.decision.operation_id, preparation.body.preparation_id))
            covered.update(SignedEvidence.parse(command.to_dict()).digest(self.crypto, "peer_trust")
                for document in saved.manifest.require_documents() for command in document.project.owner_confirmations)
        roots = {root.identifier: root for root in self.owner.store.self_roots()}
        for item in self.session.trust._state["recovery"].values():
            if item["account_subject"] == self.session.subject:
                root = self.owner.verifier.root(item, self.session.subject)
                roots[root.identifier] = root
        current = self.session.trust._confirmed_head(self.session.subject)
        if current is not None:
            roots[current.identifier] = current
        value = {"self_roots": [root.document() for root in roots.values()],
                 "confirmed_sources": [anchor.document() for anchor in state.confirmed_sources
                    if anchor.command.body.get("scope_id") == organization
                    or anchor.command.digest(self.crypto, "peer_trust") not in covered],
                 "manifests": [reference.document() for reference in references], "receipts": list(state.receipts),
                 "key_bindings": [key.public_binding() for key in state.keys],
                 "issuer_admission": admission.document()}
        if state.source_anchor is not None:
            value["source_anchor"] = state.source_anchor.document()
        snapshot = self.root_history.digest()
        if snapshot is not None:
            value["root_snapshot_digest"] = snapshot
        return OwnerSourceEvidence.parse(self.crypto, value, organization, origin=self.session.trust.origin)

    def seal_root(self, body: dict[str, Any], operation: OwnerOperation, secret: str,
                  *, qualified: VerifiedCurrentDevice) -> dict[str, str]:
        if (body["custody_revision"] != qualified.custody.custody_revision
                or body["issuer_admission"] != qualified.original_admission.document()):
            raise E2eeError("owner_custody_changed")
        return self._seal(_RootCustodyContext(body, operation), {
            "v": 1, "organization_id": body["organization_id"], "key_id": body["key_id"],
            "public_key": body["public_key"], "secret_key": secret,
            "source_evidence": self.source_evidence(body["organization_id"], qualified=qualified).document(),
        }, body["recovery_root"]["encryption_public_key"])

    def history(self, organization: str, *, qualified: VerifiedCurrentDevice | None = None,
                historical_admission: OriginalIssuerAdmission | None = None) -> dict[str, Any]:
        state = self.owner.store.get(organization)
        sources = self.source_evidence(organization, qualified=qualified, historical_admission=historical_admission)
        manifests = []
        for saved in state.manifests.values():
            manifests.append(OwnerStoredManifestReference(
                saved.manifest,
                saved.selection.preparation if saved.selection is not None else None,
                saved.selection.decision if saved.selection is not None else None,
                saved.issuer_evidence, saved.origin).document())
        value = {"v": 1, "organization_id": organization, "keys": [key.document() for key in state.keys],
                 "confirmed_sources": [anchor.document() for anchor in state.confirmed_sources],
                 "self_roots": [root.document() for root in sources.self_roots],
                 "issuer_admission": sources.issuer_admission.document(),
                 "manifests": manifests, "receipts": [receipt.to_dict() for receipt in state.receipts.values()]}
        if sources.root_snapshot_digest is not None:
            value["root_snapshot_digest"] = sources.root_snapshot_digest
        if state.source_anchor is not None:
            value["source_anchor"] = state.source_anchor.document()
        return value

    def device_backup(self, approval: dict[str, Any], admission: OriginalIssuerAdmission,
                      references: list[ScopeGenerationReference], *, qualified: VerifiedCurrentDevice | None) -> dict[str, str]:
        organizations = []
        for organization in self.owner.store.organizations():
            state = self.owner.store.get(organization)
            if not state.keys and state.candidate is None and state.registration is None:
                continue
            value = self.history(organization, qualified=qualified)
            del value["v"]
            del value["issuer_admission"]
            if state.candidate is not None:
                value["candidate"] = {"secret_key": state.candidate.secret_key, "offer": state.candidate.binding.command.document()}
            value["retained_candidates"] = [{"secret_key": item.secret_key, "offer": item.binding.command.document()}
                                             for item in state.retired_candidates]
            if state.registration is not None:
                value["key_registration"] = {"command": state.registration.command.document(), "secret_key": state.registration.key}
            organizations.append(value)
        return self._seal(_DeviceCustodyContext(approval, self.session.device_id), {
            "v": 1, "account_subject": self.session.subject, "organizations": organizations,
            "self_roots": self.root_history.roots(), "issuer_admission": admission.document(),
            "scope_generations": [reference.document() for reference in references]}, approval["encryption_public_key"])

    def _anchor_from_binding(self, binding: OwnerBinding) -> SourceAnchor:
        statement = SignedEvidence.parse(binding.body.source_anchor.to_dict())
        return SourceAnchor.parse({"command": statement.document(), "device": statement.body.get("trusted_device"),
                                   "root": statement.body.get("recovery_root")}, origin=self.session.trust.origin)

    def _root_secret(self, binding: OwnerBinding, secret: str,
                     issuer_evidence: OwnerIssuerEvidence | None = None) -> tuple[str, OwnerSourceEvidence]:
        if self.session.recovery is None:
            raise E2eeError("recovery_missing")
        root = binding.body.recovery_root.to_dict()
        if root != {name: self.session.recovery[name] for name in ROOT_FIELDS}:
            raise E2eeError("owner_custody_changed")
        historical_roots = tuple(
            candidate for candidate in self.owner.store.self_roots()
            if candidate.subject == binding.body.device.account_subject
            and candidate.origin == self.session.trust.origin
        )
        self.owner.verifier.signer(binding.body.organization_id, binding.command, binding.body.device.to_dict(), root,
                                   issuer_evidence=issuer_evidence, historical_roots=historical_roots)
        binding.command.verify(self.crypto, binding.body.device.signing_public_key, binding.operation)
        body = dict(binding.command.body)
        backup = body.pop("custody_backup", None)
        if backup is None:
            raise E2eeError("owner_private_backup_missing")
        payload = self.open_custody(_RootCustodyContext(body, binding.operation), backup, secret,
                             binding.body.device.encryption_public_key)
        if (set(payload) != {"v", "organization_id", "key_id", "public_key", "secret_key", "source_evidence"}
                or payload["v"] != 1 or payload["organization_id"] != binding.body.organization_id
                or payload["key_id"] != binding.body.key_id or payload["public_key"] != binding.body.public_key
                or self.owner.capsules.public_key(payload["secret_key"]) != binding.body.public_key):
            raise E2eeError("invalid_owner_custody_backup")
        sources = OwnerSourceEvidence.parse(self.crypto, payload["source_evidence"], binding.body.organization_id,
            origin=self.session.trust.origin)
        if sources.issuer_admission != binding.original_admission:
            raise E2eeError("owner_custody_evidence_mismatch")
        self.owner.current.original_issuer(binding.body.organization_id, binding.body.device.to_dict(),
            self.owner.verifier.root(root, self.session.subject), sources.issuer_admission,
            maximum_revision=binding.body.custody_revision, known_roots=sources.self_roots, issuer_evidence=issuer_evidence)
        return payload["secret_key"], sources

    def _current_organizations(self) -> Iterator[dict[str, Any]]:
        organizations = {
            scope["project_id"] for scope in self.session.call("e2eeListOrganizations")["projects"]
            if scope["key_epoch"] > 0 and scope["key_state"] in {"ready", "rekey_required"}
            and scope["lifecycle"] in {"active", "archived"}
        }
        if not organizations:
            return
        response = self.session.call("e2eeReadRecords", body={
            "scopes": [{"scope_id": organization, "record_ids": []} for organization in sorted(organizations)],
            "include_keys": False,
        })
        scopes = response["scopes"]
        if len(scopes) != len(organizations) or {scope["scope_id"] for scope in scopes} != organizations:
            raise E2eeError("invalid_response")
        for scope in scopes:
            error = scope.get("error")
            if error in {"access_denied", "project_access_denied", "not_found"}:
                continue
            if error is not None:
                raise E2eeError(error)
            metadata = object_value(scope.get("metadata"))
            if metadata.get("project_id") != scope["scope_id"] or metadata.get("owner_org") != scope["scope_id"]:
                raise E2eeError("invalid_response")
            if (metadata["role"] in {"owner", "editor", "viewer"}
                    and metadata["key_epoch"] > 0 and metadata["key_state"] in {"ready", "rekey_required"}
                    and metadata["lifecycle"] in {"active", "archived"}):
                yield metadata

    def restore_root(self, recovery_secret: str) -> None:
        self.root_history.restore(recovery_secret)
        self._restore_retained_bindings(recovery_secret)
        for scope in self._current_organizations():
            organization = scope["project_id"]
            self.session.load_owner_context(organization=organization)
            proof = self.session.call("e2eeGetOwnerAuthority", organization_id=organization)
            suggested = authority_head(proof.get("owner_authority"), organization)
            head = self.owner.reads.authority(organization, suggested.read_capability)
            if head != suggested:
                raise E2eeError("owner_authority_changed")
            observed = self.owner.reads.custody(organization, self.session.subject, head.read_capability)
            current_custody = custody(self.session.call("e2eeGetOwnerCustody", organization_id=organization))
            if observed.custody_revision != current_custody.custody_revision:
                raise E2eeError("owner_custody_changed")
            state = self.owner.store.get(organization)
            entries = self.session.call("e2eeGetOwnerCandidates", organization_id=organization)["candidates"]
            if head.owner_subject == self.session.subject and head.key_id:
                binding = OwnerBinding.parse(proof.get("signed_binding"))
                existing = next((key for key in state.keys if key.binding_digest == head.binding_digest), None)
                if existing is None:
                    private, sources = self._root_secret(binding, recovery_secret, OwnerIssuerEvidence.parse(proof.get("issuer_evidence")))
                else:
                    private, sources = existing.secret_key, None
                selected = self.owner.reads.selected(organization, head.binding_digest)
                if (not selected.matches(head) or binding.command.digest(self.crypto, binding.operation) != head.binding_digest):
                    raise E2eeError("owner_binding_mismatch")
                if sources is not None:
                    self.restore_sources(organization, sources, binding)
                self.owner.verifier.binding(organization, proof, head)
                selected = self.owner.reads.selected(organization, head.binding_digest).head
                self.owner.keyring.merge(organization, [OwnerKey(head.key_id, head.key_epoch, head.public_key, head.binding_digest, private, binding)])
                if sources is not None:
                    self._restore_selected_history(organization, sources, recovery_secret)
                try:
                    self.owner.keyring.restore(organization)
                except E2eeError as error:
                    if error.code != "not_found":
                        raise
            for entry in entries:
                binding = OwnerBinding.parse(entry.get("offer"))
                if (binding.operation != OwnerOperation.OFFER or binding.body.account_subject != self.session.subject
                        or binding.body.custody_revision != current_custody.custody_revision
                        or binding.command.digest(self.crypto, OwnerOperation.OFFER) != entry.get("offer_digest")):
                    continue
                try:
                    self.owner.reads.selected(organization, entry["offer_digest"])
                except E2eeError as error:
                    if error.code != "owner_binding_not_selected":
                        raise
                else:
                    continue
                if entry.get("state") != "qualified":
                    continue
                self.owner.verifier.candidate(organization, entry)
                private, sources = self._root_secret(binding, recovery_secret)
                self.restore_sources(organization, sources, binding)
                restored = CandidateSecret(private, current_custody, binding)
                if state.candidate is None:
                    state.candidate = restored
                elif state.candidate.binding.command != restored.binding.command:
                    if not any(item.binding.command == restored.binding.command for item in state.retired_candidates):
                        state.retired_candidates.append(restored)
                self.owner.store.save(organization)

    def _restore_selected_history(self, organization: str, sources: OwnerSourceEvidence, root_secret: str) -> None:
        root = {name: self.session.recovery[name] for name in ROOT_FIELDS}
        for reference in sources.key_bindings:
            if any(key.binding_digest == reference.binding_digest for key in self.owner.store.get(organization).keys):
                continue
            selected = self.owner.reads.selected(organization, reference.binding_digest).head
            if reference.to_dict() != {name: selected.to_dict()[name] for name in reference.to_dict()}:
                raise E2eeError("owner_keyring_mismatch")
            proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=reference.binding_digest)
            binding = OwnerBinding.parse(proof.get("signed_binding"))
            if binding.body.device.account_subject != self.session.subject or binding.body.recovery_root.to_dict() != root:
                continue
            private, frozen = self._root_secret(binding, root_secret, OwnerIssuerEvidence.parse(proof.get("issuer_evidence")))
            self.restore_sources(organization, frozen, binding)
            self.owner.verifier.binding(organization, proof, selected)
            self.owner.keyring.merge(organization, [OwnerKey(selected.key_id, selected.key_epoch, selected.public_key,
                selected.binding_digest, private, binding)])

    def _retained_bindings(self):
        references = (self.session.recovery or {}).get("owner_access_history", [])
        seen = set()
        for value in references:
            value = object_value(value)
            if set(value) != {"organization_id", "binding_digest"}:
                raise E2eeError("owner_keyring_mismatch")
            organization, digest = value["organization_id"], value["binding_digest"]
            if not isinstance(organization, str) or not organization or (organization, digest) in seen:
                raise E2eeError("owner_keyring_mismatch")
            seen.add((organization, digest))
            selected, proof = self.root_history.selected(organization, digest)
            if selected.head.owner_subject != self.session.subject:
                raise E2eeError("owner_keyring_mismatch")
            yield organization, selected.head, proof

    def _restore_retained_bindings(self, root_secret: str) -> None:
        for organization, selected, proof in self._retained_bindings():
            state = self.owner.store.get(organization)
            if any(key.binding_digest == selected.binding_digest for key in state.keys):
                continue
            binding = OwnerBinding.parse(proof.get("signed_binding"))
            private, sources = self._root_secret(binding, root_secret, OwnerIssuerEvidence.parse(proof.get("issuer_evidence")))
            self.restore_sources(organization, sources, binding)
            self.owner.verifier.binding(organization, proof, selected, sources=sources)
            self.owner.keyring.merge(organization, [OwnerKey(selected.key_id, selected.key_epoch, selected.public_key,
                selected.binding_digest, private, binding)])
            self._restore_selected_history(organization, sources, root_secret)
        self.require_selected_history()

    def require_selected_history(self) -> None:
        for organization, selected, proof in self._retained_bindings():
            state = self.owner.store.get(organization)
            key = next((item for item in state.keys if item.binding_digest == selected.binding_digest), None)
            if key is None:
                for candidate in (*state.retired_candidates, *((state.candidate,) if state.candidate is not None else ())):
                    if candidate.binding.command.digest(self.crypto, OwnerOperation.OFFER) == selected.binding_digest:
                        key = OwnerKey(selected.key_id, selected.key_epoch, selected.public_key, selected.binding_digest,
                            candidate.secret_key, candidate.binding)
                        self.owner.keyring.merge(organization, [key])
                        break
            if key is None or key.public_binding() != {name: selected.to_dict()[name] for name in key.public_binding()}:
                raise E2eeError("owner_history_unavailable")
            source = self.owner.verifier.binding(organization, proof, selected)
            for reference in committed_export_references(proof.get("exported_sources")):
                saved = self.owner.verifier.exported_manifest(organization, proof, source, reference,
                    retained=state.manifests.get(reference.source_manifest_id))
                self._merge_manifests(organization, [saved])
                self.owner.store.save(organization)

    def restore_sources(self, organization: str, sources: OwnerSourceEvidence, binding: OwnerBinding) -> None:
        expected = self._anchor_from_binding(binding)
        if sources.anchor is None or sources.anchor.command != expected.command:
            raise E2eeError("invalid_owner_source_evidence")
        self.restore_frozen_sources(organization, sources, binding.body.recovery_root.to_dict())

    def restore_frozen_sources(self, organization: str, sources: OwnerSourceEvidence, root: Mapping[str, Any]) -> None:
        for historical in sources.self_roots:
            if historical.origin != self.session.trust.origin or historical.subject != self.session.subject:
                raise E2eeError("account_mismatch")
        if sources.root_snapshot_digest is not None:
            self.root_history.verify_reference(sources.issuer_admission.root, sources.root_snapshot_digest)
        trusted_self_roots = self.owner.store.self_roots()
        for anchor in (*((sources.anchor,) if sources.anchor is not None else ()), *sources.confirmations):
            issuer = self.session._historical_device_material(None, anchor.command.device_id)
            if issuer["account_subject"] != self.session.subject:
                raise E2eeError("account_mismatch")
            self.owner.verifier.signer(organization, anchor.command, issuer, root,
                                       historical_roots=trusted_self_roots)
            anchor.command.verify(self.crypto, issuer["signing_public_key"], "peer_trust")
            self.owner.verifier.root(anchor.root, anchor.device["account_subject"])
        references = [self._resolve_reference(organization, reference) for reference in sources.manifests
                      if reference.operation_id is not None]
        restored = self._manifests(organization, references, sources=sources)
        for key in sources.key_bindings:
            selected = self.owner.reads.selected(organization, key.binding_digest)
            if key.to_dict() != {name: selected.head.to_dict()[name] for name in key.to_dict()}:
                raise E2eeError("owner_keyring_mismatch")
        receipts = [self._receipt(organization, identifier) for identifier in sources.receipts]
        state = self.owner.store.get(organization)
        if sources.anchor is not None:
            if state.source_anchor is None:
                state.source_anchor = sources.anchor
            elif state.source_anchor != sources.anchor and sources.anchor not in state.confirmed_sources:
                state.confirmed_sources.append(sources.anchor)
        for anchor in sources.confirmations:
            if anchor not in state.confirmed_sources:
                state.confirmed_sources.append(anchor)
        self.owner.store.retain_roots(sources.self_roots)
        self._merge_manifests(organization, restored)
        for receipt in receipts:
            state.receipts[receipt.operation_id] = receipt
        self.owner.store.save(organization)

    def _receipt(self, organization: str, identifier: str):
        receipt = committed_decision(self.owner.reads.decision(organization, identifier), organization)
        if receipt.target_subject != self.session.subject:
            raise E2eeError("owner_receipt_mismatch")
        return receipt

    def _resolve_reference(self, organization: str, reference: OwnerSourceManifestReference) -> OwnerStoredManifestReference:
        from ._owner_protocol import OwnerManifest

        if reference.operation_id is None or reference.preparation_id is None:
            raise E2eeError("owner_receipt_missing")
        retained = self.owner.store.get(organization).manifests.get(reference.manifest_id)
        if retained is None:
            artifact = self.session.call("e2eeGetOwnerManifestDocuments", organization_id=organization, manifest_id=reference.manifest_id)
            manifest = OwnerManifest.parse(self.crypto, artifact.get("signed_command"), artifact.get("documents"))
            if artifact.get("manifest_digest") != reference.manifest_digest:
                raise E2eeError("owner_source_manifest_mismatch")
            evidence = OwnerIssuerEvidence.parse(artifact.get("issuer_evidence"))
        else:
            manifest, evidence = retained.manifest, retained.issuer_evidence
        if manifest.body.manifest_id != reference.manifest_id or manifest.digest != reference.manifest_digest:
            raise E2eeError("owner_source_manifest_mismatch")
        receipt = committed_decision(self.owner.reads.decision(organization, reference.operation_id), organization)
        if receipt.preparation_id != reference.preparation_id:
            raise E2eeError("owner_receipt_mismatch")
        if retained is not None and retained.selection is not None:
            if retained.selection.decision.to_dict() != receipt.to_dict():
                raise E2eeError("owner_receipt_mismatch")
            preparation = retained.selection.preparation
        else:
            artifact = self.session.call("e2eeGetOwnerPreparation", organization_id=organization, preparation_id=reference.preparation_id)
            preparation = SignedEvidence.parse(artifact.get("signed_command"))
        return OwnerStoredManifestReference(manifest, preparation, receipt, evidence, ManifestOrigin.FROZEN)

    def restore_paired_sources(self, organization: str, value: Mapping[str, Any], admission: OriginalIssuerAdmission,
                               authenticated_roots: frozenset[_RootIdentity]) -> None:
        if self.session.recovery is None:
            raise E2eeError("recovery_missing")
        references = [OwnerStoredManifestReference.parse(self.crypto, item, organization) for item in value.get("manifests", [])]
        provenance = RootProvenance.parse({"v": 1, "self_roots": value["self_roots"]},
            self.session.trust.origin, self.session.subject)
        trusted, provisional = provenance.partition(authenticated_roots)
        self._retain_provisional_roots(provisional)
        evidence = {"self_roots": [root.document() for root in trusted], "issuer_admission": admission.document(),
                    "confirmed_sources": value.get("confirmed_sources", []), "manifests": [], "receipts": [],
                    "key_bindings": [{name: key[name] for name in ("key_id", "key_epoch", "public_key", "binding_digest")}
                                     for key in value.get("keys", [])]}
        if value.get("source_anchor") is not None:
            evidence["source_anchor"] = value["source_anchor"]
        if "root_snapshot_digest" in value:
            evidence["root_snapshot_digest"] = value["root_snapshot_digest"]
        sources = OwnerSourceEvidence.parse(self.crypto, evidence, organization, origin=self.session.trust.origin)
        restored = self._manifests(organization, references, sources=sources)
        self.restore_frozen_sources(organization, sources, self.session.recovery)
        self._merge_manifests(organization, restored)
        for item in value.get("receipts", []):
            receipt = self._receipt(organization, item["operation_id"])
            if receipt.to_dict() != item:
                raise E2eeError("owner_receipt_mismatch")
            self.owner.store.get(organization).receipts[receipt.operation_id] = receipt
        self.owner.store.save(organization)

    def _manifests(self, organization: str, references: list[OwnerStoredManifestReference], *, sources: OwnerSourceEvidence | None = None) -> list[SavedManifest]:
        restored = []
        for reference in references:
            manifest = reference.manifest
            if reference.preparation is None or reference.decision is None:
                origin = ManifestOrigin.DATA
                evidence = reference.issuer_evidence
                if sources is not None and reference.origin != ManifestOrigin.DATA:
                    head = authority_head(manifest.body.owner_authority.to_dict(), organization)
                    if head.owner_subject != self.session.subject:
                        raise E2eeError("owner_receipt_missing")
                    proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)
                    source = self.owner.verifier.binding(organization, proof, head, sources=sources)
                    evidence = self.owner.verifier.manifest(organization, manifest, source, evidence)
                    origin = ManifestOrigin.FROZEN
                restored.append(SavedManifest(manifest, origin=origin, issuer_evidence=evidence))
                continue
            decision = committed_decision(reference.decision, organization)
            head = authority_head(manifest.body.owner_authority.to_dict(), organization)
            proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)
            saved = SavedManifest(manifest, ManifestSelection(proof, reference.preparation, decision),
                issuer_evidence=reference.issuer_evidence)
            if decision.actor_subject == self.session.subject and head.owner_subject == self.session.subject:
                source = self.owner.verifier.binding(organization, proof, head, sources=sources)
                exported = E2EeOwnerCommittedExportReference(decision.operation_id, decision.head.binding_digest,
                    manifest.body.manifest_id, manifest.digest)
                saved = self.owner.verifier.exported_manifest(organization, proof, source, exported, retained=saved)
            else:
                receipt = self._receipt(organization, decision.operation_id)
                if receipt.to_dict() != decision.to_dict():
                    raise E2eeError("owner_receipt_mismatch")
                saved = self.owner.verifier.selected_manifest(organization, saved, sources=sources)
            restored.append(saved)
        return restored

    def _merge_manifests(self, organization: str, manifests: list[SavedManifest]) -> None:
        state = self.owner.store.get(organization)
        confirmations = []
        for saved in manifests:
            existing = state.manifests.get(saved.manifest.body.manifest_id)
            if existing is not None and existing.manifest.command != saved.manifest.command:
                raise E2eeError("owner_source_manifest_mismatch")
            if saved.selection is not None or saved.origin == ManifestOrigin.FROZEN:
                if saved.issuer_evidence is None:
                    raise E2eeError("owner_device_proof_missing")
                confirmations.extend(self.owner.verifier.own_confirmations(
                    organization, saved.manifest, saved.issuer_evidence))
        for saved in manifests:
            existing = state.manifests.get(saved.manifest.body.manifest_id)
            if existing is None or saved.selection is not None or (existing.origin == ManifestOrigin.DATA and saved.origin != ManifestOrigin.DATA):
                state.manifests[saved.manifest.body.manifest_id] = (
                    replace(saved, issuer_evidence=existing.issuer_evidence)
                    if existing is not None and existing.issuer_evidence is not None else saved)
            elif existing.issuer_evidence is None and saved.issuer_evidence is not None:
                state.manifests[saved.manifest.body.manifest_id] = replace(existing, issuer_evidence=saved.issuer_evidence)
        for anchor in confirmations:
            if anchor not in state.confirmed_sources:
                state.confirmed_sources.append(anchor)

    def import_history(self, organization: str, payload: dict[str, Any]) -> None:
        if payload.get("v") != 1 or payload.get("organization_id") != organization:
            raise E2eeError("owner_keyring_mismatch")
        references = [OwnerStoredManifestReference.parse(self.crypto, value, organization)
                      for value in payload.get("manifests", [])]
        restored = self._manifests(organization, references)
        keys = [OwnerKey.parse(value, organization, self.owner.capsules) for value in payload.get("keys", [])]
        for key in keys:
            selected = self.owner.reads.selected(organization, key.binding_digest)
            if key.public_binding() != {name: selected.head.to_dict()[name] for name in key.public_binding()}:
                raise E2eeError("owner_keyring_mismatch")
        self.owner.keyring.merge(organization, keys)
        self._merge_manifests(organization, restored)
        self.owner.store.save(organization)

    def _retain_provisional_roots(self, roots: tuple[_RootIdentity, ...]) -> None:
        retained = self.session._device.setdefault("owner_provisional_root_evidence", [])
        for root in roots:
            if root.document() not in retained:
                retained.append(root.document())

    def accept_device_backup(self, material: Mapping[str, Any]) -> None:
        for certificate in material.get("certificates", []):
            if certificate.get("operation") != "device_approve":
                continue
            signed = SignedEvidence.parse(certificate.get("signed_command"))
            if "owner_access_backup" not in signed.body:
                continue
            identifier = canonical_digest(self.crypto, signed.document())
            if identifier in self.session._device.get("owner_custody_receipts", []):
                continue
            body = dict(signed.body)
            backup = body.pop("owner_access_backup")
            if any(body.get(name) != self.session.public[name] for name in (
                "device_id", "encryption_public_key", "signing_public_key",
            )) or body.get("challenge") != self.session._device.get("challenge"):
                raise E2eeError("pairing_mismatch")
            issuer = self.session._historical_device_material(None, signed.device_id)
            if issuer["account_subject"] != self.session.subject:
                raise E2eeError("account_mismatch")
            signed.verify(self.crypto, issuer["signing_public_key"], "device_approve")
            if "issuer_admission" not in body or not isinstance(body.get("envelopes"), list):
                raise E2eeError("unsupported_owner_device_backup")
            admission = OriginalIssuerAdmission.parse(body["issuer_admission"])
            roots = _RootIdentity.parse(self.session.trust.origin, self.session.subject, body["recovery_root"])
            payload = self.open_custody(_DeviceCustodyContext(body, signed.device_id), backup,
                                 self.session._device["encryption_secret_key"], issuer["encryption_public_key"])
            if (set(payload) != {"v", "account_subject", "organizations", "self_roots", "issuer_admission", "scope_generations"}
                    or payload["v"] != 1 or payload["account_subject"] != self.session.subject
                    or any(not isinstance(payload[name], list) for name in ("organizations", "self_roots", "scope_generations"))
                    or OriginalIssuerAdmission.parse(payload["issuer_admission"]) != admission):
                raise E2eeError("invalid_owner_custody_backup")
            retained = RootProvenance.parse({"v": 1, "self_roots": payload["self_roots"]},
                self.session.trust.origin, self.session.subject).self_roots
            if any(root.generation > roots.generation or (
                root.generation == roots.generation and root != roots
            ) for root in retained):
                raise E2eeError("invalid_owner_custody_backup")
            references = [ScopeGenerationReference.parse(value) for value in payload["scope_generations"]]
            if len({(value.scope, value.epoch) for value in references}) != len(references):
                raise E2eeError("invalid_owner_custody_backup")
            verified = self.owner.current.historical_event("device_approve", signed, {
                "device_id": body["device_id"], "encryption_public_key": body["encryption_public_key"],
                "signing_public_key": body["signing_public_key"], "challenge": body["challenge"]},
                roots, independent=roots)
            if OriginalIssuerAdmission.parse(verified.evidence.issuer_admission.to_dict()) != admission:
                raise E2eeError("owner_custody_evidence_mismatch")
            authenticated = frozenset(root for root in verified.authenticated_roots
                                      if root.subject == self.session.subject and root.origin == self.session.trust.origin)
            trusted, provisional = RootProvenance(retained).partition(authenticated)
            self._retain_provisional_roots(provisional)
            self.owner.store.retain_roots(tuple(authenticated))
            self.session._device["root_scope_generations"] = {
                "root": roots.document(),
                "operation": "device_approve", "evidence_digest": signed.digest(self.crypto, "device_approve"),
                "references": [reference.document() for reference in references]}
            for value in payload["organizations"]:
                organization = value["organization_id"]
                head = self.owner.authority(organization, active=False)
                self.owner.current.approval(organization, signed, body, head)
                self.restore_paired_sources(organization, value, admission, authenticated)
                self.import_history(organization, {"v": 1, **value})
                state = self.owner.store.get(organization)
                current = self.owner._custody(organization)
                candidates = [*value.get("retained_candidates", []), *([value["candidate"]] if value.get("candidate") is not None else [])]
                for item in candidates:
                    binding = OwnerBinding.parse(item["offer"])
                    private = item["secret_key"]
                    if (binding.operation != OwnerOperation.OFFER or binding.body.organization_id != organization
                            or binding.body.account_subject != self.session.subject
                            or self.owner.capsules.public_key(private) != binding.body.public_key):
                        raise E2eeError("invalid_owner_custody_backup")
                    restored = CandidateSecret(private, custody({
                        "recovery_id": binding.body.recovery_id, "recovery_generation": binding.body.recovery_generation,
                        "root_revision": binding.body.root_revision, "custody_revision": binding.body.custody_revision,
                    }), binding)
                    if restored.custody == current and state.candidate is None:
                        state.candidate = restored
                    elif (state.candidate is None or state.candidate.binding.command != restored.binding.command) and not any(
                        existing.binding.command == restored.binding.command for existing in state.retired_candidates
                    ):
                        state.retired_candidates.append(restored)
                if value.get("key_registration") is not None and state.registration is None:
                    saved = value["key_registration"]
                    binding = OwnerBinding.parse(saved["command"])
                    if (binding.operation != OwnerOperation.REGISTER_KEY or binding.body.organization_id != organization
                            or binding.body.device.account_subject != self.session.subject
                            or self.owner.capsules.public_key(saved["secret_key"]) != binding.body.public_key):
                        raise E2eeError("invalid_owner_custody_backup")
                    binding.command.verify(self.crypto, binding.body.device.signing_public_key, binding.operation)
                    state.registration = SavedCommand(OwnerOperation.REGISTER_KEY, UncertainCommand(binding.command), key=saved["secret_key"])
                self.owner.store.save(organization)
            self.session._device.setdefault("owner_custody_receipts", []).append(identifier)
            self.session._persist()
