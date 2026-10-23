from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.organization_close_simple_blocker_kind import (
    OrganizationCloseSimpleBlockerKind,
)

T = TypeVar("T", bound="OrganizationCloseSimpleBlocker")


@_attrs_define
class OrganizationCloseSimpleBlocker:
    """
    Attributes:
        kind (OrganizationCloseSimpleBlockerKind):
    """

    kind: OrganizationCloseSimpleBlockerKind

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = OrganizationCloseSimpleBlockerKind(d.pop("kind"))

        organization_close_simple_blocker = cls(
            kind=kind,
        )

        return organization_close_simple_blocker
