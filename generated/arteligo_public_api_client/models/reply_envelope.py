from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.comment_reply import CommentReply


T = TypeVar("T", bound="ReplyEnvelope")


@_attrs_define
class ReplyEnvelope:
    """
    Attributes:
        reply (CommentReply):
    """

    reply: CommentReply

    def to_dict(self) -> dict[str, Any]:
        reply = self.reply.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "reply": reply,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.comment_reply import CommentReply

        d = dict(src_dict)
        reply = CommentReply.from_dict(d.pop("reply"))

        reply_envelope = cls(
            reply=reply,
        )

        return reply_envelope
