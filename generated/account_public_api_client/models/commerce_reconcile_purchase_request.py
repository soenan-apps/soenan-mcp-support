from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="CommerceReconcilePurchaseRequest")


@_attrs_define
class CommerceReconcilePurchaseRequest:
    """
    Attributes:
        request_id (UUID):
    """

    request_id: UUID

    def to_dict(self) -> dict[str, Any]:
        request_id = str(self.request_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "requestId": request_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        request_id = UUID(d.pop("requestId"))

        commerce_reconcile_purchase_request = cls(
            request_id=request_id,
        )

        return commerce_reconcile_purchase_request
