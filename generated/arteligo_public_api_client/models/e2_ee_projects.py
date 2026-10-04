from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_project import E2EeProject


T = TypeVar("T", bound="E2EeProjects")


@_attrs_define
class E2EeProjects:
    """
    Attributes:
        projects (list[E2EeProject]):
    """

    projects: list[E2EeProject]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "projects": projects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_project import E2EeProject

        d = dict(src_dict)
        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = E2EeProject.from_dict(projects_item_data)

            projects.append(projects_item)

        e2_ee_projects = cls(
            projects=projects,
        )

        e2_ee_projects.additional_properties = d
        return e2_ee_projects

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
