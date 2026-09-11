from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.chat_event import ChatEvent


T = TypeVar("T", bound="ChatCatchUpPage")


@_attrs_define
class ChatCatchUpPage:
    """
    Attributes:
        events (list[ChatEvent]):
        latest_sequence (int):
        has_more (bool):
    """

    events: list[ChatEvent]
    latest_sequence: int
    has_more: bool

    def to_dict(self) -> dict[str, Any]:
        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        latest_sequence = self.latest_sequence

        has_more = self.has_more

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "events": events,
                "latestSequence": latest_sequence,
                "hasMore": has_more,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.chat_event import ChatEvent

        d = dict(src_dict)
        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = ChatEvent.from_dict(events_item_data)

            events.append(events_item)

        latest_sequence = d.pop("latestSequence")

        has_more = d.pop("hasMore")

        chat_catch_up_page = cls(
            events=events,
            latest_sequence=latest_sequence,
            has_more=has_more,
        )

        return chat_catch_up_page
