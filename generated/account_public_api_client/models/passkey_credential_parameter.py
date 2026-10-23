from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.passkey_credential_type import PasskeyCredentialType

T = TypeVar("T", bound="PasskeyCredentialParameter")


@_attrs_define
class PasskeyCredentialParameter:
    """
    Attributes:
        type_ (PasskeyCredentialType):
        alg (int):
    """

    type_: PasskeyCredentialType
    alg: int

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        alg = self.alg

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "alg": alg,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = PasskeyCredentialType(d.pop("type"))

        alg = d.pop("alg")

        passkey_credential_parameter = cls(
            type_=type_,
            alg=alg,
        )

        return passkey_credential_parameter
