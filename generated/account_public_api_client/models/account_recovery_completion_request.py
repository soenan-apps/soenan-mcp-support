from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="AccountRecoveryCompletionRequest")


@_attrs_define
class AccountRecoveryCompletionRequest:
    """
    Attributes:
        token (str): A 256-bit random token encoded as unpadded base64url.
        new_password (str):
        code (str):
    """

    token: str
    new_password: str
    code: str

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        new_password = self.new_password

        code = self.code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "token": token,
                "newPassword": new_password,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        token = d.pop("token")

        new_password = d.pop("newPassword")

        code = d.pop("code")

        account_recovery_completion_request = cls(
            token=token,
            new_password=new_password,
            code=code,
        )

        return account_recovery_completion_request
