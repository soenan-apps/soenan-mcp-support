from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_chat_catch_up_required_reason import (
    RealtimeProjectChatCatchUpRequiredReason,
)
from ..models.realtime_project_chat_catch_up_required_type import (
    RealtimeProjectChatCatchUpRequiredType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="RealtimeProjectChatCatchUpRequired")


@_attrs_define
class RealtimeProjectChatCatchUpRequired:
    """
    Attributes:
        type_ (RealtimeProjectChatCatchUpRequiredType):
        project_id (str):
        after (int):
        reason (RealtimeProjectChatCatchUpRequiredReason):
        latest_sequence (int | Unset):
    """

    type_: RealtimeProjectChatCatchUpRequiredType
    project_id: str
    after: int
    reason: RealtimeProjectChatCatchUpRequiredReason
    latest_sequence: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        project_id = self.project_id

        after = self.after

        reason = self.reason.value

        latest_sequence = self.latest_sequence

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "projectId": project_id,
                "after": after,
                "reason": reason,
            }
        )
        if latest_sequence is not UNSET:
            field_dict["latestSequence"] = latest_sequence

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeProjectChatCatchUpRequiredType(d.pop("type"))

        project_id = d.pop("projectId")

        after = d.pop("after")

        reason = RealtimeProjectChatCatchUpRequiredReason(d.pop("reason"))

        latest_sequence = d.pop("latestSequence", UNSET)

        realtime_project_chat_catch_up_required = cls(
            type_=type_,
            project_id=project_id,
            after=after,
            reason=reason,
            latest_sequence=latest_sequence,
        )

        return realtime_project_chat_catch_up_required
