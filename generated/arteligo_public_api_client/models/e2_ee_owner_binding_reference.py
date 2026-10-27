from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="E2EeOwnerBindingReference")


@_attrs_define
class E2EeOwnerBindingReference:
    """
    Attributes:
        organization_id (str):
        binding_digest (str):
    """

    organization_id: str
    binding_digest: str

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        binding_digest = self.binding_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "binding_digest": binding_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        binding_digest = d.pop("binding_digest")

        e2_ee_owner_binding_reference = cls(
            organization_id=organization_id,
            binding_digest=binding_digest,
        )

        return e2_ee_owner_binding_reference
