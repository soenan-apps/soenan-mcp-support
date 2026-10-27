from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.o_auth_token_response_token_type import OAuthTokenResponseTokenType

T = TypeVar("T", bound="OAuthTokenResponse")


@_attrs_define
class OAuthTokenResponse:
    """
    Attributes:
        access_token (str):
        token_type (OAuthTokenResponseTokenType):
        expires_in (int):
        access_expires_at (int):
        refresh_expires_at (int):
        scope (str):
        refresh_token (str):
    """

    access_token: str
    token_type: OAuthTokenResponseTokenType
    expires_in: int
    access_expires_at: int
    refresh_expires_at: int
    scope: str
    refresh_token: str

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        token_type = self.token_type.value

        expires_in = self.expires_in

        access_expires_at = self.access_expires_at

        refresh_expires_at = self.refresh_expires_at

        scope = self.scope

        refresh_token = self.refresh_token

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "access_token": access_token,
                "token_type": token_type,
                "expires_in": expires_in,
                "access_expires_at": access_expires_at,
                "refresh_expires_at": refresh_expires_at,
                "scope": scope,
                "refresh_token": refresh_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_token = d.pop("access_token")

        token_type = OAuthTokenResponseTokenType(d.pop("token_type"))

        expires_in = d.pop("expires_in")

        access_expires_at = d.pop("access_expires_at")

        refresh_expires_at = d.pop("refresh_expires_at")

        scope = d.pop("scope")

        refresh_token = d.pop("refresh_token")

        o_auth_token_response = cls(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
            scope=scope,
            refresh_token=refresh_token,
        )

        return o_auth_token_response
