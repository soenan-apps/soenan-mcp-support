from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.member_actor import MemberActor


T = TypeVar("T", bound="CommentReply")


@_attrs_define
class CommentReply:
    """
    Attributes:
        id (str):
        body (str):
        author (MemberActor):
        created_at (datetime.datetime):
    """

    id: str
    body: str
    author: MemberActor
    created_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        body = self.body

        author = self.author.to_dict()

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "body": body,
                "author": author,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.member_actor import MemberActor

        d = dict(src_dict)
        id = d.pop("id")

        body = d.pop("body")

        author = MemberActor.from_dict(d.pop("author"))

        created_at = datetime.datetime.fromisoformat(d.pop("createdAt"))

        comment_reply = cls(
            id=id,
            body=body,
            author=author,
            created_at=created_at,
        )

        return comment_reply
