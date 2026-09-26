from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_error_code import RealtimeErrorCode
from ..models.realtime_error_type import RealtimeErrorType

T = TypeVar("T", bound="RealtimeError")


@_attrs_define
class RealtimeError:
    """
    Attributes:
        type_ (RealtimeErrorType):
        code (RealtimeErrorCode):
    """

    type_: RealtimeErrorType
    code: RealtimeErrorCode

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        code = self.code.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeErrorType(d.pop("type"))

        code = RealtimeErrorCode(d.pop("code"))

        realtime_error = cls(
            type_=type_,
            code=code,
        )

        return realtime_error
