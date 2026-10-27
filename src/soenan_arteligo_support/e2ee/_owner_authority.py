from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from arteligo_public_api_client.models.owner_authority_response import OwnerAuthorityResponse
from arteligo_public_api_client.models.owner_custody_evidence import OwnerCustodyEvidence
from arteligo_public_api_client.models.owner_custody_response import OwnerCustodyResponse
from arteligo_public_api_client.models.owner_transfer_decision import OwnerTransferDecision

from ._crypto import E2eeError
from ._owner_protocol import OwnerAuthorityHead, OwnerHandoffGate, authority_head, bytes32
from ._owner_projection import CertificateProjectionReference, CertificateSignatureProjection

if TYPE_CHECKING:
    from ._session import DeviceSession
    from ._key_operation_proof import OperationProofContext


@dataclass(frozen=True)
class OwnerSourceSelection:
    operation_id: str
    successor_binding_digest: str
    source_manifest_id: str
    source_manifest_digest: str

    @classmethod
    def parse(cls, value: Any) -> OwnerSourceSelection:
        if (not isinstance(value, dict)
                or set(value) != {"operation_id", "successor_binding_digest", "source_manifest_id", "source_manifest_digest"}
                or any(not isinstance(item, str) or not item for item in value.values())):
            raise E2eeError("invalid_owner_authority")
        bytes32(value["successor_binding_digest"])
        bytes32(value["source_manifest_digest"])
        return cls(**value)


@dataclass(frozen=True)
class SelectedOwnerHead:
    head: OwnerAuthorityHead
    predecessor: OwnerAuthorityHead | None = None
    source_selection: OwnerSourceSelection | None = None

    @classmethod
    def parse(cls, response: OwnerAuthorityResponse, organization: str) -> SelectedOwnerHead:
        value = response.to_dict()
        if "source_selection" not in value:
            raise E2eeError("invalid_owner_authority")
        head = authority_head(value["head"], organization)
        predecessor = (authority_head(value["predecessor_head"], organization)
                       if value.get("predecessor_head") is not None else None)
        selection = (OwnerSourceSelection.parse(value["source_selection"])
                     if value["source_selection"] is not None else None)
        return cls(head, predecessor, selection)

    def matches(self, head: OwnerAuthorityHead) -> bool:
        return all(getattr(self.head, field) == getattr(head, field) for field in (
            "organization_id", "ownership_revision", "owner_subject", "key_id", "key_epoch",
            "public_key", "binding_digest",
        ))


class OwnerAuthorityReads:
    """Resolve Arteligo's current selection and original evidence in a closed context."""

    def __init__(self, session: DeviceSession):
        self.session = session
        self._operation: OperationProofContext | None = None

    def _context(self, organization: str | None = None, subject: str | None = None) -> OperationProofContext:
        self.session._check_current()
        if self._operation is None:
            if self.session._root_read_set is not None or self.session._proof_read_set is not None:
                raise E2eeError("operation_proof_context_missing")
            self.session.load_owner_context(organization=organization, subject=subject)
        if self._operation is None:
            raise E2eeError("operation_proof_context_missing")
        return self._operation

    def capability(self, organization: str) -> str:
        return self._context(organization).authority(organization).head.read_capability

    def authority_snapshot(self, organization: str, capability: str) -> SelectedOwnerHead:
        snapshot = self._context(organization).authority(organization)
        if snapshot.head.read_capability != capability:
            raise E2eeError("owner_authority_changed")
        return snapshot

    def authority(self, organization: str, capability: str) -> OwnerAuthorityHead:
        return self.authority_snapshot(organization, capability).head

    def selected(self, organization: str, digest: str, *, capability: str | None = None) -> SelectedOwnerHead:
        context = self._context(organization)
        if capability is not None and context.authority(organization).head.read_capability != capability:
            raise E2eeError("owner_authority_changed")
        return context.selected(organization, digest)

    def gate(self, organization: str, gate_id: str) -> OwnerHandoffGate:
        return self._context(organization).gate(organization, gate_id)

    def decision(self, organization: str, operation_id: str, *, capability: str | None = None) -> OwnerTransferDecision:
        context = self._context(organization)
        if capability is not None and context.authority(organization).head.read_capability != capability:
            raise E2eeError("owner_authority_changed")
        decision = context.decision(organization, operation_id)
        if decision.operation_id != operation_id:
            raise E2eeError("owner_receipt_mismatch")
        return decision

    def witness(self, subject: str, digest: str) -> OwnerCustodyEvidence:
        bytes32(digest)
        evidence = self._context(subject=subject).witness(subject, digest)
        if evidence.account_subject != subject or evidence.evidence_digest != digest:
            raise E2eeError("owner_custody_evidence_mismatch")
        return evidence

    def projection(self, certificate: Mapping[str, Any]) -> CertificateSignatureProjection:
        reference = CertificateProjectionReference.parse(certificate)
        return self._context(subject=reference.witness_subject).projection(reference)

    def custody(self, organization: str, subject: str, capability: str,
                *, proof_scope: str | None = None) -> OwnerCustodyResponse:
        response = self._context(organization, subject).custody(organization, subject, proof_scope=proof_scope)
        if (response.organization_id != organization or response.account_subject != subject
                or response.head.read_capability != capability
                or not isinstance(response.revoked_device_ids, list)
                or any(not isinstance(identifier, str) or not identifier for identifier in response.revoked_device_ids)
                or len(response.revoked_device_ids) != len(set(response.revoked_device_ids))
                or type(response.custody_revision) is not int or response.custody_revision < 0
                or type(response.can_manage_organization_keys) is not bool
                or type(response.can_receive_organization_keys) is not bool):
            raise E2eeError("owner_invalidation_unconfirmed")
        bytes32(response.owner_bindings_digest)
        self.session.trust.observe_custody_revocations(subject, response.revoked_device_ids)
        return response
