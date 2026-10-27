from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.owner_key_gate_slot import OwnerKeyGateSlot


T = TypeVar("T", bound="OwnerKeyGateOffer")


@_attrs_define
class OwnerKeyGateOffer:
    """
    Attributes:
        operation_id (str):
        offer_id (str):
        slot (OwnerKeyGateSlot):
        gate_id (str):
        public_key (str):
        authorization_not_after_unix (int):
    """

    operation_id: str
    offer_id: str
    slot: OwnerKeyGateSlot
    gate_id: str
    public_key: str
    authorization_not_after_unix: int

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        offer_id = self.offer_id

        slot = self.slot.to_dict()

        gate_id = self.gate_id

        public_key = self.public_key

        authorization_not_after_unix = self.authorization_not_after_unix

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "offer_id": offer_id,
                "slot": slot,
                "gate_id": gate_id,
                "public_key": public_key,
                "authorization_not_after_unix": authorization_not_after_unix,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_key_gate_slot import OwnerKeyGateSlot

        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        offer_id = d.pop("offer_id")

        slot = OwnerKeyGateSlot.from_dict(d.pop("slot"))

        gate_id = d.pop("gate_id")

        public_key = d.pop("public_key")

        authorization_not_after_unix = d.pop("authorization_not_after_unix")

        owner_key_gate_offer = cls(
            operation_id=operation_id,
            offer_id=offer_id,
            slot=slot,
            gate_id=gate_id,
            public_key=public_key,
            authorization_not_after_unix=authorization_not_after_unix,
        )

        return owner_key_gate_offer
