from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.accepted_invitation_state_state import AcceptedInvitationStateState

T = TypeVar("T", bound="AcceptedInvitationState")


@_attrs_define
class AcceptedInvitationState:
    """
    Attributes:
        id (str):
        project_id (str):
        state (AcceptedInvitationStateState):
        consumed_at (datetime.datetime):
    """

    id: str
    project_id: str
    state: AcceptedInvitationStateState
    consumed_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project_id = self.project_id

        state = self.state.value

        consumed_at = self.consumed_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "projectId": project_id,
                "state": state,
                "consumedAt": consumed_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        project_id = d.pop("projectId")

        state = AcceptedInvitationStateState(d.pop("state"))

        consumed_at = datetime.datetime.fromisoformat(d.pop("consumedAt"))

        accepted_invitation_state = cls(
            id=id,
            project_id=project_id,
            state=state,
            consumed_at=consumed_at,
        )

        return accepted_invitation_state
