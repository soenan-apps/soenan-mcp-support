from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.project_list_item import ProjectListItem


T = TypeVar("T", bound="ProjectListEnvelope")


@_attrs_define
class ProjectListEnvelope:
    """
    Attributes:
        projects (list[ProjectListItem]):
        can_create_project (bool):
    """

    projects: list[ProjectListItem]
    can_create_project: bool

    def to_dict(self) -> dict[str, Any]:
        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        can_create_project = self.can_create_project

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "projects": projects,
                "canCreateProject": can_create_project,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project_list_item import ProjectListItem

        d = dict(src_dict)
        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = ProjectListItem.from_dict(projects_item_data)

            projects.append(projects_item)

        can_create_project = d.pop("canCreateProject")

        project_list_envelope = cls(
            projects=projects,
            can_create_project=can_create_project,
        )

        return project_list_envelope
