from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.manual_invoice_contract_inactive_reason import (
    ManualInvoiceContractInactiveReason,
)
from ..models.manual_invoice_contract_outcome import ManualInvoiceContractOutcome
from ..models.manual_invoice_contract_validity import ManualInvoiceContractValidity
from ..types import UNSET, Unset

T = TypeVar("T", bound="ManualInvoiceContract")


@_attrs_define
class ManualInvoiceContract:
    """
    Attributes:
        contract_id (UUID):
        revision (int):
        offer_version_id (str):
        quantity (int):
        validity (ManualInvoiceContractValidity):
        outcome (ManualInvoiceContractOutcome):
        start_at (datetime.datetime | Unset):
        end_at (datetime.datetime | Unset):
        inactive_reason (ManualInvoiceContractInactiveReason | Unset):
    """

    contract_id: UUID
    revision: int
    offer_version_id: str
    quantity: int
    validity: ManualInvoiceContractValidity
    outcome: ManualInvoiceContractOutcome
    start_at: datetime.datetime | Unset = UNSET
    end_at: datetime.datetime | Unset = UNSET
    inactive_reason: ManualInvoiceContractInactiveReason | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        contract_id = str(self.contract_id)

        revision = self.revision

        offer_version_id = self.offer_version_id

        quantity = self.quantity

        validity = self.validity.value

        outcome = self.outcome.value

        start_at: str | Unset = UNSET
        if not isinstance(self.start_at, Unset):
            start_at = self.start_at.isoformat()

        end_at: str | Unset = UNSET
        if not isinstance(self.end_at, Unset):
            end_at = self.end_at.isoformat()

        inactive_reason: str | Unset = UNSET
        if not isinstance(self.inactive_reason, Unset):
            inactive_reason = self.inactive_reason.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "contractId": contract_id,
                "revision": revision,
                "offerVersionId": offer_version_id,
                "quantity": quantity,
                "validity": validity,
                "outcome": outcome,
            }
        )
        if start_at is not UNSET:
            field_dict["startAt"] = start_at
        if end_at is not UNSET:
            field_dict["endAt"] = end_at
        if inactive_reason is not UNSET:
            field_dict["inactiveReason"] = inactive_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        contract_id = UUID(d.pop("contractId"))

        revision = d.pop("revision")

        offer_version_id = d.pop("offerVersionId")

        quantity = d.pop("quantity")

        validity = ManualInvoiceContractValidity(d.pop("validity"))

        outcome = ManualInvoiceContractOutcome(d.pop("outcome"))

        _start_at = d.pop("startAt", UNSET)
        start_at: datetime.datetime | Unset
        if isinstance(_start_at, Unset):
            start_at = UNSET
        else:
            start_at = isoparse(_start_at)

        _end_at = d.pop("endAt", UNSET)
        end_at: datetime.datetime | Unset
        if isinstance(_end_at, Unset):
            end_at = UNSET
        else:
            end_at = isoparse(_end_at)

        _inactive_reason = d.pop("inactiveReason", UNSET)
        inactive_reason: ManualInvoiceContractInactiveReason | Unset
        if isinstance(_inactive_reason, Unset):
            inactive_reason = UNSET
        else:
            inactive_reason = ManualInvoiceContractInactiveReason(_inactive_reason)

        manual_invoice_contract = cls(
            contract_id=contract_id,
            revision=revision,
            offer_version_id=offer_version_id,
            quantity=quantity,
            validity=validity,
            outcome=outcome,
            start_at=start_at,
            end_at=end_at,
            inactive_reason=inactive_reason,
        )

        return manual_invoice_contract
