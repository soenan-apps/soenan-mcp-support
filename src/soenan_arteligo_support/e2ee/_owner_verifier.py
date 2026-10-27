from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Mapping

from arteligo_public_api_client.models.e2_ee_owner_candidate_offer import E2EeOwnerCandidateOffer
from arteligo_public_api_client.models.e2_ee_owner_committed_export_reference import E2EeOwnerCommittedExportReference
from arteligo_public_api_client.models.e2_ee_owner_source_project import E2EeOwnerSourceProject

from ._crypto import E2eeError
from ._owner_authority import OwnerAuthorityReads, OwnerSourceSelection, SelectedOwnerHead
from ._owner_current import CustodyPurpose
from ._owner_protocol import (
    OwnerAuthorityHead, OwnerBinding, OwnerManifest, OwnerOperation, OwnerPreparation,
    ROOT_FIELDS, OwnerSourceDocument, OwnerTransferDecision, SignedEvidence, authority_head, canonical_digest, committed_decision,
    object_value,
)
from ._owner_state import ManifestSelection, OwnerStateStore, SavedManifest, SourceAnchor
from ._owner_sources import OriginalIssuerAdmission, OwnerSourceEvidence, OwnerIssuerEvidence, OwnerSourceManifestReference
from ._owner_envelopes import OWNER_KEY_PROOF
from ._project_identity import committed_creator, creation_recovery_id, has_committed_creator
from ._trust import _IdentityBoundEvidence, _RootIdentity, _TrustPathUnavailable, public_device

if TYPE_CHECKING:
    from ._session import DeviceSession


@dataclass(frozen=True)
class SelectedSourceManifest:
    reference: OwnerSourceManifestReference
    authority: OwnerAuthorityHead
    root: _RootIdentity
    lineage_length: int
    preparation: OwnerPreparation
    issuer_evidence: OwnerIssuerEvidence


@dataclass(frozen=True)
class OriginalProjectCreation:
    command: SignedEvidence
    creator: dict[str, Any]
    root: _RootIdentity


@dataclass(frozen=True)
class NoSelectedHistory:
    pass


@dataclass(frozen=True)
class AuthenticatedAbsent:
    last_source_epoch: int


@dataclass(frozen=True)
class FrozenProjectOrigin:
    document: OwnerSourceDocument
    creator: dict[str, Any]
    root: _RootIdentity

    @property
    def project(self) -> E2EeOwnerSourceProject:
        return self.document.project


ProjectOriginConstraint = NoSelectedHistory | AuthenticatedAbsent | FrozenProjectOrigin


@dataclass(frozen=True)
class VerifiedProjectOrigin:
    document: OwnerSourceDocument
    creator: dict[str, Any]
    root: _RootIdentity

    @property
    def project(self) -> E2EeOwnerSourceProject:
        return self.document.project


@dataclass(frozen=True)
class SelectedBindingLink:
    binding: OwnerBinding
    authority: OwnerAuthorityHead
    root: _RootIdentity
    issuer_evidence: OwnerIssuerEvidence
    independent_activation: bool

    @property
    def device(self) -> dict[str, Any]:
        return public_device(self.binding.body.device.to_dict())


@dataclass(frozen=True)
class SelectedBinding:
    binding: OwnerBinding
    authority: OwnerAuthorityHead
    root: _RootIdentity
    lineage: tuple[OwnerBinding, ...]
    selected_manifests: tuple[SelectedSourceManifest, ...]
    links: tuple[SelectedBindingLink, ...]

    @property
    def device(self) -> dict[str, Any]:
        return public_device(self.binding.body.device.to_dict())


@dataclass(frozen=True)
class VerifiedBinding(SelectedBinding):
    independent_anchor: _RootIdentity
    positive_lineage_start: int

    @property
    def positive_roots(self) -> tuple[_RootIdentity, ...]:
        return tuple(link.root for link in self.links[self.positive_lineage_start:])


