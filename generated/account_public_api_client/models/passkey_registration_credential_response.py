from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="PasskeyRegistrationCredentialResponse")


@_attrs_define
class PasskeyRegistrationCredentialResponse:
    """
    Attributes:
        client_data_json (str):
        attestation_object (str):
        transports (list[str]):
    """

    client_data_json: str
    attestation_object: str
    transports: list[str]

    def to_dict(self) -> dict[str, Any]:
        client_data_json = self.client_data_json

        attestation_object = self.attestation_object

        transports = self.transports

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clientDataJSON": client_data_json,
                "attestationObject": attestation_object,
                "transports": transports,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        client_data_json = d.pop("clientDataJSON")

        attestation_object = d.pop("attestationObject")

        transports = cast(list[str], d.pop("transports"))

        passkey_registration_credential_response = cls(
            client_data_json=client_data_json,
            attestation_object=attestation_object,
            transports=transports,
        )

        return passkey_registration_credential_response
