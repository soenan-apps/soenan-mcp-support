from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.owner_transfer_decision import OwnerTransferDecision


T = TypeVar("T", bound="OwnerTransferDecisionResponse")


@_attrs_define
class OwnerTransferDecisionResponse:
    """
    Attributes:
        challenge (str):
        decision (OwnerTransferDecision): The exact durable ownership decision. Binding, candidate-offer, source-
            manifest, and preparation digests use the full signed-command commitment described by
            OwnerAuthorityHead.binding_digest, with their respective operation name. History-manifest digests hash canonical
            JSON.
    """

    challenge: str
    decision: OwnerTransferDecision

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        decision = self.decision.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "decision": decision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_transfer_decision import OwnerTransferDecision

        d = dict(src_dict)
        challenge = d.pop("challenge")

        decision = OwnerTransferDecision.from_dict(d.pop("decision"))

        owner_transfer_decision_response = cls(
            challenge=challenge,
            decision=decision,
        )

        return owner_transfer_decision_response
