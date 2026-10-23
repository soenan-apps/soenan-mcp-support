from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.account_permission import AccountPermission
from ..models.organization_role_detail_kind import OrganizationRoleDetailKind
from ..models.organization_role_detail_state import OrganizationRoleDetailState

T = TypeVar("T", bound="OrganizationRoleDetail")


@_attrs_define
class OrganizationRoleDetail:
    """
    Attributes:
        role_key (str):
        display_name (str):
        kind (OrganizationRoleDetailKind):
        state (OrganizationRoleDetailState):
        permissions (list[AccountPermission]):
    """

    role_key: str
    display_name: str
    kind: OrganizationRoleDetailKind
    state: OrganizationRoleDetailState
    permissions: list[AccountPermission]

    def to_dict(self) -> dict[str, Any]:
        role_key = self.role_key

        display_name = self.display_name

        kind = self.kind.value

        state = self.state.value

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "roleKey": role_key,
                "displayName": display_name,
                "kind": kind,
                "state": state,
                "permissions": permissions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        role_key = d.pop("roleKey")

        display_name = d.pop("displayName")

        kind = OrganizationRoleDetailKind(d.pop("kind"))

        state = OrganizationRoleDetailState(d.pop("state"))

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = AccountPermission(permissions_item_data)

            permissions.append(permissions_item)

        organization_role_detail = cls(
            role_key=role_key,
            display_name=display_name,
            kind=kind,
            state=state,
            permissions=permissions,
        )

        return organization_role_detail
