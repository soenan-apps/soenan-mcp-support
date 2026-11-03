from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.o_auth_client_registration_request_grant_types_item import (
    OAuthClientRegistrationRequestGrantTypesItem,
)
from ..models.o_auth_client_registration_request_response_types_item import (
    OAuthClientRegistrationRequestResponseTypesItem,
)
from ..models.o_auth_client_registration_request_token_endpoint_auth_method import (
    OAuthClientRegistrationRequestTokenEndpointAuthMethod,
)

T = TypeVar("T", bound="OAuthClientRegistrationRequest")


@_attrs_define
class OAuthClientRegistrationRequest:
    """
    Attributes:
        client_name (str):
        redirect_uris (list[str]):
        token_endpoint_auth_method (OAuthClientRegistrationRequestTokenEndpointAuthMethod):
        grant_types (list[OAuthClientRegistrationRequestGrantTypesItem]):
        response_types (list[OAuthClientRegistrationRequestResponseTypesItem]):
    """

    client_name: str
    redirect_uris: list[str]
    token_endpoint_auth_method: OAuthClientRegistrationRequestTokenEndpointAuthMethod
    grant_types: list[OAuthClientRegistrationRequestGrantTypesItem]
    response_types: list[OAuthClientRegistrationRequestResponseTypesItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_name = self.client_name

        redirect_uris = self.redirect_uris

        token_endpoint_auth_method = self.token_endpoint_auth_method.value

        grant_types = []
        for grant_types_item_data in self.grant_types:
            grant_types_item = grant_types_item_data.value
            grant_types.append(grant_types_item)

        response_types = []
        for response_types_item_data in self.response_types:
            response_types_item = response_types_item_data.value
            response_types.append(response_types_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_name": client_name,
                "redirect_uris": redirect_uris,
                "token_endpoint_auth_method": token_endpoint_auth_method,
                "grant_types": grant_types,
                "response_types": response_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_name = d.pop("client_name")

        redirect_uris = cast(list[str], d.pop("redirect_uris"))

        token_endpoint_auth_method = (
            OAuthClientRegistrationRequestTokenEndpointAuthMethod(
                d.pop("token_endpoint_auth_method")
            )
        )

        grant_types = []
        _grant_types = d.pop("grant_types")
        for grant_types_item_data in _grant_types:
            grant_types_item = OAuthClientRegistrationRequestGrantTypesItem(
                grant_types_item_data
            )

            grant_types.append(grant_types_item)

        response_types = []
        _response_types = d.pop("response_types")
        for response_types_item_data in _response_types:
            response_types_item = OAuthClientRegistrationRequestResponseTypesItem(
                response_types_item_data
            )

            response_types.append(response_types_item)

        o_auth_client_registration_request = cls(
            client_name=client_name,
            redirect_uris=redirect_uris,
            token_endpoint_auth_method=token_endpoint_auth_method,
            grant_types=grant_types,
            response_types=response_types,
        )

        o_auth_client_registration_request.additional_properties = d
        return o_auth_client_registration_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
