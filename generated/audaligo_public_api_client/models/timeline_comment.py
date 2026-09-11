from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.comment_reply import CommentReply
    from ..models.file_review_anchor import FileReviewAnchor
    from ..models.member_actor import MemberActor
    from ..models.review_pin_region import ReviewPinRegion
    from ..models.review_rectangle_region import ReviewRectangleRegion
    from ..models.review_time_span import ReviewTimeSpan
    from ..models.stage_review_anchor import StageReviewAnchor


T = TypeVar("T", bound="TimelineComment")


@_attrs_define
class TimelineComment:
    """
    Attributes:
        id (str):
        anchor (FileReviewAnchor | StageReviewAnchor):
        time_span (None | ReviewTimeSpan):
        region (None | ReviewPinRegion | ReviewRectangleRegion):
        tag (None | str):
        body (str):
        author (MemberActor):
        resolved (bool):
        created_at (datetime.datetime):
        replies (list[CommentReply]):
    """

    id: str
    anchor: FileReviewAnchor | StageReviewAnchor
    time_span: None | ReviewTimeSpan
    region: None | ReviewPinRegion | ReviewRectangleRegion
    tag: None | str
    body: str
    author: MemberActor
    resolved: bool
    created_at: datetime.datetime
    replies: list[CommentReply]

    def to_dict(self) -> dict[str, Any]:
        from ..models.file_review_anchor import FileReviewAnchor
        from ..models.review_pin_region import ReviewPinRegion
        from ..models.review_rectangle_region import ReviewRectangleRegion
        from ..models.review_time_span import ReviewTimeSpan

        id = self.id

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

        tag: None | str
        tag = self.tag

        body = self.body

        author = self.author.to_dict()

        resolved = self.resolved

        created_at = self.created_at.isoformat()

        replies = []
        for replies_item_data in self.replies:
            replies_item = replies_item_data.to_dict()
            replies.append(replies_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "anchor": anchor,
                "timeSpan": time_span,
                "region": region,
                "tag": tag,
                "body": body,
                "author": author,
                "resolved": resolved,
                "createdAt": created_at,
                "replies": replies,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.comment_reply import CommentReply
        from ..models.file_review_anchor import FileReviewAnchor
        from ..models.member_actor import MemberActor
        from ..models.review_pin_region import ReviewPinRegion
        from ..models.review_rectangle_region import (
            ReviewRectangleRegion,
        )
        from ..models.review_time_span import ReviewTimeSpan
        from ..models.stage_review_anchor import StageReviewAnchor

        d = dict(src_dict)
        id = d.pop("id")

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

        def _parse_tag(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        tag = _parse_tag(d.pop("tag"))

        body = d.pop("body")

        author = MemberActor.from_dict(d.pop("author"))

        resolved = d.pop("resolved")

        created_at = datetime.datetime.fromisoformat(d.pop("createdAt"))

        replies = []
        _replies = d.pop("replies")
        for replies_item_data in _replies:
            replies_item = CommentReply.from_dict(replies_item_data)

            replies.append(replies_item)

        timeline_comment = cls(
            id=id,
            anchor=anchor,
            time_span=time_span,
            region=region,
            tag=tag,
            body=body,
            author=author,
            resolved=resolved,
            created_at=created_at,
            replies=replies,
        )

        return timeline_comment
