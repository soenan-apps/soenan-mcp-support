from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.current_membership_access_role import CurrentMembershipAccessRole

T = TypeVar("T", bound="CurrentMembership")


@_attrs_define
class CurrentMembership:
    """
    Attributes:
        membership_id (str):
        user_id (str):
        display_name (str):
        access_role (CurrentMembershipAccessRole):
    """

    membership_id: str
    user_id: str
    display_name: str
    access_role: CurrentMembershipAccessRole

    def to_dict(self) -> dict[str, Any]:
        membership_id = self.membership_id

        user_id = self.user_id

        display_name = self.display_name

        access_role = self.access_role.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "membershipId": membership_id,
                "userId": user_id,
                "displayName": display_name,
                "accessRole": access_role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        membership_id = d.pop("membershipId")

        user_id = d.pop("userId")

        display_name = d.pop("displayName")

        access_role = CurrentMembershipAccessRole(d.pop("accessRole"))

        current_membership = cls(
            membership_id=membership_id,
            user_id=user_id,
            display_name=display_name,
            access_role=access_role,
        )

        return current_membership
