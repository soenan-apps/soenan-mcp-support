from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.owner_custody_root_identity import OwnerCustodyRootIdentity


T = TypeVar("T", bound="OwnerKeyGateSlot")


@_attrs_define
class OwnerKeyGateSlot:
    """
    Attributes:
        slot_id (str):
        organization_id (str):
        candidate_subject (str):
        candidate_id (str):
        proposed_candidate (bool):
        ownership_revision (int):
        source_key_epoch (int):
        expected_root (OwnerCustodyRootIdentity):
    """

    slot_id: str
    organization_id: str
    candidate_subject: str
    candidate_id: str
    proposed_candidate: bool
    ownership_revision: int
    source_key_epoch: int
    expected_root: OwnerCustodyRootIdentity

    def to_dict(self) -> dict[str, Any]:
        slot_id = self.slot_id

        organization_id = self.organization_id

        candidate_subject = self.candidate_subject

        candidate_id = self.candidate_id

        proposed_candidate = self.proposed_candidate

        ownership_revision = self.ownership_revision

        source_key_epoch = self.source_key_epoch

        expected_root = self.expected_root.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "slot_id": slot_id,
                "organization_id": organization_id,
                "candidate_subject": candidate_subject,
                "candidate_id": candidate_id,
                "proposed_candidate": proposed_candidate,
                "ownership_revision": ownership_revision,
                "source_key_epoch": source_key_epoch,
                "expected_root": expected_root,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_custody_root_identity import OwnerCustodyRootIdentity

        d = dict(src_dict)
        slot_id = d.pop("slot_id")

        organization_id = d.pop("organization_id")

        candidate_subject = d.pop("candidate_subject")

        candidate_id = d.pop("candidate_id")

        proposed_candidate = d.pop("proposed_candidate")

        ownership_revision = d.pop("ownership_revision")

        source_key_epoch = d.pop("source_key_epoch")

        expected_root = OwnerCustodyRootIdentity.from_dict(d.pop("expected_root"))

        owner_key_gate_slot = cls(
            slot_id=slot_id,
            organization_id=organization_id,
            candidate_subject=candidate_subject,
            candidate_id=candidate_id,
            proposed_candidate=proposed_candidate,
            ownership_revision=ownership_revision,
            source_key_epoch=source_key_epoch,
            expected_root=expected_root,
        )

        return owner_key_gate_slot
