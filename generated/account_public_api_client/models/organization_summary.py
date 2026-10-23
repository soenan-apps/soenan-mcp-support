from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.account_permission import AccountPermission
from ..models.organization_summary_arteligo_access_state import (
    OrganizationSummaryArteligoAccessState,
)
from ..models.organization_summary_membership_state import (
    OrganizationSummaryMembershipState,
)
from ..models.organization_summary_organization_state import (
    OrganizationSummaryOrganizationState,
)

T = TypeVar("T", bound="OrganizationSummary")


@_attrs_define
class OrganizationSummary:
    """
    Attributes:
        organization_id (str):
        display_name (str):
        organization_state (OrganizationSummaryOrganizationState):
        membership_state (OrganizationSummaryMembershipState):
        permissions (list[AccountPermission]):
        arteligo_access_state (OrganizationSummaryArteligoAccessState):
    """

    organization_id: str
    display_name: str
    organization_state: OrganizationSummaryOrganizationState
    membership_state: OrganizationSummaryMembershipState
    permissions: list[AccountPermission]
    arteligo_access_state: OrganizationSummaryArteligoAccessState

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        display_name = self.display_name

        organization_state = self.organization_state.value

        membership_state = self.membership_state.value

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        arteligo_access_state = self.arteligo_access_state.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organizationId": organization_id,
                "displayName": display_name,
                "organizationState": organization_state,
                "membershipState": membership_state,
                "permissions": permissions,
                "arteligoAccessState": arteligo_access_state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        organization_id = d.pop("organizationId")

        display_name = d.pop("displayName")

        organization_state = OrganizationSummaryOrganizationState(
            d.pop("organizationState")
        )

        membership_state = OrganizationSummaryMembershipState(d.pop("membershipState"))

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = AccountPermission(permissions_item_data)

            permissions.append(permissions_item)

        arteligo_access_state = OrganizationSummaryArteligoAccessState(
            d.pop("arteligoAccessState")
        )

        organization_summary = cls(
            organization_id=organization_id,
            display_name=display_name,
            organization_state=organization_state,
            membership_state=membership_state,
            permissions=permissions,
            arteligo_access_state=arteligo_access_state,
        )

        return organization_summary
