from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ProductSessionUser")


@_attrs_define
class ProductSessionUser:
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("displayName")

        product_session_user = cls(
            id=id,
            display_name=display_name,
        )

        return product_session_user
