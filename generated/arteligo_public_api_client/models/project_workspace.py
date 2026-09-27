from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_detail import ProjectDetail
    from ..models.project_stage import ProjectStage
    from ..models.timeline_comment import TimelineComment


T = TypeVar("T", bound="ProjectWorkspace")


@_attrs_define
class ProjectWorkspace:
    """
    Attributes:
        project (ProjectDetail):
        stages (list[ProjectStage]):
        comments (list[TimelineComment]):
    """

    project: ProjectDetail
    stages: list[ProjectStage]
    comments: list[TimelineComment]

    def to_dict(self) -> dict[str, Any]:
        project = self.project.to_dict()

        stages = []
        for stages_item_data in self.stages:
            stages_item = stages_item_data.to_dict()
            stages.append(stages_item)

        comments = []
        for comments_item_data in self.comments:
            comments_item = comments_item_data.to_dict()
            comments.append(comments_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project": project,
                "stages": stages,
                "comments": comments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_detail import ProjectDetail
        from ..models.project_stage import ProjectStage
        from ..models.timeline_comment import TimelineComment

        d = dict(src_dict)
        project = ProjectDetail.from_dict(d.pop("project"))

        stages = []
        _stages = d.pop("stages")
        for stages_item_data in _stages:
            stages_item = ProjectStage.from_dict(stages_item_data)

            stages.append(stages_item)

        comments = []
        _comments = d.pop("comments")
        for comments_item_data in _comments:
            comments_item = TimelineComment.from_dict(comments_item_data)

            comments.append(comments_item)

        project_workspace = cls(
            project=project,
            stages=stages,
            comments=comments,
        )

        return project_workspace
