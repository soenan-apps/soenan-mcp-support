from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_chat_subscribed_type import (
    RealtimeProjectChatSubscribedType,
)

T = TypeVar("T", bound="RealtimeProjectChatSubscribed")


@_attrs_define
class RealtimeProjectChatSubscribed:
    """
    Attributes:
        type_ (RealtimeProjectChatSubscribedType):
        project_id (str):
        after (int):
        latest_sequence (int):
    """

    type_: RealtimeProjectChatSubscribedType
    project_id: str
    after: int
    latest_sequence: int

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        project_id = self.project_id

        after = self.after

        latest_sequence = self.latest_sequence

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "projectId": project_id,
                "after": after,
                "latestSequence": latest_sequence,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeProjectChatSubscribedType(d.pop("type"))

        project_id = d.pop("projectId")

        after = d.pop("after")

        latest_sequence = d.pop("latestSequence")

        realtime_project_chat_subscribed = cls(
            type_=type_,
            project_id=project_id,
            after=after,
            latest_sequence=latest_sequence,
        )

        return realtime_project_chat_subscribed
