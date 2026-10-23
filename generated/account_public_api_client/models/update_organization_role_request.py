from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.account_permission import AccountPermission

T = TypeVar("T", bound="UpdateOrganizationRoleRequest")


@_attrs_define
class UpdateOrganizationRoleRequest:
    """
    Attributes:
        display_name (str):
        permissions (list[AccountPermission]):
    """

    display_name: str
    permissions: list[AccountPermission]

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "displayName": display_name,
                "permissions": permissions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        display_name = d.pop("displayName")

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = AccountPermission(permissions_item_data)

            permissions.append(permissions_item)

        update_organization_role_request = cls(
            display_name=display_name,
            permissions=permissions,
        )

        return update_organization_role_request
