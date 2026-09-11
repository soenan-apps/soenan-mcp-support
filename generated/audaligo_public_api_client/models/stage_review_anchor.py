from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.stage_review_anchor_kind import StageReviewAnchorKind

T = TypeVar("T", bound="StageReviewAnchor")


@_attrs_define
class StageReviewAnchor:
    """
    Attributes:
        kind (StageReviewAnchorKind):
        stage_id (str):
    """

    kind: StageReviewAnchorKind
    stage_id: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        stage_id = self.stage_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "stageId": stage_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = StageReviewAnchorKind(d.pop("kind"))

        stage_id = d.pop("stageId")

        stage_review_anchor = cls(
            kind=kind,
            stage_id=stage_id,
        )

        return stage_review_anchor
