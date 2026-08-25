from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import parse_datetime

if TYPE_CHECKING:
    from ..models.comment_reply import CommentReply
    from ..models.member_actor import MemberActor


T = TypeVar("T", bound="TimelineComment")


@_attrs_define
class TimelineComment:
    """
    Attributes:
        id (str):
        version_id (None | str):
        time_seconds (float | None):
        end_time_seconds (float | None): Exclusive end of a reviewed time range. Null means the comment is anchored to
            the point at timeSeconds.
        tag (None | str):
        body (str):
        author (MemberActor):
        resolved (bool):
        created_at (datetime.datetime):
        replies (list[CommentReply]):
    """

    id: str
    version_id: None | str
    time_seconds: float | None
    end_time_seconds: float | None
    tag: None | str
    body: str
    author: MemberActor
    resolved: bool
    created_at: datetime.datetime
    replies: list[CommentReply]

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        version_id: None | str
        version_id = self.version_id

        time_seconds: float | None
        time_seconds = self.time_seconds

        end_time_seconds: float | None
        end_time_seconds = self.end_time_seconds

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
                "versionId": version_id,
                "timeSeconds": time_seconds,
                "endTimeSeconds": end_time_seconds,
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.comment_reply import CommentReply
        from ..models.member_actor import MemberActor

        d = dict(src_dict)
        id = d.pop("id")

        def _parse_version_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        version_id = _parse_version_id(d.pop("versionId"))

        def _parse_time_seconds(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        time_seconds = _parse_time_seconds(d.pop("timeSeconds"))

        def _parse_end_time_seconds(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        end_time_seconds = _parse_end_time_seconds(d.pop("endTimeSeconds"))

        def _parse_tag(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        tag = _parse_tag(d.pop("tag"))

        body = d.pop("body")

        author = MemberActor.from_dict(d.pop("author"))

        resolved = d.pop("resolved")

        created_at = parse_datetime(d.pop("createdAt"))

        replies = []
        _replies = d.pop("replies")
        for replies_item_data in _replies:
            replies_item = CommentReply.from_dict(replies_item_data)

            replies.append(replies_item)

        timeline_comment = cls(
            id=id,
            version_id=version_id,
            time_seconds=time_seconds,
            end_time_seconds=end_time_seconds,
            tag=tag,
            body=body,
            author=author,
            resolved=resolved,
            created_at=created_at,
            replies=replies,
        )

        return timeline_comment
