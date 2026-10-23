from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.sign_up_completion_status import SignUpCompletionStatus

T = TypeVar("T", bound="SignUpCompletion")


@_attrs_define
class SignUpCompletion:
    """
    Attributes:
        status (SignUpCompletionStatus):
    """

    status: SignUpCompletionStatus

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
        status = SignUpCompletionStatus(d.pop("status"))

        sign_up_completion = cls(
            status=status,
        )

        return sign_up_completion
