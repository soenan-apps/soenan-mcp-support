from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ProjectFileEntryIntent")


@_attrs_define
class ProjectFileEntryIntent:
    """
    Attributes:
        parent_folder_id (None | str):
        name (str):
    """

    parent_folder_id: None | str
    name: str

    def to_dict(self) -> dict[str, Any]:
        parent_folder_id: None | str
        parent_folder_id = self.parent_folder_id

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "parentFolderId": parent_folder_id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)

        def _parse_parent_folder_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        parent_folder_id = _parse_parent_folder_id(d.pop("parentFolderId"))

        name = d.pop("name")

        project_file_entry_intent = cls(
            parent_folder_id=parent_folder_id,
            name=name,
        )

        return project_file_entry_intent
