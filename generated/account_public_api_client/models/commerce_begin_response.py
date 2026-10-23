from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.commerce_begin_response_outcome import CommerceBeginResponseOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.commerce_purchase_attempt import CommercePurchaseAttempt


T = TypeVar("T", bound="CommerceBeginResponse")


@_attrs_define
class CommerceBeginResponse:
    """
    Attributes:
        outcome (CommerceBeginResponseOutcome):
        attempt (CommercePurchaseAttempt | Unset):
        attempt_id (UUID | Unset):
        purchase_id (UUID | Unset):
    """

    outcome: CommerceBeginResponseOutcome
    attempt: CommercePurchaseAttempt | Unset = UNSET
    attempt_id: UUID | Unset = UNSET
    purchase_id: UUID | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        outcome = self.outcome.value

        attempt: dict[str, Any] | Unset = UNSET
        if not isinstance(self.attempt, Unset):
            attempt = self.attempt.to_dict()

        attempt_id: str | Unset = UNSET
        if not isinstance(self.attempt_id, Unset):
            attempt_id = str(self.attempt_id)

        purchase_id: str | Unset = UNSET
        if not isinstance(self.purchase_id, Unset):
            purchase_id = str(self.purchase_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "outcome": outcome,
            }
        )
        if attempt is not UNSET:
            field_dict["attempt"] = attempt
        if attempt_id is not UNSET:
            field_dict["attemptId"] = attempt_id
        if purchase_id is not UNSET:
            field_dict["purchaseId"] = purchase_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.commerce_purchase_attempt import CommercePurchaseAttempt

        d = dict(src_dict)
        outcome = CommerceBeginResponseOutcome(d.pop("outcome"))

        _attempt = d.pop("attempt", UNSET)
        attempt: CommercePurchaseAttempt | Unset
        if isinstance(_attempt, Unset):
            attempt = UNSET
        else:
            attempt = CommercePurchaseAttempt.from_dict(_attempt)

        _attempt_id = d.pop("attemptId", UNSET)
        attempt_id: UUID | Unset
        if isinstance(_attempt_id, Unset):
            attempt_id = UNSET
        else:
            attempt_id = UUID(_attempt_id)

        _purchase_id = d.pop("purchaseId", UNSET)
        purchase_id: UUID | Unset
        if isinstance(_purchase_id, Unset):
            purchase_id = UNSET
        else:
            purchase_id = UUID(_purchase_id)

        commerce_begin_response = cls(
            outcome=outcome,
            attempt=attempt,
            attempt_id=attempt_id,
            purchase_id=purchase_id,
        )

        return commerce_begin_response
