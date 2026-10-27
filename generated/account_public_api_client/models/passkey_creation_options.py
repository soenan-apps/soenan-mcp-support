from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.passkey_creation_options_attestation import (
    PasskeyCreationOptionsAttestation,
)

if TYPE_CHECKING:
    from ..models.passkey_authenticator_selection import PasskeyAuthenticatorSelection
    from ..models.passkey_credential_descriptor import PasskeyCredentialDescriptor
    from ..models.passkey_credential_parameter import PasskeyCredentialParameter
    from ..models.passkey_relying_party import PasskeyRelyingParty
    from ..models.passkey_user import PasskeyUser


T = TypeVar("T", bound="PasskeyCreationOptions")


@_attrs_define
class PasskeyCreationOptions:
    """
    Attributes:
        challenge (str):
        rp (PasskeyRelyingParty):
        user (PasskeyUser):
        pub_key_cred_params (list[PasskeyCredentialParameter]):
        timeout (int):
        attestation (PasskeyCreationOptionsAttestation):
        authenticator_selection (PasskeyAuthenticatorSelection):
        exclude_credentials (list[PasskeyCredentialDescriptor]):
    """

    challenge: str
    rp: PasskeyRelyingParty
    user: PasskeyUser
    pub_key_cred_params: list[PasskeyCredentialParameter]
    timeout: int
    attestation: PasskeyCreationOptionsAttestation
    authenticator_selection: PasskeyAuthenticatorSelection
    exclude_credentials: list[PasskeyCredentialDescriptor]

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        rp = self.rp.to_dict()

        user = self.user.to_dict()

        pub_key_cred_params = []
        for pub_key_cred_params_item_data in self.pub_key_cred_params:
            pub_key_cred_params_item = pub_key_cred_params_item_data.to_dict()
            pub_key_cred_params.append(pub_key_cred_params_item)

        timeout = self.timeout

        attestation = self.attestation.value

        authenticator_selection = self.authenticator_selection.to_dict()

        exclude_credentials = []
        for exclude_credentials_item_data in self.exclude_credentials:
            exclude_credentials_item = exclude_credentials_item_data.to_dict()
            exclude_credentials.append(exclude_credentials_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "rp": rp,
                "user": user,
                "pubKeyCredParams": pub_key_cred_params,
                "timeout": timeout,
                "attestation": attestation,
                "authenticatorSelection": authenticator_selection,
                "excludeCredentials": exclude_credentials,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.passkey_authenticator_selection import (
            PasskeyAuthenticatorSelection,
        )
        from ..models.passkey_credential_descriptor import PasskeyCredentialDescriptor
        from ..models.passkey_credential_parameter import PasskeyCredentialParameter
        from ..models.passkey_relying_party import PasskeyRelyingParty
        from ..models.passkey_user import PasskeyUser

        d = dict(src_dict)
        challenge = d.pop("challenge")

        rp = PasskeyRelyingParty.from_dict(d.pop("rp"))

        user = PasskeyUser.from_dict(d.pop("user"))

        pub_key_cred_params = []
        _pub_key_cred_params = d.pop("pubKeyCredParams")
        for pub_key_cred_params_item_data in _pub_key_cred_params:
            pub_key_cred_params_item = PasskeyCredentialParameter.from_dict(
                pub_key_cred_params_item_data
            )

            pub_key_cred_params.append(pub_key_cred_params_item)

        timeout = d.pop("timeout")

        attestation = PasskeyCreationOptionsAttestation(d.pop("attestation"))

        authenticator_selection = PasskeyAuthenticatorSelection.from_dict(
            d.pop("authenticatorSelection")
        )

        exclude_credentials = []
        _exclude_credentials = d.pop("excludeCredentials")
        for exclude_credentials_item_data in _exclude_credentials:
            exclude_credentials_item = PasskeyCredentialDescriptor.from_dict(
                exclude_credentials_item_data
            )

            exclude_credentials.append(exclude_credentials_item)

        passkey_creation_options = cls(
            challenge=challenge,
            rp=rp,
            user=user,
            pub_key_cred_params=pub_key_cred_params,
            timeout=timeout,
            attestation=attestation,
            authenticator_selection=authenticator_selection,
            exclude_credentials=exclude_credentials,
        )

        return passkey_creation_options
