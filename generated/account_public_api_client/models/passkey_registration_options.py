from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.passkey_creation_options import PasskeyCreationOptions


T = TypeVar("T", bound="PasskeyRegistrationOptions")


@_attrs_define
class PasskeyRegistrationOptions:
    """
    Attributes:
        ceremony_id (UUID):
        public_key (PasskeyCreationOptions):
    """

    ceremony_id: UUID
    public_key: PasskeyCreationOptions

    def to_dict(self) -> dict[str, Any]:
        ceremony_id = str(self.ceremony_id)

        public_key = self.public_key.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ceremonyId": ceremony_id,
                "publicKey": public_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.passkey_creation_options import PasskeyCreationOptions

        d = dict(src_dict)
        ceremony_id = UUID(d.pop("ceremonyId"))

        public_key = PasskeyCreationOptions.from_dict(d.pop("publicKey"))

        passkey_registration_options = cls(
            ceremony_id=ceremony_id,
            public_key=public_key,
        )

        return passkey_registration_options
