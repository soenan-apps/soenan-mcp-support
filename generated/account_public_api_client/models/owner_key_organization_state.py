from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_dependency_outcome import OwnerKeyDependencyOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_authority_response import OwnerAuthorityResponse
    from ..models.owner_key_candidate import OwnerKeyCandidate
    from ..models.owner_key_membership import OwnerKeyMembership
    from ..models.owner_transfer_decision import OwnerTransferDecision


T = TypeVar("T", bound="OwnerKeyOrganizationState")


@_attrs_define
class OwnerKeyOrganizationState:
    """Multiple frames for one organization concatenate memberships, candidates and pending_transfers in sequence order.
    Other fields agree. The enclosing complete marker closes all organization sets.

        Attributes:
            organization_id (str):
            outcome (OwnerKeyDependencyOutcome):
            memberships (list[OwnerKeyMembership]):
            candidates (list[OwnerKeyCandidate]):
            pending_transfers (list[OwnerTransferDecision]):
            authority (OwnerAuthorityResponse | Unset):
    """

    organization_id: str
    outcome: OwnerKeyDependencyOutcome
    memberships: list[OwnerKeyMembership]
    candidates: list[OwnerKeyCandidate]
    pending_transfers: list[OwnerTransferDecision]
    authority: OwnerAuthorityResponse | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        outcome = self.outcome.value

        memberships = []
        for memberships_item_data in self.memberships:
            memberships_item = memberships_item_data.to_dict()
            memberships.append(memberships_item)

        candidates = []
        for candidates_item_data in self.candidates:
            candidates_item = candidates_item_data.to_dict()
            candidates.append(candidates_item)

        pending_transfers = []
        for pending_transfers_item_data in self.pending_transfers:
            pending_transfers_item = pending_transfers_item_data.to_dict()
            pending_transfers.append(pending_transfers_item)

        authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.authority, Unset):
            authority = self.authority.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "outcome": outcome,
                "memberships": memberships,
                "candidates": candidates,
                "pending_transfers": pending_transfers,
            }
        )
        if authority is not UNSET:
            field_dict["authority"] = authority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_authority_response import OwnerAuthorityResponse
        from ..models.owner_key_candidate import OwnerKeyCandidate
        from ..models.owner_key_membership import OwnerKeyMembership
        from ..models.owner_transfer_decision import OwnerTransferDecision

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        outcome = OwnerKeyDependencyOutcome(d.pop("outcome"))

        memberships = []
        _memberships = d.pop("memberships")
        for memberships_item_data in _memberships:
            memberships_item = OwnerKeyMembership.from_dict(memberships_item_data)

            memberships.append(memberships_item)

        candidates = []
        _candidates = d.pop("candidates")
        for candidates_item_data in _candidates:
            candidates_item = OwnerKeyCandidate.from_dict(candidates_item_data)

            candidates.append(candidates_item)

        pending_transfers = []
        _pending_transfers = d.pop("pending_transfers")
        for pending_transfers_item_data in _pending_transfers:
            pending_transfers_item = OwnerTransferDecision.from_dict(
                pending_transfers_item_data
            )

            pending_transfers.append(pending_transfers_item)

        _authority = d.pop("authority", UNSET)
        authority: OwnerAuthorityResponse | Unset
        if isinstance(_authority, Unset):
            authority = UNSET
        else:
            authority = OwnerAuthorityResponse.from_dict(_authority)

        owner_key_organization_state = cls(
            organization_id=organization_id,
            outcome=outcome,
            memberships=memberships,
            candidates=candidates,
            pending_transfers=pending_transfers,
            authority=authority,
        )

        return owner_key_organization_state
