from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.mix_version import MixVersion
    from ..models.project_detail import ProjectDetail
    from ..models.timeline_comment import TimelineComment


T = TypeVar("T", bound="ProjectWorkspace")


@_attrs_define
class ProjectWorkspace:
    """
    Attributes:
        project (ProjectDetail):
        versions (list[MixVersion]):
        comments (list[TimelineComment]):
    """

    project: ProjectDetail
    versions: list[MixVersion]
    comments: list[TimelineComment]

    def to_dict(self) -> dict[str, Any]:
        project = self.project.to_dict()

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        comments = []
        for comments_item_data in self.comments:
            comments_item = comments_item_data.to_dict()
            comments.append(comments_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project": project,
                "versions": versions,
                "comments": comments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mix_version import MixVersion
        from ..models.project_detail import ProjectDetail
        from ..models.timeline_comment import TimelineComment

        d = dict(src_dict)
        project = ProjectDetail.from_dict(d.pop("project"))

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = MixVersion.from_dict(versions_item_data)

            versions.append(versions_item)

        comments = []
        _comments = d.pop("comments")
        for comments_item_data in _comments:
            comments_item = TimelineComment.from_dict(comments_item_data)

            comments.append(comments_item)

        project_workspace = cls(
            project=project,
            versions=versions,
            comments=comments,
        )

        return project_workspace
