from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_member_access_role import ProjectMemberAccessRole
from ..models.project_member_origin_kind import ProjectMemberOriginKind
from ..models.project_member_state import ProjectMemberState

T = TypeVar("T", bound="ProjectMember")


@_attrs_define
class ProjectMember:
    """
    Attributes:
        membership_id (str):
        user_id (str):
        display_name (str):
        access_role (ProjectMemberAccessRole):
        state (ProjectMemberState):
        origin_kind (ProjectMemberOriginKind):
    """

    membership_id: str
    user_id: str
    display_name: str
    access_role: ProjectMemberAccessRole
    state: ProjectMemberState
    origin_kind: ProjectMemberOriginKind

    def to_dict(self) -> dict[str, Any]:
        membership_id = self.membership_id

        user_id = self.user_id

        display_name = self.display_name

        access_role = self.access_role.value

        state = self.state.value

        origin_kind = self.origin_kind.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "membershipId": membership_id,
                "userId": user_id,
                "displayName": display_name,
                "accessRole": access_role,
                "state": state,
                "originKind": origin_kind,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        membership_id = d.pop("membershipId")

        user_id = d.pop("userId")

        display_name = d.pop("displayName")

        access_role = ProjectMemberAccessRole(d.pop("accessRole"))

        state = ProjectMemberState(d.pop("state"))

        origin_kind = ProjectMemberOriginKind(d.pop("originKind"))

        project_member = cls(
            membership_id=membership_id,
            user_id=user_id,
            display_name=display_name,
            access_role=access_role,
            state=state,
            origin_kind=origin_kind,
        )

        return project_member
