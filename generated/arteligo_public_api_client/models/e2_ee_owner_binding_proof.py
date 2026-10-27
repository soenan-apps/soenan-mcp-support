from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_owner_binding_proof_operation import E2EeOwnerBindingProofOperation
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_owner_committed_export_reference import (
        E2EeOwnerCommittedExportReference,
    )
    from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
    from ..models.e2_ee_owner_transfer_decision import E2EeOwnerTransferDecision
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerBindingProof")


@_attrs_define
class E2EeOwnerBindingProof:
    """Original binding and selected historical identity evidence. predecessor_authority is the immutable prior Account
    head before a key registration, including an unprovisioned head. Authenticate any provisioned predecessor
    recursively and match the signed registration's expected ownership revision and key epoch. Candidate offers have no
    predecessor.

        Attributes:
            owner_authority (E2EeOwnerAuthority):
            issuer_evidence (E2EeOwnerIssuerEvidence): Immutable public issuer proof graph for the selected binding.
                Includes only exact certificate references frozen by its signed issuer_admission and recursively by accepted
                Account witnesses, plus the corresponding public recovery checkpoints. This is not a current device directory
                and grants no content or key-distribution authority. Fetch on demand; retain references rather than embedding
                full certificate wrappers in private history.
            exported_sources (list[E2EeOwnerCommittedExportReference]): Exact committed exports made by this selected
                binding's immutable subject. Populated only for that subject's authenticated request; all other readers receive
                an empty array. Discovery only, not proof of absence or authorization for later exports.
            signed_binding (E2EeSignedCommand | Unset):
            operation (E2EeOwnerBindingProofOperation | Unset):
            device (E2EeDevice | Unset):
            recovery (E2EeRecoveryPublic | Unset):
            preparation (E2EeSignedCommand | Unset):
            decision (E2EeOwnerTransferDecision | Unset):
            predecessor_authority (E2EeOwnerAuthority | Unset):
    """

    owner_authority: E2EeOwnerAuthority
    issuer_evidence: E2EeOwnerIssuerEvidence
    exported_sources: list[E2EeOwnerCommittedExportReference]
    signed_binding: E2EeSignedCommand | Unset = UNSET
    operation: E2EeOwnerBindingProofOperation | Unset = UNSET
    device: E2EeDevice | Unset = UNSET
    recovery: E2EeRecoveryPublic | Unset = UNSET
    preparation: E2EeSignedCommand | Unset = UNSET
    decision: E2EeOwnerTransferDecision | Unset = UNSET
    predecessor_authority: E2EeOwnerAuthority | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        owner_authority = self.owner_authority.to_dict()

        issuer_evidence = self.issuer_evidence.to_dict()

        exported_sources = []
        for exported_sources_item_data in self.exported_sources:
            exported_sources_item = exported_sources_item_data.to_dict()
            exported_sources.append(exported_sources_item)

        signed_binding: dict[str, Any] | Unset = UNSET
        if not isinstance(self.signed_binding, Unset):
            signed_binding = self.signed_binding.to_dict()

        operation: str | Unset = UNSET
        if not isinstance(self.operation, Unset):
            operation = self.operation.value

        device: dict[str, Any] | Unset = UNSET
        if not isinstance(self.device, Unset):
            device = self.device.to_dict()

        recovery: dict[str, Any] | Unset = UNSET
        if not isinstance(self.recovery, Unset):
            recovery = self.recovery.to_dict()

        preparation: dict[str, Any] | Unset = UNSET
        if not isinstance(self.preparation, Unset):
            preparation = self.preparation.to_dict()

        decision: dict[str, Any] | Unset = UNSET
        if not isinstance(self.decision, Unset):
            decision = self.decision.to_dict()

        predecessor_authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.predecessor_authority, Unset):
            predecessor_authority = self.predecessor_authority.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "owner_authority": owner_authority,
                "issuer_evidence": issuer_evidence,
                "exported_sources": exported_sources,
            }
        )
        if signed_binding is not UNSET:
            field_dict["signed_binding"] = signed_binding
        if operation is not UNSET:
            field_dict["operation"] = operation
        if device is not UNSET:
            field_dict["device"] = device
        if recovery is not UNSET:
            field_dict["recovery"] = recovery
        if preparation is not UNSET:
            field_dict["preparation"] = preparation
        if decision is not UNSET:
            field_dict["decision"] = decision
        if predecessor_authority is not UNSET:
            field_dict["predecessor_authority"] = predecessor_authority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_owner_committed_export_reference import (
            E2EeOwnerCommittedExportReference,
        )
        from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
        from ..models.e2_ee_owner_transfer_decision import E2EeOwnerTransferDecision
        from ..models.e2_ee_recovery_public import E2EeRecoveryPublic
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        issuer_evidence = E2EeOwnerIssuerEvidence.from_dict(d.pop("issuer_evidence"))

        exported_sources = []
        _exported_sources = d.pop("exported_sources")
        for exported_sources_item_data in _exported_sources:
            exported_sources_item = E2EeOwnerCommittedExportReference.from_dict(
                exported_sources_item_data
            )

            exported_sources.append(exported_sources_item)

        _signed_binding = d.pop("signed_binding", UNSET)
        signed_binding: E2EeSignedCommand | Unset
        if isinstance(_signed_binding, Unset):
            signed_binding = UNSET
        else:
            signed_binding = E2EeSignedCommand.from_dict(_signed_binding)

        _operation = d.pop("operation", UNSET)
        operation: E2EeOwnerBindingProofOperation | Unset
        if isinstance(_operation, Unset):
            operation = UNSET
        else:
            operation = E2EeOwnerBindingProofOperation(_operation)

        _device = d.pop("device", UNSET)
        device: E2EeDevice | Unset
        if isinstance(_device, Unset):
            device = UNSET
        else:
            device = E2EeDevice.from_dict(_device)

        _recovery = d.pop("recovery", UNSET)
        recovery: E2EeRecoveryPublic | Unset
        if isinstance(_recovery, Unset):
            recovery = UNSET
        else:
            recovery = E2EeRecoveryPublic.from_dict(_recovery)

        _preparation = d.pop("preparation", UNSET)
        preparation: E2EeSignedCommand | Unset
        if isinstance(_preparation, Unset):
            preparation = UNSET
        else:
            preparation = E2EeSignedCommand.from_dict(_preparation)

        _decision = d.pop("decision", UNSET)
        decision: E2EeOwnerTransferDecision | Unset
        if isinstance(_decision, Unset):
            decision = UNSET
        else:
            decision = E2EeOwnerTransferDecision.from_dict(_decision)

        _predecessor_authority = d.pop("predecessor_authority", UNSET)
        predecessor_authority: E2EeOwnerAuthority | Unset
        if isinstance(_predecessor_authority, Unset):
            predecessor_authority = UNSET
        else:
            predecessor_authority = E2EeOwnerAuthority.from_dict(_predecessor_authority)

        e2_ee_owner_binding_proof = cls(
            owner_authority=owner_authority,
            issuer_evidence=issuer_evidence,
            exported_sources=exported_sources,
            signed_binding=signed_binding,
            operation=operation,
            device=device,
            recovery=recovery,
            preparation=preparation,
            decision=decision,
            predecessor_authority=predecessor_authority,
        )

        return e2_ee_owner_binding_proof
