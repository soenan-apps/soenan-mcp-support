from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.passkey_authentication_credential import (
        PasskeyAuthenticationCredential,
    )


T = TypeVar("T", bound="PasskeyAuthenticationRequest")


@_attrs_define
class PasskeyAuthenticationRequest:
    """
    Attributes:
        ceremony_id (UUID):
        credential (PasskeyAuthenticationCredential):
    """

    ceremony_id: UUID
    credential: PasskeyAuthenticationCredential

    def to_dict(self) -> dict[str, Any]:
        ceremony_id = str(self.ceremony_id)

        credential = self.credential.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ceremonyId": ceremony_id,
                "credential": credential,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.passkey_authentication_credential import (
            PasskeyAuthenticationCredential,
        )

        d = dict(src_dict)
        ceremony_id = UUID(d.pop("ceremonyId"))

        credential = PasskeyAuthenticationCredential.from_dict(d.pop("credential"))

        passkey_authentication_request = cls(
            ceremony_id=ceremony_id,
            credential=credential,
        )

        return passkey_authentication_request
