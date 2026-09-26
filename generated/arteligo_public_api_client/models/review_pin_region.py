from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.review_pin_region_kind import ReviewPinRegionKind

T = TypeVar("T", bound="ReviewPinRegion")


@_attrs_define
class ReviewPinRegion:
    """
    Attributes:
        kind (ReviewPinRegionKind):
        x (float):
        y (float):
    """

    kind: ReviewPinRegionKind
    x: float
    y: float

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        x = self.x

        y = self.y

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "x": x,
                "y": y,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = ReviewPinRegionKind(d.pop("kind"))

        x = d.pop("x")

        y = d.pop("y")

        review_pin_region = cls(
            kind=kind,
            x=x,
            y=y,
        )

        return review_pin_region
