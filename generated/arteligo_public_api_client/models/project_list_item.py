from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_list_access_source import ProjectListAccessSource

if TYPE_CHECKING:
    from ..models.project_organization import ProjectOrganization
    from ..models.project_summary import ProjectSummary


T = TypeVar("T", bound="ProjectListItem")


@_attrs_define
class ProjectListItem:
    """
    Attributes:
        owner_organization (ProjectOrganization):
        project (ProjectSummary):
        access_source (ProjectListAccessSource): Describes why the current subject can see the project in the list.
            Organization covers current membership in the Owner organization; invitation covers an active membership created
            by an accepted invitation.
        storage_used_bytes (int):
    """

    owner_organization: ProjectOrganization
    project: ProjectSummary
    access_source: ProjectListAccessSource
    storage_used_bytes: int

    def to_dict(self) -> dict[str, Any]:
        owner_organization = self.owner_organization.to_dict()

        project = self.project.to_dict()

        access_source = self.access_source.value

        storage_used_bytes = self.storage_used_bytes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ownerOrganization": owner_organization,
                "project": project,
                "accessSource": access_source,
                "storageUsedBytes": storage_used_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_organization import ProjectOrganization
        from ..models.project_summary import ProjectSummary

        d = dict(src_dict)
        owner_organization = ProjectOrganization.from_dict(d.pop("ownerOrganization"))

        project = ProjectSummary.from_dict(d.pop("project"))

        access_source = ProjectListAccessSource(d.pop("accessSource"))

        storage_used_bytes = d.pop("storageUsedBytes")

        project_list_item = cls(
            owner_organization=owner_organization,
            project=project,
            access_source=access_source,
            storage_used_bytes=storage_used_bytes,
        )

        return project_list_item
