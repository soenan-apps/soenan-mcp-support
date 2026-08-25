from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.invitation_membership_access_role import InvitationMembershipAccessRole
from ..models.invitation_membership_state import InvitationMembershipState
from ..types import UNSET, Unset

T = TypeVar("T", bound="InvitationMembership")


@_attrs_define
class InvitationMembership:
    """
    Attributes:
        id (str):
        project_id (str):
        user_id (str):
        display_name (str):
        access_role (InvitationMembershipAccessRole):
        state (InvitationMembershipState):
        joined_at (datetime.datetime | None | Unset):
        removed_at (datetime.datetime | None | Unset):
    """

    id: str
    project_id: str
    user_id: str
    display_name: str
    access_role: InvitationMembershipAccessRole
    state: InvitationMembershipState
    joined_at: datetime.datetime | None | Unset = UNSET
    removed_at: datetime.datetime | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project_id = self.project_id

        user_id = self.user_id

        display_name = self.display_name

        access_role = self.access_role.value

        state = self.state.value

        joined_at: None | str | Unset
        if isinstance(self.joined_at, Unset):
            joined_at = UNSET
        elif isinstance(self.joined_at, datetime.datetime):
            joined_at = self.joined_at.isoformat()
        else:
            joined_at = self.joined_at

        removed_at: None | str | Unset
        if isinstance(self.removed_at, Unset):
            removed_at = UNSET
        elif isinstance(self.removed_at, datetime.datetime):
            removed_at = self.removed_at.isoformat()
        else:
            removed_at = self.removed_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "projectId": project_id,
                "userId": user_id,
                "displayName": display_name,
                "accessRole": access_role,
                "state": state,
            }
        )
        if joined_at is not UNSET:
            field_dict["joinedAt"] = joined_at
        if removed_at is not UNSET:
            field_dict["removedAt"] = removed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        project_id = d.pop("projectId")

        user_id = d.pop("userId")

        display_name = d.pop("displayName")

        access_role = InvitationMembershipAccessRole(d.pop("accessRole"))

        state = InvitationMembershipState(d.pop("state"))

        def _parse_joined_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                joined_at_type_1 = datetime.datetime.fromisoformat(data)

                return joined_at_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        joined_at = _parse_joined_at(d.pop("joinedAt", UNSET))

        def _parse_removed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                removed_at_type_1 = datetime.datetime.fromisoformat(data)

                return removed_at_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        removed_at = _parse_removed_at(d.pop("removedAt", UNSET))

        invitation_membership = cls(
            id=id,
            project_id=project_id,
            user_id=user_id,
            display_name=display_name,
            access_role=access_role,
            state=state,
            joined_at=joined_at,
            removed_at=removed_at,
        )

        return invitation_membership
