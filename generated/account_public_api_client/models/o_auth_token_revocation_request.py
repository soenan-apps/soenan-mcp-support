from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.o_auth_token_revocation_request_token_type_hint import (
    OAuthTokenRevocationRequestTokenTypeHint,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthTokenRevocationRequest")


@_attrs_define
class OAuthTokenRevocationRequest:
    """
    Attributes:
        token (str):
        client_id (str):
        resource (str):
        token_type_hint (OAuthTokenRevocationRequestTokenTypeHint | Unset):
    """

    token: str
    client_id: str
    resource: str
    token_type_hint: OAuthTokenRevocationRequestTokenTypeHint | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        client_id = self.client_id

        resource = self.resource

        token_type_hint: str | Unset = UNSET
        if not isinstance(self.token_type_hint, Unset):
            token_type_hint = self.token_type_hint.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "token": token,
                "client_id": client_id,
                "resource": resource,
            }
        )
        if token_type_hint is not UNSET:
            field_dict["token_type_hint"] = token_type_hint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        token = d.pop("token")

        client_id = d.pop("client_id")

        resource = d.pop("resource")

        _token_type_hint = d.pop("token_type_hint", UNSET)
        token_type_hint: OAuthTokenRevocationRequestTokenTypeHint | Unset
        if isinstance(_token_type_hint, Unset):
            token_type_hint = UNSET
        else:
            token_type_hint = OAuthTokenRevocationRequestTokenTypeHint(_token_type_hint)

        o_auth_token_revocation_request = cls(
            token=token,
            client_id=client_id,
            resource=resource,
            token_type_hint=token_type_hint,
        )

        return o_auth_token_revocation_request
