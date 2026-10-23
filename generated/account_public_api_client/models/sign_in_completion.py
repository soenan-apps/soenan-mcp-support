from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.sign_in_completion_status import SignInCompletionStatus

T = TypeVar("T", bound="SignInCompletion")


@_attrs_define
class SignInCompletion:
    """
    Attributes:
        status (SignInCompletionStatus):
    """

    status: SignInCompletionStatus

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
        status = SignInCompletionStatus(d.pop("status"))

        sign_in_completion = cls(
            status=status,
        )

        return sign_in_completion
