from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_changes_subscribed_type import (
    RealtimeProjectChangesSubscribedType,
)

T = TypeVar("T", bound="RealtimeProjectChangesSubscribed")


@_attrs_define
class RealtimeProjectChangesSubscribed:
    """
    Attributes:
        type_ (RealtimeProjectChangesSubscribedType):
        revision (int):
    """

    type_: RealtimeProjectChangesSubscribedType
    revision: int

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        revision = self.revision

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "revision": revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeProjectChangesSubscribedType(d.pop("type"))

        revision = d.pop("revision")

        realtime_project_changes_subscribed = cls(
            type_=type_,
            revision=revision,
        )

        return realtime_project_changes_subscribed
