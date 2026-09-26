from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.realtime_project_summaries_invalidated_type import (
    RealtimeProjectSummariesInvalidatedType,
)

T = TypeVar("T", bound="RealtimeProjectSummariesInvalidated")


@_attrs_define
class RealtimeProjectSummariesInvalidated:
    """
    Attributes:
        type_ (RealtimeProjectSummariesInvalidatedType):
        revision (int):
    """

    type_: RealtimeProjectSummariesInvalidatedType
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
        type_ = RealtimeProjectSummariesInvalidatedType(d.pop("type"))

        revision = d.pop("revision")

        realtime_project_summaries_invalidated = cls(
            type_=type_,
            revision=revision,
        )

        return realtime_project_summaries_invalidated
