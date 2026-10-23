from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse
from typing_extensions import Self

from ..models.manual_customer_invoice_status import ManualCustomerInvoiceStatus

if TYPE_CHECKING:
    from ..models.manual_external_reference import ManualExternalReference
    from ..models.manual_invoice_contract import ManualInvoiceContract


T = TypeVar("T", bound="ManualCustomerInvoice")


@_attrs_define
class ManualCustomerInvoice:
    """
    Attributes:
        id (UUID):
        revision (int):
        reference (ManualExternalReference):
        issued_on (datetime.date):
        due_on (datetime.date):
        currency (str):
        total_minor (str): Exact signed integer in the currency's smallest unit; never a JSON floating-point number.
        allocated_minor (str): Exact signed integer in the currency's smallest unit; never a JSON floating-point number.
        remaining_minor (str): Exact signed integer in the currency's smallest unit; never a JSON floating-point number.
        status (ManualCustomerInvoiceStatus):
        contracts (list[ManualInvoiceContract]):
    """

    id: UUID
    revision: int
    reference: ManualExternalReference
    issued_on: datetime.date
    due_on: datetime.date
    currency: str
    total_minor: str
    allocated_minor: str
    remaining_minor: str
    status: ManualCustomerInvoiceStatus
    contracts: list[ManualInvoiceContract]

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        revision = self.revision

        reference = self.reference.to_dict()

        issued_on = self.issued_on.isoformat()

        due_on = self.due_on.isoformat()

        currency = self.currency

        total_minor = self.total_minor

        allocated_minor = self.allocated_minor

        remaining_minor = self.remaining_minor

        status = self.status.value

        contracts = []
        for contracts_item_data in self.contracts:
            contracts_item = contracts_item_data.to_dict()
            contracts.append(contracts_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "revision": revision,
                "reference": reference,
                "issuedOn": issued_on,
                "dueOn": due_on,
                "currency": currency,
                "totalMinor": total_minor,
                "allocatedMinor": allocated_minor,
                "remainingMinor": remaining_minor,
                "status": status,
                "contracts": contracts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.manual_external_reference import ManualExternalReference
        from ..models.manual_invoice_contract import ManualInvoiceContract

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        revision = d.pop("revision")

        reference = ManualExternalReference.from_dict(d.pop("reference"))

        issued_on = isoparse(d.pop("issuedOn")).date()

        due_on = isoparse(d.pop("dueOn")).date()

        currency = d.pop("currency")

        total_minor = d.pop("totalMinor")

        allocated_minor = d.pop("allocatedMinor")

        remaining_minor = d.pop("remainingMinor")

        status = ManualCustomerInvoiceStatus(d.pop("status"))

        contracts = []
        _contracts = d.pop("contracts")
        for contracts_item_data in _contracts:
            contracts_item = ManualInvoiceContract.from_dict(contracts_item_data)

            contracts.append(contracts_item)

        manual_customer_invoice = cls(
            id=id,
            revision=revision,
            reference=reference,
            issued_on=issued_on,
            due_on=due_on,
            currency=currency,
            total_minor=total_minor,
            allocated_minor=allocated_minor,
            remaining_minor=remaining_minor,
            status=status,
            contracts=contracts,
        )

        return manual_customer_invoice
