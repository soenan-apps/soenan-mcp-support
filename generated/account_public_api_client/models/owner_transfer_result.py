from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

from ..models.owner_transfer_result_state import OwnerTransferResultState

T = TypeVar("T", bound="OwnerTransferResult")


@_attrs_define
class OwnerTransferResult:
    """
    Attributes:
        state (OwnerTransferResultState):
        request_id (UUID):
        owner_role_revision (int):
        change_id (UUID):
    """

    state: OwnerTransferResultState
    request_id: UUID
    owner_role_revision: int
    change_id: UUID

    def to_dict(self) -> dict[str, Any]:
        state = self.state.value

        request_id = str(self.request_id)

        owner_role_revision = self.owner_role_revision

        change_id = str(self.change_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "state": state,
                "requestId": request_id,
                "ownerRoleRevision": owner_role_revision,
                "changeId": change_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        state = OwnerTransferResultState(d.pop("state"))

        request_id = UUID(d.pop("requestId"))

        owner_role_revision = d.pop("ownerRoleRevision")

        change_id = UUID(d.pop("changeId"))

        owner_transfer_result = cls(
            state=state,
            request_id=request_id,
            owner_role_revision=owner_role_revision,
            change_id=change_id,
        )

        return owner_transfer_result
