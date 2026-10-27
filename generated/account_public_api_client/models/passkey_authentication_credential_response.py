from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PasskeyAuthenticationCredentialResponse")


@_attrs_define
class PasskeyAuthenticationCredentialResponse:
    """
    Attributes:
        client_data_json (str):
        authenticator_data (str):
        signature (str):
        user_handle (str | Unset):
        attestation_object (str | Unset):
    """

    client_data_json: str
    authenticator_data: str
    signature: str
    user_handle: str | Unset = UNSET
    attestation_object: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        client_data_json = self.client_data_json

        authenticator_data = self.authenticator_data

        signature = self.signature

        user_handle = self.user_handle

        attestation_object = self.attestation_object

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clientDataJSON": client_data_json,
                "authenticatorData": authenticator_data,
                "signature": signature,
            }
        )
        if user_handle is not UNSET:
            field_dict["userHandle"] = user_handle
        if attestation_object is not UNSET:
            field_dict["attestationObject"] = attestation_object

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_data_json = d.pop("clientDataJSON")

        authenticator_data = d.pop("authenticatorData")

        signature = d.pop("signature")

        user_handle = d.pop("userHandle", UNSET)

        attestation_object = d.pop("attestationObject", UNSET)

        passkey_authentication_credential_response = cls(
            client_data_json=client_data_json,
            authenticator_data=authenticator_data,
            signature=signature,
            user_handle=user_handle,
            attestation_object=attestation_object,
        )

        return passkey_authentication_credential_response
