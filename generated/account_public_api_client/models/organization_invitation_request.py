from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="OrganizationInvitationRequest")


@_attrs_define
class OrganizationInvitationRequest:
    """
    Attributes:
        organization_id (str):
        target_email (str):
        role_keys (list[str]):
    """

    organization_id: str
    target_email: str
    role_keys: list[str]

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        target_email = self.target_email

        role_keys = self.role_keys

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organizationId": organization_id,
                "targetEmail": target_email,
                "roleKeys": role_keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        organization_id = d.pop("organizationId")

        target_email = d.pop("targetEmail")

        role_keys = cast(list[str], d.pop("roleKeys"))

        organization_invitation_request = cls(
            organization_id=organization_id,
            target_email=target_email,
            role_keys=role_keys,
        )

        return organization_invitation_request
