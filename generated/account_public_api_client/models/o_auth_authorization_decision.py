from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OAuthAuthorizationDecision")


@_attrs_define
class OAuthAuthorizationDecision:
    """
    Attributes:
        redirect_uri (str):
    """

    redirect_uri: str

    def to_dict(self) -> dict[str, Any]:
        redirect_uri = self.redirect_uri

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "redirectUri": redirect_uri,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        redirect_uri = d.pop("redirectUri")

        o_auth_authorization_decision = cls(
            redirect_uri=redirect_uri,
        )

        return o_auth_authorization_decision
