from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_custody_target_purpose import OwnerKeyCustodyTargetPurpose

T = TypeVar("T", bound="OwnerKeyCustodyTarget")


@_attrs_define
class OwnerKeyCustodyTarget:
    """
    Attributes:
        account_subject (str):
        organization_id (str):
        scope_id (str):
        purpose (OwnerKeyCustodyTargetPurpose):
        origin_reference (str):
    """

    account_subject: str
    organization_id: str
    scope_id: str
    purpose: OwnerKeyCustodyTargetPurpose
    origin_reference: str

    def to_dict(self) -> dict[str, Any]:
        account_subject = self.account_subject

        organization_id = self.organization_id

        scope_id = self.scope_id

        purpose = self.purpose.value

        origin_reference = self.origin_reference

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "account_subject": account_subject,
                "organization_id": organization_id,
                "scope_id": scope_id,
                "purpose": purpose,
                "origin_reference": origin_reference,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        account_subject = d.pop("account_subject")

        organization_id = d.pop("organization_id")

        scope_id = d.pop("scope_id")

        purpose = OwnerKeyCustodyTargetPurpose(d.pop("purpose"))

        origin_reference = d.pop("origin_reference")

        owner_key_custody_target = cls(
            account_subject=account_subject,
            organization_id=organization_id,
            scope_id=scope_id,
            purpose=purpose,
            origin_reference=origin_reference,
        )

        return owner_key_custody_target
