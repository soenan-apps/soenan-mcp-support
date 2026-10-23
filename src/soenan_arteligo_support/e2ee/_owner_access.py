from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from account_public_api_client.models.owner_authority_head_state import OwnerAuthorityHeadState
from arteligo_public_api_client.models.e2_ee_owner_custody import E2EeOwnerCustody

from ._crypto import E2eeError, decode, wipe
from ._owner_account import OwnerAccountReads
from ._owner_commands import OwnerCommands
from ._owner_envelopes import OWNER_KEY_PROOF, OwnerEnvelopeIssuer
from ._owner_publication import OwnerPublicationKeys
from ._owner_handoff import OwnerHandoffs
from ._owner_keyring import OwnerKeyring
from ._owner_recovery import OwnerRecovery
from ._owner_current import OwnerCurrentCustody, VerifiedCurrentDevice
from ._owner_organization import OwnerOrganizationKeys
from ._owner_key_commands import OwnerEnvelopeCommands
from ._owner_protocol import (
    GENERATION_BLOCKERS, ROOT_FIELDS, OwnerAuthorityHead, OwnerBinding, OwnerCapsuleCrypto,
    OwnerManifest, OwnerOperation, OwnerSourceDocument, SignedEvidence, authority_head,
    custody, object_value, require_active,
)
from ._owner_state import CandidateSecret, OwnerKey, OwnerStateStore, SavedManifest, SourceAnchor
from ._owner_sources import OriginalIssuerAdmission
from ._owner_verifier import (
    AuthenticatedAbsent, FrozenProjectOrigin, NoSelectedHistory, OriginalProjectCreation,
    OwnerEvidenceVerifier, ProjectOriginConstraint, VerifiedProjectOrigin,
)
from ._signed_commands import AcceptedCommand, RejectedCommand, SavedCommand, UncertainCommand
from ._trust import _RootIdentity, _TrustPathUnavailable, public_device

if TYPE_CHECKING:
    from ._session import DeviceSession






@dataclass(frozen=True)
class CurrentCreatorQualification:
    scope: str
    origin: FrozenProjectOrigin | None
    current: VerifiedCurrentDevice


