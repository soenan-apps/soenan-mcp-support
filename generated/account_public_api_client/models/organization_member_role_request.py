from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OrganizationMemberRoleRequest")


@_attrs_define
class OrganizationMemberRoleRequest:
    """
    Attributes:
        organization_id (str):
        target_subject (str):
        role_key (str):
    """

    organization_id: str
    target_subject: str
    role_key: str

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        target_subject = self.target_subject

        role_key = self.role_key

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organizationId": organization_id,
                "targetSubject": target_subject,
                "roleKey": role_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organizationId")

        target_subject = d.pop("targetSubject")

        role_key = d.pop("roleKey")

        organization_member_role_request = cls(
            organization_id=organization_id,
            target_subject=target_subject,
            role_key=role_key,
        )

        return organization_member_role_request
