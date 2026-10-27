from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OwnerKeyMembership")


@_attrs_define
class OwnerKeyMembership:
    """
    Attributes:
        membership_id (str):
        organization_id (str):
        subject (str):
        revision (int):
        state (str):
        role (str):
    """

    membership_id: str
    organization_id: str
    subject: str
    revision: int
    state: str
    role: str

    def to_dict(self) -> dict[str, Any]:
        membership_id = self.membership_id

        organization_id = self.organization_id

        subject = self.subject

        revision = self.revision

        state = self.state

        role = self.role

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "membership_id": membership_id,
                "organization_id": organization_id,
                "subject": subject,
                "revision": revision,
                "state": state,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        membership_id = d.pop("membership_id")

        organization_id = d.pop("organization_id")

        subject = d.pop("subject")

        revision = d.pop("revision")

        state = d.pop("state")

        role = d.pop("role")

        owner_key_membership = cls(
            membership_id=membership_id,
            organization_id=organization_id,
            subject=subject,
            revision=revision,
            state=state,
            role=role,
        )

        return owner_key_membership
