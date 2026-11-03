from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="ManualCustomerAllocation")


@_attrs_define
class ManualCustomerAllocation:
    """
    Attributes:
        id (UUID):
        amount_minor (str): Exact signed integer in the currency's smallest unit; never a JSON floating-point number.
        reversed_ (bool):
    """

    id: UUID
    amount_minor: str
    reversed_: bool

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        amount_minor = self.amount_minor

        reversed_ = self.reversed_

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "amountMinor": amount_minor,
                "reversed": reversed_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        amount_minor = d.pop("amountMinor")

        reversed_ = d.pop("reversed")

        manual_customer_allocation = cls(
            id=id,
            amount_minor=amount_minor,
            reversed_=reversed_,
        )

        return manual_customer_allocation
