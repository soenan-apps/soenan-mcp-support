from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_preview_lifecycle_invalidated_type import (
    RealtimePreviewLifecycleInvalidatedType,
)

T = TypeVar("T", bound="RealtimePreviewLifecycleInvalidated")


@_attrs_define
class RealtimePreviewLifecycleInvalidated:
    """
    Attributes:
        type_ (RealtimePreviewLifecycleInvalidatedType):
        revision (int):
        project_id (str):
        file_revision_id (str):
    """

    type_: RealtimePreviewLifecycleInvalidatedType
    revision: int
    project_id: str
    file_revision_id: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        revision = self.revision

        project_id = self.project_id

        file_revision_id = self.file_revision_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "revision": revision,
                "projectId": project_id,
                "fileRevisionId": file_revision_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimePreviewLifecycleInvalidatedType(d.pop("type"))

        revision = d.pop("revision")

        project_id = d.pop("projectId")

        file_revision_id = d.pop("fileRevisionId")

        realtime_preview_lifecycle_invalidated = cls(
            type_=type_,
            revision=revision,
            project_id=project_id,
            file_revision_id=file_revision_id,
        )

        return realtime_preview_lifecycle_invalidated
