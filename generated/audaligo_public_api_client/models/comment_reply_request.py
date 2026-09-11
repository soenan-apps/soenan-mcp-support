from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.file_project_reference import FileProjectReference


T = TypeVar("T", bound="CommentReplyRequest")


@_attrs_define
class CommentReplyRequest:
    """
    Attributes:
        body (str):
        references (list[FileProjectReference]):
    """

    body: str
    references: list[FileProjectReference]

    def to_dict(self) -> dict[str, Any]:
        body = self.body

        references = []
        for references_item_data in self.references:
            references_item = references_item_data.to_dict()
            references.append(references_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "body": body,
                "references": references,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.file_project_reference import (
            FileProjectReference,
        )

        d = dict(src_dict)
        body = d.pop("body")

        references = []
        _references = d.pop("references")
        for references_item_data in _references:
            references_item = FileProjectReference.from_dict(references_item_data)

            references.append(references_item)

        comment_reply_request = cls(
            body=body,
            references=references,
        )

        return comment_reply_request
