from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="UpdateProjectEntryRequest")


@_attrs_define
class UpdateProjectEntryRequest:
    """
    Attributes:
        expected_revision (int):
        parent_folder_id (None | str):
        name (str):
    """

    expected_revision: int
    parent_folder_id: None | str
    name: str

    def to_dict(self) -> dict[str, Any]:
        expected_revision = self.expected_revision

        parent_folder_id: None | str
        parent_folder_id = self.parent_folder_id

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expectedRevision": expected_revision,
                "parentFolderId": parent_folder_id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        expected_revision = d.pop("expectedRevision")

        def _parse_parent_folder_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        parent_folder_id = _parse_parent_folder_id(d.pop("parentFolderId"))

        name = d.pop("name")

        update_project_entry_request = cls(
            expected_revision=expected_revision,
            parent_folder_id=parent_folder_id,
            name=name,
        )

        return update_project_entry_request
