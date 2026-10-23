from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="TOTPCompletionRequest")


@_attrs_define
class TOTPCompletionRequest:
    """
    Attributes:
        challenge_id (str):
        code (str):
    """

    challenge_id: str
    code: str

    def to_dict(self) -> dict[str, Any]:
        challenge_id = self.challenge_id

        code = self.code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challengeId": challenge_id,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        challenge_id = d.pop("challengeId")

        code = d.pop("code")

        totp_completion_request = cls(
            challenge_id=challenge_id,
            code=code,
        )

        return totp_completion_request
