from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_management_session_kind import CommerceManagementSessionKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="CommerceManagementSession")


@_attrs_define
class CommerceManagementSession:
    """
    Attributes:
        kind (CommerceManagementSessionKind):
        url (str | Unset):
    """

    kind: CommerceManagementSessionKind
    url: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        url = self.url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
            }
        )
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = CommerceManagementSessionKind(d.pop("kind"))

        url = d.pop("url", UNSET)

        commerce_management_session = cls(
            kind=kind,
            url=url,
        )

        return commerce_management_session
