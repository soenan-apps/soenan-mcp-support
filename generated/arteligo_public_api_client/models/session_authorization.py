from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.session_authorization_outcome import SessionAuthorizationOutcome

T = TypeVar("T", bound="SessionAuthorization")


@_attrs_define
class SessionAuthorization:
    """
    Attributes:
        outcome (SessionAuthorizationOutcome):
        denied_organization_ids (list[str]):
        expires_at_unix_seconds (int):
        access_token_id (str):
    """

    outcome: SessionAuthorizationOutcome
    denied_organization_ids: list[str]
    expires_at_unix_seconds: int
    access_token_id: str

    def to_dict(self) -> dict[str, Any]:
        outcome = self.outcome.value

        denied_organization_ids = self.denied_organization_ids

        expires_at_unix_seconds = self.expires_at_unix_seconds

        access_token_id = self.access_token_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "outcome": outcome,
                "denied_organization_ids": denied_organization_ids,
                "expires_at_unix_seconds": expires_at_unix_seconds,
                "access_token_id": access_token_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        outcome = SessionAuthorizationOutcome(d.pop("outcome"))

        denied_organization_ids = cast(list[str], d.pop("denied_organization_ids"))

        expires_at_unix_seconds = d.pop("expires_at_unix_seconds")

        access_token_id = d.pop("access_token_id")

        session_authorization = cls(
            outcome=outcome,
            denied_organization_ids=denied_organization_ids,
            expires_at_unix_seconds=expires_at_unix_seconds,
            access_token_id=access_token_id,
        )

        return session_authorization
