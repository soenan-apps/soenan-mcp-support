from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.invitation_state_access_role import InvitationStateAccessRole
from ..models.invitation_state_state import InvitationStateState
from ..types import UNSET, Unset, parse_datetime

T = TypeVar("T", bound="InvitationState")


@_attrs_define
class InvitationState:
    """
    Attributes:
        id (str):
        project_id (str):
        state (InvitationStateState):
        access_role (InvitationStateAccessRole):
        token_generation (int):
        issued_at (datetime.datetime):
        expires_at (datetime.datetime):
        consumed_at (datetime.datetime | None | Unset):
        revoked_at (datetime.datetime | None | Unset):
    """

    id: str
    project_id: str
    state: InvitationStateState
    access_role: InvitationStateAccessRole
    token_generation: int
    issued_at: datetime.datetime
    expires_at: datetime.datetime
    consumed_at: datetime.datetime | None | Unset = UNSET
    revoked_at: datetime.datetime | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project_id = self.project_id

        state = self.state.value

        access_role = self.access_role.value

        token_generation = self.token_generation

        issued_at = self.issued_at.isoformat()

        expires_at = self.expires_at.isoformat()

        consumed_at: None | str | Unset
        if isinstance(self.consumed_at, Unset):
            consumed_at = UNSET
        elif isinstance(self.consumed_at, datetime.datetime):
            consumed_at = self.consumed_at.isoformat()
        else:
            consumed_at = self.consumed_at

        revoked_at: None | str | Unset
        if isinstance(self.revoked_at, Unset):
            revoked_at = UNSET
        elif isinstance(self.revoked_at, datetime.datetime):
            revoked_at = self.revoked_at.isoformat()
        else:
            revoked_at = self.revoked_at

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
            }
        )
        if consumed_at is not UNSET:
            field_dict["consumedAt"] = consumed_at
        if revoked_at is not UNSET:
            field_dict["revokedAt"] = revoked_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        project_id = d.pop("projectId")

        state = InvitationStateState(d.pop("state"))

        access_role = InvitationStateAccessRole(d.pop("accessRole"))

        token_generation = d.pop("tokenGeneration")

        issued_at = parse_datetime(d.pop("issuedAt"))

        expires_at = parse_datetime(d.pop("expiresAt"))

        def _parse_consumed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                consumed_at_type_1 = parse_datetime(data)

                return consumed_at_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        consumed_at = _parse_consumed_at(d.pop("consumedAt", UNSET))

        def _parse_revoked_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                revoked_at_type_1 = parse_datetime(data)

                return revoked_at_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        revoked_at = _parse_revoked_at(d.pop("revokedAt", UNSET))

        invitation_state = cls(
            id=id,
            project_id=project_id,
            state=state,
            access_role=access_role,
            token_generation=token_generation,
            issued_at=issued_at,
            expires_at=expires_at,
            consumed_at=consumed_at,
            revoked_at=revoked_at,
        )

        return invitation_state
