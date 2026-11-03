from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_transfer_blocker import OwnerTransferBlocker
from ..models.owner_transfer_result_email_delivery_state import (
    OwnerTransferResultEmailDeliveryState,
)
from ..models.owner_transfer_result_state import OwnerTransferResultState

T = TypeVar("T", bound="OwnerTransferResult")


@_attrs_define
class OwnerTransferResult:
    """
    Attributes:
        state (OwnerTransferResultState):
        blocker (OwnerTransferBlocker):
        request_id (str):
        ownership_revision (int):
        email_delivery_state (OwnerTransferResultEmailDeliveryState):
    """

    state: OwnerTransferResultState
    blocker: OwnerTransferBlocker
    request_id: str
    ownership_revision: int
    email_delivery_state: OwnerTransferResultEmailDeliveryState

    def to_dict(self) -> dict[str, Any]:
        state = self.state.value

        blocker = self.blocker.value

        request_id = self.request_id

        ownership_revision = self.ownership_revision

        email_delivery_state = self.email_delivery_state.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "state": state,
                "blocker": blocker,
                "requestId": request_id,
                "ownershipRevision": ownership_revision,
                "emailDeliveryState": email_delivery_state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        state = OwnerTransferResultState(d.pop("state"))

        blocker = OwnerTransferBlocker(d.pop("blocker"))

        request_id = d.pop("requestId")

        ownership_revision = d.pop("ownershipRevision")

        email_delivery_state = OwnerTransferResultEmailDeliveryState(
            d.pop("emailDeliveryState")
        )

        owner_transfer_result = cls(
            state=state,
            blocker=blocker,
            request_id=request_id,
            ownership_revision=ownership_revision,
            email_delivery_state=email_delivery_state,
        )

        return owner_transfer_result
