from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping

from account_public_api_client.models.owner_custody_device_identity import OwnerCustodyDeviceIdentity
from account_public_api_client.models.owner_custody_evidence import OwnerCustodyEvidence
from account_public_api_client.models.owner_custody_response import OwnerCustodyResponse
from account_public_api_client.models.owner_custody_root_identity import OwnerCustodyRootIdentity
from account_public_api_client.models.owner_custody_organization_admission import OwnerCustodyOrganizationAdmission

from ._crypto import E2eeError, encode, wipe
from ._organization_admission import OrganizationAdmission
from ._owner_protocol import OwnerAuthorityHead, ROOT_FIELDS, SignedEvidence, authority_head, bytes32, canonical_digest
from ._owner_sources import OriginalAdmissionCertificate, OriginalIssuerAdmission, OwnerIssuerEvidence
from ._owner_projection import CertificateSignatureProjection, original_certificate_digest
from ._trust import (
    _CurrentCustodyEvidence, _CurrentDeviceQualification, _CurrentRecipientSet,
    _CurrentRootClaim, _CurrentRootHead, _DEVICE_ROOT_DOMAIN, _RootIdentity,
    _TrustPathUnavailable, public_device,
)

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
                 facts: dict[tuple[str, str], OwnerCustodyEvidence] | None = None,
                 visiting: set[tuple[str, str, str]] | None = None,
                 historical_anchors: frozenset[_RootIdentity] = frozenset(),
                 purpose: CustodyPurpose = CustodyPurpose.IDENTITY,
                 authenticated_roots: set[_RootIdentity] | None = None):
        self.owner, self.session, self.snapshot = owner, owner.session, snapshot
        self.current_anchor, self.independent_anchors = current_anchor, frozenset(anchors)
        self.purpose = purpose
        self.historical_anchors = historical_anchors
        self.anchors = self.independent_anchors | historical_anchors
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
        self.facts: dict[tuple[str, str], OwnerCustodyEvidence] = facts if facts is not None else {}
        self.roots: dict[str, _RootCheckpoint] = {}
        self.visiting = visiting if visiting is not None else set()

    def fact(self, digest: str) -> OwnerCustodyEvidence:
        bytes32(digest)
        identity = (self.snapshot.account_subject, digest)
        fact = self.facts.get(identity)
        if fact is None:
            latest = self.snapshot.latest_root_transition if isinstance(self.snapshot, OwnerCustodyResponse) else None
            fact = (latest if isinstance(latest, OwnerCustodyEvidence) and latest.evidence_digest == digest
                    else self.owner.account.witness(self.snapshot.account_subject, digest))
        if (fact.account_subject != self.snapshot.account_subject or fact.evidence_digest != digest
                or type(fact.accepted_custody_revision) is not int or fact.accepted_custody_revision < 1
                or (self.maximum_revision is not None and fact.accepted_custody_revision > self.maximum_revision)):
            raise E2eeError("owner_custody_evidence_mismatch")
        if fact.issuer_root_evidence_digest is not None:
            bytes32(fact.issuer_root_evidence_digest)
        self.facts[identity] = fact
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
            allowed_certificates=self.allowed_certificates, facts=self.facts, visiting=self.visiting,
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
        self.owner.current.observe_device(value, self.scope)
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
                if self.accepted_admission(fact, command).root != checkpoint.identity:
                    raise _TrustPathUnavailable()
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
        self.owner.current.observe_device(issuer, self.scope)
        root = self.owner.verifier.root(command.body["participation"]["approver_recovery"], issuer["account_subject"])
        project_scope = self.scope is not None and self.scope != organization
        purpose = self.purpose
        if isinstance(self.snapshot, OwnerCustodyResponse) and purpose is not CustodyPurpose.IDENTITY:
            raise E2eeError("owner_identity_verification_required")
        if purpose is CustodyPurpose.IDENTITY:
            if project_scope:
                roots = {
                    candidate for candidate in (
                        *self.authenticated_roots, *self.independent_anchors, *self.historical_anchors,
                    )
                    if candidate.subject == issuer["account_subject"] and candidate.origin == self.session.trust.origin
                }
                if issuer["account_subject"] == self.session.subject:
                    roots.update(
                        self.owner.verifier.root(value, issuer["account_subject"])
                        for (scope, _), value in self.session.trust._scope_roots.items()
                        if scope == self.scope and value["account_subject"] == issuer["account_subject"]
                    )
                if not roots:
                    roots.add(self.owner.current.independent_root(self.scope, issuer))
                anchors = tuple(roots)
                anchor = min(roots, key=lambda value: value.generation)
                if root != anchor:
                    earlier, later = sorted((root, anchor), key=lambda value: value.generation)
                    self.owner.current.assert_root_lineage(self.scope, earlier, later)
            else:
                anchor = self.owner.current.independent_root(organization, issuer)
                anchors = self.owner.current._anchors(organization, anchor)
        elif issuer["account_subject"] == self.snapshot.account_subject:
            anchor, anchors = self.current_anchor, tuple(self.independent_anchors)
        else:
            anchor, anchors = root, (root,)
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(issuer["account_subject"]), anchor,
            anchors, proof_scope=self.scope,
            maximum_revision=self.maximum_revision if issuer["account_subject"] == self.snapshot.account_subject else None,
            issuer_evidence=self.issuer_evidence, allowed_certificates=self.allowed_certificates,
            facts=self.facts, visiting=self.visiting,
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

    def observe_device(self, device: Mapping[str, Any], scope: str | None) -> None:
        self.session.trust.observe_devices(
            [dict(device)], None if device.get("account_subject") == self.session.subject else scope)

    def _require_nonnegative(self, device: Mapping[str, Any], scope: str | None = None) -> None:
        if self.session.trust.known_revoked(device, scope):
            raise E2eeError("device_revoked")

    def current_root_identity_device_ids(
        self,
        organization: str,
        scope: str,
        devices: tuple[Mapping[str, Any], ...],
    ) -> frozenset[str]:
        root = self.session.trust._confirmed_head(self.session.subject)
        if (root is None or root.subject != self.session.subject
                or root.origin != self.session.trust.origin):
            raise E2eeError("owner_identity_verification_required")
        recovery = self.session.call("e2eeGetRecovery")
        if self.owner.verifier.root(recovery, self.session.subject) != root:
            raise E2eeError("owner_custody_changed")
        head = self.owner.account.authority(
            organization, self.owner.account.capability(organization),
        )
        current = self.qualify(
            organization, self.session.public, root, head, expected_root=root, proof_scope=scope,
        )
        if (current.device != self.session.public or current.root != root
                or current.custody.organization_id != organization
                or current.custody.account_subject != self.session.subject):
            raise E2eeError("owner_custody_changed")
        requested = {}
        for device in devices:
            if device["account_subject"] != self.session.subject:
                raise E2eeError("account_mismatch")
            identifier = device["device_id"]
            previous = requested.get(identifier)
            if previous is not None and public_device(previous) != public_device(device):
                raise E2eeError("device_key_changed")
            requested[identifier] = device
        device_roots = recovery.get("device_roots")
        if not isinstance(device_roots, list):
            raise E2eeError("owner_root_proof_missing")
        associations = {}
        for item in device_roots:
            if (not isinstance(item, Mapping) or set(item) != {"public_device", "root_signature"}
                    or not isinstance(item["root_signature"], str) or not item["root_signature"]
                    or not isinstance(item["public_device"], Mapping)):
                raise E2eeError("owner_custody_evidence_mismatch")
            associated = item["public_device"]
            immutable = public_device(associated)
            if set(associated) != set(immutable) or associated["state"] != "approved":
                raise E2eeError("owner_custody_evidence_mismatch")
            identifier = immutable["device_id"]
            if identifier not in requested:
                continue
            if identifier in associations:
                raise E2eeError("owner_custody_evidence_mismatch")
            if immutable != public_device(requested[identifier]):
                raise E2eeError("device_key_changed")
            associations[identifier] = (associated, item["root_signature"])
        revoked = set(current.custody.revoked_device_ids)
        identities = set()
        for identifier, device in requested.items():
            association = associations.get(identifier)
            if association is None or identifier in revoked:
                continue
            try:
                material = self.session._device_material(None, identifier, refresh=True)
            except E2eeError as error:
                if error.code == "untrusted_device":
                    continue
                raise
            self.observe_device(material, scope)
            if material.get("state") != "approved":
                continue
            if public_device(material) != public_device(device):
                raise E2eeError("device_key_changed")
            try:
                self._require_nonnegative(material, scope)
            except E2eeError as error:
                if error.code == "device_revoked":
                    continue
                raise
            associated, signature = association
            message = bytearray(_DEVICE_ROOT_DOMAIN)
            message.extend(self.owner.crypto.canonical(associated))
            try:
                self.owner.crypto.execute({
                    "op": "verify_bytes",
                    "public_key": root.signing_key,
                    "bytes": encode(message),
                    "signature": signature,
                })
            finally:
                wipe(message)
            identities.add(identifier)
        self.session.require_approved()
        self.session.trust._require_current_head(root)
        if self.session.trust.known_revoked(self.session.public, scope):
            raise E2eeError("device_revoked")
        return frozenset(
            identifier for identifier in identities
            if not self.session.trust.known_revoked(requested[identifier], scope)
        )

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

    def _anchors(self, organization: str, anchor: _RootIdentity, extra: tuple[_RootIdentity, ...] = (),
                 *, proof_scope: str | None = None) -> tuple[_RootIdentity, ...]:
        scope = organization if proof_scope is None else proof_scope
        roots = {anchor, *extra}
        if anchor.subject == self.session.subject:
            roots.update(self.owner.store.self_roots())
        state = self.owner.store.find(organization)
        if state is not None:
            for source in (*((state.source_anchor,) if state.source_anchor is not None else ()), *state.confirmed_sources):
                if source.command.body.get("scope_id") == scope and source.device["account_subject"] == anchor.subject:
                    roots.add(self.owner.verifier.root(source.root, anchor.subject))
        return tuple(roots)

    def _scope_authority(self, scope: str) -> OwnerAuthorityHead:
        organization = self.session.scope_metadata(scope).get("owner_org")
        if not organization:
            raise E2eeError("organization_required")
        suggested = authority_head(self.session.call(
            "e2eeGetOwnerAuthority", organization_id=organization)["owner_authority"], organization)
        head = self.owner.account.authority(organization, suggested.read_capability)
        if head != suggested:
            raise E2eeError("owner_authority_changed")
        return head

    def recipient_set(self, scope: str, claims: tuple[_CurrentRootClaim, ...],
                      devices: tuple[Mapping[str, Any], ...], *,
                      authority: OwnerAuthorityHead | None = None) -> _CurrentRecipientSet:
        if not claims and not devices:
            return _CurrentRecipientSet(scope, (), ())
        head = authority or self._scope_authority(scope)
        contexts: dict[str, tuple[_CustodyProofs, _RootCheckpoint]] = {}
        roots = []
        for claim in claims:
            proofs, checkpoint = self._current_proofs(scope, claim.root, claim.anchor, authority=head)
            contexts[claim.root.subject] = (proofs, checkpoint)
            roots.append(_CurrentRootHead(checkpoint.identity,
                scope if claim.root.subject != self.session.subject else None))
        qualified = []
        for device in devices:
            context = contexts.get(device["account_subject"])
            if context is None:
                raise E2eeError("untrusted_recovery")
            proofs, checkpoint = context
            qualified.append(self._qualified_device(proofs, checkpoint, device))
        self.session._check_current()
        for proofs, checkpoint in contexts.values():
            self.session.trust._check_head(checkpoint.identity, scope)
        for device in qualified:
            self._require_nonnegative(device, scope)
        return _CurrentRecipientSet(scope, tuple(qualified), tuple(roots))

    def _current_proofs(self, scope: str | None, root: _RootIdentity,
                        anchor: _RootIdentity, *,
                        authority: OwnerAuthorityHead | None = None) -> tuple[_CustodyProofs, _RootCheckpoint]:
        if scope is not None:
            head = authority or self._scope_authority(scope)
            organization = head.organization_id
            snapshot = self.observe(organization, root.subject, head)
            proofs = _CustodyProofs(self.owner, snapshot, anchor, self._anchors(organization, anchor),
                proof_scope=scope)
            latest = snapshot.latest_root_transition
            checkpoint = (proofs.root(latest.evidence_digest) if isinstance(latest, OwnerCustodyEvidence)
                          else _RootCheckpoint(anchor, None))
        else:
            if root.subject != self.session.subject:
                raise E2eeError("recovery_scope_required")
            proofs = _CustodyProofs(self.owner, _HistoricalCustody(root.subject), anchor, (anchor,))
            checkpoint = _RootCheckpoint(anchor, None)
            recovery = self.session.call("e2eeGetRecovery")
            if self.owner.verifier.root(recovery, root.subject) != root:
                raise E2eeError("owner_custody_changed")
            self.session.trust.remember_recoveries([{**recovery, "account_subject": root.subject}])
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
            raise E2eeError("owner_custody_changed")
        return proofs, checkpoint

    def current_recovery(self, recovery: Mapping[str, Any], scope: str | None,
                         anchor: _RootIdentity) -> _CurrentRootHead:
        root = self.owner.verifier.root(recovery, anchor.subject)
        self._current_proofs(scope, root, anchor)
        return _CurrentRootHead(root, scope if root.subject != self.session.subject else None)

    def _paired_self_admission(self, proofs: _CustodyProofs, checkpoint: _RootCheckpoint,
                               device: Mapping[str, Any]) -> bool:
        if (device["account_subject"] != self.session.subject
                or device["device_id"] != self.session.device_id):
            return False
        if isinstance(proofs.snapshot, OwnerCustodyResponse) and (
            checkpoint.identity.generation != 1 or not proofs.snapshot.can_receive_organization_keys
        ):
            return False
        saved = self.session._device.get("paired_admission")
        if saved is None:
            return False
        from ._root_admission import PairedAdmissionProof

        paired = PairedAdmissionProof.parse(self.owner.crypto, self.session.trust.origin,
            self.session.subject, device, self.session._device["challenge"], saved)
        if paired.root != checkpoint.identity:
            return False
        if self.session.trust._enrollment_identity_consent(device, paired.command.body) is None:
            raise E2eeError("invalid_certificate")
        return True

    def _qualified_device(self, proofs: _CustodyProofs, checkpoint: _RootCheckpoint,
                          device: Mapping[str, Any]) -> dict[str, Any]:
        if device["account_subject"] != checkpoint.identity.subject:
            raise E2eeError("recovery_subject_mismatch")
        self._require_nonnegative(device, proofs.scope)
        if device.get("state") != "approved":
            raise E2eeError("device_approval_required")
        verified = (public_device(device) if self._paired_self_admission(proofs, checkpoint, device)
                    else proofs.qualify_at(device, checkpoint, allow_genesis=True))
        self._require_nonnegative(verified, proofs.scope)
        return verified

    def current_device(self, device: Mapping[str, Any], scope: str | None,
                       root: _RootIdentity) -> _CurrentDeviceQualification:
        if device["account_subject"] != root.subject:
            raise E2eeError("recovery_subject_mismatch")
        proofs, checkpoint = self._current_proofs(scope, root, root)
        material = proofs.material(device["device_id"])
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        return _CurrentDeviceQualification(root, self._qualified_device(proofs, checkpoint, material))


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
        proofs.qualify_at(device, checkpoint, allow_genesis=True)
        return proofs.original_admission(checkpoint)

    def qualify(self, organization: str, device: Mapping[str, Any], anchor: _RootIdentity,
                head: OwnerAuthorityHead, *, expected_root: _RootIdentity | None = None,
                known_roots: tuple[_RootIdentity, ...] = (), proof_scope: str | None = None,
                issuer_evidence: OwnerIssuerEvidence | None = None) -> VerifiedCurrentDevice:
        subject, identifier = device["account_subject"], device["device_id"]
        if anchor.subject != subject:
            raise E2eeError("recovery_subject_mismatch")
        snapshot = self.observe(organization, subject, head)
        proofs = _CustodyProofs(self.owner, snapshot, anchor,
            self._anchors(organization, anchor, known_roots, proof_scope=proof_scope),
            proof_scope=proof_scope, issuer_evidence=issuer_evidence)
        material = proofs.material(identifier)
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        latest = snapshot.latest_root_transition
        checkpoint = proofs.root(latest.evidence_digest) if isinstance(latest, OwnerCustodyEvidence) else _RootCheckpoint(anchor, None)
        if expected_root is not None and checkpoint.identity != expected_root:
            raise E2eeError("owner_custody_changed")
        self._require_nonnegative(material, proofs.scope)
        if material.get("state") != "approved":
            raise E2eeError("device_approval_required")
        verified = proofs.qualify_at(material, checkpoint, allow_genesis=True)
        self._require_nonnegative(verified, proofs.scope)
        self.session.trust._check_head(checkpoint.identity, proof_scope or organization)
        return VerifiedCurrentDevice(verified, checkpoint.identity, snapshot, proofs.original_admission(checkpoint))

    def qualify_self_recipients(self, organization: str, devices: list[dict[str, Any]],
                                anchor: _RootIdentity, head: OwnerAuthorityHead,
                                expected_root: _RootIdentity) -> list[dict[str, Any]]:
        if anchor.subject != self.session.subject or expected_root.subject != self.session.subject:
            raise E2eeError("recovery_subject_mismatch")
        return list(self.recipient_set(organization, (_CurrentRootClaim(expected_root, anchor),),
            tuple(devices), authority=head).devices)


    def original_issuer(self, organization: str, device: Mapping[str, Any], root: _RootIdentity,
                        admission: OriginalIssuerAdmission, *,
                        maximum_revision: int | None, known_roots: tuple[_RootIdentity, ...] = (),
                        issuer_evidence: OwnerIssuerEvidence | None = None, anchor: _RootIdentity | None = None,
                        purpose: CustodyPurpose = CustodyPurpose.IDENTITY,
                        proof_scope: str | None = None) -> None:
        if admission.root != root:
            raise E2eeError("owner_custody_evidence_mismatch")
        scope = organization if proof_scope is None else proof_scope
        anchor = anchor or self.independent_root(scope, device)
        if anchor.subject != root.subject or anchor.origin != root.origin:
            raise E2eeError("recovery_subject_mismatch")
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(device["account_subject"]), anchor,
            self._anchors(organization, anchor, known_roots, proof_scope=scope), original=admission,
            maximum_revision=maximum_revision,
            proof_scope=scope,
            issuer_evidence=issuer_evidence, purpose=purpose)
        checkpoint = proofs.root(admission.root_evidence_digest) if admission.root_evidence_digest is not None else _RootCheckpoint(root, None)
        if checkpoint.identity != root or (checkpoint.digest is None and root not in proofs.anchors):
            raise E2eeError("owner_custody_evidence_mismatch")
        material = proofs.material(device["device_id"])
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        proofs.qualify_at(material, checkpoint, allow_genesis=True)

    def verify_root_identity(self, organization: str, proposed: _RootIdentity, anchor: _RootIdentity,
                             admission: OriginalIssuerAdmission, *, maximum_revision: int | None,
                             known_roots: tuple[_RootIdentity, ...] = (),
                             issuer_evidence: OwnerIssuerEvidence | None = None,
                             proof_scope: str | None = None) -> None:
        anchors = self._anchors(organization, anchor, known_roots, proof_scope=proof_scope)
        if proposed in anchors:
            return
        if admission.root != proposed or admission.root_evidence_digest is None:
            raise E2eeError("owner_root_requalification_required")
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(proposed.subject), anchor, anchors,
            original=admission, maximum_revision=maximum_revision,
            proof_scope=organization if proof_scope is None else proof_scope,
            issuer_evidence=issuer_evidence)
        if proofs.root(admission.root_evidence_digest).identity != proposed:
            raise E2eeError("owner_custody_evidence_mismatch")

    def historical_organization_admission(self, organization: str, command: SignedEvidence,
                                          approver: Mapping[str, Any], anchor: _RootIdentity) -> OrganizationAdmission:
        admission = OrganizationAdmission.parse(self.owner.crypto, self.session.trust.origin, command, approver)
        if (admission.organization != organization or admission.approver_root.subject != anchor.subject
                or admission.approver_root.origin != anchor.origin):
            raise E2eeError("participant_scope_mismatch")
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(anchor.subject), anchor,
            self._anchors(organization, anchor), proof_scope=organization)
        fact = proofs.match("envelopes_save", command, admission.target())
        issuer = proofs.accepted_issuer(fact, command, admission.approver_root)
        if issuer != public_device(approver):
            raise E2eeError("device_key_changed")
        return admission


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
                         root: _RootIdentity, *, issuer_evidence: OwnerIssuerEvidence | None = None,
                         independent: _RootIdentity | None = None) -> VerifiedHistoricalEvent:
        if root.subject != self.session.subject:
            raise E2eeError("account_mismatch")
        anchor = independent or self.independent_root("", self.session.public)
        proofs = _CustodyProofs(self.owner, _HistoricalCustody(self.session.subject), anchor,
            self._anchors("", anchor), issuer_evidence=issuer_evidence)
        fact = proofs.match(operation, command, target)
        issuer = proofs.accepted_issuer(fact, command, root)
        command.verify(self.owner.crypto, issuer["signing_public_key"], operation)
        return VerifiedHistoricalEvent(fact, frozenset(proofs.authenticated_roots))

    def approval(self, organization: str, command: SignedEvidence, target: Mapping[str, Any], head: OwnerAuthorityHead) -> None:
        snapshot = self.observe(organization, self.session.subject, head)
        identity = {"account_subject": self.session.subject, "device_id": target["device_id"]}
        self._require_nonnegative(identity)
        anchor = self.independent_root(organization, self.session.public)
        proofs = _CustodyProofs(self.owner, snapshot, anchor, self._anchors(organization, anchor))
        fact = proofs.match("device_approve", command, {name: target[name] for name in (
            "device_id", "encryption_public_key", "signing_public_key", "challenge",
        )})
        root = self.owner.verifier.root(command.body["recovery_root"], self.session.subject)
        proofs.accepted_issuer(fact, command, root)
        self._require_nonnegative(identity)
