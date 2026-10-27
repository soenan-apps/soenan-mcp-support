from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_dependency_outcome import OwnerKeyDependencyOutcome

if TYPE_CHECKING:
    from ..models.owner_key_gate_slot import OwnerKeyGateSlot


T = TypeVar("T", bound="OwnerKeyGateSlotResult")


@_attrs_define
class OwnerKeyGateSlotResult:
    """
    Attributes:
        slot (OwnerKeyGateSlot):
        outcome (OwnerKeyDependencyOutcome):
    """

    slot: OwnerKeyGateSlot
    outcome: OwnerKeyDependencyOutcome

    def to_dict(self) -> dict[str, Any]:
        slot = self.slot.to_dict()

        outcome = self.outcome.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "slot": slot,
                "outcome": outcome,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_key_gate_slot import OwnerKeyGateSlot

        d = dict(src_dict)
        slot = OwnerKeyGateSlot.from_dict(d.pop("slot"))

        outcome = OwnerKeyDependencyOutcome(d.pop("outcome"))

        owner_key_gate_slot_result = cls(
            slot=slot,
            outcome=outcome,
        )

        return owner_key_gate_slot_result
