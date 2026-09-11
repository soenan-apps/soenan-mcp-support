from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.file_review_anchor import FileReviewAnchor
    from ..models.review_pin_region import ReviewPinRegion
    from ..models.review_rectangle_region import ReviewRectangleRegion
    from ..models.review_time_span import ReviewTimeSpan
    from ..models.stage_review_anchor import StageReviewAnchor


T = TypeVar("T", bound="TimelineCommentRequest")


@_attrs_define
class TimelineCommentRequest:
    """
    Attributes:
        anchor (FileReviewAnchor | StageReviewAnchor):
        time_span (None | ReviewTimeSpan):
        region (None | ReviewPinRegion | ReviewRectangleRegion):
        tag (str):
        body (str):
    """

    anchor: FileReviewAnchor | StageReviewAnchor
    time_span: None | ReviewTimeSpan
    region: None | ReviewPinRegion | ReviewRectangleRegion
    tag: str
    body: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.file_review_anchor import FileReviewAnchor
        from ..models.review_pin_region import ReviewPinRegion
        from ..models.review_rectangle_region import (
            ReviewRectangleRegion,
        )
        from ..models.review_time_span import ReviewTimeSpan

        anchor: dict[str, Any]
        if isinstance(self.anchor, FileReviewAnchor):
            anchor = self.anchor.to_dict()
        else:
            anchor = self.anchor.to_dict()

        time_span: dict[str, Any] | None
        if isinstance(self.time_span, ReviewTimeSpan):
            time_span = self.time_span.to_dict()
        else:
            time_span = self.time_span

        region: dict[str, Any] | None
        if isinstance(self.region, ReviewPinRegion) or isinstance(
            self.region, ReviewRectangleRegion
        ):
            region = self.region.to_dict()
        else:
            region = self.region

        tag = self.tag

        body = self.body

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "anchor": anchor,
                "timeSpan": time_span,
                "region": region,
                "tag": tag,
                "body": body,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.file_review_anchor import FileReviewAnchor
        from ..models.review_pin_region import ReviewPinRegion
        from ..models.review_rectangle_region import (
            ReviewRectangleRegion,
        )
        from ..models.review_time_span import ReviewTimeSpan
        from ..models.stage_review_anchor import StageReviewAnchor

        d = dict(src_dict)

        def _parse_anchor(data: object) -> FileReviewAnchor | StageReviewAnchor:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_review_anchor_type_0 = FileReviewAnchor.from_dict(
                    data
                )

                return componentsschemas_review_anchor_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_review_anchor_type_1 = StageReviewAnchor.from_dict(data)

            return componentsschemas_review_anchor_type_1

        anchor = _parse_anchor(d.pop("anchor"))

        def _parse_time_span(data: object) -> None | ReviewTimeSpan:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                time_span_type_1 = ReviewTimeSpan.from_dict(data)

                return time_span_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReviewTimeSpan, data)

        time_span = _parse_time_span(d.pop("timeSpan"))

        def _parse_region(
            data: object,
        ) -> None | ReviewPinRegion | ReviewRectangleRegion:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_review_region_type_0 = ReviewPinRegion.from_dict(data)

                return componentsschemas_review_region_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_review_region_type_1 = (
                    ReviewRectangleRegion.from_dict(data)
                )

                return componentsschemas_review_region_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReviewPinRegion | ReviewRectangleRegion, data)

        region = _parse_region(d.pop("region"))

        tag = d.pop("tag")

        body = d.pop("body")

        timeline_comment_request = cls(
            anchor=anchor,
            time_span=time_span,
            region=region,
            tag=tag,
            body=body,
        )

        return timeline_comment_request
