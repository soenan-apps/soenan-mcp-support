from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.mcpo_auth_scope import MCPOAuthScope
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthAuthorizationRequest")


@_attrs_define
class OAuthAuthorizationRequest:
    """
    Attributes:
        request_id (str):
        client_name (str):
        resource (str):
        scopes (list[MCPOAuthScope]):
        available_scopes (list[MCPOAuthScope]):
        applies_to_all_current_resources (bool):
        requires_consent (bool):
        previously_granted_scopes (list[MCPOAuthScope] | Unset):
    """

    request_id: str
    client_name: str
    resource: str
    scopes: list[MCPOAuthScope]
    available_scopes: list[MCPOAuthScope]
    applies_to_all_current_resources: bool
    requires_consent: bool
    previously_granted_scopes: list[MCPOAuthScope] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        client_name = self.client_name

        resource = self.resource

        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.value
            scopes.append(scopes_item)

        available_scopes = []
        for available_scopes_item_data in self.available_scopes:
            available_scopes_item = available_scopes_item_data.value
            available_scopes.append(available_scopes_item)

        applies_to_all_current_resources = self.applies_to_all_current_resources

        requires_consent = self.requires_consent

        previously_granted_scopes: list[str] | Unset = UNSET
        if not isinstance(self.previously_granted_scopes, Unset):
            previously_granted_scopes = []
            for previously_granted_scopes_item_data in self.previously_granted_scopes:
                previously_granted_scopes_item = (
                    previously_granted_scopes_item_data.value
                )
                previously_granted_scopes.append(previously_granted_scopes_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "requestId": request_id,
                "clientName": client_name,
                "resource": resource,
                "scopes": scopes,
                "availableScopes": available_scopes,
                "appliesToAllCurrentResources": applies_to_all_current_resources,
                "requiresConsent": requires_consent,
            }
        )
        if previously_granted_scopes is not UNSET:
            field_dict["previouslyGrantedScopes"] = previously_granted_scopes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        request_id = d.pop("requestId")

        client_name = d.pop("clientName")

        resource = d.pop("resource")

        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = MCPOAuthScope(scopes_item_data)

            scopes.append(scopes_item)

        available_scopes = []
        _available_scopes = d.pop("availableScopes")
        for available_scopes_item_data in _available_scopes:
            available_scopes_item = MCPOAuthScope(available_scopes_item_data)

            available_scopes.append(available_scopes_item)

        applies_to_all_current_resources = d.pop("appliesToAllCurrentResources")

        requires_consent = d.pop("requiresConsent")

        _previously_granted_scopes = d.pop("previouslyGrantedScopes", UNSET)
        previously_granted_scopes: list[MCPOAuthScope] | Unset = UNSET
        if _previously_granted_scopes is not UNSET:
            previously_granted_scopes = []
            for previously_granted_scopes_item_data in _previously_granted_scopes:
                previously_granted_scopes_item = MCPOAuthScope(
                    previously_granted_scopes_item_data
                )

                previously_granted_scopes.append(previously_granted_scopes_item)

        o_auth_authorization_request = cls(
            request_id=request_id,
            client_name=client_name,
            resource=resource,
            scopes=scopes,
            available_scopes=available_scopes,
            applies_to_all_current_resources=applies_to_all_current_resources,
            requires_consent=requires_consent,
            previously_granted_scopes=previously_granted_scopes,
        )

        return o_auth_authorization_request
