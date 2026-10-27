from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.mcpo_auth_scope import MCPOAuthScope

T = TypeVar("T", bound="OAuthAuthorizationApproval")


@_attrs_define
class OAuthAuthorizationApproval:
    """
    Attributes:
        scopes (list[MCPOAuthScope]):
    """

    scopes: list[MCPOAuthScope]

    def to_dict(self) -> dict[str, Any]:
        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.value
            scopes.append(scopes_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scopes": scopes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = MCPOAuthScope(scopes_item_data)

            scopes.append(scopes_item)

        o_auth_authorization_approval = cls(
            scopes=scopes,
        )

        return o_auth_authorization_approval
