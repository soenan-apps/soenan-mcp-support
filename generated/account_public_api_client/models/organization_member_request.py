from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="OrganizationMemberRequest")


@_attrs_define
class OrganizationMemberRequest:
    """
    Attributes:
        organization_id (str):
        target_subject (str):
    """

    organization_id: str
    target_subject: str

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        target_subject = self.target_subject

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organizationId": organization_id,
                "targetSubject": target_subject,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        organization_id = d.pop("organizationId")

        target_subject = d.pop("targetSubject")

        organization_member_request = cls(
            organization_id=organization_id,
            target_subject=target_subject,
        )

        return organization_member_request
