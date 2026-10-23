from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.passkey_credential_type import PasskeyCredentialType
from ..models.passkey_registration_credential_authenticator_attachment import (
    PasskeyRegistrationCredentialAuthenticatorAttachment,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.passkey_registration_credential_response import (
        PasskeyRegistrationCredentialResponse,
    )


T = TypeVar("T", bound="PasskeyRegistrationCredential")


@_attrs_define
class PasskeyRegistrationCredential:
    """
    Attributes:
        id (str):
        raw_id (str):
        type_ (PasskeyCredentialType):
        response (PasskeyRegistrationCredentialResponse):
        authenticator_attachment (PasskeyRegistrationCredentialAuthenticatorAttachment | Unset):
    """

    id: str
    raw_id: str
    type_: PasskeyCredentialType
    response: PasskeyRegistrationCredentialResponse
    authenticator_attachment: (
        PasskeyRegistrationCredentialAuthenticatorAttachment | Unset
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
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.passkey_registration_credential_response import (
            PasskeyRegistrationCredentialResponse,
        )

        d = dict(src_dict)
        id = d.pop("id")

        raw_id = d.pop("rawId")

        type_ = PasskeyCredentialType(d.pop("type"))

        response = PasskeyRegistrationCredentialResponse.from_dict(d.pop("response"))

        _authenticator_attachment = d.pop("authenticatorAttachment", UNSET)
        authenticator_attachment: (
            PasskeyRegistrationCredentialAuthenticatorAttachment | Unset
        )
        if isinstance(_authenticator_attachment, Unset):
            authenticator_attachment = UNSET
        else:
            authenticator_attachment = (
                PasskeyRegistrationCredentialAuthenticatorAttachment(
                    _authenticator_attachment
                )
            )

        passkey_registration_credential = cls(
            id=id,
            raw_id=raw_id,
            type_=type_,
            response=response,
            authenticator_attachment=authenticator_attachment,
        )

        return passkey_registration_credential
