from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_stage_status import ProjectStageStatus

if TYPE_CHECKING:
    from ..models.stage_content import StageContent


T = TypeVar("T", bound="ProjectStage")


@_attrs_define
class ProjectStage:
    """
    Attributes:
        id (str):
        project_id (str):
        status (ProjectStageStatus):
        revision (int):
        version_number (int | None):
        contents (list[StageContent]):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        published_at (datetime.datetime | None):
    """

    id: str
    project_id: str
    status: ProjectStageStatus
    revision: int
    version_number: int | None
    contents: list[StageContent]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    published_at: datetime.datetime | None

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project_id = self.project_id

        status = self.status.value

        revision = self.revision

        version_number: int | None
        version_number = self.version_number

        contents = []
        for contents_item_data in self.contents:
            contents_item = contents_item_data.to_dict()
            contents.append(contents_item)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        published_at: None | str
        if isinstance(self.published_at, datetime.datetime):
            published_at = self.published_at.isoformat()
        else:
            published_at = self.published_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "projectId": project_id,
                "status": status,
                "revision": revision,
                "versionNumber": version_number,
                "contents": contents,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "publishedAt": published_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.stage_content import StageContent

        d = dict(src_dict)
        id = d.pop("id")

        project_id = d.pop("projectId")

        status = ProjectStageStatus(d.pop("status"))

        revision = d.pop("revision")

        def _parse_version_number(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        version_number = _parse_version_number(d.pop("versionNumber"))

        contents = []
        _contents = d.pop("contents")
        for contents_item_data in _contents:
            contents_item = StageContent.from_dict(contents_item_data)

            contents.append(contents_item)

        created_at = datetime.datetime.fromisoformat(d.pop("createdAt"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updatedAt"))

        def _parse_published_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                published_at_type_0 = datetime.datetime.fromisoformat(data)

                return published_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        published_at = _parse_published_at(d.pop("publishedAt"))

        project_stage = cls(
            id=id,
            project_id=project_id,
            status=status,
            revision=revision,
            version_number=version_number,
            contents=contents,
            created_at=created_at,
            updated_at=updated_at,
            published_at=published_at,
        )

        return project_stage
