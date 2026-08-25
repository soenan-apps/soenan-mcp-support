from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.project_list_access_source import ProjectListAccessSource

if TYPE_CHECKING:
    from ..models.project_summary import ProjectSummary


T = TypeVar("T", bound="ProjectListItem")


@_attrs_define
class ProjectListItem:
    """
    Attributes:
        project (ProjectSummary):
        access_source (ProjectListAccessSource): Describes why the current subject can see the project in the list.
            Organization covers the active Owner-organization context; invitation covers an active membership created by an
            accepted invitation.
    """

    project: ProjectSummary
    access_source: ProjectListAccessSource

    def to_dict(self) -> dict[str, Any]:
        project = self.project.to_dict()

        access_source = self.access_source.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project": project,
                "accessSource": access_source,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project_summary import ProjectSummary

        d = dict(src_dict)
        project = ProjectSummary.from_dict(d.pop("project"))

        access_source = ProjectListAccessSource(d.pop("accessSource"))

        project_list_item = cls(
            project=project,
            access_source=access_source,
        )

        return project_list_item
