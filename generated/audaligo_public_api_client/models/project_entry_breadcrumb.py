from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ProjectEntryBreadcrumb")


@_attrs_define
class ProjectEntryBreadcrumb:
    """
    Attributes:
        folder_id (str):
        name (str):
    """

    folder_id: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        folder_id = self.folder_id

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "folderId": folder_id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        folder_id = d.pop("folderId")

        name = d.pop("name")

        project_entry_breadcrumb = cls(
            folder_id=folder_id,
            name=name,
        )

        return project_entry_breadcrumb
