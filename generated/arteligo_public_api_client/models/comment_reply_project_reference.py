from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.comment_reply_project_reference_kind import (
    CommentReplyProjectReferenceKind,
)

T = TypeVar("T", bound="CommentReplyProjectReference")


@_attrs_define
class CommentReplyProjectReference:
    """
    Attributes:
        kind (CommentReplyProjectReferenceKind):
        reply_id (str):
    """

    kind: CommentReplyProjectReferenceKind
    reply_id: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        reply_id = self.reply_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "replyId": reply_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = CommentReplyProjectReferenceKind(d.pop("kind"))

        reply_id = d.pop("replyId")

        comment_reply_project_reference = cls(
            kind=kind,
            reply_id=reply_id,
        )

        return comment_reply_project_reference