class OwnerEvidenceVerifier:
    def __init__(self, session: DeviceSession, store: OwnerStateStore, account: OwnerAuthorityReads):
        self.session, self.store, self.reads = session, store, account
        self.crypto = session.crypto
        self._project_origins: dict[tuple[str, str], dict[str, FrozenProjectOrigin | VerifiedProjectOrigin]] = {}
        self._constraints: dict[tuple[str, str, str], ProjectOriginConstraint] = {}

    def clear(self) -> None:
        self._project_origins.clear()
        self._constraints.clear()

    def root(self, value: Mapping[str, Any], subject: str) -> _RootIdentity:
        return _RootIdentity.parse(self.session.trust.origin, subject, value)

    def signer(self, organization: str, command: SignedEvidence, device: Mapping[str, Any],
               root: Mapping[str, Any], *, current: bool = False,
               issuer_evidence: OwnerIssuerEvidence | None = None, proof_scope: str | None = None,
               historical_roots: tuple[_RootIdentity, ...] = ()) -> dict[str, Any]:
        public = public_device(device)
        if command.device_id != public["device_id"]:
            raise E2eeError("owner_signer_mismatch")
        scope = proof_scope if proof_scope is not None else (
            None if public["account_subject"] == self.session.subject else organization
        )
        if issuer_evidence is None and not current and self.session._root_read_set is not None:
            issuer_evidence = self.session._root_read_set.historical_evidence
        if issuer_evidence is None:
            material = self.session._device_material(scope, command.device_id)
            lookup = self.session._current_device_lookup(scope)
        else:
            def lookup(identifier: str) -> dict[str, Any]:
                value = issuer_evidence.device(identifier)
                self.session.owner_access.current.observe_device(value, scope)
                return value

            material = lookup(command.device_id)
        if public_device(material) != public:
            raise E2eeError("device_key_changed")
        if current:
            context = self.session.owner_access
            suggested = authority_head(self.session.call("e2eeGetOwnerAuthority", organization_id=organization)["owner_authority"], organization)
            head = self.reads.authority(organization, suggested.read_capability)
            identity = self.root(root, public["account_subject"])
            return context.current.qualify(organization, material, identity, head, expected_root=identity,
                proof_scope=scope).device
        evidence = _IdentityBoundEvidence(scope)
        for trusted_root in historical_roots:
            if (trusted_root.subject != public["account_subject"]
                    or trusted_root.origin != self.session.trust.origin):
                raise E2eeError("recovery_subject_mismatch")
            evidence.pin_root(trusted_root)
        evidence.pin_root(self.root(root, public["account_subject"]))
        try:
            self.session.trust._verify_device(
                material, lookup,
                frozenset(), issuer_evidence.recovery if issuer_evidence is not None
                else lambda identifier: self.session._recovery_material(scope, identifier), scope, evidence,
            )
        except _TrustPathUnavailable:
            raise E2eeError("owner_identity_verification_required") from None
        return public

    def anchor(self, organization: str, proof: Mapping[str, Any]) -> SourceAnchor:
        state = self.store.get(organization)
        if state.source_anchor is not None:
            return state.source_anchor
        head = authority_head(proof.get("owner_authority"), organization)
        for value in self.session.trust._endorsements:
            statement = SignedEvidence.parse(value)
            body = statement.body
            if (statement.device_id != self.session.device_id or body.get("scope_id") != organization
                    or body.get("trusted_device", {}).get("account_subject") != head.owner_subject):
                continue
            issuer = self.session.device(None, statement.device_id)
            if issuer["account_subject"] != self.session.subject:
                raise E2eeError("owner_identity_verification_required")
            statement.verify(self.crypto, issuer["signing_public_key"], "peer_trust")
            anchor = SourceAnchor(statement, object_value(body["trusted_device"]), object_value(body["recovery_root"]))
            break
        else:
            if head.owner_subject == self.session.subject:
                device, root = self.session.public, self.session.recovery
            else:
                device, root = proof.get("device"), proof.get("recovery")
                if not isinstance(device, dict) or not isinstance(root, dict):
                    raise E2eeError("owner_identity_verification_required")
                proposed = self.root(root, head.owner_subject)
                pinned = self.session.trust._load("recovery", proposed.identifier)
                if pinned is None or self.root(pinned, head.owner_subject) != proposed:
                    raise E2eeError("owner_identity_verification_required")
            if root is None:
                raise E2eeError("owner_identity_verification_required")
            root = {name: root[name] for name in ROOT_FIELDS}
            command = SignedEvidence.parse(self.session.sign("peer_trust", {
                "scope_id": organization, "trusted_device": device, "recovery_root": root,
            }))
            anchor = SourceAnchor(command, device, root)
        state.source_anchor = anchor
        self.store.save(organization)
        return anchor

    def selected_binding(self, organization: str, proof: Mapping[str, Any], head: OwnerAuthorityHead,
                         *, sources: OwnerSourceEvidence | None = None,
                         proof_scope: str | None = None) -> SelectedBinding:
        evidence_scope = organization if proof_scope is None else proof_scope
        newest: list[SelectedBindingLink] = []
        preparations: dict[str, tuple[OwnerPreparation, str]] = {}
        visiting: set[str] = set()
        current, current_head = proof, head
        while True:
            if current_head.binding_digest in visiting:
                raise E2eeError("invalid_owner_evidence")
            visiting.add(current_head.binding_digest)
            selected = self.reads.selected(organization, current_head.binding_digest, capability=current_head.read_capability)
            if not selected.matches(current_head):
                raise E2eeError("owner_binding_mismatch")
            binding = OwnerBinding.parse(current.get("signed_binding"))
            body, command = binding.body, binding.command
            if (command.digest(self.crypto, binding.operation) != current_head.binding_digest
                    or body.organization_id != organization or body.key_id != current_head.key_id
                    or body.public_key != current_head.public_key
                    or body.device.account_subject != current_head.owner_subject):
                raise E2eeError("owner_binding_mismatch")
            command.verify(self.crypto, body.device.signing_public_key, binding.operation)
            proposed = self.root(body.recovery_root.to_dict(), body.device.account_subject)
            issuer_evidence = OwnerIssuerEvidence.parse(current.get("issuer_evidence"))
            self.session.owner_access.current.original_issuer(organization, body.device.to_dict(), proposed,
                binding.original_admission, maximum_revision=body.custody_revision,
                known_roots=sources.self_roots if sources is not None and proposed.subject == self.session.subject else (),
                issuer_evidence=issuer_evidence, anchor=proposed, purpose=CustodyPurpose.ORIGIN_CONSTRAINT,
                proof_scope=evidence_scope)
            newest.append(SelectedBindingLink(binding, current_head, proposed, issuer_evidence,
                binding.operation == OwnerOperation.REGISTER_KEY and (selected.predecessor is None or not selected.predecessor.key_id)))
            if binding.operation == OwnerOperation.OFFER:
                prepared = OwnerPreparation.parse(current.get("preparation"))
                predecessor = authority_head(prepared.body.owner_authority.to_dict(), organization)
                if (prepared.body.offer_digest != current_head.binding_digest
                        or prepared.body.candidate_id != body.candidate_id
                        or current_head.ownership_revision != predecessor.ownership_revision + 1
                        or current_head.key_epoch != predecessor.key_epoch + 1 or not predecessor.key_id):
                    raise E2eeError("owner_binding_mismatch")
                offered = object_value(current.get("decision"))
                operation_id = offered.get("operation_id")
                if not isinstance(operation_id, str) or not operation_id:
                    raise E2eeError("owner_receipt_missing")
                decision = self.verify_decision(organization, self.reads.decision(organization, operation_id),
                    prepared, body, selected.head)
                preparations[current_head.binding_digest] = (prepared, decision.operation_id)
            else:
                predecessor = selected.predecessor
                advertised = authority_head(current.get("predecessor_authority"), organization)
                if (predecessor is None or any(getattr(advertised, field) != getattr(predecessor, field) for field in (
                    "organization_id", "ownership_revision", "owner_subject", "key_id", "key_epoch", "public_key", "binding_digest",
                )) or predecessor.owner_subject != current_head.owner_subject
                        or predecessor.ownership_revision != body.expected_ownership_revision
                        or predecessor.key_epoch != body.expected_key_epoch
                        or body.expected_ownership_revision != current_head.ownership_revision
                        or body.expected_key_epoch + 1 != current_head.key_epoch):
                    raise E2eeError("owner_binding_mismatch")
                if not predecessor.key_id:
                    if selected.source_selection is None:
                        break
                    predecessor = self.reads.selected(organization, selected.source_selection.successor_binding_digest).head
                    if predecessor.ownership_revision > current_head.ownership_revision:
                        raise E2eeError("owner_binding_mismatch")
            current_head = predecessor
            current = self.session.call("e2eeGetOwnerBinding", organization_id=organization,
                binding_digest=predecessor.binding_digest)
        links = tuple(reversed(newest))
        manifests: list[SelectedSourceManifest] = []
        for index, link in enumerate(links):
            if link.binding.operation != OwnerOperation.OFFER:
                continue
            prepared, operation_id = preparations[link.authority.binding_digest]
            previous = links[index - 1]
            self.preparation_issuer(organization, prepared, previous, link.issuer_evidence,
                purpose=CustodyPurpose.ORIGIN_CONSTRAINT, proof_scope=evidence_scope)
            manifests.append(SelectedSourceManifest(
                OwnerSourceManifestReference(prepared.body.source_manifest_id, prepared.body.source_manifest_digest,
                    operation_id, prepared.body.preparation_id),
                previous.authority, previous.root, index, prepared, link.issuer_evidence))
        return SelectedBinding(links[-1].binding, head, links[-1].root,
            tuple(link.binding for link in links), tuple(manifests), links)

    def _project_authority_index(self, organization: str, creation: SignedEvidence,
                                 links: tuple[SelectedBindingLink, ...]) -> int:
        endorsed = authority_head(creation.body.get("owner_authority"), organization)
        fields = ("organization_id", "ownership_revision", "owner_subject", "key_id", "key_epoch",
                  "public_key", "binding_digest")
        matches = [index for index, link in enumerate(links)
                   if all(getattr(endorsed, field) == getattr(link.authority, field) for field in fields)]
        if not matches:
            raise E2eeError("owner_identity_verification_required")
        if len(matches) != 1:
            raise E2eeError("owner_project_source_mismatch")
        return matches[0]

    def _anchored_owner_link_index(self, scope: str, links: tuple[SelectedBindingLink, ...],
                                   anchor: _RootIdentity) -> tuple[int, bool] | None:
        matches = [(index, link.root) for index, link in enumerate(links)
                   if link.root.subject == anchor.subject and link.root.origin == anchor.origin]
        if not matches:
            return None
        older = [(index, root) for index, root in matches if root.generation < anchor.generation]
        if older:
            index, candidate = min(older, key=lambda item: item[1].generation)
            self.session.owner_access.current.assert_root_lineage(scope, candidate, anchor)
            return index, True
        exact = next((index for index, root in matches if root == anchor), None)
        if exact is not None:
            return exact, False
        index, candidate = min(matches, key=lambda item: abs(item[1].generation - anchor.generation))
        self.session.owner_access.current.assert_root_lineage(scope, candidate, anchor)
        return index, True

    def binding(self, organization: str, proof: Mapping[str, Any], head: OwnerAuthorityHead,
                *, sources: OwnerSourceEvidence | None = None,
                proof_scope: str | None = None) -> VerifiedBinding:
        evidence_scope = organization if proof_scope is None else proof_scope
        selected = self.selected_binding(organization, proof, head, sources=sources, proof_scope=evidence_scope)
        project_scope = evidence_scope != organization
        state = self.store.find(organization) if project_scope else self.store.get(organization)
        anchor = sources.anchor if sources is not None else (state.source_anchor if state is not None else None)
        confirmations = sources.confirmations if sources is not None else (
            state.confirmed_sources if state is not None else ())
        project_anchor = None
        start_root_ancestry_verified = False
        if project_scope:
            stored_anchors = (*((anchor,) if anchor is not None else ()), *confirmations)
            frozen_owner_anchor = None
            start = None
            for candidate in stored_anchors:
                if candidate.command.body.get("scope_id") != organization:
                    continue
                candidate_root = self.root(candidate.root, candidate.device["account_subject"])
                owner_match = self._anchored_owner_link_index(evidence_scope, selected.links, candidate_root)
                if owner_match is not None:
                    (start, start_root_ancestry_verified), frozen_owner_anchor = owner_match, candidate
                    break
            if frozen_owner_anchor is not None:
                anchor = frozen_owner_anchor
            else:
                anchor = None
                for link in selected.links:
                    try:
                        candidate_root = self.session.owner_access.current.independent_root(
                            evidence_scope, link.binding.body.device.to_dict())
                    except E2eeError as error:
                        if error.code != "owner_identity_verification_required":
                            raise
                        continue
                    owner_match = self._anchored_owner_link_index(evidence_scope, selected.links, candidate_root)
                    if owner_match is not None:
                        (start, start_root_ancestry_verified), project_anchor = owner_match, candidate_root
                        break
                if project_anchor is None:
                    creation = self.session.owner_access._project_creation_command(
                        organization, evidence_scope,
                    )
                    creation_index = (
                        self._project_authority_index(organization, creation, selected.links)
                        if "owner_authority" in creation.body else None
                    )
                    if creation_index is not None:
                        independent = self.session.owner_access._independent_project_creation(
                            organization, evidence_scope, creation, (),
                        )
                        if independent is not None:
                            start = creation_index
                            project_anchor = selected.links[start].root
                    if project_anchor is None:
                        introductions = self.session._participants.project_owner_inviter_introductions(
                            organization, evidence_scope,
                        )
                        for introduction in introductions:
                            if introduction.scope != evidence_scope:
                                raise E2eeError("participant_scope_mismatch")
                            owner_match = self._anchored_owner_link_index(
                                evidence_scope, selected.links, introduction.root,
                            )
                            if owner_match is None:
                                continue
                            candidate_start, candidate_ancestry_verified = owner_match
                            if start is None or candidate_start < start:
                                start = candidate_start
                                start_root_ancestry_verified = candidate_ancestry_verified
                                project_anchor = introduction.root
                        if project_anchor is None:
                            independent = self.session.owner_access._independent_project_creation(
                                organization, evidence_scope, creation, introductions,
                            )
                            if independent is None:
                                raise E2eeError("owner_identity_verification_required")
                            if creation_index is None:
                                raise E2eeError("owner_identity_verification_required")
                            start = creation_index
                            project_anchor = selected.links[start].root
        else:
            start = max(index for index, link in enumerate(selected.links) if link.independent_activation)
            if anchor is None and sources is None:
                first = selected.links[start]
                anchor = self.anchor(organization, {
                    "owner_authority": first.authority.to_dict(), "device": first.binding.body.device.to_dict(),
                    "recovery": first.root.document(),
                })
        anchored = self.root(anchor.root, anchor.device["account_subject"]) if anchor is not None else project_anchor
        confirmation_scope = organization if project_scope and anchor is not None else evidence_scope
        owner_subjects = {link.authority.owner_subject for link in selected.links[start:]}
        confirmed = [self.root(item.root, item.device["account_subject"]) for item in confirmations
                     if item.command.body.get("scope_id") == confirmation_scope
                     and (not project_scope or item.device["account_subject"] in owner_subjects)]
        independent_anchor = anchored or selected.links[start].root
        previous = None
        for link in selected.links[start:]:
            proposed, binding = link.root, link.binding
            independently_anchored = proposed == anchored or proposed in confirmed or (
                previous is None and start_root_ancestry_verified
            ) or (
                proposed.subject == self.session.subject
                and proposed == self.session.trust._confirmed_head(self.session.subject, evidence_scope)
            )
            if previous is not None:
                if binding.operation == OwnerOperation.OFFER or proposed == previous.root:
                    independently_anchored = True
                else:
                    anchored = previous.root
            if not independently_anchored and anchored is not None and proposed.subject == anchored.subject:
                self.session.owner_access.current.verify_root_identity(organization, proposed, anchored,
                    binding.original_admission, maximum_revision=binding.body.custody_revision,
                    known_roots=sources.self_roots if sources is not None and proposed.subject == self.session.subject else (),
                    issuer_evidence=link.issuer_evidence, proof_scope=evidence_scope)
                independently_anchored = True
            if not independently_anchored:
                raise E2eeError("owner_identity_verification_required")
            self.session.owner_access.current.original_issuer(organization, binding.body.device.to_dict(), proposed,
                binding.original_admission, maximum_revision=binding.body.custody_revision,
                known_roots=sources.self_roots if sources is not None and proposed.subject == self.session.subject else (),
                issuer_evidence=link.issuer_evidence, anchor=proposed,
                purpose=CustodyPurpose.IDENTITY, proof_scope=evidence_scope)
            previous = link
        for manifest in selected.selected_manifests:
            if manifest.lineage_length > start:
                self.preparation_issuer(organization, manifest.preparation,
                    selected.links[manifest.lineage_length - 1], manifest.issuer_evidence,
                    purpose=CustodyPurpose.IDENTITY, proof_scope=evidence_scope)
        return VerifiedBinding(selected.binding, selected.authority, selected.root, selected.lineage,
            selected.selected_manifests, selected.links, independent_anchor, start)

    def preparation_issuer(self, organization: str, preparation: OwnerPreparation,
                           source: SelectedBinding | SelectedBindingLink, issuer_evidence: OwnerIssuerEvidence,
                           *, purpose: CustodyPurpose = CustodyPurpose.IDENTITY,
                           proof_scope: str | None = None) -> dict[str, Any]:
        admission = preparation.original_admission
        if admission.root != source.root:
            raise E2eeError("owner_custody_evidence_mismatch")
        sender = issuer_evidence.device(preparation.command.device_id)
        self.session.owner_access.current.observe_device(sender, organization if proof_scope is None else proof_scope)
        if sender["account_subject"] != source.device["account_subject"]:
            raise E2eeError("owner_signer_mismatch")
        self.session.owner_access.current.original_issuer(organization, sender, source.root, admission,
            maximum_revision=None, issuer_evidence=issuer_evidence, anchor=source.root, purpose=purpose,
            proof_scope=proof_scope)
        preparation.command.verify(self.crypto, sender["signing_public_key"], OwnerOperation.PREPARE)
        return sender

    def verify_decision(self, organization: str, decision: OwnerTransferDecision, preparation: OwnerPreparation,
                        candidate: E2EeOwnerCandidateOffer, head: OwnerAuthorityHead) -> OwnerTransferDecision:
        decision = committed_decision(decision, organization)
        body, gate = preparation.body, preparation.body.gate_descriptor
        expected = {
            "actor_subject": body.owner_authority.owner_subject,
            "target_subject": candidate.account_subject, "preparation_id": body.preparation_id,
            "preparation_digest": preparation.command.digest(self.crypto, OwnerOperation.PREPARE),
            "source_manifest_id": body.source_manifest_id, "source_manifest_digest": body.source_manifest_digest,
            "candidate_id": candidate.candidate_id, "candidate_offer_digest": body.offer_digest,
            "gate_id": gate.gate_id, "history_manifest_digest": canonical_digest(self.crypto, [item.to_dict() for item in body.keyring_manifest]),
            "head": head.to_dict(), "expected_ownership_revision": body.owner_authority.ownership_revision,
        }
        document = decision.to_dict()
        if any(document.get(name) != value for name, value in expected.items()):
            raise E2eeError("owner_receipt_mismatch")
        return decision

    def candidate(self, organization: str, entry: Mapping[str, Any]) -> OwnerBinding:
        binding = OwnerBinding.parse(entry.get("offer"))
        body = binding.body
        if (binding.operation != OwnerOperation.OFFER or body.organization_id != organization
                or binding.command.digest(self.crypto, OwnerOperation.OFFER) != entry.get("offer_digest")):
            raise E2eeError("owner_candidate_mismatch")
        context = self.session.owner_access
        material = self.session._device_material(organization, binding.command.device_id, refresh=True)
        context.current.observe_device(material, organization)
        if public_device(material) != public_device(body.device.to_dict()):
            raise E2eeError("owner_candidate_mismatch")
        try:
            anchor = context.current.independent_root(organization, material)
        except E2eeError as error:
            if (error.code != "owner_identity_verification_required"
                    or self.session.scope_metadata(organization).get("owner_org") != organization):
                raise
            from ._participant_sources import organization_anchor

            try:
                anchor = organization_anchor(
                    self.session._participants, organization, material["account_subject"], frozenset(),
                )
            except _TrustPathUnavailable:
                raise E2eeError("owner_identity_verification_required") from None
            if anchor is None:
                raise
        head = context.authority(organization, active=False)
        context.current.qualify(organization, material, anchor, head,
            expected_root=self.root(body.recovery_root.to_dict(), body.account_subject))
        binding.command.verify(self.crypto, body.device.signing_public_key, OwnerOperation.OFFER)
        return binding

    def selected_source(self, organization: str, snapshot: SelectedOwnerHead,
                        *, proof_scope: str | None = None) -> SelectedBinding | None:
        selection = snapshot.source_selection
        if selection is None:
            return None
        selected = self.reads.selected(organization, selection.successor_binding_digest,
            capability=snapshot.head.read_capability)
        proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization,
            binding_digest=selection.successor_binding_digest)
        source = self.selected_binding(organization, proof, selected.head, proof_scope=proof_scope)
        if not source.selected_manifests:
            raise E2eeError("owner_source_manifest_mismatch")
        reference = source.selected_manifests[-1].reference
        if (reference.operation_id != selection.operation_id or reference.manifest_id != selection.source_manifest_id
                or reference.manifest_digest != selection.source_manifest_digest
                or selected.head.ownership_revision > snapshot.head.ownership_revision):
            raise E2eeError("owner_source_manifest_mismatch")
        return source

    def _verify_project(self, organization: str, document: OwnerSourceDocument,
                        lineage: tuple[OwnerBinding, ...], issuer_evidence: OwnerIssuerEvidence,
                        *, purpose: CustodyPurpose, proof_scope: str | None = None) -> tuple[dict[str, Any], _RootIdentity]:
        project = document.project
        creation = SignedEvidence.parse(project.creation_command.to_dict())
        commands = [("project_create", creation), *(("peer_trust", SignedEvidence.parse(value.to_dict()))
                    for value in (*project.peer_trust, *project.owner_confirmations))]
        issuers = {}
        for value in project.command_issuers:
            key = (value.operation.value, value.command_digest)
            if key in issuers:
                raise E2eeError("owner_project_source_mismatch")
            issuers[key] = (public_device(value.device.to_dict()), OriginalIssuerAdmission.parse(value.issuer_admission.to_dict()))
        if set(issuers) != {(operation, command.digest(self.crypto, operation)) for operation, command in commands}:
            raise E2eeError("owner_project_source_mismatch")

        def verify(operation: str, command: SignedEvidence, *, owner_statement: bool = False):
            device, admission = issuers[(operation, command.digest(self.crypto, operation))]
            if command.device_id != device["device_id"]:
                raise E2eeError("owner_signer_mismatch")
            anchors = [self.root(binding.body.recovery_root.to_dict(), device["account_subject"])
                       for binding in lineage if binding.body.device.account_subject == device["account_subject"]]
            anchor = next((candidate for candidate in anchors if candidate == admission.root), None)
            if owner_statement and anchor is None:
                raise E2eeError("owner_signer_mismatch")
            self.session.owner_access.current.original_issuer(organization, device, admission.root, admission,
                maximum_revision=None, issuer_evidence=issuer_evidence, anchor=anchor or admission.root,
                purpose=purpose, proof_scope=proof_scope)
            command.verify(self.crypto, device["signing_public_key"], operation)
            return device, admission.root

        creator, original_root = verify("project_create", creation)
        if creation.body.get("project_id") != project.project_id or creation.body.get("owner_org") != organization:
            raise E2eeError("owner_project_source_mismatch")
        self.creation_root(organization, creation, creator, original_root, proof_scope=proof_scope)
        if has_committed_creator(project.project_id) and not committed_creator(project.project_id, creator["signing_public_key"]):
            raise E2eeError("owner_project_source_mismatch")
        endorsed = False
        for value in project.peer_trust:
            statement = SignedEvidence.parse(value.to_dict())
            verify("peer_trust", statement, owner_statement=True)
            peer = statement.body
            if peer.get("scope_id") != project.project_id:
                raise E2eeError("owner_project_source_mismatch")
            target = public_device(object_value(peer.get("trusted_device")))
            root = self.root(object_value(peer.get("recovery_root")), target["account_subject"])
            if target == creator and root == original_root:
                endorsed = True
        if not endorsed:
            raise E2eeError("owner_project_source_mismatch")
        confirmed = False
        for value in project.owner_confirmations:
            command = SignedEvidence.parse(value.to_dict())
            verify("peer_trust", command, owner_statement=True)
            if (command.body.get("scope_id") != project.project_id
                    or public_device(object_value(command.body.get("trusted_device"))) != creator
                    or self.root(object_value(command.body.get("recovery_root")), creator["account_subject"]) != original_root):
                raise E2eeError("owner_project_source_mismatch")
            confirmed = True
        if not has_committed_creator(project.project_id) and not confirmed:
            raise E2eeError("owner_confirmation_required")
        return creator, original_root

    def own_confirmations(self, organization: str, manifest: OwnerManifest,
                          issuer_evidence: OwnerIssuerEvidence) -> tuple[SourceAnchor, ...]:
        confirmations = []
        for document in manifest.require_documents():
            issuers = {item.command_digest: item for item in document.project.command_issuers
                       if item.operation.value == "peer_trust"}
            for value in document.project.owner_confirmations:
                command = SignedEvidence.parse(value.to_dict())
                issuer = issuers.get(command.digest(self.crypto, "peer_trust"))
                if issuer is None or issuer.device.device_id != command.device_id:
                    raise E2eeError("owner_signer_mismatch")
                if issuer.device.account_subject != self.session.subject:
                    continue
                device = public_device(issuer.device.to_dict())
                admission = OriginalIssuerAdmission.parse(issuer.issuer_admission.to_dict())
                self.session.owner_access.current.original_issuer(organization, device, admission.root, admission,
                    maximum_revision=None, issuer_evidence=issuer_evidence)
                command.verify(self.crypto, device["signing_public_key"], "peer_trust")
                confirmations.append(SourceAnchor.parse({"command": command.document(),
                    "device": command.body.get("trusted_device"), "root": command.body.get("recovery_root")},
                    origin=self.session.trust.origin))
        return tuple(confirmations)

    def creation_root(self, organization: str, creation: SignedEvidence,
                      creator: Mapping[str, Any], root: _RootIdentity | None = None,
                      *, proof_scope: str | None = None) -> _RootIdentity:
        generated = (authority_head(creation.body["owner_authority"], organization)
                     if "owner_authority" in creation.body else None)
        if creation.body.get("owner_key_proof") == OWNER_KEY_PROOF:
            if generated is None or generated.owner_subject != creator["account_subject"]:
                raise E2eeError("owner_project_source_mismatch")
            if not self.reads.selected(organization, generated.binding_digest).matches(generated):
                raise E2eeError("owner_project_source_mismatch")
            proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=generated.binding_digest)
            binding = OwnerBinding.parse(proof.get("signed_binding"))
            if (binding.command.digest(self.crypto, binding.operation) != generated.binding_digest
                    or binding.body.device.account_subject != creator["account_subject"]):
                raise E2eeError("owner_project_source_mismatch")
            actual = self.root(binding.body.recovery_root.to_dict(), creator["account_subject"])
        else:
            if generated is not None and generated.owner_subject == creator["account_subject"]:
                raise E2eeError("unsupported_owner_key_proof")
            identifier = creation_recovery_id(creation.body, creation.device_id)
            if root is not None:
                if root.identifier != identifier:
                    raise E2eeError("owner_project_source_mismatch")
                actual = root
            else:
                material = self.session._recovery_material(proof_scope or creation.body["project_id"], identifier)
                if material is None:
                    raise E2eeError("owner_root_proof_missing")
                actual = self.root(material, creator["account_subject"])
        if root is not None and actual != root:
            raise E2eeError("owner_project_source_mismatch")
        return actual

    def _require_creation_epoch(self, organization: str, creation: SignedEvidence,
                                previous_epoch: int | None, maximum_epoch: int | None) -> None:
        if previous_epoch is None:
            return
        if "owner_authority" not in creation.body:
            raise E2eeError("owner_identity_verification_required")
        generated = authority_head(creation.body["owner_authority"], organization)
        if generated.key_epoch <= previous_epoch or maximum_epoch is not None and generated.key_epoch > maximum_epoch:
            raise E2eeError("owner_identity_verification_required")
        if not self.reads.selected(organization, generated.binding_digest).matches(generated):
            raise E2eeError("owner_project_source_mismatch")

    def _require_new_project(self, organization: str, project: E2EeOwnerSourceProject,
                             authority: OwnerAuthorityHead, previous_epoch: int | None) -> None:
        self._require_creation_epoch(organization, SignedEvidence.parse(project.creation_command.to_dict()),
            previous_epoch, authority.key_epoch)

    def absent_creation(self, organization: str, scope: str, absence: AuthenticatedAbsent) -> OriginalProjectCreation:
        proof = self.session.call("e2eeGetOwnerGeneration", scope_id=scope, epoch=1)
        command = SignedEvidence.parse(proof.get("signed_command"))
        if (proof.get("operation") != "project_create" or proof.get("key_epoch") != 1
                or command.body.get("project_id") != scope or command.body.get("owner_org") != organization
                or command.body.get("owner_authority") != proof.get("owner_authority")):
            raise E2eeError("owner_project_source_mismatch")
        self._require_creation_epoch(organization, command, absence.last_source_epoch, None)
        creator = public_device(self.session._historical_device_material(scope, command.device_id))
        command.verify(self.crypto, creator["signing_public_key"], "project_create")
        if has_committed_creator(scope) and not committed_creator(scope, creator["signing_public_key"]):
            raise E2eeError("owner_project_source_mismatch")
        return OriginalProjectCreation(command, creator, self.creation_root(organization, command, creator,
            proof_scope=scope))

    def _manifest_header(self, organization: str, manifest: OwnerManifest,
                         authority: OwnerAuthorityHead, root: _RootIdentity, issuer_evidence: OwnerIssuerEvidence,
                         *, purpose: CustodyPurpose, proof_scope: str | None = None) -> None:
        head = authority_head(manifest.body.owner_authority.to_dict(), organization)
        if head != authority or manifest.body.organization_id != organization:
            raise E2eeError("owner_source_manifest_mismatch")
        sender = issuer_evidence.device(manifest.command.device_id)
        self.session.owner_access.current.observe_device(
            sender, organization if proof_scope is None else proof_scope)
        admission = OriginalIssuerAdmission.parse(manifest.command.body["issuer_admission"])
        if sender["account_subject"] != authority.owner_subject or admission.root != root:
            raise E2eeError("owner_signer_mismatch")
        self.session.owner_access.current.original_issuer(organization, sender, root, admission,
            maximum_revision=None, issuer_evidence=issuer_evidence, anchor=root, purpose=purpose,
            proof_scope=proof_scope)
        manifest.command.verify(self.crypto, sender["signing_public_key"], OwnerOperation.MANIFEST)

    def source_indexes(self, organization: str, source: SelectedBinding,
                       *, purpose: CustodyPurpose, proof_scope: str | None = None) -> tuple[tuple[SelectedSourceManifest, OwnerManifest], ...]:
        result = []
        previous: dict[str, str] = {}
        for selected in source.selected_manifests:
            reference = selected.reference
            artifact = self.session.call("e2eeGetOwnerManifest", organization_id=organization, manifest_id=reference.manifest_id)
            manifest = OwnerManifest.parse(self.crypto, artifact.get("signed_command"))
            if (manifest.body.manifest_id != reference.manifest_id or manifest.digest != reference.manifest_digest
                    or artifact.get("manifest_digest") != reference.manifest_digest):
                raise E2eeError("owner_source_manifest_mismatch")
            header_purpose = (CustodyPurpose.ORIGIN_CONSTRAINT
                if isinstance(source, VerifiedBinding) and selected.lineage_length <= source.positive_lineage_start
                else purpose)
            self._manifest_header(organization, manifest, selected.authority, selected.root,
                OwnerIssuerEvidence.parse(artifact.get("issuer_evidence")), purpose=header_purpose,
                proof_scope=proof_scope)
            entries = manifest.entries()
            if any(entries.get(key) != digest for key, digest in previous.items()):
                raise E2eeError("owner_project_source_mismatch")
            previous = entries
            result.append((selected, manifest))
        return tuple(result)

    def origin_constraint(self, organization: str, scope: str, source: SelectedBinding,
                          *, proof_scope: str | None = None) -> ProjectOriginConstraint:
        key = (organization, source.authority.binding_digest, scope)
        if key in self._constraints:
            return self._constraints[key]
        indexes = self.source_indexes(organization, source, purpose=CustodyPurpose.ORIGIN_CONSTRAINT,
            proof_scope=proof_scope)
        project_key = OwnerSourceDocument.key(scope)
        result: ProjectOriginConstraint = NoSelectedHistory()
        previous_epoch = None
        for selected, manifest in indexes:
            digest = manifest.entries().get(project_key)
            if digest is None:
                result = AuthenticatedAbsent(selected.authority.key_epoch)
            elif not isinstance(result, FrozenProjectOrigin):
                artifact = self.session.call("e2eeGetProjectOwnerSourceEvidence", scope_id=scope,
                    manifest_id=manifest.body.manifest_id)
                if (artifact.get("manifest_id") != manifest.body.manifest_id
                        or artifact.get("manifest_digest") != manifest.digest):
                    raise E2eeError("owner_source_manifest_mismatch")
                document = OwnerSourceDocument.parse(self.crypto, artifact.get("document"))
                if document.project.project_id != scope or document.digest != digest:
                    raise E2eeError("owner_project_source_mismatch")
                self._require_new_project(organization, document.project, selected.authority, previous_epoch)
                creation = self.session.owner_access._project_creation_command(organization, scope)
                if creation != SignedEvidence.parse(document.project.creation_command.to_dict()):
                    raise E2eeError("owner_project_source_mismatch")
                if "owner_authority" in creation.body:
                    anchor_index = self._project_authority_index(organization, creation, source.links)
                    if anchor_index >= selected.lineage_length:
                        raise E2eeError("owner_project_source_mismatch")
                lineage = source.lineage[:selected.lineage_length]
                creator, root = self._verify_project(organization, document, lineage,
                    OwnerIssuerEvidence.parse(artifact.get("issuer_evidence")), purpose=CustodyPurpose.ORIGIN_CONSTRAINT,
                    proof_scope=scope)
                result = FrozenProjectOrigin(document, creator, root)
            previous_epoch = selected.authority.key_epoch
        self._constraints[key] = result
        return result

    def project_origins(self, organization: str, source: VerifiedBinding) -> Mapping[str, FrozenProjectOrigin | VerifiedProjectOrigin]:
        key = (organization, source.authority.binding_digest)
        if key in self._project_origins:
            return self._project_origins[key]
        origins: dict[str, FrozenProjectOrigin | VerifiedProjectOrigin] = {}
        indexes = self.source_indexes(organization, source, purpose=CustodyPurpose.IDENTITY)
        if not indexes:
            return origins
        latest = indexes[-1][1]
        artifact = self.session.call("e2eeGetOwnerManifestDocuments", organization_id=organization,
            manifest_id=latest.body.manifest_id)
        bundle = OwnerManifest.parse(self.crypto, artifact.get("signed_command"), artifact.get("documents"))
        if bundle.command != latest.command or artifact.get("manifest_digest") != latest.digest:
            raise E2eeError("owner_source_manifest_mismatch")
        documents = {item.project_key: item for item in bundle.require_documents()}
        evidence = OwnerIssuerEvidence.parse(artifact.get("issuer_evidence"))
        previous_epoch = None
        for selected, index in indexes:
            for project_key, digest in index.entries().items():
                document = documents.get(project_key)
                if document is None or document.digest != digest:
                    raise E2eeError("owner_source_document_missing")
                project_id = document.project.project_id
                original = origins.get(project_id)
                if original is None:
                    self._require_new_project(organization, document.project, selected.authority, previous_epoch)
                    purpose = (CustodyPurpose.IDENTITY if selected.lineage_length > source.positive_lineage_start
                               else CustodyPurpose.ORIGIN_CONSTRAINT)
                    lineage = source.lineage[:selected.lineage_length]
                    if purpose is CustodyPurpose.IDENTITY:
                        lineage = lineage[source.positive_lineage_start:]
                    creator, root = self._verify_project(organization, document, lineage, evidence,
                        purpose=purpose, proof_scope=project_id)
                    origins[project_id] = (
                        VerifiedProjectOrigin(document, creator, root) if purpose is CustodyPurpose.IDENTITY
                        else FrozenProjectOrigin(document, creator, root))
                    continue
                if document.digest != original.document.digest:
                    raise E2eeError("owner_project_source_mismatch")
                if (isinstance(original, FrozenProjectOrigin)
                        and selected.lineage_length > source.positive_lineage_start):
                    origins[project_id] = VerifiedProjectOrigin(
                        original.document, original.creator, original.root,
                    )
            previous_epoch = selected.authority.key_epoch
        self._project_origins[key] = origins
        return origins

    def project_origin(self, organization: str, scope: str, source: VerifiedBinding) -> VerifiedProjectOrigin | None:
        indexes = self.source_indexes(organization, source, purpose=CustodyPurpose.IDENTITY, proof_scope=scope)
        project_key = OwnerSourceDocument.key(scope)
        original: FrozenProjectOrigin | VerifiedProjectOrigin | None = None
        previous_epoch = None
        for selected, manifest in indexes:
            digest = manifest.entries().get(project_key)
            if digest is not None:
                if original is None:
                    artifact = self.session.call("e2eeGetProjectOwnerSourceEvidence", scope_id=scope,
                        manifest_id=manifest.body.manifest_id)
                    if (artifact.get("manifest_id") != manifest.body.manifest_id
                            or artifact.get("manifest_digest") != manifest.digest):
                        raise E2eeError("owner_source_manifest_mismatch")
                    document = OwnerSourceDocument.parse(self.crypto, artifact.get("document"))
                    if document.project.project_id != scope or document.digest != digest:
                        raise E2eeError("owner_project_source_mismatch")
                    self._require_new_project(organization, document.project, selected.authority, previous_epoch)
                    creation = self.session.owner_access._project_creation_command(organization, scope)
                    if creation != SignedEvidence.parse(document.project.creation_command.to_dict()):
                        raise E2eeError("owner_project_source_mismatch")
                    if "owner_authority" in creation.body:
                        anchor_index = self._project_authority_index(organization, creation, source.links)
                        if anchor_index >= selected.lineage_length:
                            raise E2eeError("owner_project_source_mismatch")
                    start = source.positive_lineage_start
                    purpose = (CustodyPurpose.IDENTITY if selected.lineage_length > start
                               else CustodyPurpose.ORIGIN_CONSTRAINT)
                    lineage = source.lineage[:selected.lineage_length]
                    if purpose is CustodyPurpose.IDENTITY:
                        lineage = lineage[start:]
                    creator, root = self._verify_project(organization, document, lineage,
                        OwnerIssuerEvidence.parse(artifact.get("issuer_evidence")),
                        purpose=purpose, proof_scope=scope)
                    original = (VerifiedProjectOrigin(document, creator, root)
                                if purpose is CustodyPurpose.IDENTITY
                                else FrozenProjectOrigin(document, creator, root))
                elif (isinstance(original, FrozenProjectOrigin)
                      and selected.lineage_length > source.positive_lineage_start):
                    if digest != original.document.digest:
                        raise E2eeError("owner_project_source_mismatch")
                    original = VerifiedProjectOrigin(
                        original.document, original.creator, original.root,
                    )
            previous_epoch = selected.authority.key_epoch
        if isinstance(original, FrozenProjectOrigin):
            raise E2eeError("owner_identity_verification_required")
        return original

    def project(self, organization: str, document: OwnerSourceDocument, source: VerifiedBinding,
                issuer_evidence: OwnerIssuerEvidence) -> tuple[dict[str, Any], _RootIdentity]:
        original = self.project_origins(organization, source).get(document.project.project_id)
        if original is not None:
            if document.document_bytes != original.document.document_bytes:
                raise E2eeError("owner_project_source_mismatch")
            return original.creator, original.root
        self._require_new_project(organization, document.project, source.authority,
            source.selected_manifests[-1].authority.key_epoch if source.selected_manifests else None)
        return self._verify_project(organization, document, source.lineage[source.positive_lineage_start:],
            issuer_evidence, purpose=CustodyPurpose.IDENTITY, proof_scope=document.project.project_id)

    def manifest(self, organization: str, manifest: OwnerManifest, source: VerifiedBinding,
                 issuer_evidence: OwnerIssuerEvidence | None = None) -> OwnerIssuerEvidence:
        if issuer_evidence is None:
            artifact = self.session.call("e2eeGetOwnerManifestDocuments", organization_id=organization,
                manifest_id=manifest.body.manifest_id)
            original = OwnerManifest.parse(self.crypto, artifact.get("signed_command"), artifact.get("documents"))
            if (original.command != manifest.command or original.digest != artifact.get("manifest_digest")
                    or {item.project_key: item.document_bytes for item in original.require_documents()}
                    != {item.project_key: item.document_bytes for item in manifest.require_documents()}):
                raise E2eeError("owner_source_manifest_mismatch")
            issuer_evidence = OwnerIssuerEvidence.parse(artifact.get("issuer_evidence"))
        self._manifest_header(organization, manifest, source.authority, source.root, issuer_evidence, purpose=CustodyPurpose.IDENTITY)
        previous = self.project_origins(organization, source)
        entries = manifest.entries()
        if any(entries.get(value.document.project_key) != value.document.digest for value in previous.values()):
            raise E2eeError("owner_project_source_mismatch")
        for document in manifest.require_documents():
            self.project(organization, document, source, issuer_evidence)
        return issuer_evidence

    def selected_manifest(self, organization: str, saved: SavedManifest, *, sources: OwnerSourceEvidence | None = None) -> SavedManifest:
        manifest = saved.manifest
        head = authority_head(manifest.body.owner_authority.to_dict(), organization)
        selection = saved.selection
        if selection is None:
            raise E2eeError("owner_receipt_missing")
        source = self.binding(organization, selection.source_binding, head, sources=sources)
        preparation = OwnerPreparation.parse(selection.preparation.document())
        selected_head = authority_head(selection.decision.head.to_dict(), organization)
        target_proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization,
                                         binding_digest=selected_head.binding_digest)
        self.preparation_issuer(organization, preparation, source, OwnerIssuerEvidence.parse(target_proof.get("issuer_evidence")))
        candidate = OwnerBinding.parse(target_proof.get("signed_binding"))
        if candidate.operation != OwnerOperation.OFFER:
            raise E2eeError("owner_receipt_mismatch")
        decision = self.verify_decision(organization, self.reads.decision(organization, selection.decision.operation_id),
            preparation, candidate.body, selected_head)
        if decision.to_dict() != selection.decision.to_dict():
            raise E2eeError("owner_receipt_mismatch")
        if (authority_head(preparation.body.owner_authority.to_dict(), organization) != source.authority
                or preparation.body.source_manifest_id != manifest.body.manifest_id
                or preparation.body.source_manifest_digest != manifest.digest):
            raise E2eeError("owner_source_manifest_mismatch")
        evidence = self.manifest(organization, manifest, source, saved.issuer_evidence)
        return replace(saved, issuer_evidence=evidence)

    def exported_manifest(self, organization: str, source_proof: Mapping[str, Any], source: VerifiedBinding,
                          reference: E2EeOwnerCommittedExportReference, *,
                          retained: SavedManifest | None = None) -> SavedManifest:
        if source.authority.owner_subject != self.session.subject:
            raise E2eeError("owner_receipt_mismatch")
        selected = self.reads.selected(organization, reference.successor_binding_digest,
            capability=source.authority.read_capability)
        if selected.source_selection != OwnerSourceSelection.parse(reference.to_dict()):
            raise E2eeError("owner_source_manifest_mismatch")
        decision = committed_decision(self.reads.decision(organization, reference.operation_id,
            capability=source.authority.read_capability), organization)
        head = selected.head
        if (decision.actor_subject != self.session.subject or decision.target_subject != head.owner_subject
                or decision.expected_ownership_revision != source.authority.ownership_revision
                or decision.head.to_dict() != head.to_dict()
                or head.ownership_revision != source.authority.ownership_revision + 1
                or head.key_epoch != source.authority.key_epoch + 1
                or decision.candidate_offer_digest != reference.successor_binding_digest
                or decision.source_manifest_id != reference.source_manifest_id
                or decision.source_manifest_digest != reference.source_manifest_digest):
            raise E2eeError("owner_receipt_mismatch")
        artifact = self.session.call("e2eeGetOwnerPreparation", organization_id=organization,
            preparation_id=decision.preparation_id)
        preparation = OwnerPreparation.parse(artifact.get("signed_command"))
        if (artifact.get("state") != "committed"
                or artifact.get("preparation_digest") != decision.preparation_digest
                or authority_head(preparation.body.owner_authority.to_dict(), organization) != source.authority):
            raise E2eeError("owner_receipt_mismatch")
        target_proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization,
            binding_digest=reference.successor_binding_digest)
        candidate = OwnerBinding.parse(target_proof.get("signed_binding"))
        if (candidate.operation != OwnerOperation.OFFER or candidate.body.organization_id != organization
                or candidate.body.account_subject != head.owner_subject or candidate.body.key_id != head.key_id
                or candidate.body.public_key != head.public_key
                or candidate.command.digest(self.crypto, candidate.operation) != head.binding_digest
                or authority_head(target_proof.get("owner_authority"), organization) != head
                or OwnerPreparation.parse(target_proof.get("preparation")).command != preparation.command):
            raise E2eeError("owner_receipt_mismatch")
        candidate.command.verify(self.crypto, candidate.body.device.signing_public_key, candidate.operation)
        self.preparation_issuer(organization, preparation, source,
            OwnerIssuerEvidence.parse(target_proof.get("issuer_evidence")))
        self.verify_decision(organization, decision, preparation, candidate.body, head)
        if retained is not None:
            manifest = retained.manifest
            evidence = retained.issuer_evidence
            if retained.selection is not None and (
                    retained.selection.preparation != preparation.command
                    or retained.selection.decision.to_dict() != decision.to_dict()):
                raise E2eeError("owner_receipt_mismatch")
        else:
            artifact = self.session.call("e2eeGetOwnerManifestDocuments", organization_id=organization,
                manifest_id=reference.source_manifest_id)
            manifest = OwnerManifest.parse(self.crypto, artifact.get("signed_command"), artifact.get("documents"))
            if artifact.get("manifest_digest") != reference.source_manifest_digest:
                raise E2eeError("owner_source_manifest_mismatch")
            evidence = OwnerIssuerEvidence.parse(artifact.get("issuer_evidence"))
        if (manifest.body.manifest_id != reference.source_manifest_id or manifest.digest != reference.source_manifest_digest
                or manifest.body.manifest_id != preparation.body.source_manifest_id
                or manifest.digest != preparation.body.source_manifest_digest):
            raise E2eeError("owner_source_manifest_mismatch")
        evidence = self.manifest(organization, manifest, source, evidence)
        return SavedManifest(manifest, ManifestSelection(dict(source_proof), preparation.command, decision),
            issuer_evidence=evidence)
