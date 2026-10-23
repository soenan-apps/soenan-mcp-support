from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.owner_handoff_gate import OwnerHandoffGate


T = TypeVar("T", bound="OwnerHandoffGateResponse")


@_attrs_define
class OwnerHandoffGateResponse:
    """
    Attributes:
        challenge (str):
        gate (OwnerHandoffGate):
    """

    challenge: str
    gate: OwnerHandoffGate

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        gate = self.gate.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "gate": gate,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_handoff_gate import OwnerHandoffGate

        d = dict(src_dict)
        challenge = d.pop("challenge")

        gate = OwnerHandoffGate.from_dict(d.pop("gate"))

        owner_handoff_gate_response = cls(
            challenge=challenge,
            gate=gate,
        )

        return owner_handoff_gate_response
