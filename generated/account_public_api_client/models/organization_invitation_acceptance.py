from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OrganizationInvitationAcceptance")


@_attrs_define
class OrganizationInvitationAcceptance:
    """
    Attributes:
        organization_id (str):
    """

    organization_id: str

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organizationId": organization_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organizationId")

        organization_invitation_acceptance = cls(
            organization_id=organization_id,
        )

        return organization_invitation_acceptance
