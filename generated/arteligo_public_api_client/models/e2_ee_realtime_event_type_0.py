from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.e2_ee_realtime_event_type_0_type import E2EeRealtimeEventType0Type

T = TypeVar("T", bound="E2EeRealtimeEventType0")


@_attrs_define
class E2EeRealtimeEventType0:
    """
    Attributes:
        type_ (E2EeRealtimeEventType0Type):
        scope_id (str):
    """

    type_: E2EeRealtimeEventType0Type
    scope_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        scope_id = self.scope_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "scope_id": scope_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = E2EeRealtimeEventType0Type(d.pop("type"))

        scope_id = d.pop("scope_id")

        e2_ee_realtime_event_type_0 = cls(
            type_=type_,
            scope_id=scope_id,
        )

        e2_ee_realtime_event_type_0.additional_properties = d
        return e2_ee_realtime_event_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
