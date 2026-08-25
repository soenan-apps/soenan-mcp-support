from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.project_participation_policy import ProjectParticipationPolicy

T = TypeVar("T", bound="UpdateProjectParticipationPolicyRequest")


@_attrs_define
class UpdateProjectParticipationPolicyRequest:
    """
    Attributes:
        participation_policy (ProjectParticipationPolicy): Controls who may participate in the project as an Editor.
            Organization includes current members of the Owner organization; private includes only the Owner and
            individually invited Editors. Every participant has the same project capabilities except Owner-only invitation
            and member management.
    """

    participation_policy: ProjectParticipationPolicy

    def to_dict(self) -> dict[str, Any]:
        participation_policy = self.participation_policy.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "participationPolicy": participation_policy,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        participation_policy = ProjectParticipationPolicy(d.pop("participationPolicy"))

        update_project_participation_policy_request = cls(
            participation_policy=participation_policy,
        )

        return update_project_participation_policy_request
