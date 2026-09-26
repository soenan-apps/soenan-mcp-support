from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.error_code import ErrorCode

T = TypeVar("T", bound="ErrorBody")


@_attrs_define
class ErrorBody:
    """
    Attributes:
        code (ErrorCode):
    """

    code: ErrorCode

    def to_dict(self) -> dict[str, Any]:
        code = self.code.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        code = ErrorCode(d.pop("code"))

        error_body = cls(
            code=code,
        )

        return error_body
