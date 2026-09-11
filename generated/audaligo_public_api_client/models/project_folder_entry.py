from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_folder_entry_kind import ProjectFolderEntryKind

if TYPE_CHECKING:
    from ..models.project_entry_breadcrumb import ProjectEntryBreadcrumb


T = TypeVar("T", bound="ProjectFolderEntry")


@_attrs_define
class ProjectFolderEntry:
    """
    Attributes:
        kind (ProjectFolderEntryKind):
        id (str):
        project_id (str):
        parent_folder_id (None | str):
        name (str):
        revision (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        deleted_at (datetime.datetime | None):
        breadcrumbs (list[ProjectEntryBreadcrumb]):
    """

    kind: ProjectFolderEntryKind
    id: str
    project_id: str
    parent_folder_id: None | str
    name: str
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None
    breadcrumbs: list[ProjectEntryBreadcrumb]

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        id = self.id

        project_id = self.project_id

        parent_folder_id: None | str
        parent_folder_id = self.parent_folder_id

        name = self.name

        revision = self.revision

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        deleted_at: None | str
        if isinstance(self.deleted_at, datetime.datetime):
            deleted_at = self.deleted_at.isoformat()
        else:
            deleted_at = self.deleted_at

        breadcrumbs = []
        for breadcrumbs_item_data in self.breadcrumbs:
            breadcrumbs_item = breadcrumbs_item_data.to_dict()
            breadcrumbs.append(breadcrumbs_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "id": id,
                "projectId": project_id,
                "parentFolderId": parent_folder_id,
                "name": name,
                "revision": revision,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "deletedAt": deleted_at,
                "breadcrumbs": breadcrumbs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_entry_breadcrumb import (
            ProjectEntryBreadcrumb,
        )

        d = dict(src_dict)
        kind = ProjectFolderEntryKind(d.pop("kind"))

        id = d.pop("id")

        project_id = d.pop("projectId")

        def _parse_parent_folder_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        parent_folder_id = _parse_parent_folder_id(d.pop("parentFolderId"))

        name = d.pop("name")

        revision = d.pop("revision")

        created_at = datetime.datetime.fromisoformat(d.pop("createdAt"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updatedAt"))

        def _parse_deleted_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deleted_at_type_1 = datetime.datetime.fromisoformat(data)

                return deleted_at_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        deleted_at = _parse_deleted_at(d.pop("deletedAt"))

        breadcrumbs = []
        _breadcrumbs = d.pop("breadcrumbs")
        for breadcrumbs_item_data in _breadcrumbs:
            breadcrumbs_item = ProjectEntryBreadcrumb.from_dict(breadcrumbs_item_data)

            breadcrumbs.append(breadcrumbs_item)

        project_folder_entry = cls(
            kind=kind,
            id=id,
            project_id=project_id,
            parent_folder_id=parent_folder_id,
            name=name,
            revision=revision,
            created_at=created_at,
            updated_at=updated_at,
            deleted_at=deleted_at,
            breadcrumbs=breadcrumbs,
        )

        return project_folder_entry
