from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.project_participation_policy import ProjectParticipationPolicy

T = TypeVar("T", bound="CreateProjectRequest")


@_attrs_define
class CreateProjectRequest:
    """
    Attributes:
        title (str):
        participation_policy (ProjectParticipationPolicy): Controls who may participate in the project as an Editor.
            Organization includes current members of the Owner organization; private includes only the Owner and
            individually invited Editors. Every participant has the same project capabilities except Owner-only invitation
            and member management.
    """

    title: str
    participation_policy: ProjectParticipationPolicy

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        participation_policy = self.participation_policy.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "title": title,
                "participationPolicy": participation_policy,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        participation_policy = ProjectParticipationPolicy(d.pop("participationPolicy"))

        create_project_request = cls(
            title=title,
            participation_policy=participation_policy,
        )

        return create_project_request
