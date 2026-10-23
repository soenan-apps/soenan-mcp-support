from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping

from account_public_api_client.models.owner_custody_device_identity import OwnerCustodyDeviceIdentity
from account_public_api_client.models.owner_custody_evidence import OwnerCustodyEvidence
from account_public_api_client.models.owner_custody_response import OwnerCustodyResponse
from account_public_api_client.models.owner_custody_root_identity import OwnerCustodyRootIdentity
from account_public_api_client.models.owner_custody_organization_admission import OwnerCustodyOrganizationAdmission

from ._crypto import E2eeError
from ._owner_protocol import OwnerAuthorityHead, ROOT_FIELDS, SignedEvidence, bytes32, canonical_digest
from ._owner_sources import OriginalAdmissionCertificate, OriginalIssuerAdmission, OwnerIssuerEvidence
from ._owner_projection import CertificateSignatureProjection, original_certificate_digest
from ._trust import _CurrentCustodyEvidence, _RootIdentity, _TrustPathUnavailable, public_device

if TYPE_CHECKING:
    from ._owner_access import OwnerAccess


class CustodyPurpose(Enum):
    IDENTITY = "identity"
    ORIGIN_CONSTRAINT = "origin_constraint"
    ORIGIN_LINEAGE = "origin_lineage"


@dataclass(frozen=True)
class VerifiedCurrentDevice:
    device: dict[str, Any]
    root: _RootIdentity
    custody: OwnerCustodyResponse
    original_admission: OriginalIssuerAdmission


@dataclass(frozen=True)
class VerifiedHistoricalEvent:
    evidence: OwnerCustodyEvidence
    authenticated_roots: frozenset[_RootIdentity]


@dataclass(frozen=True)
class _RootCheckpoint:
    identity: _RootIdentity
    digest: str | None


@dataclass(frozen=True)
class _HistoricalCustody:
    account_subject: str
    custody_revision: int | None = None


