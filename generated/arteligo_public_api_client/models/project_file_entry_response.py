from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_file_entry import ProjectFileEntry


T = TypeVar("T", bound="ProjectFileEntryResponse")


@_attrs_define
class ProjectFileEntryResponse:
    """
    Attributes:
        entry (ProjectFileEntry):
    """

    entry: ProjectFileEntry

    def to_dict(self) -> dict[str, Any]:
        entry = self.entry.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "entry": entry,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_file_entry import ProjectFileEntry

        d = dict(src_dict)
        entry = ProjectFileEntry.from_dict(d.pop("entry"))

        project_file_entry_response = cls(
            entry=entry,
        )

        return project_file_entry_response
