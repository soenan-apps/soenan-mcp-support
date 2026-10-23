from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.passkey_authentication_completion_status import (
    PasskeyAuthenticationCompletionStatus,
)

T = TypeVar("T", bound="PasskeyAuthenticationCompletion")


@_attrs_define
class PasskeyAuthenticationCompletion:
    """
    Attributes:
        status (PasskeyAuthenticationCompletionStatus):
    """

    status: PasskeyAuthenticationCompletionStatus

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        status = PasskeyAuthenticationCompletionStatus(d.pop("status"))

        passkey_authentication_completion = cls(
            status=status,
        )

        return passkey_authentication_completion
