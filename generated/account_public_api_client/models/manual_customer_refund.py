from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.manual_customer_refund_effect import ManualCustomerRefundEffect
from ..types import UNSET, Unset

T = TypeVar("T", bound="ManualCustomerRefund")


@_attrs_define
class ManualCustomerRefund:
    """
    Attributes:
        refunded_on (datetime.date):
        amount_minor (str): Exact signed integer in the currency's smallest unit; never a JSON floating-point number.
        effect (ManualCustomerRefundEffect):
        terminate_at (datetime.datetime | Unset):
    """

    refunded_on: datetime.date
    amount_minor: str
    effect: ManualCustomerRefundEffect
    terminate_at: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        refunded_on = self.refunded_on.isoformat()

        amount_minor = self.amount_minor

        effect = self.effect.value

        terminate_at: str | Unset = UNSET
        if not isinstance(self.terminate_at, Unset):
            terminate_at = self.terminate_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "refundedOn": refunded_on,
                "amountMinor": amount_minor,
                "effect": effect,
            }
        )
        if terminate_at is not UNSET:
            field_dict["terminateAt"] = terminate_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        refunded_on = isoparse(d.pop("refundedOn")).date()

        amount_minor = d.pop("amountMinor")

        effect = ManualCustomerRefundEffect(d.pop("effect"))

        _terminate_at = d.pop("terminateAt", UNSET)
        terminate_at: datetime.datetime | Unset
        if isinstance(_terminate_at, Unset):
            terminate_at = UNSET
        else:
            terminate_at = isoparse(_terminate_at)

        manual_customer_refund = cls(
            refunded_on=refunded_on,
            amount_minor=amount_minor,
            effect=effect,
            terminate_at=terminate_at,
        )

        return manual_customer_refund
