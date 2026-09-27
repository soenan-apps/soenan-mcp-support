from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ProductSessionOrganization")


@_attrs_define
class ProductSessionOrganization:
    """
    Attributes:
        id (str):
        display_name (str):
    """

    id: str
    display_name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "displayName": display_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("displayName")

        product_session_organization = cls(
            id=id,
            display_name=display_name,
        )

        return product_session_organization
