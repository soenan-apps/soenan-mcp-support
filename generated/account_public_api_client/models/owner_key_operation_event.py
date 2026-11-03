from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_handoff_gate import OwnerHandoffGate
    from ..models.owner_key_gate_offer import OwnerKeyGateOffer
    from ..models.owner_key_gate_slot_result import OwnerKeyGateSlotResult
    from ..models.owner_key_operation_complete import OwnerKeyOperationComplete
    from ..models.owner_key_operation_prepared import OwnerKeyOperationPrepared
    from ..models.owner_key_operation_receipt import OwnerKeyOperationReceipt
    from ..models.owner_key_operation_rejection import OwnerKeyOperationRejection
    from ..models.owner_key_organization_state import OwnerKeyOrganizationState
    from ..models.owner_key_reference_result import OwnerKeyReferenceResult
    from ..models.owner_key_scope_authorization_result import (
        OwnerKeyScopeAuthorizationResult,
    )
    from ..models.owner_key_subject_state import OwnerKeySubjectState
    from ..models.owner_key_target_result import OwnerKeyTargetResult


T = TypeVar("T", bound="OwnerKeyOperationEvent")


@_attrs_define
class OwnerKeyOperationEvent:
    """Exactly one typed part accompanies sequence. SHA-256 covers uint64 big-endian byte length followed by the exact
    Account canonical JSON event bytes before complete. The complete part is excluded. Private frames carry these exact
    bytes as canonical_json.

        Attributes:
            sequence (int):
            prepared (OwnerKeyOperationPrepared | Unset):
            subject (OwnerKeySubjectState | Unset): Repeated frames for the same account_subject concatenate
                revoked_device_ids. All other fields agree. The enclosing complete marker closes the subject state.
            target (OwnerKeyTargetResult | Unset): Outcome is evaluated for the target purpose and scope. Project recipients
                use current sponsored access, independent of organization membership or seats. Historical references do not
                grant current eligibility.
            reference (OwnerKeyReferenceResult | Unset):
            organization (OwnerKeyOrganizationState | Unset): Multiple frames for one organization concatenate memberships,
                candidates and pending_transfers in sequence order. Other fields agree. The enclosing complete marker closes all
                organization sets.
            gate_offer (OwnerKeyGateOffer | Unset):
            receipt (OwnerKeyOperationReceipt | Unset):
            gate (OwnerHandoffGate | Unset):
            scope_authorization (OwnerKeyScopeAuthorizationResult | Unset):
            gate_slot_result (OwnerKeyGateSlotResult | Unset):
            rejection (OwnerKeyOperationRejection | Unset):
            complete (OwnerKeyOperationComplete | Unset):
    """

    sequence: int
    prepared: OwnerKeyOperationPrepared | Unset = UNSET
    subject: OwnerKeySubjectState | Unset = UNSET
    target: OwnerKeyTargetResult | Unset = UNSET
    reference: OwnerKeyReferenceResult | Unset = UNSET
    organization: OwnerKeyOrganizationState | Unset = UNSET
    gate_offer: OwnerKeyGateOffer | Unset = UNSET
    receipt: OwnerKeyOperationReceipt | Unset = UNSET
    gate: OwnerHandoffGate | Unset = UNSET
    scope_authorization: OwnerKeyScopeAuthorizationResult | Unset = UNSET
    gate_slot_result: OwnerKeyGateSlotResult | Unset = UNSET
    rejection: OwnerKeyOperationRejection | Unset = UNSET
    complete: OwnerKeyOperationComplete | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        sequence = self.sequence

        prepared: dict[str, Any] | Unset = UNSET
        if not isinstance(self.prepared, Unset):
            prepared = self.prepared.to_dict()

        subject: dict[str, Any] | Unset = UNSET
        if not isinstance(self.subject, Unset):
            subject = self.subject.to_dict()

        target: dict[str, Any] | Unset = UNSET
        if not isinstance(self.target, Unset):
            target = self.target.to_dict()

        reference: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reference, Unset):
            reference = self.reference.to_dict()

        organization: dict[str, Any] | Unset = UNSET
        if not isinstance(self.organization, Unset):
            organization = self.organization.to_dict()

        gate_offer: dict[str, Any] | Unset = UNSET
        if not isinstance(self.gate_offer, Unset):
            gate_offer = self.gate_offer.to_dict()

        receipt: dict[str, Any] | Unset = UNSET
        if not isinstance(self.receipt, Unset):
            receipt = self.receipt.to_dict()

        gate: dict[str, Any] | Unset = UNSET
        if not isinstance(self.gate, Unset):
            gate = self.gate.to_dict()

        scope_authorization: dict[str, Any] | Unset = UNSET
        if not isinstance(self.scope_authorization, Unset):
            scope_authorization = self.scope_authorization.to_dict()

        gate_slot_result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.gate_slot_result, Unset):
            gate_slot_result = self.gate_slot_result.to_dict()

        rejection: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rejection, Unset):
            rejection = self.rejection.to_dict()

        complete: dict[str, Any] | Unset = UNSET
        if not isinstance(self.complete, Unset):
            complete = self.complete.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sequence": sequence,
            }
        )
        if prepared is not UNSET:
            field_dict["prepared"] = prepared
        if subject is not UNSET:
            field_dict["subject"] = subject
        if target is not UNSET:
            field_dict["target"] = target
        if reference is not UNSET:
            field_dict["reference"] = reference
        if organization is not UNSET:
            field_dict["organization"] = organization
        if gate_offer is not UNSET:
            field_dict["gate_offer"] = gate_offer
        if receipt is not UNSET:
            field_dict["receipt"] = receipt
        if gate is not UNSET:
            field_dict["gate"] = gate
        if scope_authorization is not UNSET:
            field_dict["scope_authorization"] = scope_authorization
        if gate_slot_result is not UNSET:
            field_dict["gate_slot_result"] = gate_slot_result
        if rejection is not UNSET:
            field_dict["rejection"] = rejection
        if complete is not UNSET:
            field_dict["complete"] = complete

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_handoff_gate import OwnerHandoffGate
        from ..models.owner_key_gate_offer import OwnerKeyGateOffer
        from ..models.owner_key_gate_slot_result import OwnerKeyGateSlotResult
        from ..models.owner_key_operation_complete import OwnerKeyOperationComplete
        from ..models.owner_key_operation_prepared import OwnerKeyOperationPrepared
        from ..models.owner_key_operation_receipt import OwnerKeyOperationReceipt
        from ..models.owner_key_operation_rejection import OwnerKeyOperationRejection
        from ..models.owner_key_organization_state import OwnerKeyOrganizationState
        from ..models.owner_key_reference_result import OwnerKeyReferenceResult
        from ..models.owner_key_scope_authorization_result import (
            OwnerKeyScopeAuthorizationResult,
        )
        from ..models.owner_key_subject_state import OwnerKeySubjectState
        from ..models.owner_key_target_result import OwnerKeyTargetResult

        d = dict(src_dict)
        sequence = d.pop("sequence")

        _prepared = d.pop("prepared", UNSET)
        prepared: OwnerKeyOperationPrepared | Unset
        if isinstance(_prepared, Unset):
            prepared = UNSET
        else:
            prepared = OwnerKeyOperationPrepared.from_dict(_prepared)

        _subject = d.pop("subject", UNSET)
        subject: OwnerKeySubjectState | Unset
        if isinstance(_subject, Unset):
            subject = UNSET
        else:
            subject = OwnerKeySubjectState.from_dict(_subject)

        _target = d.pop("target", UNSET)
        target: OwnerKeyTargetResult | Unset
        if isinstance(_target, Unset):
            target = UNSET
        else:
            target = OwnerKeyTargetResult.from_dict(_target)

        _reference = d.pop("reference", UNSET)
        reference: OwnerKeyReferenceResult | Unset
        if isinstance(_reference, Unset):
            reference = UNSET
        else:
            reference = OwnerKeyReferenceResult.from_dict(_reference)

        _organization = d.pop("organization", UNSET)
        organization: OwnerKeyOrganizationState | Unset
        if isinstance(_organization, Unset):
            organization = UNSET
        else:
            organization = OwnerKeyOrganizationState.from_dict(_organization)

        _gate_offer = d.pop("gate_offer", UNSET)
        gate_offer: OwnerKeyGateOffer | Unset
        if isinstance(_gate_offer, Unset):
            gate_offer = UNSET
        else:
            gate_offer = OwnerKeyGateOffer.from_dict(_gate_offer)

        _receipt = d.pop("receipt", UNSET)
        receipt: OwnerKeyOperationReceipt | Unset
        if isinstance(_receipt, Unset):
            receipt = UNSET
        else:
            receipt = OwnerKeyOperationReceipt.from_dict(_receipt)

        _gate = d.pop("gate", UNSET)
        gate: OwnerHandoffGate | Unset
        if isinstance(_gate, Unset):
            gate = UNSET
        else:
            gate = OwnerHandoffGate.from_dict(_gate)

        _scope_authorization = d.pop("scope_authorization", UNSET)
        scope_authorization: OwnerKeyScopeAuthorizationResult | Unset
        if isinstance(_scope_authorization, Unset):
            scope_authorization = UNSET
        else:
            scope_authorization = OwnerKeyScopeAuthorizationResult.from_dict(
                _scope_authorization
            )

        _gate_slot_result = d.pop("gate_slot_result", UNSET)
        gate_slot_result: OwnerKeyGateSlotResult | Unset
        if isinstance(_gate_slot_result, Unset):
            gate_slot_result = UNSET
        else:
            gate_slot_result = OwnerKeyGateSlotResult.from_dict(_gate_slot_result)

        _rejection = d.pop("rejection", UNSET)
        rejection: OwnerKeyOperationRejection | Unset
        if isinstance(_rejection, Unset):
            rejection = UNSET
        else:
            rejection = OwnerKeyOperationRejection.from_dict(_rejection)

        _complete = d.pop("complete", UNSET)
        complete: OwnerKeyOperationComplete | Unset
        if isinstance(_complete, Unset):
            complete = UNSET
        else:
            complete = OwnerKeyOperationComplete.from_dict(_complete)

        owner_key_operation_event = cls(
            sequence=sequence,
            prepared=prepared,
            subject=subject,
            target=target,
            reference=reference,
            organization=organization,
            gate_offer=gate_offer,
            receipt=receipt,
            gate=gate,
            scope_authorization=scope_authorization,
            gate_slot_result=gate_slot_result,
            rejection=rejection,
            complete=complete,
        )

        return owner_key_operation_event
