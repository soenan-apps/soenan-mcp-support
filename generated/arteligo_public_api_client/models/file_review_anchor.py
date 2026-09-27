from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.file_review_anchor_kind import FileReviewAnchorKind

T = TypeVar("T", bound="FileReviewAnchor")


@_attrs_define
class FileReviewAnchor:
    """
    Attributes:
        kind (FileReviewAnchorKind):
        file_id (str):
    """

    kind: FileReviewAnchorKind
    file_id: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        file_id = self.file_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "fileId": file_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = FileReviewAnchorKind(d.pop("kind"))

        file_id = d.pop("fileId")

        file_review_anchor = cls(
            kind=kind,
            file_id=file_id,
        )

        return file_review_anchor
