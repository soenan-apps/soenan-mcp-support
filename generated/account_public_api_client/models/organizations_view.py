from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.organization_summary import OrganizationSummary


T = TypeVar("T", bound="OrganizationsView")


@_attrs_define
class OrganizationsView:
    """
    Attributes:
        organizations (list[OrganizationSummary]):
    """

    organizations: list[OrganizationSummary]

    def to_dict(self) -> dict[str, Any]:
        organizations = []
        for organizations_item_data in self.organizations:
            organizations_item = organizations_item_data.to_dict()
            organizations.append(organizations_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organizations": organizations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.organization_summary import OrganizationSummary

        d = dict(src_dict)
        organizations = []
        _organizations = d.pop("organizations")
        for organizations_item_data in _organizations:
            organizations_item = OrganizationSummary.from_dict(organizations_item_data)

            organizations.append(organizations_item)

        organizations_view = cls(
            organizations=organizations,
        )

        return organizations_view
