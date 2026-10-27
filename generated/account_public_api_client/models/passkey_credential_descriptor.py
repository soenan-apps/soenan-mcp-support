from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.passkey_credential_type import PasskeyCredentialType

T = TypeVar("T", bound="PasskeyCredentialDescriptor")


@_attrs_define
class PasskeyCredentialDescriptor:
    """
    Attributes:
        type_ (PasskeyCredentialType):
        id (str):
        transports (list[str]):
    """

    type_: PasskeyCredentialType
    id: str
    transports: list[str]

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        id = self.id

        transports = self.transports

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "id": id,
                "transports": transports,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = PasskeyCredentialType(d.pop("type"))

        id = d.pop("id")

        transports = cast(list[str], d.pop("transports"))

        passkey_credential_descriptor = cls(
            type_=type_,
            id=id,
            transports=transports,
        )

        return passkey_credential_descriptor
