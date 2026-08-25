from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="MemberIdentity")


@_attrs_define
class MemberIdentity:
    """
    Attributes:
        membership_id (str):
        user_id (str):
        display_name (str):
    """

    membership_id: str
    user_id: str
    display_name: str

    def to_dict(self) -> dict[str, Any]:
        membership_id = self.membership_id

        user_id = self.user_id

        display_name = self.display_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "membershipId": membership_id,
                "userId": user_id,
                "displayName": display_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        membership_id = d.pop("membershipId")

        user_id = d.pop("userId")

        display_name = d.pop("displayName")

        member_identity = cls(
            membership_id=membership_id,
            user_id=user_id,
            display_name=display_name,
        )

        return member_identity
