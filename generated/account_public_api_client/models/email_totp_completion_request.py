from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="EmailTOTPCompletionRequest")


@_attrs_define
class EmailTOTPCompletionRequest:
    """
    Attributes:
        token (str): A 256-bit random token encoded as unpadded base64url.
        code (str):
    """

    token: str
    code: str

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        code = self.code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "token": token,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        token = d.pop("token")

        code = d.pop("code")

        email_totp_completion_request = cls(
            token=token,
            code=code,
        )

        return email_totp_completion_request