class _CustodyProofs:
    def __init__(self, owner: OwnerAccess, snapshot: OwnerCustodyResponse | _HistoricalCustody, current_anchor: _RootIdentity,
                 anchors: tuple[_RootIdentity, ...], *, original: OriginalIssuerAdmission | None = None,
                 maximum_revision: int | None = None, proof_scope: str | None = None,
                 issuer_evidence: OwnerIssuerEvidence | None = None,
                 allowed_certificates: frozenset[OriginalAdmissionCertificate] | None = None,
                 visiting: set[tuple[str, str, str]] | None = None,
                 provisional_roots: frozenset[_RootIdentity] = frozenset(),
                 historical_anchors: frozenset[_RootIdentity] = frozenset(),
                 purpose: CustodyPurpose = CustodyPurpose.IDENTITY,
                 authenticated_roots: set[_RootIdentity] | None = None):
        self.owner, self.session, self.snapshot = owner, owner.session, snapshot
        self.current_anchor, self.independent_anchors = current_anchor, frozenset(anchors)
        self.purpose = purpose
        self.provisional_roots = provisional_roots
        self.historical_anchors = historical_anchors
        self.anchors = self.independent_anchors | provisional_roots | historical_anchors
        self.authenticated_roots = authenticated_roots if authenticated_roots is not None else set(self.independent_anchors)
        self.scope = proof_scope if proof_scope is not None else (
            None if snapshot.account_subject == self.session.subject
            else snapshot.organization_id if isinstance(snapshot, OwnerCustodyResponse) else None
        )
        self._lookup = self.session._current_device_lookup(self.scope)
        self.allowed_certificates = frozenset(original.certificates) if original is not None else None
        if allowed_certificates is not None:
            self.allowed_certificates = (allowed_certificates if self.allowed_certificates is None
                                         else self.allowed_certificates & allowed_certificates)
        self.issuer_evidence = issuer_evidence
        self.certificates: set[OriginalAdmissionCertificate] = set()
        self.maximum_revision = snapshot.custody_revision if maximum_revision is None else maximum_revision
        self.facts: dict[str, OwnerCustodyEvidence] = {}
        self.roots: dict[str, _RootCheckpoint] = {}
        self.visiting = visiting if visiting is not None else set()
        if isinstance(snapshot, OwnerCustodyResponse) and isinstance(snapshot.latest_root_transition, OwnerCustodyEvidence):
            self.facts[snapshot.latest_root_transition.evidence_digest] = snapshot.latest_root_transition

    def fact(self, digest: str) -> OwnerCustodyEvidence:
        bytes32(digest)
        if digest not in self.facts:
            self.facts[digest] = self.owner.account.witness(self.snapshot.account_subject, digest)
        fact = self.facts[digest]
        if (fact.account_subject != self.snapshot.account_subject or fact.evidence_digest != digest
                or type(fact.accepted_custody_revision) is not int or fact.accepted_custody_revision < 1
                or (self.maximum_revision is not None and fact.accepted_custody_revision > self.maximum_revision)):
            raise E2eeError("owner_custody_evidence_mismatch")
        if fact.issuer_root_evidence_digest is not None:
            bytes32(fact.issuer_root_evidence_digest)
        return fact

    def match(self, operation: str, command: SignedEvidence | CertificateSignatureProjection,
              target: Mapping[str, Any]) -> OwnerCustodyEvidence:
        fact = self.fact(command.digest(self.owner.crypto, operation))
        expected = {"device_approve": OwnerCustodyDeviceIdentity, "recovery_public": OwnerCustodyRootIdentity,
                    "envelopes_save": OwnerCustodyOrganizationAdmission}[operation]
        if (not isinstance(fact.target, expected) or fact.operation.value != operation
                or fact.issuer_device_id != command.device_id):
            raise E2eeError("owner_custody_evidence_mismatch")
        if isinstance(command, CertificateSignatureProjection) and command.reference.witness_subject != fact.account_subject:
            raise E2eeError("owner_custody_evidence_mismatch")
        actual = fact.target.to_dict()
        actual.pop("kind")
        if dict(target) != actual or fact.target_identity_digest != canonical_digest(self.owner.crypto, actual):
            raise E2eeError("owner_custody_evidence_mismatch")
        return fact

    def accepted_admission(self, fact: OwnerCustodyEvidence,
                          command: SignedEvidence | CertificateSignatureProjection) -> OriginalIssuerAdmission:
        admission = OriginalIssuerAdmission.parse(fact.issuer_admission.to_dict())
        declared = command.body.get("issuer_admission")
        if declared is not None and OriginalIssuerAdmission.parse(declared) != admission:
            raise E2eeError("owner_custody_evidence_mismatch")
        if admission.root_evidence_digest != fact.issuer_root_evidence_digest:
            raise E2eeError("owner_custody_evidence_mismatch")
        return admission

    def original_proofs(self, admission: OriginalIssuerAdmission, revision: int,
                        *, historical: _RootIdentity | None = None) -> _CustodyProofs:
        return _CustodyProofs(self.owner, self.snapshot, self.current_anchor, tuple(self.independent_anchors),
            original=admission, maximum_revision=min(self.maximum_revision, revision) if self.maximum_revision is not None else revision,
            proof_scope=self.scope, issuer_evidence=self.issuer_evidence,
            allowed_certificates=self.allowed_certificates, visiting=self.visiting, provisional_roots=self.provisional_roots,
            historical_anchors=self.historical_anchors | (frozenset((historical,)) if historical is not None else frozenset()),
            purpose=self.purpose, authenticated_roots=self.authenticated_roots)

    def _root_predecessor(self, target: _RootIdentity, source: _RootIdentity) -> None:
        if source != target and (source.subject != target.subject or source.origin != target.origin
                                  or source.generation + 1 != target.generation):
            raise E2eeError("owner_root_requalification_required")

    def accepted_issuer(self, fact: OwnerCustodyEvidence, command: SignedEvidence | CertificateSignatureProjection,
                        expected: _RootIdentity) -> dict[str, Any]:
        visit = (self.snapshot.account_subject, "issuer", fact.evidence_digest)
        if visit in self.visiting:
            raise E2eeError("invalid_owner_evidence")
        self.visiting.add(visit)
        try:
            admission = self.accepted_admission(fact, command)
            if admission.root != expected:
                raise E2eeError("owner_custody_evidence_mismatch")
            historical = None
            if isinstance(fact.target, OwnerCustodyRootIdentity):
                target = self.owner.verifier.root(fact.target.to_dict(), self.snapshot.account_subject)
                self._root_predecessor(target, expected)
                if target != expected:
                    if target in self.independent_anchors or target in self.historical_anchors:
                        historical = expected
            original = self.original_proofs(admission, fact.accepted_custody_revision, historical=historical)
            checkpoint = original.issuer_root(fact, expected)
            if checkpoint.identity != expected:
                raise E2eeError("owner_custody_evidence_mismatch")
            issuer = original.qualify_at(original.material(command.device_id), checkpoint, allow_genesis=True)
            self.certificates.update(original.certificates)
            command.verify(self.owner.crypto, issuer["signing_public_key"], fact.operation.value)
            self.authenticated_roots.add(expected)
            return issuer
        finally:
            self.visiting.remove(visit)

    def _material(self, value: Mapping[str, Any]) -> Mapping[str, Any]:
        certificates = []
        for certificate in value.get("certificates", []):
            reference = OriginalAdmissionCertificate(value["device_id"], original_certificate_digest(self.owner.crypto, certificate))
            if self.allowed_certificates is None or reference in self.allowed_certificates:
                certificates.append(certificate)
        return {**value, "certificates": certificates} if self.allowed_certificates is not None else value

    def lookup(self, identifier: str) -> Mapping[str, Any]:
        return self._material(self.issuer_evidence.device(identifier) if self.issuer_evidence is not None else self._lookup(identifier))

    def material(self, identifier: str) -> Mapping[str, Any]:
        return self._material(self.issuer_evidence.device(identifier) if self.issuer_evidence is not None
                              else self.session._device_material(self.scope, identifier, refresh=True))

    def original_admission(self, checkpoint: _RootCheckpoint) -> OriginalIssuerAdmission:
        return OriginalIssuerAdmission(checkpoint.identity, checkpoint.digest,
            tuple(sorted(self.certificates, key=lambda value: (value.device_id, value.certificate_digest))))

    def recovery(self, identifier: str) -> Mapping[str, Any]:
        result = (self.issuer_evidence.recovery(identifier) if self.issuer_evidence is not None
                  else self.session._recovery_material(self.scope, identifier))
        if result is None:
            raise E2eeError("owner_root_proof_missing")
        return result

    def qualify_at(self, device: Mapping[str, Any], checkpoint: _RootCheckpoint, *, allow_genesis: bool = False) -> dict[str, Any]:
        def authorize(operation: str, command: SignedEvidence | CertificateSignatureProjection,
                      target: Mapping[str, Any]) -> None:
            if operation == "envelopes_save":
                issuer = self.organization_issuer(command, target, checkpoint.identity)
            else:
                fact = self.match(operation, command, target)
                issuer = self.accepted_issuer(fact, command, checkpoint.identity)
            evidence.pin_device(issuer)

        def admitted(material: Mapping[str, Any], certificate: Mapping[str, Any],
                     consent: Mapping[str, Any] | None) -> None:
            for value in (certificate, *((consent,) if consent is not None else ())):
                self.certificates.add(OriginalAdmissionCertificate(material["device_id"],
                    original_certificate_digest(self.owner.crypto, value)))

        genesis = checkpoint.identity if allow_genesis and checkpoint.identity.generation == 1 and checkpoint.identity in self.anchors else None
        evidence = _CurrentCustodyEvidence(self.scope, checkpoint.identity, authorize, admitted, genesis)
        certificates = sorted(device.get("certificates", []),
            key=lambda value: value.get("operation") != "device_add_by_key")
        material = {**device, "certificates": certificates}
        try:
            return self.session.trust._verify_device(material, self.lookup, frozenset(), self.recovery, self.scope, evidence)
        except _TrustPathUnavailable:
            raise E2eeError("owner_device_requalification_required") from None

    def organization_issuer(self, command: SignedEvidence | CertificateSignatureProjection, target: Mapping[str, Any],
                            expected: _RootIdentity) -> dict[str, Any]:
        organization = target.get("organization_id")
        if ((isinstance(self.snapshot, OwnerCustodyResponse) and organization != self.snapshot.organization_id)
                or self.owner.verifier.root(target["recovery_root"], expected.subject) != expected):
            raise E2eeError("owner_custody_evidence_mismatch")
        issuer = (self.issuer_evidence.device(command.device_id) if self.issuer_evidence is not None
                  else self.session._device_material(self.scope, command.device_id, refresh=True))
        root = self.owner.verifier.root(command.body["participation"]["approver_recovery"], issuer["account_subject"])
        if self.purpose is CustodyPurpose.IDENTITY:
            anchor = self.owner.current.independent_root(organization, issuer)
            anchors = self.owner.current._anchors(organization, anchor)
            purpose = self.purpose
        elif issuer["account_subject"] == self.snapshot.account_subject:
            anchor, anchors, purpose = self.current_anchor, tuple(self.independent_anchors), self.purpose
        else:
            anchor, anchors, purpose = root, (root,), CustodyPurpose.ORIGIN_CONSTRAINT
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(issuer["account_subject"]), anchor,
            anchors, proof_scope=self.scope,
            maximum_revision=self.maximum_revision if issuer["account_subject"] == self.snapshot.account_subject else None,
            issuer_evidence=self.issuer_evidence, allowed_certificates=self.allowed_certificates, visiting=self.visiting,
            provisional_roots=frozenset(root for root in self.provisional_roots if root.subject == issuer["account_subject"]),
            historical_anchors=frozenset(root for root in self.historical_anchors if root.subject == issuer["account_subject"]),
            purpose=purpose, authenticated_roots=self.authenticated_roots)
        fact = proofs.match("envelopes_save", command, target)
        admission = proofs.accepted_admission(fact, command)
        if admission.root != root:
            raise E2eeError("owner_custody_evidence_mismatch")
        verified = proofs.accepted_issuer(fact, command, root)
        command.verify(self.owner.crypto, verified["signing_public_key"], "envelopes_save")
        self.certificates.update(proofs.certificates)
        return verified

    def initial_anchor(self, root: _RootIdentity) -> bool:
        return (root in self.independent_anchors or root in self.historical_anchors
                or (root.generation == 1 and root in self.provisional_roots)
                or (self.purpose is CustodyPurpose.ORIGIN_CONSTRAINT
                    and root.subject == self.snapshot.account_subject and root.origin == self.session.trust.origin))

    def issuer_root(self, fact: OwnerCustodyEvidence, independent: _RootIdentity) -> _RootCheckpoint:
        digest = fact.issuer_root_evidence_digest
        if digest is None:
            if not self.initial_anchor(independent):
                raise E2eeError("owner_root_requalification_required")
            return _RootCheckpoint(independent, None)
        return self.root(digest)

    def root(self, digest: str) -> _RootCheckpoint:
        if digest in self.roots:
            return self.roots[digest]
        visit = (self.snapshot.account_subject, "root", digest)
        if visit in self.visiting:
            raise E2eeError("invalid_owner_evidence")
        self.visiting.add(visit)
        try:
            fact = self.fact(digest)
            if fact.operation.value != "recovery_public" or not isinstance(fact.target, OwnerCustodyRootIdentity):
                raise E2eeError("owner_custody_evidence_mismatch")
            target = fact.target.to_dict()
            target.pop("kind")
            identity = self.owner.verifier.root(target, self.snapshot.account_subject)
            recovery = self.recovery(identity.identifier)
            if self.owner.verifier.root(recovery, identity.subject) != identity:
                raise E2eeError("owner_custody_changed")
            command = None
            for certificate in recovery.get("certificates", []):
                if certificate.get("operation") == "recovery_public":
                    candidate = SignedEvidence.parse(certificate["signed_command"])
                    if candidate.digest(self.owner.crypto, "recovery_public") == digest:
                        command = candidate
                        break
            if command is None:
                raise E2eeError("owner_root_proof_missing")
            self.match("recovery_public", command, {"account_subject": identity.subject,
                **{name: recovery[name] for name in ROOT_FIELDS}})
            admission = self.accepted_admission(fact, command)
            self._root_predecessor(identity, admission.root)
            issuer = self.material(command.device_id)
            if issuer["account_subject"] != identity.subject:
                raise E2eeError("account_mismatch")
            if fact.issuer_root_evidence_digest is None and admission.root == identity:
                if not self.initial_anchor(identity):
                    raise E2eeError("owner_root_requalification_required")
                original = self.original_proofs(admission, fact.accepted_custody_revision)
                original.qualify_at(original.material(command.device_id), _RootCheckpoint(identity, None), allow_genesis=True)
                self.certificates.update(original.certificates)
            else:
                issuer = self.accepted_issuer(fact, command, admission.root)
            command.verify(self.owner.crypto, issuer["signing_public_key"], "recovery_public")
            checkpoint = _RootCheckpoint(identity, digest)
            self.roots[digest] = checkpoint
            self.authenticated_roots.add(identity)
            return checkpoint
        finally:
            self.visiting.remove(visit)


