from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.o_auth_authorization_server_metadata_code_challenge_methods_supported_item import (
    OAuthAuthorizationServerMetadataCodeChallengeMethodsSupportedItem,
)
from ..models.o_auth_authorization_server_metadata_grant_types_supported_item import (
    OAuthAuthorizationServerMetadataGrantTypesSupportedItem,
)
from ..models.o_auth_authorization_server_metadata_response_types_supported_item import (
    OAuthAuthorizationServerMetadataResponseTypesSupportedItem,
)
from ..models.o_auth_authorization_server_metadata_token_endpoint_auth_methods_supported_item import (
    OAuthAuthorizationServerMetadataTokenEndpointAuthMethodsSupportedItem,
)

T = TypeVar("T", bound="OAuthAuthorizationServerMetadata")


@_attrs_define
class OAuthAuthorizationServerMetadata:
    """
    Attributes:
        issuer (str):
        authorization_endpoint (str):
        jwks_uri (str):
        token_endpoint (str):
        registration_endpoint (str):
        revocation_endpoint (str):
        response_types_supported (list[OAuthAuthorizationServerMetadataResponseTypesSupportedItem]):
        grant_types_supported (list[OAuthAuthorizationServerMetadataGrantTypesSupportedItem]):
        code_challenge_methods_supported (list[OAuthAuthorizationServerMetadataCodeChallengeMethodsSupportedItem]):
        token_endpoint_auth_methods_supported
            (list[OAuthAuthorizationServerMetadataTokenEndpointAuthMethodsSupportedItem]):
        scopes_supported (list[str]):
        authorization_response_iss_parameter_supported (bool):
        client_id_metadata_document_supported (bool):
    """

    issuer: str
    authorization_endpoint: str
    jwks_uri: str
    token_endpoint: str
    registration_endpoint: str
    revocation_endpoint: str
    response_types_supported: list[
        OAuthAuthorizationServerMetadataResponseTypesSupportedItem
    ]
    grant_types_supported: list[OAuthAuthorizationServerMetadataGrantTypesSupportedItem]
    code_challenge_methods_supported: list[
        OAuthAuthorizationServerMetadataCodeChallengeMethodsSupportedItem
    ]
    token_endpoint_auth_methods_supported: list[
        OAuthAuthorizationServerMetadataTokenEndpointAuthMethodsSupportedItem
    ]
    scopes_supported: list[str]
    authorization_response_iss_parameter_supported: bool
    client_id_metadata_document_supported: bool

    def to_dict(self) -> dict[str, Any]:
        issuer = self.issuer

        authorization_endpoint = self.authorization_endpoint

        jwks_uri = self.jwks_uri

        token_endpoint = self.token_endpoint

        registration_endpoint = self.registration_endpoint

        revocation_endpoint = self.revocation_endpoint

        response_types_supported = []
        for response_types_supported_item_data in self.response_types_supported:
            response_types_supported_item = response_types_supported_item_data.value
            response_types_supported.append(response_types_supported_item)

        grant_types_supported = []
        for grant_types_supported_item_data in self.grant_types_supported:
            grant_types_supported_item = grant_types_supported_item_data.value
            grant_types_supported.append(grant_types_supported_item)

        code_challenge_methods_supported = []
        for (
            code_challenge_methods_supported_item_data
        ) in self.code_challenge_methods_supported:
            code_challenge_methods_supported_item = (
                code_challenge_methods_supported_item_data.value
            )
            code_challenge_methods_supported.append(
                code_challenge_methods_supported_item
            )

        token_endpoint_auth_methods_supported = []
        for (
            token_endpoint_auth_methods_supported_item_data
        ) in self.token_endpoint_auth_methods_supported:
            token_endpoint_auth_methods_supported_item = (
                token_endpoint_auth_methods_supported_item_data.value
            )
            token_endpoint_auth_methods_supported.append(
                token_endpoint_auth_methods_supported_item
            )

        scopes_supported = self.scopes_supported

        authorization_response_iss_parameter_supported = (
            self.authorization_response_iss_parameter_supported
        )

        client_id_metadata_document_supported = (
            self.client_id_metadata_document_supported
        )

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "issuer": issuer,
                "authorization_endpoint": authorization_endpoint,
                "jwks_uri": jwks_uri,
                "token_endpoint": token_endpoint,
                "registration_endpoint": registration_endpoint,
                "revocation_endpoint": revocation_endpoint,
                "response_types_supported": response_types_supported,
                "grant_types_supported": grant_types_supported,
                "code_challenge_methods_supported": code_challenge_methods_supported,
                "token_endpoint_auth_methods_supported": token_endpoint_auth_methods_supported,
                "scopes_supported": scopes_supported,
                "authorization_response_iss_parameter_supported": authorization_response_iss_parameter_supported,
                "client_id_metadata_document_supported": client_id_metadata_document_supported,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        issuer = d.pop("issuer")

        authorization_endpoint = d.pop("authorization_endpoint")

        jwks_uri = d.pop("jwks_uri")

        token_endpoint = d.pop("token_endpoint")

        registration_endpoint = d.pop("registration_endpoint")

        revocation_endpoint = d.pop("revocation_endpoint")

        response_types_supported = []
        _response_types_supported = d.pop("response_types_supported")
        for response_types_supported_item_data in _response_types_supported:
            response_types_supported_item = (
                OAuthAuthorizationServerMetadataResponseTypesSupportedItem(
                    response_types_supported_item_data
                )
            )

            response_types_supported.append(response_types_supported_item)

        grant_types_supported = []
        _grant_types_supported = d.pop("grant_types_supported")
        for grant_types_supported_item_data in _grant_types_supported:
            grant_types_supported_item = (
                OAuthAuthorizationServerMetadataGrantTypesSupportedItem(
                    grant_types_supported_item_data
                )
            )

            grant_types_supported.append(grant_types_supported_item)

        code_challenge_methods_supported = []
        _code_challenge_methods_supported = d.pop("code_challenge_methods_supported")
        for (
            code_challenge_methods_supported_item_data
        ) in _code_challenge_methods_supported:
            code_challenge_methods_supported_item = (
                OAuthAuthorizationServerMetadataCodeChallengeMethodsSupportedItem(
                    code_challenge_methods_supported_item_data
                )
            )

            code_challenge_methods_supported.append(
                code_challenge_methods_supported_item
            )

        token_endpoint_auth_methods_supported = []
        _token_endpoint_auth_methods_supported = d.pop(
            "token_endpoint_auth_methods_supported"
        )
        for (
            token_endpoint_auth_methods_supported_item_data
        ) in _token_endpoint_auth_methods_supported:
            token_endpoint_auth_methods_supported_item = (
                OAuthAuthorizationServerMetadataTokenEndpointAuthMethodsSupportedItem(
                    token_endpoint_auth_methods_supported_item_data
                )
            )

            token_endpoint_auth_methods_supported.append(
                token_endpoint_auth_methods_supported_item
            )

        scopes_supported = cast(list[str], d.pop("scopes_supported"))

        authorization_response_iss_parameter_supported = d.pop(
            "authorization_response_iss_parameter_supported"
        )

        client_id_metadata_document_supported = d.pop(
            "client_id_metadata_document_supported"
        )

        o_auth_authorization_server_metadata = cls(
            issuer=issuer,
            authorization_endpoint=authorization_endpoint,
            jwks_uri=jwks_uri,
            token_endpoint=token_endpoint,
            registration_endpoint=registration_endpoint,
            revocation_endpoint=revocation_endpoint,
            response_types_supported=response_types_supported,
            grant_types_supported=grant_types_supported,
            code_challenge_methods_supported=code_challenge_methods_supported,
            token_endpoint_auth_methods_supported=token_endpoint_auth_methods_supported,
            scopes_supported=scopes_supported,
            authorization_response_iss_parameter_supported=authorization_response_iss_parameter_supported,
            client_id_metadata_document_supported=client_id_metadata_document_supported,
        )

        return o_auth_authorization_server_metadata
