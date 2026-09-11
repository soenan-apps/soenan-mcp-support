from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_file_source_state import ProjectFileSourceState

if TYPE_CHECKING:
    from ..models.project_file_media import ProjectFileMedia


T = TypeVar("T", bound="ProjectFile")


@_attrs_define
class ProjectFile:
    """
    Attributes:
        id (str):
        original_filename (str):
        size_bytes (int):
        created_at (datetime.datetime):
        source_state (ProjectFileSourceState):
        media (ProjectFileMedia):
    """

    id: str
    original_filename: str
    size_bytes: int
    created_at: datetime.datetime
    source_state: ProjectFileSourceState
    media: ProjectFileMedia

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        original_filename = self.original_filename

        size_bytes = self.size_bytes

        created_at = self.created_at.isoformat()

        source_state = self.source_state.value

        media = self.media.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "originalFilename": original_filename,
                "sizeBytes": size_bytes,
                "createdAt": created_at,
                "sourceState": source_state,
                "media": media,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_file_media import ProjectFileMedia

        d = dict(src_dict)
        id = d.pop("id")

        original_filename = d.pop("originalFilename")

        size_bytes = d.pop("sizeBytes")

        created_at = datetime.datetime.fromisoformat(d.pop("createdAt"))

        source_state = ProjectFileSourceState(d.pop("sourceState"))

        media = ProjectFileMedia.from_dict(d.pop("media"))

        project_file = cls(
            id=id,
            original_filename=original_filename,
            size_bytes=size_bytes,
            created_at=created_at,
            source_state=source_state,
            media=media,
        )

        return project_file
