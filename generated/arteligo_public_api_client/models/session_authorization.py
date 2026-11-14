from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.session_authorization_outcome import SessionAuthorizationOutcome






T = TypeVar("T", bound="SessionAuthorization")



@_attrs_define
class SessionAuthorization:
    """ 
        Attributes:
            outcome (SessionAuthorizationOutcome):
            expires_at_unix_seconds (int):
            access_token_id (str):
            subject (str):
     """

    outcome: SessionAuthorizationOutcome
    expires_at_unix_seconds: int
    access_token_id: str
    subject: str





    def to_dict(self) -> dict[str, Any]:
        outcome = self.outcome.value

        expires_at_unix_seconds = self.expires_at_unix_seconds

        access_token_id = self.access_token_id

        subject = self.subject


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "outcome": outcome,
            "expires_at_unix_seconds": expires_at_unix_seconds,
            "access_token_id": access_token_id,
            "subject": subject,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        outcome = SessionAuthorizationOutcome(d.pop("outcome"))




        expires_at_unix_seconds = d.pop("expires_at_unix_seconds")

        access_token_id = d.pop("access_token_id")

        subject = d.pop("subject")

        session_authorization = cls(
            outcome=outcome,
            expires_at_unix_seconds=expires_at_unix_seconds,
            access_token_id=access_token_id,
            subject=subject,
        )

        return session_authorization

