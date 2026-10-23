from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="PasskeyUser")


@_attrs_define
class PasskeyUser:
    """
    Attributes:
        id (str):
        name (str):
        display_name (str):
    """

    id: str
    name: str
    display_name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "displayName": display_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        display_name = d.pop("displayName")

        passkey_user = cls(
            id=id,
            name=name,
            display_name=display_name,
        )

        return passkey_user
