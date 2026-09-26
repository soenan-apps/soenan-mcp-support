from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_chat_error_code import RealtimeProjectChatErrorCode
from ..models.realtime_project_chat_error_type import RealtimeProjectChatErrorType

T = TypeVar("T", bound="RealtimeProjectChatError")


@_attrs_define
class RealtimeProjectChatError:
    """
    Attributes:
        type_ (RealtimeProjectChatErrorType):
        project_id (str):
        code (RealtimeProjectChatErrorCode):
    """

    type_: RealtimeProjectChatErrorType
    project_id: str
    code: RealtimeProjectChatErrorCode

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        project_id = self.project_id

        code = self.code.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "projectId": project_id,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeProjectChatErrorType(d.pop("type"))

        project_id = d.pop("projectId")

        code = RealtimeProjectChatErrorCode(d.pop("code"))

        realtime_project_chat_error = cls(
            type_=type_,
            project_id=project_id,
            code=code,
        )

        return realtime_project_chat_error
