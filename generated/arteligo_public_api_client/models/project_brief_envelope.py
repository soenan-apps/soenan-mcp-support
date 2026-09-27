from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_brief import ProjectBrief


T = TypeVar("T", bound="ProjectBriefEnvelope")


@_attrs_define
class ProjectBriefEnvelope:
    """
    Attributes:
        brief (ProjectBrief):
    """

    brief: ProjectBrief

    def to_dict(self) -> dict[str, Any]:
        brief = self.brief.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "brief": brief,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_brief import ProjectBrief

        d = dict(src_dict)
        brief = ProjectBrief.from_dict(d.pop("brief"))

        project_brief_envelope = cls(
            brief=brief,
        )

        return project_brief_envelope
