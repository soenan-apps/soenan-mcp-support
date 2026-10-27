from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.manual_customer_invoice import ManualCustomerInvoice
    from ..models.manual_customer_receipt import ManualCustomerReceipt


T = TypeVar("T", bound="ManualInvoiceCustomerDetail")


@_attrs_define
class ManualInvoiceCustomerDetail:
    """
    Attributes:
        invoice (ManualCustomerInvoice):
        receipts (list[ManualCustomerReceipt]):
        next_receipt_offset (int | Unset):
    """

    invoice: ManualCustomerInvoice
    receipts: list[ManualCustomerReceipt]
    next_receipt_offset: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        invoice = self.invoice.to_dict()

        receipts = []
        for receipts_item_data in self.receipts:
            receipts_item = receipts_item_data.to_dict()
            receipts.append(receipts_item)

        next_receipt_offset = self.next_receipt_offset

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invoice": invoice,
                "receipts": receipts,
            }
        )
        if next_receipt_offset is not UNSET:
            field_dict["nextReceiptOffset"] = next_receipt_offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.manual_customer_invoice import ManualCustomerInvoice
        from ..models.manual_customer_receipt import ManualCustomerReceipt

        d = dict(src_dict)
        invoice = ManualCustomerInvoice.from_dict(d.pop("invoice"))

        receipts = []
        _receipts = d.pop("receipts")
        for receipts_item_data in _receipts:
            receipts_item = ManualCustomerReceipt.from_dict(receipts_item_data)

            receipts.append(receipts_item)

        next_receipt_offset = d.pop("nextReceiptOffset", UNSET)

        manual_invoice_customer_detail = cls(
            invoice=invoice,
            receipts=receipts,
            next_receipt_offset=next_receipt_offset,
        )

        return manual_invoice_customer_detail
