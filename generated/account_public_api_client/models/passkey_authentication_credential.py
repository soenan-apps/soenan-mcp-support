from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.passkey_authentication_credential_authenticator_attachment import (
    PasskeyAuthenticationCredentialAuthenticatorAttachment,
)
from ..models.passkey_credential_type import PasskeyCredentialType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.passkey_authentication_credential_response import (
        PasskeyAuthenticationCredentialResponse,
    )


T = TypeVar("T", bound="PasskeyAuthenticationCredential")


@_attrs_define
class PasskeyAuthenticationCredential:
    """
    Attributes:
        id (str):
        raw_id (str):
        type_ (PasskeyCredentialType):
        response (PasskeyAuthenticationCredentialResponse):
        authenticator_attachment (PasskeyAuthenticationCredentialAuthenticatorAttachment | Unset):
    """

    id: str
    raw_id: str
    type_: PasskeyCredentialType
    response: PasskeyAuthenticationCredentialResponse
    authenticator_attachment: (
        PasskeyAuthenticationCredentialAuthenticatorAttachment | Unset
    ) = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        raw_id = self.raw_id

        type_ = self.type_.value

        response = self.response.to_dict()

        authenticator_attachment: str | Unset = UNSET
        if not isinstance(self.authenticator_attachment, Unset):
            authenticator_attachment = self.authenticator_attachment.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "rawId": raw_id,
                "type": type_,
                "response": response,
            }
        )
        if authenticator_attachment is not UNSET:
            field_dict["authenticatorAttachment"] = authenticator_attachment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.passkey_authentication_credential_response import (
            PasskeyAuthenticationCredentialResponse,
        )

        d = dict(src_dict)
        id = d.pop("id")

        raw_id = d.pop("rawId")

        type_ = PasskeyCredentialType(d.pop("type"))

        response = PasskeyAuthenticationCredentialResponse.from_dict(d.pop("response"))

        _authenticator_attachment = d.pop("authenticatorAttachment", UNSET)
        authenticator_attachment: (
            PasskeyAuthenticationCredentialAuthenticatorAttachment | Unset
        )
        if isinstance(_authenticator_attachment, Unset):
            authenticator_attachment = UNSET
        else:
            authenticator_attachment = (
                PasskeyAuthenticationCredentialAuthenticatorAttachment(
                    _authenticator_attachment
                )
            )

        passkey_authentication_credential = cls(
            id=id,
            raw_id=raw_id,
            type_=type_,
            response=response,
            authenticator_attachment=authenticator_attachment,
        )

        return passkey_authentication_credential
