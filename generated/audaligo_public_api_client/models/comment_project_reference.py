from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.comment_project_reference_kind import CommentProjectReferenceKind

T = TypeVar("T", bound="CommentProjectReference")


@_attrs_define
class CommentProjectReference:
    """
    Attributes:
        kind (CommentProjectReferenceKind):
        comment_id (str):
    """

    kind: CommentProjectReferenceKind
    comment_id: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        comment_id = self.comment_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "commentId": comment_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = CommentProjectReferenceKind(d.pop("kind"))

        comment_id = d.pop("commentId")

        comment_project_reference = cls(
            kind=kind,
            comment_id=comment_id,
        )

        return comment_project_reference
