from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.account_permission import AccountPermission

T = TypeVar("T", bound="OrganizationRoleRequest")


@_attrs_define
class OrganizationRoleRequest:
    """
    Attributes:
        organization_id (str):
        role_key (str):
        display_name (str):
        permissions (list[AccountPermission]):
    """

    organization_id: str
    role_key: str
    display_name: str
    permissions: list[AccountPermission]

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        role_key = self.role_key

        display_name = self.display_name

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organizationId": organization_id,
                "roleKey": role_key,
                "displayName": display_name,
                "permissions": permissions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organizationId")

        role_key = d.pop("roleKey")

        display_name = d.pop("displayName")

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = AccountPermission(permissions_item_data)

            permissions.append(permissions_item)

        organization_role_request = cls(
            organization_id=organization_id,
            role_key=role_key,
            display_name=display_name,
            permissions=permissions,
        )

        return organization_role_request
