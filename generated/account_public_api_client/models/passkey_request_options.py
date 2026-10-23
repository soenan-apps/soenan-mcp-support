from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.passkey_request_options_user_verification import (
    PasskeyRequestOptionsUserVerification,
)

T = TypeVar("T", bound="PasskeyRequestOptions")


@_attrs_define
class PasskeyRequestOptions:
    """
    Attributes:
        challenge (str):
        timeout (int):
        rp_id (str):
        user_verification (PasskeyRequestOptionsUserVerification):
    """

    challenge: str
    timeout: int
    rp_id: str
    user_verification: PasskeyRequestOptionsUserVerification

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        timeout = self.timeout

        rp_id = self.rp_id

        user_verification = self.user_verification.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "timeout": timeout,
                "rpId": rp_id,
                "userVerification": user_verification,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        challenge = d.pop("challenge")

        timeout = d.pop("timeout")

        rp_id = d.pop("rpId")

        user_verification = PasskeyRequestOptionsUserVerification(
            d.pop("userVerification")
        )

        passkey_request_options = cls(
            challenge=challenge,
            timeout=timeout,
            rp_id=rp_id,
            user_verification=user_verification,
        )

        return passkey_request_options
