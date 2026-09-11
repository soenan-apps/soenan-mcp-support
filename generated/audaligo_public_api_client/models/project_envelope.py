from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_summary import ProjectSummary


T = TypeVar("T", bound="ProjectEnvelope")


@_attrs_define
class ProjectEnvelope:
    """
    Attributes:
        project (ProjectSummary):
    """

    project: ProjectSummary

    def to_dict(self) -> dict[str, Any]:
        project = self.project.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project": project,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_summary import ProjectSummary

        d = dict(src_dict)
        project = ProjectSummary.from_dict(d.pop("project"))

        project_envelope = cls(
            project=project,
        )

        return project_envelope
