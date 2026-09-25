from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_chat_event_hint_type import (
    RealtimeProjectChatEventHintType,
)

T = TypeVar("T", bound="RealtimeProjectChatEventHint")


@_attrs_define
class RealtimeProjectChatEventHint:
    """
    Attributes:
        type_ (RealtimeProjectChatEventHintType):
        project_id (str):
        sequence (int):
    """

    type_: RealtimeProjectChatEventHintType
    project_id: str
    sequence: int

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        project_id = self.project_id

        sequence = self.sequence

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "projectId": project_id,
                "sequence": sequence,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeProjectChatEventHintType(d.pop("type"))

        project_id = d.pop("projectId")

        sequence = d.pop("sequence")

        realtime_project_chat_event_hint = cls(
            type_=type_,
            project_id=project_id,
            sequence=sequence,
        )

        return realtime_project_chat_event_hint
