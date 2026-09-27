from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_file_entry import ProjectFileEntry
    from ..models.project_folder_entry import ProjectFolderEntry


T = TypeVar("T", bound="ProjectEntryListResponse")


@_attrs_define
class ProjectEntryListResponse:
    """
    Attributes:
        entries (list[ProjectFileEntry | ProjectFolderEntry]):
        next_cursor (None | str):
    """

    entries: list[ProjectFileEntry | ProjectFolderEntry]
    next_cursor: None | str

    def to_dict(self) -> dict[str, Any]:
        from ..models.project_folder_entry import ProjectFolderEntry

        entries = []
        for entries_item_data in self.entries:
            entries_item: dict[str, Any]
            if isinstance(entries_item_data, ProjectFolderEntry):
                entries_item = entries_item_data.to_dict()
            else:
                entries_item = entries_item_data.to_dict()

            entries.append(entries_item)

        next_cursor: None | str
        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "entries": entries,
                "nextCursor": next_cursor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_file_entry import ProjectFileEntry
        from ..models.project_folder_entry import ProjectFolderEntry

        d = dict(src_dict)
        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:

            def _parse_entries_item(
                data: object,
            ) -> ProjectFileEntry | ProjectFolderEntry:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_project_entry_type_0 = (
                        ProjectFolderEntry.from_dict(data)
                    )

                    return componentsschemas_project_entry_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_project_entry_type_1 = ProjectFileEntry.from_dict(
                    data
                )

                return componentsschemas_project_entry_type_1

            entries_item = _parse_entries_item(entries_item_data)

            entries.append(entries_item)

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("nextCursor"))

        project_entry_list_response = cls(
            entries=entries,
            next_cursor=next_cursor,
        )

        return project_entry_list_response
