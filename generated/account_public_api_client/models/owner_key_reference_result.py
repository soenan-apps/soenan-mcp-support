from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_dependency_outcome import OwnerKeyDependencyOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_authority_response import OwnerAuthorityResponse
    from ..models.owner_certificate_signature_projection import (
        OwnerCertificateSignatureProjection,
    )
    from ..models.owner_custody_evidence import OwnerCustodyEvidence
    from ..models.owner_key_reference import OwnerKeyReference
    from ..models.owner_key_root_receipt import OwnerKeyRootReceipt
    from ..models.owner_transfer_decision import OwnerTransferDecision


T = TypeVar("T", bound="OwnerKeyReferenceResult")


@_attrs_define
class OwnerKeyReferenceResult:
    """
    Attributes:
        reference (OwnerKeyReference):
        outcome (OwnerKeyDependencyOutcome):
        evidence (OwnerCustodyEvidence | Unset):
        selected_binding (OwnerAuthorityResponse | Unset):
        certificate_projection (OwnerCertificateSignatureProjection | Unset):
        custody_receipt (OwnerKeyRootReceipt | Unset):
        transfer_decision (OwnerTransferDecision | Unset): The exact durable ownership decision. Binding, candidate-
            offer, source-manifest, and preparation digests use the full signed-command commitment described by
            OwnerAuthorityHead.binding_digest, with their respective operation name. History-manifest digests hash canonical
            JSON.
    """

    reference: OwnerKeyReference
    outcome: OwnerKeyDependencyOutcome
    evidence: OwnerCustodyEvidence | Unset = UNSET
    selected_binding: OwnerAuthorityResponse | Unset = UNSET
    certificate_projection: OwnerCertificateSignatureProjection | Unset = UNSET
    custody_receipt: OwnerKeyRootReceipt | Unset = UNSET
    transfer_decision: OwnerTransferDecision | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        reference = self.reference.to_dict()

        outcome = self.outcome.value

        evidence: dict[str, Any] | Unset = UNSET
        if not isinstance(self.evidence, Unset):
            evidence = self.evidence.to_dict()

        selected_binding: dict[str, Any] | Unset = UNSET
        if not isinstance(self.selected_binding, Unset):
            selected_binding = self.selected_binding.to_dict()

        certificate_projection: dict[str, Any] | Unset = UNSET
        if not isinstance(self.certificate_projection, Unset):
            certificate_projection = self.certificate_projection.to_dict()

        custody_receipt: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custody_receipt, Unset):
            custody_receipt = self.custody_receipt.to_dict()

        transfer_decision: dict[str, Any] | Unset = UNSET
        if not isinstance(self.transfer_decision, Unset):
            transfer_decision = self.transfer_decision.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "reference": reference,
                "outcome": outcome,
            }
        )
        if evidence is not UNSET:
            field_dict["evidence"] = evidence
        if selected_binding is not UNSET:
            field_dict["selected_binding"] = selected_binding
        if certificate_projection is not UNSET:
            field_dict["certificate_projection"] = certificate_projection
        if custody_receipt is not UNSET:
            field_dict["custody_receipt"] = custody_receipt
        if transfer_decision is not UNSET:
            field_dict["transfer_decision"] = transfer_decision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_authority_response import OwnerAuthorityResponse
        from ..models.owner_certificate_signature_projection import (
            OwnerCertificateSignatureProjection,
        )
        from ..models.owner_custody_evidence import OwnerCustodyEvidence
        from ..models.owner_key_reference import OwnerKeyReference
        from ..models.owner_key_root_receipt import OwnerKeyRootReceipt
        from ..models.owner_transfer_decision import OwnerTransferDecision

        d = dict(src_dict)
        reference = OwnerKeyReference.from_dict(d.pop("reference"))

        outcome = OwnerKeyDependencyOutcome(d.pop("outcome"))

        _evidence = d.pop("evidence", UNSET)
        evidence: OwnerCustodyEvidence | Unset
        if isinstance(_evidence, Unset):
            evidence = UNSET
        else:
            evidence = OwnerCustodyEvidence.from_dict(_evidence)

        _selected_binding = d.pop("selected_binding", UNSET)
        selected_binding: OwnerAuthorityResponse | Unset
        if isinstance(_selected_binding, Unset):
            selected_binding = UNSET
        else:
            selected_binding = OwnerAuthorityResponse.from_dict(_selected_binding)

        _certificate_projection = d.pop("certificate_projection", UNSET)
        certificate_projection: OwnerCertificateSignatureProjection | Unset
        if isinstance(_certificate_projection, Unset):
            certificate_projection = UNSET
        else:
            certificate_projection = OwnerCertificateSignatureProjection.from_dict(
                _certificate_projection
            )

        _custody_receipt = d.pop("custody_receipt", UNSET)
        custody_receipt: OwnerKeyRootReceipt | Unset
        if isinstance(_custody_receipt, Unset):
            custody_receipt = UNSET
        else:
            custody_receipt = OwnerKeyRootReceipt.from_dict(_custody_receipt)

        _transfer_decision = d.pop("transfer_decision", UNSET)
        transfer_decision: OwnerTransferDecision | Unset
        if isinstance(_transfer_decision, Unset):
            transfer_decision = UNSET
        else:
            transfer_decision = OwnerTransferDecision.from_dict(_transfer_decision)

        owner_key_reference_result = cls(
            reference=reference,
            outcome=outcome,
            evidence=evidence,
            selected_binding=selected_binding,
            certificate_projection=certificate_projection,
            custody_receipt=custody_receipt,
            transfer_decision=transfer_decision,
        )

        return owner_key_reference_result
