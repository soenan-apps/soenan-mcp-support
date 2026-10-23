from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.manual_customer_invoice import ManualCustomerInvoice


T = TypeVar("T", bound="ManualInvoicePage")


@_attrs_define
class ManualInvoicePage:
    """
    Attributes:
        invoices (list[ManualCustomerInvoice]):
        next_offset (int | Unset):
    """

    invoices: list[ManualCustomerInvoice]
    next_offset: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        invoices = []
        for invoices_item_data in self.invoices:
            invoices_item = invoices_item_data.to_dict()
            invoices.append(invoices_item)

        next_offset = self.next_offset

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invoices": invoices,
            }
        )
        if next_offset is not UNSET:
            field_dict["nextOffset"] = next_offset

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.manual_customer_invoice import ManualCustomerInvoice

        d = dict(src_dict)
        invoices = []
        _invoices = d.pop("invoices")
        for invoices_item_data in _invoices:
            invoices_item = ManualCustomerInvoice.from_dict(invoices_item_data)

            invoices.append(invoices_item)

        next_offset = d.pop("nextOffset", UNSET)

        manual_invoice_page = cls(
            invoices=invoices,
            next_offset=next_offset,
        )

        return manual_invoice_page
