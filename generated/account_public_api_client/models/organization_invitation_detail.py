from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.organization_invitation_detail_state import (
    OrganizationInvitationDetailState,
)

T = TypeVar("T", bound="OrganizationInvitationDetail")


@_attrs_define
class OrganizationInvitationDetail:
    """
    Attributes:
        invitation_id (UUID):
        target_email (str):
        state (OrganizationInvitationDetailState):
        expires_at (datetime.datetime):
        role_keys (list[str]):
    """

    invitation_id: UUID
    target_email: str
    state: OrganizationInvitationDetailState
    expires_at: datetime.datetime
    role_keys: list[str]

    def to_dict(self) -> dict[str, Any]:
        invitation_id = str(self.invitation_id)

        target_email = self.target_email

        state = self.state.value

        expires_at = self.expires_at.isoformat()

        role_keys = self.role_keys

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitationId": invitation_id,
                "targetEmail": target_email,
                "state": state,
                "expiresAt": expires_at,
                "roleKeys": role_keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        invitation_id = UUID(d.pop("invitationId"))

        target_email = d.pop("targetEmail")

        state = OrganizationInvitationDetailState(d.pop("state"))

        expires_at = isoparse(d.pop("expiresAt"))

        role_keys = cast(list[str], d.pop("roleKeys"))

        organization_invitation_detail = cls(
            invitation_id=invitation_id,
            target_email=target_email,
            state=state,
            expires_at=expires_at,
            role_keys=role_keys,
        )

        return organization_invitation_detail
