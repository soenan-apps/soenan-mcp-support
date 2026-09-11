from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ReviewTimeSpan")


@_attrs_define
class ReviewTimeSpan:
    """
    Attributes:
        start_seconds (float):
        end_seconds (float | None): Exclusive end of a reviewed time range.
    """

    start_seconds: float
    end_seconds: float | None

    def to_dict(self) -> dict[str, Any]:
        start_seconds = self.start_seconds

        end_seconds: float | None
        end_seconds = self.end_seconds

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "startSeconds": start_seconds,
                "endSeconds": end_seconds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        start_seconds = d.pop("startSeconds")

        def _parse_end_seconds(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        end_seconds = _parse_end_seconds(d.pop("endSeconds"))

        review_time_span = cls(
            start_seconds=start_seconds,
            end_seconds=end_seconds,
        )

        return review_time_span
