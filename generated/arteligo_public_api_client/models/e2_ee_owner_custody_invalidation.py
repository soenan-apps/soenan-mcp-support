from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeOwnerCustodyInvalidation")


@_attrs_define
class E2EeOwnerCustodyInvalidation:
    """
    Attributes:
        organization_id (str):
        request_id (str):
        custody_revision (int):
    """

    organization_id: str
    request_id: str
    custody_revision: int

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        request_id = self.request_id

        custody_revision = self.custody_revision

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "request_id": request_id,
                "custody_revision": custody_revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        request_id = d.pop("request_id")

        custody_revision = d.pop("custody_revision")

        e2_ee_owner_custody_invalidation = cls(
            organization_id=organization_id,
            request_id=request_id,
            custody_revision=custody_revision,
        )

        return e2_ee_owner_custody_invalidation
