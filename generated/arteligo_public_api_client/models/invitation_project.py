from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="InvitationProject")


@_attrs_define
class InvitationProject:
    """
    Attributes:
        id (str):
        title (str):
    """

    id: str
    title: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        invitation_project = cls(
            id=id,
            title=title,
        )

        return invitation_project
