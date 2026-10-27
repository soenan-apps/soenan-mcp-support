from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_realtime_event_type_2_type import E2EeRealtimeEventType2Type

T = TypeVar("T", bound="E2EeRealtimeEventType2")


@_attrs_define
class E2EeRealtimeEventType2:
    """
    Attributes:
        type_ (E2EeRealtimeEventType2Type):
        root_operation_id (str):
    """

    type_: E2EeRealtimeEventType2Type
    root_operation_id: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        root_operation_id = self.root_operation_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "root_operation_id": root_operation_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = E2EeRealtimeEventType2Type(d.pop("type"))

        root_operation_id = d.pop("root_operation_id")

        e2_ee_realtime_event_type_2 = cls(
            type_=type_,
            root_operation_id=root_operation_id,
        )

        return e2_ee_realtime_event_type_2
