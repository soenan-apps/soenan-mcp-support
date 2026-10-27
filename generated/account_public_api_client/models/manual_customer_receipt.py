from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.manual_customer_allocation import ManualCustomerAllocation
    from ..models.manual_customer_refund import ManualCustomerRefund


T = TypeVar("T", bound="ManualCustomerReceipt")


@_attrs_define
class ManualCustomerReceipt:
    """
    Attributes:
        id (UUID):
        received_on (datetime.date):
        currency (str):
        amount_minor (str): Exact signed integer in the currency's smallest unit; never a JSON floating-point number.
        refunded_minor (str): Exact signed integer in the currency's smallest unit; never a JSON floating-point number.
        reversed_ (bool):
        allocations (list[ManualCustomerAllocation]):
        refunds (list[ManualCustomerRefund]):
    """

    id: UUID
    received_on: datetime.date
    currency: str
    amount_minor: str
    refunded_minor: str
    reversed_: bool
    allocations: list[ManualCustomerAllocation]
    refunds: list[ManualCustomerRefund]

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        received_on = self.received_on.isoformat()

        currency = self.currency

        amount_minor = self.amount_minor

        refunded_minor = self.refunded_minor

        reversed_ = self.reversed_

        allocations = []
        for allocations_item_data in self.allocations:
            allocations_item = allocations_item_data.to_dict()
            allocations.append(allocations_item)

        refunds = []
        for refunds_item_data in self.refunds:
            refunds_item = refunds_item_data.to_dict()
            refunds.append(refunds_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "receivedOn": received_on,
                "currency": currency,
                "amountMinor": amount_minor,
                "refundedMinor": refunded_minor,
                "reversed": reversed_,
                "allocations": allocations,
                "refunds": refunds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.manual_customer_allocation import ManualCustomerAllocation
        from ..models.manual_customer_refund import ManualCustomerRefund

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        received_on = isoparse(d.pop("receivedOn")).date()

        currency = d.pop("currency")

        amount_minor = d.pop("amountMinor")

        refunded_minor = d.pop("refundedMinor")

        reversed_ = d.pop("reversed")

        allocations = []
        _allocations = d.pop("allocations")
        for allocations_item_data in _allocations:
            allocations_item = ManualCustomerAllocation.from_dict(allocations_item_data)

            allocations.append(allocations_item)

        refunds = []
        _refunds = d.pop("refunds")
        for refunds_item_data in _refunds:
            refunds_item = ManualCustomerRefund.from_dict(refunds_item_data)

            refunds.append(refunds_item)

        manual_customer_receipt = cls(
            id=id,
            received_on=received_on,
            currency=currency,
            amount_minor=amount_minor,
            refunded_minor=refunded_minor,
            reversed_=reversed_,
            allocations=allocations,
            refunds=refunds,
        )

        return manual_customer_receipt
