from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.timeline_comment import TimelineComment


T = TypeVar("T", bound="CommentEnvelope")


@_attrs_define
class CommentEnvelope:
    """
    Attributes:
        comment (TimelineComment):
    """

    comment: TimelineComment

    def to_dict(self) -> dict[str, Any]:
        comment = self.comment.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "comment": comment,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.timeline_comment import TimelineComment

        d = dict(src_dict)
        comment = TimelineComment.from_dict(d.pop("comment"))

        comment_envelope = cls(
            comment=comment,
        )

        return comment_envelope
