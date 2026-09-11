from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_file_entry import ProjectFileEntry
    from ..models.project_folder_entry import ProjectFolderEntry


T = TypeVar("T", bound="ProjectEntryResponse")


@_attrs_define
class ProjectEntryResponse:
    """
    Attributes:
        entry (ProjectFileEntry | ProjectFolderEntry):
    """

    entry: ProjectFileEntry | ProjectFolderEntry

    def to_dict(self) -> dict[str, Any]:
        from ..models.project_folder_entry import ProjectFolderEntry

        entry: dict[str, Any]
        if isinstance(self.entry, ProjectFolderEntry):
            entry = self.entry.to_dict()
        else:
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
        from ..models.project_folder_entry import ProjectFolderEntry

        d = dict(src_dict)

        def _parse_entry(data: object) -> ProjectFileEntry | ProjectFolderEntry:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_project_entry_type_0 = ProjectFolderEntry.from_dict(
                    data
                )

                return componentsschemas_project_entry_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_project_entry_type_1 = ProjectFileEntry.from_dict(data)

            return componentsschemas_project_entry_type_1

        entry = _parse_entry(d.pop("entry"))

        project_entry_response = cls(
            entry=entry,
        )

        return project_entry_response
