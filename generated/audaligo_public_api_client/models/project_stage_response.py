from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_stage import ProjectStage


T = TypeVar("T", bound="ProjectStageResponse")


@_attrs_define
class ProjectStageResponse:
    """
    Attributes:
        stage (ProjectStage):
    """

    stage: ProjectStage

    def to_dict(self) -> dict[str, Any]:
        stage = self.stage.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "stage": stage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_stage import ProjectStage

        d = dict(src_dict)
        stage = ProjectStage.from_dict(d.pop("stage"))

        project_stage_response = cls(
            stage=stage,
        )

        return project_stage_response
