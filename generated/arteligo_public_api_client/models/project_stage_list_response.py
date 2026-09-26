from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_stage import ProjectStage


T = TypeVar("T", bound="ProjectStageListResponse")


@_attrs_define
class ProjectStageListResponse:
    """
    Attributes:
        stages (list[ProjectStage]):
        next_cursor (None | str):
    """

    stages: list[ProjectStage]
    next_cursor: None | str

    def to_dict(self) -> dict[str, Any]:
        stages = []
        for stages_item_data in self.stages:
            stages_item = stages_item_data.to_dict()
            stages.append(stages_item)

        next_cursor: None | str
        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "stages": stages,
                "nextCursor": next_cursor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_stage import ProjectStage

        d = dict(src_dict)
        stages = []
        _stages = d.pop("stages")
        for stages_item_data in _stages:
            stages_item = ProjectStage.from_dict(stages_item_data)

            stages.append(stages_item)

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("nextCursor"))

        project_stage_list_response = cls(
            stages=stages,
            next_cursor=next_cursor,
        )

        return project_stage_list_response
