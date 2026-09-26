from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.review_rectangle_region_kind import ReviewRectangleRegionKind

T = TypeVar("T", bound="ReviewRectangleRegion")


@_attrs_define
class ReviewRectangleRegion:
    """
    Attributes:
        kind (ReviewRectangleRegionKind):
        x (float):
        y (float):
        width (float):
        height (float):
    """

    kind: ReviewRectangleRegionKind
    x: float
    y: float
    width: float
    height: float

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        x = self.x

        y = self.y

        width = self.width

        height = self.height

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = ReviewRectangleRegionKind(d.pop("kind"))

        x = d.pop("x")

        y = d.pop("y")

        width = d.pop("width")

        height = d.pop("height")

        review_rectangle_region = cls(
            kind=kind,
            x=x,
            y=y,
            width=width,
            height=height,
        )

        return review_rectangle_region
