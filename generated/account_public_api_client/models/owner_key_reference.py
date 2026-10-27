from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_reference_kind import OwnerKeyReferenceKind

T = TypeVar("T", bound="OwnerKeyReference")


@_attrs_define
class OwnerKeyReference:
    """
    Attributes:
        kind (OwnerKeyReferenceKind):
        account_subject (str):
        organization_id (str):
        digest (str):
        origin_reference (str):
    """

    kind: OwnerKeyReferenceKind
    account_subject: str
    organization_id: str
    digest: str
    origin_reference: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        account_subject = self.account_subject

        organization_id = self.organization_id

        digest = self.digest

        origin_reference = self.origin_reference

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "account_subject": account_subject,
                "organization_id": organization_id,
                "digest": digest,
                "origin_reference": origin_reference,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = OwnerKeyReferenceKind(d.pop("kind"))

        account_subject = d.pop("account_subject")

        organization_id = d.pop("organization_id")

        digest = d.pop("digest")

        origin_reference = d.pop("origin_reference")

        owner_key_reference = cls(
            kind=kind,
            account_subject=account_subject,
            organization_id=organization_id,
            digest=digest,
            origin_reference=origin_reference,
        )

        return owner_key_reference
