from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.passkey_registration_credential import PasskeyRegistrationCredential


T = TypeVar("T", bound="PasskeyRegistrationRequest")


@_attrs_define
class PasskeyRegistrationRequest:
    """
    Attributes:
        ceremony_id (UUID):
        name (str):
        credential (PasskeyRegistrationCredential):
    """

    ceremony_id: UUID
    name: str
    credential: PasskeyRegistrationCredential

    def to_dict(self) -> dict[str, Any]:
        ceremony_id = str(self.ceremony_id)

        name = self.name

        credential = self.credential.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ceremonyId": ceremony_id,
                "name": name,
                "credential": credential,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.passkey_registration_credential import (
            PasskeyRegistrationCredential,
        )

        d = dict(src_dict)
        ceremony_id = UUID(d.pop("ceremonyId"))

        name = d.pop("name")

        credential = PasskeyRegistrationCredential.from_dict(d.pop("credential"))

        passkey_registration_request = cls(
            ceremony_id=ceremony_id,
            name=name,
            credential=credential,
        )

        return passkey_registration_request
