from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_schedule_invalidated_type import (
    RealtimeProjectScheduleInvalidatedType,
)

T = TypeVar("T", bound="RealtimeProjectScheduleInvalidated")


@_attrs_define
class RealtimeProjectScheduleInvalidated:
    """
    Attributes:
        type_ (RealtimeProjectScheduleInvalidatedType):
        revision (int):
        project_id (str):
    """

    type_: RealtimeProjectScheduleInvalidatedType
    revision: int
    project_id: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        revision = self.revision

        project_id = self.project_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "revision": revision,
                "projectId": project_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeProjectScheduleInvalidatedType(d.pop("type"))

        revision = d.pop("revision")

        project_id = d.pop("projectId")

        realtime_project_schedule_invalidated = cls(
            type_=type_,
            revision=revision,
            project_id=project_id,
        )

        return realtime_project_schedule_invalidated
