from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_changes_catch_up_required_reason import (
    RealtimeProjectChangesCatchUpRequiredReason,
)
from ..models.realtime_project_changes_catch_up_required_type import (
    RealtimeProjectChangesCatchUpRequiredType,
)

T = TypeVar("T", bound="RealtimeProjectChangesCatchUpRequired")


@_attrs_define
class RealtimeProjectChangesCatchUpRequired:
    """
    Attributes:
        type_ (RealtimeProjectChangesCatchUpRequiredType):
        after_revision (int):
        reason (RealtimeProjectChangesCatchUpRequiredReason):
    """

    type_: RealtimeProjectChangesCatchUpRequiredType
    after_revision: int
    reason: RealtimeProjectChangesCatchUpRequiredReason

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        after_revision = self.after_revision

        reason = self.reason.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "afterRevision": after_revision,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = RealtimeProjectChangesCatchUpRequiredType(d.pop("type"))

        after_revision = d.pop("afterRevision")

        reason = RealtimeProjectChangesCatchUpRequiredReason(d.pop("reason"))

        realtime_project_changes_catch_up_required = cls(
            type_=type_,
            after_revision=after_revision,
            reason=reason,
        )

        return realtime_project_changes_catch_up_required
