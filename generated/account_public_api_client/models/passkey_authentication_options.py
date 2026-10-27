from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.passkey_request_options import PasskeyRequestOptions


T = TypeVar("T", bound="PasskeyAuthenticationOptions")


@_attrs_define
class PasskeyAuthenticationOptions:
    """
    Attributes:
        ceremony_id (UUID):
        public_key (PasskeyRequestOptions):
    """

    ceremony_id: UUID
    public_key: PasskeyRequestOptions

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
        from ..models.passkey_request_options import PasskeyRequestOptions

        d = dict(src_dict)
        ceremony_id = UUID(d.pop("ceremonyId"))

        public_key = PasskeyRequestOptions.from_dict(d.pop("publicKey"))

        passkey_authentication_options = cls(
            ceremony_id=ceremony_id,
            public_key=public_key,
        )

        return passkey_authentication_options