class OwnerAccess:
    """Coordinates separate Owner custody without conferring project-writing authority."""

    def __init__(self, session: DeviceSession):
        self.session, self.crypto = session, session.crypto
        self.capsules = OwnerCapsuleCrypto(session.crypto)
        self.store = OwnerStateStore(session, self.capsules)
        self.account = OwnerAccountReads(session)
        self.commands = OwnerCommands(session, self.store)
        self.verifier = OwnerEvidenceVerifier(session, self.store, self.account)
        self.current = OwnerCurrentCustody(self)
        self.keyring = OwnerKeyring(session, self.store, self.commands, self.verifier, self.capsules)
        self.handoffs = OwnerHandoffs(session, self.store, self.account, self.commands, self.verifier, self.capsules, self.keyring)
        self.publications = OwnerPublicationKeys(session, self)
        self.recovery = OwnerRecovery(self)
        self.organizations = OwnerOrganizationKeys(self)
        self.envelopes = OwnerEnvelopeCommands(self)
        self.blockers: dict[str, str] = {}
        self._maintaining = False

    def authority(self, organization: str, *, active: bool = True) -> OwnerAuthorityHead:
        proof = self.session.call("e2eeGetOwnerAuthority", organization_id=organization)
        suggested = authority_head(proof.get("owner_authority"), organization)
        head = self.account.authority(organization, suggested.read_capability)
        if head != suggested:
            raise E2eeError("owner_authority_changed")
        state = self.store.get(organization)
        previous = state.observed_head
        if previous is not None and (
            head.ownership_revision < previous.ownership_revision or head.key_epoch < previous.key_epoch
            or (head.key_epoch == previous.key_epoch and head.binding_digest != previous.binding_digest)
        ):
            raise E2eeError("owner_authority_rollback")
        verified = None
        if head.state != OwnerAuthorityHeadState.UNPROVISIONED:
            verified = self.verifier.binding(organization, proof, head)
            if head.owner_subject == self.session.subject and not any(key.key_id == head.key_id for key in state.keys):
                for candidate in (*state.retired_candidates, *((state.candidate,) if state.candidate is not None else ())):
                    if (candidate.binding.command.digest(self.crypto, OwnerOperation.OFFER) == head.binding_digest
                            and candidate.binding.body.key_id == head.key_id
                            and self.capsules.public_key(candidate.secret_key) == head.public_key):
                        self.keyring.merge(organization, [OwnerKey(head.key_id, head.key_epoch, head.public_key,
                            head.binding_digest, candidate.secret_key, candidate.binding)])
                        break
        state.observed_head = head
        self.store.save(organization)
        if active:
            require_active(head)
            if verified is None:
                raise E2eeError("owner_binding_mismatch")
            self.current.qualify(organization, verified.device, verified.root, head, expected_root=verified.root)
        return head


    def envelope_binding(self, organization: str, recipient: str, epoch: int, digest: str) -> None:
        state = self.store.find(organization)
        if state is None or not any(key.key_id == recipient and key.key_epoch == epoch
                                    and key.binding_digest == digest for key in state.keys):
            raise E2eeError("invalid_envelope")

    def _custody(self, organization: str) -> E2EeOwnerCustody:
        current = custody(self.session.call("e2eeGetOwnerCustody", organization_id=organization))
        proof = self.session.call("e2eeGetOwnerAuthority", organization_id=organization)
        suggested = authority_head(proof.get("owner_authority"), organization)
        head = self.account.authority(organization, suggested.read_capability)
        observed = self.account.custody(organization, self.session.subject, head.read_capability)
        if (head != suggested or observed.custody_revision != current.custody_revision
                or observed.head.to_dict() != head.to_dict()):
            raise E2eeError("owner_custody_changed")
        root = self.session.recovery
        if root is None or current.recovery_id != root["recovery_id"] or current.recovery_generation != root["generation"]:
            raise E2eeError("owner_custody_changed")
        return current

    def _identity(self) -> dict[str, Any]:
        if self.session.recovery is None:
            raise E2eeError("recovery_missing")
        return {"device": self.session.public,
                "recovery_root": {name: self.session.recovery[name] for name in ROOT_FIELDS}}

    def _qualify_local(self, organization: str, head: OwnerAuthorityHead) -> VerifiedCurrentDevice:
        if self.session.recovery is None:
            raise E2eeError("recovery_missing")
        root = self.verifier.root(self.session.recovery, self.session.subject)
        anchor = self.current.independent_root(organization, self.session.public)
        return self.current.qualify(organization, self.session.public, anchor, head, expected_root=root)

    def _maintain_candidate(self, organization: str, proof: dict[str, Any], current_custody: E2EeOwnerCustody) -> None:
        state = self.store.get(organization)
        candidate = state.candidate
        if candidate is not None and any(key.public_key == candidate.binding.body.public_key for key in state.keys):
            state.candidate = candidate = None
        if candidate is None:
            qualified = self._qualify_local(organization, authority_head(proof["owner_authority"], organization))
            anchor = self.verifier.anchor(organization, proof)
            pair = self.crypto.keypair()
            body = {"organization_id": organization, "candidate_id": secrets.token_urlsafe(24),
                    "account_subject": self.session.subject, "key_id": secrets.token_urlsafe(24),
                    "public_key": pair["encryption_public_key"], **current_custody.to_dict(),
                    "issuer_admission": qualified.original_admission.document(),
                    "source_anchor": anchor.command.document(), **self._identity()}
            body["custody_backup"] = self.recovery.seal_root(body, OwnerOperation.OFFER, pair["encryption_secret_key"], qualified=qualified)
            binding = OwnerBinding.parse(self.session.sign(OwnerOperation.OFFER, body))
            candidate = CandidateSecret(pair["encryption_secret_key"], current_custody, binding)
            state.candidate = candidate
            self.store.save(organization)
            pair.clear()
        if (candidate.custody != current_custody
                or self.capsules.public_key(candidate.secret_key) != candidate.binding.body.public_key):
            raise E2eeError("owner_candidate_secret_missing")
        self.session.call("e2eeRegisterOwnerCandidate", organization_id=organization, body=candidate.binding.command.document())
        candidate.registered = True
        self.store.save(organization)

    def provision_key(self, organization: str, head: OwnerAuthorityHead) -> OwnerAuthorityHead:
        if head.owner_subject != self.session.subject:
            raise E2eeError("owner_rotation_required")
        state = self.store.get(organization)
        pending = state.registration
        if pending is None:
            proof = self.session.call("e2eeGetOwnerAuthority", organization_id=organization)
            qualified = self._qualify_local(organization, head)
            anchor = self.verifier.anchor(organization, proof)
            pair, current_custody = self.crypto.keypair(), self._custody(organization)
            body = {"organization_id": organization, "request_id": secrets.token_urlsafe(24),
                    "expected_ownership_revision": head.ownership_revision, "expected_key_epoch": head.key_epoch,
                    "key_id": secrets.token_urlsafe(24), "public_key": pair["encryption_public_key"],
                    "recovery_id": current_custody.recovery_id, "recovery_generation": current_custody.recovery_generation,
                    "custody_revision": current_custody.custody_revision,
                    "issuer_admission": qualified.original_admission.document(),
                    "source_anchor": anchor.command.document(), **self._identity()}
            body["custody_backup"] = self.recovery.seal_root(body, OwnerOperation.REGISTER_KEY, pair["encryption_secret_key"], qualified=qualified)
            pending = SavedCommand(OwnerOperation.REGISTER_KEY,
                UncertainCommand(SignedEvidence.parse(self.session.sign(OwnerOperation.REGISTER_KEY, body))),
                key=pair["encryption_secret_key"])
            state.registration = pending
            self.store.save(organization)
            pair.clear()
        digest = pending.command.digest(self.crypto, OwnerOperation.REGISTER_KEY)
        try:
            pending.submit(lambda command: self.session.call("e2eeRegisterOwnerKey", organization_id=organization, body=command),
                           lambda: self.store.save(organization), rejections=frozenset())
        except E2eeError as error:
            try:
                selected = self.account.selected(organization, digest).head
            except E2eeError as lookup_error:
                if lookup_error.code == "owner_binding_not_selected" and error.code in {
                    "revision_conflict", "owner_authority_changed", "owner_custody_changed",
                }:
                    pending.outcome = RejectedCommand(pending.command, error.code)
                    state.registration = None
                    self.store.save(organization)
                raise error
            pending.outcome = AcceptedCommand(pending.command, selected.to_dict())
            self.store.save(organization)
        current = self.authority(organization, active=False)
        selected = self.account.selected(organization, digest).head
        binding = OwnerBinding.parse(pending.command.document())
        if (selected.key_id != binding.body.key_id or pending.key is None
                or selected.public_key != self.capsules.public_key(pending.key)):
            raise E2eeError("owner_binding_mismatch")
        key = OwnerKey(selected.key_id, selected.key_epoch, selected.public_key, selected.binding_digest, pending.key, binding)
        self.keyring.merge(organization, [key])
        state.registration = None
        state.custody = self._custody(organization)
        self.store.save(organization)
        if current.owner_subject == self.session.subject and (current.key_id != selected.key_id or current.state != OwnerAuthorityHeadState.ACTIVE):
            return self.provision_key(organization, current)
        if current.owner_subject == self.session.subject:
            self.keyring.backup(organization, current)
        return current

    def invalidate_custody(self, organization: str, current_custody: E2EeOwnerCustody) -> None:
        state = self.store.get(organization)
        self.commands.submit(organization, "invalidate", OwnerOperation.INVALIDATE, {
            "organization_id": organization, "request_id": secrets.token_urlsafe(24),
            "custody_revision": current_custody.custody_revision,
        })
        head = self.authority(organization, active=False)
        invalidated = self.account.custody(organization, self.session.subject, head.read_capability)
        if (invalidated.custody_revision < current_custody.custody_revision
                or authority_head(invalidated.head.to_dict(), organization) != head):
            raise E2eeError("owner_invalidation_unconfirmed")
        if head.owner_subject == self.session.subject and head.state == OwnerAuthorityHeadState.ACTIVE:
            proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)
            binding = self.verifier.binding(organization, proof, head)
            if (binding.binding.body.custody_revision < current_custody.custody_revision
                    or binding.binding.body.recovery_id != current_custody.recovery_id
                    or binding.binding.body.recovery_generation != current_custody.recovery_generation):
                raise E2eeError("owner_invalidation_unconfirmed")
            self.current.qualify(organization, binding.device, binding.root, head, expected_root=binding.root)
        if state.candidate is not None and state.candidate.custody != current_custody:
            state.retired_candidates.append(state.candidate)
            state.candidate = None
        state.custody = current_custody
        state.prepared.clear()
        self.store.finish(organization, "invalidate")

    def after_custody_change(self) -> None:
        holders = []
        memberships = {scope["project_id"] for scope in self.session.call("e2eeListOrganizations")["projects"]}
        for organization in self.store.organizations():
            if organization not in memberships:
                continue
            state = self.store.get(organization)
            if state.candidate is not None or (state.observed_head is not None and state.observed_head.owner_subject == self.session.subject):
                holders.append(organization)
        for organization in holders:
            self.invalidate_custody(organization, self._custody(organization))
        self.maintain()
        for organization in holders:
            head = self.authority(organization, active=False)
            if head.owner_subject == self.session.subject:
                require_active(head)
                self.keyring.active(organization, head)
            candidate = self.store.get(organization).candidate
            if candidate is None or not candidate.registered:
                raise E2eeError("owner_candidate_secret_missing")


    def _selected_project(self, organization: str, scope: str) -> VerifiedProjectOrigin | None:
        head = self.authority(organization, active=False)
        if not head.key_id:
            return None
        proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)
        source = self.verifier.binding(organization, proof, head)
        return self.verifier.project_origin(organization, scope, source)

    def project_origin_constraint(self, scope: str) -> ProjectOriginConstraint:
        organization = self.session.scope_metadata(scope).get("owner_org")
        self.store.source_namespace(scope, organization)
        if not organization or organization == scope:
            return NoSelectedHistory()
        proof = self.session.call("e2eeGetOwnerAuthority", organization_id=organization)
        suggested = authority_head(proof.get("owner_authority"), organization)
        snapshot = self.account.authority_snapshot(organization, suggested.read_capability)
        if snapshot.head != suggested:
            raise E2eeError("owner_authority_changed")
        selected = self.verifier.selected_source(organization, snapshot)
        result = (self.verifier.origin_constraint(organization, scope, selected)
                  if selected is not None else NoSelectedHistory())
        self.store.observe_source(scope, organization, result.document if isinstance(result, FrozenProjectOrigin) else None)
        return result

    @staticmethod
    def _assert_creator_identity(original: FrozenProjectOrigin | OriginalProjectCreation, root: _RootIdentity,
                                 device: Mapping[str, Any] | None) -> None:
        if root.subject != original.creator["account_subject"] or root.origin != original.root.origin:
            raise E2eeError("owner_project_source_mismatch")
        if device is not None:
            candidate = public_device(device)
            if candidate["account_subject"] != root.subject:
                raise E2eeError("owner_project_source_mismatch")
            if candidate["device_id"] == original.creator["device_id"] and candidate != original.creator:
                raise E2eeError("device_key_changed")

    def assert_project_creator(self, scope: str, root: _RootIdentity, *, device: Mapping[str, Any] | None = None,
                               qualification: CurrentCreatorQualification | None = None) -> FrozenProjectOrigin | None:
        constraint = self.project_origin_constraint(scope)
        original = constraint if isinstance(constraint, FrozenProjectOrigin) else None
        if qualification is not None:
            if (qualification.scope != scope or qualification.origin != original or qualification.current.root != root
                    or device is not None and qualification.current.device != public_device(device)):
                raise E2eeError("owner_project_source_mismatch")
        claimed = (self.verifier.absent_creation(self.session.scope_metadata(scope)["owner_org"], scope, constraint)
                   if isinstance(constraint, AuthenticatedAbsent) else original)
        if claimed is not None:
            self._assert_creator_identity(claimed, root, device)
            if qualification is None:
                self.current.assert_root_lineage(scope, claimed.root, root)
        return original

    def assert_creator_evidence(self, scope: str, root: _RootIdentity,
                                device: Mapping[str, Any], *, independent: _RootIdentity) -> CurrentCreatorQualification | None:
        try:
            self.assert_project_creator(scope, root, device=device)
            return None
        except E2eeError as error:
            if error.code not in {"owner_root_proof_missing", "owner_root_requalification_required"}:
                raise
        return self.qualify_current_creator(scope, device, independent, root)

    def qualify_current_creator(self, scope: str, device: Mapping[str, Any], anchor: _RootIdentity,
                                expected_root: _RootIdentity) -> CurrentCreatorQualification:
        constraint = self.project_origin_constraint(scope)
        original = constraint if isinstance(constraint, FrozenProjectOrigin) else None
        if original is not None:
            self._assert_creator_identity(original, expected_root, device)
        organization = self.session.scope_metadata(scope).get("owner_org")
        if not organization:
            raise E2eeError("organization_required")
        proof = self.session.call("e2eeGetOwnerAuthority", organization_id=organization)
        suggested = authority_head(proof.get("owner_authority"), organization)
        head = self.account.authority(organization, suggested.read_capability)
        if head != suggested:
            raise E2eeError("owner_authority_changed")
        qualified = self.current.qualify(organization, device, anchor, head,
            expected_root=expected_root, proof_scope=scope)
        result = CurrentCreatorQualification(scope, original, qualified)
        self.assert_project_creator(scope, expected_root, device=device, qualification=result)
        return result

    def project_owner_anchor(self, scope: str, subject: str) -> tuple[dict[str, Any], _RootIdentity] | None:
        organization = self.session.scope_metadata(scope).get("owner_org")
        if not organization or organization == scope:
            return None
        state = self.store.find(organization)
        if state is None:
            return None
        for anchor in state.confirmed_sources:
            if (anchor.command.body.get("scope_id") == scope
                    and anchor.device["account_subject"] == subject):
                return anchor.device, self.verifier.root(anchor.root, subject)
        return None

    def _project_source(self, organization: str, scope: str) -> OriginalProjectCreation:
        selected = self._selected_project(organization, scope)
        if selected is not None:
            return OriginalProjectCreation(SignedEvidence.parse(selected.project.creation_command.to_dict()), selected.creator, selected.root)
        from ._participant_sources import committed_owner

        page = self.session.call("e2eeGetScopeParticipantProofs", scope_id=scope, source_scope_id=organization, limit=256)
        context = object_value(page.get("source"))
        original = SignedEvidence.parse(context.get("project_command"))
        material = self.session._device_material(scope, original.device_id)
        subject = material["account_subject"]
        lookup = self.session._current_device_lookup(scope)
        roots = lambda identifier: self.session._recovery_material(scope, identifier)
        try:
            committed = committed_owner(self.session._participants, scope, subject, lookup, roots)
        except _TrustPathUnavailable:
            committed = None
        if committed is not None:
            if committed.device != public_device(material):
                raise E2eeError("device_key_changed")
            original.verify(self.crypto, committed.device["signing_public_key"], "project_create")
            if original.body.get("project_id") != scope or original.body.get("owner_org") != organization:
                raise E2eeError("owner_project_source_mismatch")
            return OriginalProjectCreation(original, committed.device, committed.root)
        anchor = self.project_owner_anchor(scope, subject)
        if anchor is None:
            raise E2eeError("owner_confirmation_required")
        root = self.verifier.creation_root(organization, original, material)
        creator = self.verifier.signer(organization, original, material, root.document(), proof_scope=scope)
        original.verify(self.crypto, creator["signing_public_key"], "project_create")
        if original.body.get("project_id") != scope or original.body.get("owner_org") != organization:
            raise E2eeError("owner_project_source_mismatch")
        return OriginalProjectCreation(original, creator, root)

    def _project_evidence(self, organization: str, project: dict[str, Any],
                          admission: OriginalIssuerAdmission) -> OwnerSourceDocument:
        scope = project["project_id"]
        inherited = self._selected_project(organization, scope)
        if inherited is not None:
            if inherited.project.creation_command.to_dict() != project["creation_command"]:
                raise E2eeError("owner_project_source_mismatch")
            return inherited.document
        source = self._project_source(organization, scope)
        if source.command.document() != project["creation_command"]:
            raise E2eeError("owner_project_source_mismatch")
        self.verifier.creation_root(organization, source.command, source.creator, source.root)
        confirmations = [anchor.command for anchor in self.store.get(organization).confirmed_sources
                         if anchor.command.body.get("scope_id") == scope
                         and public_device(anchor.command.body.get("trusted_device", {})) == source.creator
                         and self.verifier.root(anchor.root, source.root.subject) == source.root]
        from ._project_identity import has_committed_creator

        if not has_committed_creator(scope) and not confirmations:
            raise E2eeError("owner_confirmation_required")
        peer = SignedEvidence.parse(self.session.sign("peer_trust", {"scope_id": scope, "trusted_device": source.creator,
            "recovery_root": {name: source.root.document()[name] for name in ROOT_FIELDS}}))
        original = self.current.capture_original(scope, source.creator, source.root)
        issuers = {("project_create", source.command.digest(self.crypto, "project_create")): {
            "operation": "project_create", "command_digest": source.command.digest(self.crypto, "project_create"),
            "device": source.creator, "issuer_admission": original.document(),
        }, ("peer_trust", peer.digest(self.crypto, "peer_trust")): {
            "operation": "peer_trust", "command_digest": peer.digest(self.crypto, "peer_trust"),
            "device": self.session.public, "issuer_admission": admission.document(),
        }}
        for command in confirmations:
            material = self.session._device_material(None, command.device_id)
            if material["account_subject"] != self.session.subject:
                raise E2eeError("owner_signer_mismatch")
            command.verify(self.crypto, material["signing_public_key"], "peer_trust")
            original = self.current.capture_original(scope, material, admission.root)
            issuers[("peer_trust", command.digest(self.crypto, "peer_trust"))] = {
                "operation": "peer_trust", "command_digest": command.digest(self.crypto, "peer_trust"),
                "device": public_device(material), "issuer_admission": original.document(),
            }
        return OwnerSourceDocument.create(self.crypto, {
            "project_id": scope, "creation_command": source.command.document(), "peer_trust": [peer.document()],
            "owner_confirmations": [item.document() for item in confirmations], "command_issuers": list(issuers.values()),
        })

    def _manifest(self, organization: str, head: OwnerAuthorityHead, inventory: dict[str, Any]) -> OwnerManifest:
        state = self.store.get(organization)
        pending = state.journal.get("manifest")
        if pending is not None:
            self.commands.submit(organization, "manifest", OwnerOperation.MANIFEST)
            if pending.source_documents is None:
                raise E2eeError("owner_source_document_missing")
            saved = OwnerManifest.parse(self.crypto, pending.command.document(), pending.source_documents)
            original_head = authority_head(saved.body.owner_authority.to_dict(), organization)
            proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=original_head.binding_digest)
            self.verifier.manifest(organization, saved, self.verifier.binding(organization, proof, original_head))
            state.manifests[saved.body.manifest_id] = SavedManifest(saved)
            self.store.finish(organization, "manifest")
        proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)
        source = self.verifier.binding(organization, proof, head)
        qualified = self._qualify_local(organization, head)
        documents = {item.document.project_key: item.document for item in self.verifier.project_origins(organization, source).values()}
        for project in inventory["projects"]:
            document = self._project_evidence(organization, project, qualified.original_admission)
            if document.project_key in documents and documents[document.project_key].document_bytes != document.document_bytes:
                raise E2eeError("owner_project_source_mismatch")
            documents[document.project_key] = document
        ordered = tuple(documents[key] for key in sorted(documents, key=lambda value: bytes(decode(value))))
        entries = [document.entry() for document in ordered]
        for saved in state.manifests.values():
            if saved.manifest.body.owner_authority.to_dict() == head.to_dict() and saved.manifest.command.body["entries"] == entries:
                return saved.manifest
        command = SignedEvidence.parse(self.session.sign(OwnerOperation.MANIFEST, {
            "format": "project_index_v1", "organization_id": organization, "manifest_id": secrets.token_urlsafe(24),
            "owner_authority": head.to_dict(), "issuer_admission": qualified.original_admission.document(), "entries": entries,
        }))
        pending = SavedCommand(OwnerOperation.MANIFEST, UncertainCommand(command),
            source_documents=tuple(document.document() for document in ordered))
        state.journal["manifest"] = pending
        self.store.save(organization)
        self.commands.submit(organization, "manifest", OwnerOperation.MANIFEST)
        manifest = OwnerManifest.parse(self.crypto, command.document(), pending.source_documents)
        self.verifier.manifest(organization, manifest, source)
        state.manifests[manifest.body.manifest_id] = SavedManifest(manifest)
        self.store.finish(organization, "manifest")
        return manifest

    def public_identity(self, organization: str) -> dict[str, Any]:
        head = self.authority(organization)
        if head.owner_subject != self.session.subject:
            raise E2eeError("owner_required")
        return self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)

    def confirm_authority(self, organization: str, identity: Mapping[str, Any]) -> str:
        proposed = authority_head(identity.get("owner_authority"), organization)
        current = self.account.authority(organization, proposed.read_capability)
        if current != proposed:
            raise E2eeError("owner_authority_changed")
        require_active(current)
        binding = OwnerBinding.parse(identity.get("signed_binding"))
        if (binding.command.digest(self.crypto, binding.operation) != current.binding_digest
                or binding.body.organization_id != organization or binding.body.key_id != current.key_id
                or binding.body.public_key != current.public_key or binding.body.device.account_subject != current.owner_subject):
            raise E2eeError("owner_binding_mismatch")
        binding.command.verify(self.crypto, binding.body.device.signing_public_key, binding.operation)
        device, root = binding.body.device.to_dict(), binding.body.recovery_root.to_dict()
        self.verifier.signer(organization, binding.command, device, root, current=True)
        command = SignedEvidence.parse(self.session.sign("peer_trust", {
            "scope_id": organization, "trusted_device": device, "recovery_root": root,
        }))
        anchor = SourceAnchor(command, device, root)
        state = self.store.get(organization)
        if state.source_anchor is None:
            state.source_anchor = anchor
        elif anchor not in state.confirmed_sources:
            state.confirmed_sources.append(anchor)
        self.store.save(organization)
        return current.binding_digest

    def organization_anchors(self, organization: str) -> list[dict[str, Any]]:
        state = self.store.find(organization)
        return [state.source_anchor.command.document()] if state is not None and state.source_anchor is not None else []

    consume_link = staticmethod(OwnerHandoffs.consume_link)

    def import_handoff(self, action: dict[str, str] | None = None) -> dict[str, str]:
        self.session.require_approved()
        return self.handoffs.import_action(action, lambda organization: self.authority(organization, active=False))

    def _maintain_organization(self, organization: str) -> None:
        self.commands.resume(organization)
        proof = self.session.call("e2eeGetOwnerAuthority", organization_id=organization)
        head = self.authority(organization, active=False)
        state, current_custody = self.store.get(organization), self._custody(organization)
        if ((state.custody is not None and state.custody != current_custody)
                or (state.candidate is not None and state.candidate.custody != current_custody)):
            self.invalidate_custody(organization, current_custody)
            head = self.authority(organization, active=False)
        self._maintain_candidate(organization, proof, current_custody)
        if head.owner_subject != self.session.subject:
            if head.state == OwnerAuthorityHeadState.ACTIVE:
                self.provision_member_projects(organization, head)
            return
        if head.state != OwnerAuthorityHeadState.ACTIVE or state.registration is not None:
            head = self.provision_key(organization, head)
        self.keyring.active(organization, head)
        self.organizations.maintain(organization, head)
        inventory = self.session.call("e2eeGetOwnerInventory", organization_id=organization)
        for missing in inventory["missing_coverage"]:
            self.provision_envelope(organization, head, missing["project_id"], missing["key_epoch"])
        inventory = self.session.call("e2eeGetOwnerInventory", organization_id=organization)
        if inventory["missing_coverage"]:
            raise E2eeError("owner_coverage_incomplete")
        for project in inventory["projects"]:
            metadata = self.session.scope_metadata(project["project_id"], refresh=True)
            try:
                self.publications.require_generation(project["project_id"], metadata["key_epoch"])
            except E2eeError as error:
                if error.code not in GENERATION_BLOCKERS:
                    raise
                self.session.rotate_scope(metadata)
            else:
                if metadata["key_state"] == "rekey_required":
                    self.session.rotate_scope(metadata)
        inventory = self.session.call("e2eeGetOwnerInventory", organization_id=organization)
        manifest = self._manifest(organization, head, inventory)
        self.keyring.backup(organization, head)
        candidates = self.session.call("e2eeGetOwnerCandidates", organization_id=organization)["candidates"]
        for candidate in candidates:
            if candidate["state"] == "qualified":
                self.handoffs.prepare(organization, head, candidate, manifest)
        state.custody = current_custody
        self.store.save(organization)

    def maintain(self) -> None:
        if self._maintaining:
            return
        self.session.require_approved()
        self._maintaining = True
        self.blockers.clear()
        try:
            for scope in self.session.call("e2eeListOrganizations")["projects"]:
                organization = scope["project_id"]
                try:
                    self._maintain_organization(organization)
                except E2eeError as error:
                    if error.code in {"device_session_superseded", "authentication_superseded"}:
                        raise
                    self.blockers[organization] = error.code
        finally:
            self._maintaining = False


    def maintenance_issuer(self, head: OwnerAuthorityHead) -> OwnerEnvelopeIssuer:
        return OwnerEnvelopeIssuer(self.session, head, self.keyring.active(head.organization_id, head))


    def wrap(self, scope: str, epoch: int, key: bytearray, head: OwnerAuthorityHead) -> dict[str, Any]:
        return self.session.wrap_key(scope, epoch, key, recipient=head.key_id, kind="owner", public_key=head.public_key,
                                     owner_key_epoch=head.key_epoch, owner_binding_digest=head.binding_digest)

    def provision_envelope(self, organization: str, head: OwnerAuthorityHead, scope: str, epoch: int, *, ordinary: bool = False) -> None:
        state = self.store.get(organization)
        slot = f"envelope:{scope}:{epoch}:{head.key_id}"
        body = None
        if slot not in state.journal:
            key = self.session.scope_key(scope, epoch)
            try:
                if ordinary:
                    envelope = self.wrap(scope, epoch, key, head)
                    body = {"scope_id": scope, "key_epoch": epoch, "owner_authority": head.to_dict(),
                            "envelopes": [envelope]}
                else:
                    envelope = self.maintenance_issuer(head).wrap(scope, epoch, key,
                        recipient=head.key_id, kind="owner", public_key=head.public_key,
                        owner_key_epoch=head.key_epoch, owner_binding_digest=head.binding_digest)
                    body = {"scope_id": scope, "key_epoch": epoch, "owner_authority": head.to_dict(),
                            "owner_key_proof": OWNER_KEY_PROOF, "envelopes": [envelope]}
            finally:
                wipe(key)
        self.commands.submit(organization, slot, OwnerOperation.ORDINARY_ENVELOPES if ordinary else OwnerOperation.ENVELOPES, body)
        self.store.finish(organization, slot)

    def provision_member_projects(self, organization: str, head: OwnerAuthorityHead) -> None:
        for project in self.session.call("e2eeListProjects")["projects"]:
            if project.get("owner_org") != organization or project.get("role") not in {"owner", "editor"}:
                continue
            scope = project["project_id"]
            for epoch in range(1, project["key_epoch"] + 1):
                existing = self.session.call("e2eeGetEnvelopes", scope_id=scope, epoch=epoch,
                    recipient_id=head.key_id, recipient_kind="owner")["envelopes"]
                if existing:
                    self.envelopes.sender(scope, epoch, existing[0])
                    if existing[0].get("owner_key_epoch") != head.key_epoch or existing[0].get("owner_binding_digest") != head.binding_digest:
                        raise E2eeError("owner_binding_mismatch")
                else:
                    self.provision_envelope(organization, head, scope, epoch, ordinary=True)
            try:
                publication = self.publications.key(scope, project["key_epoch"])
                wipe(publication.key)
            except E2eeError as error:
                if error.code not in GENERATION_BLOCKERS:
                    raise
                self.session.rotate_scope(self.session.scope_metadata(scope, refresh=True))

    def read_key(self, scope: str, epoch: int) -> bytearray:
        organization = self.session.scope_metadata(scope).get("owner_org")
        if not organization:
            raise E2eeError("key_redistribution_required")
        head = self.authority(organization, active=False)
        if head.owner_subject != self.session.subject:
            raise E2eeError("key_redistribution_required")
        keys = self.store.get(organization).keys
        if not keys:
            raise E2eeError("owner_candidate_secret_missing")
        for key in reversed(keys):
            try:
                return self.session._read_key(scope, epoch, recipient=key.key_id, kind="owner", secret_key=key.secret_key)
            except E2eeError as error:
                if error.code != "key_redistribution_required":
                    raise
        raise E2eeError("key_redistribution_required")


    def clear(self) -> None:
        self.store.clear()
        self.verifier.clear()
        self.blockers.clear()
