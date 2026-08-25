from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.invitation_summary_access_role import InvitationSummaryAccessRole
from ..models.invitation_summary_state import InvitationSummaryState
from ..types import parse_datetime

T = TypeVar("T", bound="InvitationSummary")


@_attrs_define
class InvitationSummary:
    """
    Attributes:
        id (str):
        project_id (str):
        state (InvitationSummaryState):
        access_role (InvitationSummaryAccessRole):
        token_generation (int):
        issued_at (datetime.datetime):
        expires_at (datetime.datetime):
        created_at (datetime.datetime):
    """

    id: str
    project_id: str
    state: InvitationSummaryState
    access_role: InvitationSummaryAccessRole
    token_generation: int
    issued_at: datetime.datetime
    expires_at: datetime.datetime
    created_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project_id = self.project_id

        state = self.state.value

        access_role = self.access_role.value

        token_generation = self.token_generation

        issued_at = self.issued_at.isoformat()

        expires_at = self.expires_at.isoformat()

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "projectId": project_id,
                "state": state,
                "accessRole": access_role,
                "tokenGeneration": token_generation,
                "issuedAt": issued_at,
                "expiresAt": expires_at,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        project_id = d.pop("projectId")

        state = InvitationSummaryState(d.pop("state"))

        access_role = InvitationSummaryAccessRole(d.pop("accessRole"))

        token_generation = d.pop("tokenGeneration")

        issued_at = parse_datetime(d.pop("issuedAt"))

        expires_at = parse_datetime(d.pop("expiresAt"))

        created_at = parse_datetime(d.pop("createdAt"))

        invitation_summary = cls(
            id=id,
            project_id=project_id,
            state=state,
            access_role=access_role,
            token_generation=token_generation,
            issued_at=issued_at,
            expires_at=expires_at,
            created_at=created_at,
        )

        return invitation_summary
