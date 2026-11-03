from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.account_permission import AccountPermission
from ..models.organization_member_detail_membership_state import (
    OrganizationMemberDetailMembershipState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationMemberDetail")


@_attrs_define
class OrganizationMemberDetail:
    """
    Attributes:
        account_subject (str):
        primary_email (str):
        membership_state (OrganizationMemberDetailMembershipState):
        role_keys (list[str]):
        permissions (list[AccountPermission]):
        display_name (str | Unset):
        arteligo_seat_assigned (bool | Unset):
    """

    account_subject: str
    primary_email: str
    membership_state: OrganizationMemberDetailMembershipState
    role_keys: list[str]
    permissions: list[AccountPermission]
    display_name: str | Unset = UNSET
    arteligo_seat_assigned: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        account_subject = self.account_subject

        primary_email = self.primary_email

        membership_state = self.membership_state.value

        role_keys = self.role_keys

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        display_name = self.display_name

        arteligo_seat_assigned = self.arteligo_seat_assigned

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "accountSubject": account_subject,
                "primaryEmail": primary_email,
                "membershipState": membership_state,
                "roleKeys": role_keys,
                "permissions": permissions,
            }
        )
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if arteligo_seat_assigned is not UNSET:
            field_dict["arteligoSeatAssigned"] = arteligo_seat_assigned

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        account_subject = d.pop("accountSubject")

        primary_email = d.pop("primaryEmail")

        membership_state = OrganizationMemberDetailMembershipState(
            d.pop("membershipState")
        )

        role_keys = cast(list[str], d.pop("roleKeys"))

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = AccountPermission(permissions_item_data)

            permissions.append(permissions_item)

        display_name = d.pop("displayName", UNSET)

        arteligo_seat_assigned = d.pop("arteligoSeatAssigned", UNSET)

        organization_member_detail = cls(
            account_subject=account_subject,
            primary_email=primary_email,
            membership_state=membership_state,
            role_keys=role_keys,
            permissions=permissions,
            display_name=display_name,
            arteligo_seat_assigned=arteligo_seat_assigned,
        )

        return organization_member_detail
