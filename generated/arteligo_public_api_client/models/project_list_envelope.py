from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_list_item import ProjectListItem
    from ..models.project_organization import ProjectOrganization


T = TypeVar("T", bound="ProjectListEnvelope")


@_attrs_define
class ProjectListEnvelope:
    """
    Attributes:
        projects (list[ProjectListItem]):
        creation_organizations (list[ProjectOrganization]):
    """

    projects: list[ProjectListItem]
    creation_organizations: list[ProjectOrganization]

    def to_dict(self) -> dict[str, Any]:
        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        creation_organizations = []
        for creation_organizations_item_data in self.creation_organizations:
            creation_organizations_item = creation_organizations_item_data.to_dict()
            creation_organizations.append(creation_organizations_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "projects": projects,
                "creationOrganizations": creation_organizations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_list_item import ProjectListItem
        from ..models.project_organization import ProjectOrganization

        d = dict(src_dict)
        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = ProjectListItem.from_dict(projects_item_data)

            projects.append(projects_item)

        creation_organizations = []
        _creation_organizations = d.pop("creationOrganizations")
        for creation_organizations_item_data in _creation_organizations:
            creation_organizations_item = ProjectOrganization.from_dict(
                creation_organizations_item_data
            )

            creation_organizations.append(creation_organizations_item)

        project_list_envelope = cls(
            projects=projects,
            creation_organizations=creation_organizations,
        )

        return project_list_envelope
