from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.passkey_authenticator_selection_resident_key import (
    PasskeyAuthenticatorSelectionResidentKey,
)
from ..models.passkey_authenticator_selection_user_verification import (
    PasskeyAuthenticatorSelectionUserVerification,
)

T = TypeVar("T", bound="PasskeyAuthenticatorSelection")


@_attrs_define
class PasskeyAuthenticatorSelection:
    """
    Attributes:
        resident_key (PasskeyAuthenticatorSelectionResidentKey):
        require_resident_key (bool):
        user_verification (PasskeyAuthenticatorSelectionUserVerification):
    """

    resident_key: PasskeyAuthenticatorSelectionResidentKey
    require_resident_key: bool
    user_verification: PasskeyAuthenticatorSelectionUserVerification

    def to_dict(self) -> dict[str, Any]:
        resident_key = self.resident_key.value

        require_resident_key = self.require_resident_key

        user_verification = self.user_verification.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "residentKey": resident_key,
                "requireResidentKey": require_resident_key,
                "userVerification": user_verification,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resident_key = PasskeyAuthenticatorSelectionResidentKey(d.pop("residentKey"))

        require_resident_key = d.pop("requireResidentKey")

        user_verification = PasskeyAuthenticatorSelectionUserVerification(
            d.pop("userVerification")
        )

        passkey_authenticator_selection = cls(
            resident_key=resident_key,
            require_resident_key=require_resident_key,
            user_verification=user_verification,
        )

        return passkey_authenticator_selection
