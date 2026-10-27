from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.o_auth_token_request_grant_type import OAuthTokenRequestGrantType
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthTokenRequest")


@_attrs_define
class OAuthTokenRequest:
    """
    Attributes:
        grant_type (OAuthTokenRequestGrantType):
        client_id (str):
        resource (str):
        code (str | Unset):
        redirect_uri (str | Unset):
        code_verifier (str | Unset):
        refresh_token (str | Unset):
    """

    grant_type: OAuthTokenRequestGrantType
    client_id: str
    resource: str
    code: str | Unset = UNSET
    redirect_uri: str | Unset = UNSET
    code_verifier: str | Unset = UNSET
    refresh_token: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        grant_type = self.grant_type.value

        client_id = self.client_id

        resource = self.resource

        code = self.code

        redirect_uri = self.redirect_uri

        code_verifier = self.code_verifier

        refresh_token = self.refresh_token

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "grant_type": grant_type,
                "client_id": client_id,
                "resource": resource,
            }
        )
        if code is not UNSET:
            field_dict["code"] = code
        if redirect_uri is not UNSET:
            field_dict["redirect_uri"] = redirect_uri
        if code_verifier is not UNSET:
            field_dict["code_verifier"] = code_verifier
        if refresh_token is not UNSET:
            field_dict["refresh_token"] = refresh_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        grant_type = OAuthTokenRequestGrantType(d.pop("grant_type"))

        client_id = d.pop("client_id")

        resource = d.pop("resource")

        code = d.pop("code", UNSET)

        redirect_uri = d.pop("redirect_uri", UNSET)

        code_verifier = d.pop("code_verifier", UNSET)

        refresh_token = d.pop("refresh_token", UNSET)

        o_auth_token_request = cls(
            grant_type=grant_type,
            client_id=client_id,
            resource=resource,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            refresh_token=refresh_token,
        )

        return o_auth_token_request