class OwnerCurrentCustody:
    def __init__(self, owner: OwnerAccess):
        self.owner, self.session = owner, owner.session

    def observe(self, organization: str, subject: str, head: OwnerAuthorityHead) -> OwnerCustodyResponse:
        snapshot = self.owner.account.custody(organization, subject, head.read_capability)
        if snapshot.head.to_dict() != head.to_dict():
            raise E2eeError("owner_authority_changed")
        return snapshot

    def independent_root(self, scope: str, device: Mapping[str, Any]) -> _RootIdentity:
        subject = device["account_subject"]
        if subject == self.session.subject:
            root = self.session.trust._confirmed_head(subject)
            if root is not None:
                return root
            historical = self.owner.store.self_roots()
            if historical:
                return min(historical, key=lambda value: value.generation)
        roots = [self.owner.verifier.root(value, subject)
                 for (selected, _), value in self.session.trust._scope_roots.items()
                 if selected == scope and value["account_subject"] == subject]
        state = self.owner.store.find(scope)
        if state is not None:
            for source in (*((state.source_anchor,) if state.source_anchor is not None else ()), *state.confirmed_sources):
                if source.command.body.get("scope_id") == scope and source.device["account_subject"] == subject:
                    roots.append(self.owner.verifier.root(source.root, subject))
        if not roots:
            raise E2eeError("owner_identity_verification_required")
        return min(roots, key=lambda value: value.generation)

    def _anchors(self, organization: str, anchor: _RootIdentity, extra: tuple[_RootIdentity, ...] = ()) -> tuple[_RootIdentity, ...]:
        roots = {anchor, *extra}
        state = self.owner.store.find(organization)
        if anchor.subject == self.session.subject:
            roots.update(self.owner.store.self_roots())
        if state is not None:
            for source in (*((state.source_anchor,) if state.source_anchor is not None else ()), *state.confirmed_sources):
                if source.command.body.get("scope_id") == organization and source.device["account_subject"] == anchor.subject:
                    roots.add(self.owner.verifier.root(source.root, anchor.subject))
        return tuple(roots)

    def projected_device(self, device: Mapping[str, Any], projection: CertificateSignatureProjection,
                         scope: str | None, anchors: tuple[_RootIdentity, ...]) -> dict[str, Any]:
        subject = device["account_subject"]
        if not anchors or any(root.subject != subject or root.origin != self.session.trust.origin for root in anchors):
            raise E2eeError("owner_identity_verification_required")
        anchor = min(anchors, key=lambda root: root.generation)
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(subject), anchor, anchors, proof_scope=scope)
        if projection.operation == "device_approve":
            if projection.reference.witness_subject != subject:
                raise E2eeError("account_mismatch")
            target = {name: projection.body[name] for name in (
                "device_id", "encryption_public_key", "signing_public_key", "challenge",
            )}
            fact = proofs.match("device_approve", projection, target)
            admission = proofs.accepted_admission(fact, projection)
            declared = projection.body.get("recovery_root")
            if declared is not None and self.owner.verifier.root(declared, subject) != admission.root:
                raise E2eeError("owner_custody_evidence_mismatch")
            checkpoint = proofs.issuer_root(fact, admission.root)
        else:
            from ._organization_admission import OrganizationAdmission

            issuer = self.session._device_material(scope, projection.device_id)
            approval = OrganizationAdmission.parse(self.owner.crypto, self.session.trust.origin, projection, issuer)
            if approval.device != public_device(device) or approval.root not in anchors:
                raise E2eeError("owner_custody_evidence_mismatch")
            checkpoint = _RootCheckpoint(approval.root, None)
        return proofs.qualify_at(device, checkpoint)

    def capture_original(self, scope: str, device: Mapping[str, Any], root: _RootIdentity) -> OriginalIssuerAdmission:
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(device["account_subject"]), root, (root,), proof_scope=scope)
        checkpoint = _RootCheckpoint(root, None)
        recovery = self.session._recovery_material(scope, root.identifier)
        if recovery is None or self.owner.verifier.root(recovery, root.subject) != root:
            raise E2eeError("owner_root_proof_missing")
        for certificate in recovery.get("certificates", []):
            if certificate.get("operation") != "recovery_public":
                continue
            command = SignedEvidence.parse(certificate["signed_command"])
            if self.owner.verifier.root(command.body, root.subject) != root:
                continue
            digest = command.digest(self.owner.crypto, "recovery_public")
            try:
                proofs.fact(digest)
            except E2eeError as error:
                if error.code == "owner_custody_evidence_missing":
                    continue
                raise
            checkpoint = proofs.root(digest)
            break
        if checkpoint.identity != root:
            raise E2eeError("owner_custody_evidence_mismatch")
        material = proofs.material(device["device_id"])
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        proofs.qualify_at(material, checkpoint, allow_genesis=True)
        return proofs.original_admission(checkpoint)

    def proposed_local_admission(self, device: Mapping[str, Any], root: _RootIdentity,
                                 root_digest: str | None) -> OriginalIssuerAdmission:
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(self.session.subject), root, self._anchors("", root))
        checkpoint = proofs.root(root_digest) if root_digest is not None else _RootCheckpoint(root, None)
        if checkpoint.identity != root:
            raise E2eeError("owner_custody_evidence_mismatch")
        proofs.qualify_at(device, checkpoint)
        return proofs.original_admission(checkpoint)

    def qualify(self, organization: str, device: Mapping[str, Any], anchor: _RootIdentity,
                head: OwnerAuthorityHead, *, expected_root: _RootIdentity | None = None,
                known_roots: tuple[_RootIdentity, ...] = (), proof_scope: str | None = None,
                issuer_evidence: OwnerIssuerEvidence | None = None) -> VerifiedCurrentDevice:
        subject, identifier = device["account_subject"], device["device_id"]
        if anchor.subject != subject:
            raise E2eeError("recovery_subject_mismatch")
        snapshot = self.observe(organization, subject, head)
        if identifier in snapshot.revoked_device_ids:
            raise E2eeError("device_revoked")
        proofs = _CustodyProofs(self.owner, snapshot, anchor, self._anchors(organization, anchor, known_roots),
            proof_scope=proof_scope, issuer_evidence=issuer_evidence)
        material = proofs.material(identifier)
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        if material.get("state") != "approved":
            raise E2eeError("device_approval_required")
        latest = snapshot.latest_root_transition
        checkpoint = proofs.root(latest.evidence_digest) if isinstance(latest, OwnerCustodyEvidence) else _RootCheckpoint(anchor, None)
        if expected_root is not None and checkpoint.identity != expected_root:
            raise E2eeError("owner_custody_changed")
        verified = proofs.qualify_at(material, checkpoint)
        return VerifiedCurrentDevice(verified, checkpoint.identity, snapshot, proofs.original_admission(checkpoint))

    def original_issuer(self, organization: str, device: Mapping[str, Any], root: _RootIdentity,
                        admission: OriginalIssuerAdmission, *,
                        maximum_revision: int | None, known_roots: tuple[_RootIdentity, ...] = (),
                        issuer_evidence: OwnerIssuerEvidence | None = None, anchor: _RootIdentity | None = None,
                        purpose: CustodyPurpose = CustodyPurpose.IDENTITY) -> None:
        if admission.root != root:
            raise E2eeError("owner_custody_evidence_mismatch")
        anchor = anchor or self.independent_root(organization, device)
        if anchor.subject != root.subject or anchor.origin != root.origin:
            raise E2eeError("recovery_subject_mismatch")
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(device["account_subject"]), anchor,
            self._anchors(organization, anchor, known_roots), original=admission,
            maximum_revision=maximum_revision, proof_scope=organization, issuer_evidence=issuer_evidence, purpose=purpose)
        checkpoint = proofs.root(admission.root_evidence_digest) if admission.root_evidence_digest is not None else _RootCheckpoint(root, None)
        if checkpoint.identity != root or (checkpoint.digest is None and root not in proofs.anchors):
            raise E2eeError("owner_custody_evidence_mismatch")
        material = proofs.material(device["device_id"])
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        proofs.qualify_at(material, checkpoint, allow_genesis=True)

    def verify_root_identity(self, organization: str, proposed: _RootIdentity, anchor: _RootIdentity,
                             admission: OriginalIssuerAdmission, *, maximum_revision: int,
                             known_roots: tuple[_RootIdentity, ...] = (), issuer_evidence: OwnerIssuerEvidence | None = None) -> None:
        anchors = self._anchors(organization, anchor, known_roots)
        if proposed in anchors:
            return
        if admission.root != proposed or admission.root_evidence_digest is None:
            raise E2eeError("owner_root_requalification_required")
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(proposed.subject), anchor, anchors,
            original=admission, maximum_revision=maximum_revision, proof_scope=organization, issuer_evidence=issuer_evidence)
        if proofs.root(admission.root_evidence_digest).identity != proposed:
            raise E2eeError("owner_custody_evidence_mismatch")

    def assert_root_lineage(self, scope: str, original: _RootIdentity, candidate: _RootIdentity) -> None:
        if candidate == original:
            return
        if candidate.subject != original.subject or candidate.origin != original.origin:
            raise E2eeError("owner_project_source_mismatch")
        if candidate.generation == original.generation:
            raise E2eeError("recovery_key_changed")
        earlier, later = sorted((original, candidate), key=lambda root: root.generation)
        recovery = self.session._recovery_material(scope, later.identifier)
        if recovery is None or self.owner.verifier.root(recovery, later.subject) != later:
            raise E2eeError("owner_root_proof_missing")
        for certificate in recovery.get("certificates", []):
            if certificate.get("operation") != "recovery_public":
                continue
            command = SignedEvidence.parse(certificate.get("signed_command"))
            if self.owner.verifier.root(command.body, later.subject) != later:
                raise E2eeError("owner_custody_evidence_mismatch")
            proofs = _CustodyProofs(self.owner, _HistoricalCustody(later.subject), earlier, (earlier,),
                proof_scope=scope, purpose=CustodyPurpose.ORIGIN_LINEAGE)
            fact = proofs.match("recovery_public", command, {
                "account_subject": later.subject, **{name: recovery[name] for name in ROOT_FIELDS},
            })
            if proofs.root(fact.evidence_digest).identity != later:
                raise E2eeError("owner_custody_evidence_mismatch")
            return
        raise E2eeError("owner_root_proof_missing")

    def historical_event(self, operation: str, command: SignedEvidence, target: Mapping[str, Any],
                         root: _RootIdentity, *, known_roots: tuple[_RootIdentity, ...] = (),
                         issuer_evidence: OwnerIssuerEvidence | None = None, independent: _RootIdentity | None = None,
                         provisional_roots: tuple[_RootIdentity, ...] = ()) -> VerifiedHistoricalEvent:
        if root.subject != self.session.subject:
            raise E2eeError("account_mismatch")
        anchor = independent or self.independent_root("", self.session.public)
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(self.session.subject), anchor,
            self._anchors("", anchor, known_roots), issuer_evidence=issuer_evidence, provisional_roots=frozenset(provisional_roots))
        fact = proofs.match(operation, command, target)
        issuer = proofs.accepted_issuer(fact, command, root)
        command.verify(self.owner.crypto, issuer["signing_public_key"], operation)
        return VerifiedHistoricalEvent(fact, frozenset(proofs.authenticated_roots))

    def approval(self, organization: str, command: SignedEvidence, target: Mapping[str, Any], head: OwnerAuthorityHead) -> None:
        snapshot = self.observe(organization, self.session.subject, head)
        if target["device_id"] in snapshot.revoked_device_ids:
            raise E2eeError("device_revoked")
        anchor = self.independent_root(organization, self.session.public)
        proofs = _CustodyProofs(self.owner, snapshot, anchor, self._anchors(organization, anchor))
        fact = proofs.match("device_approve", command, {name: target[name] for name in (
            "device_id", "encryption_public_key", "signing_public_key", "challenge",
        )})
        root = self.owner.verifier.root(command.body["recovery_root"], self.session.subject)
        proofs.accepted_issuer(fact, command, root)
