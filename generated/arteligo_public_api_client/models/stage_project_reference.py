from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.stage_project_reference_kind import StageProjectReferenceKind

T = TypeVar("T", bound="StageProjectReference")


@_attrs_define
class StageProjectReference:
    """
    Attributes:
        kind (StageProjectReferenceKind):
        stage_id (str):
    """

    kind: StageProjectReferenceKind
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
        kind = StageProjectReferenceKind(d.pop("kind"))

        stage_id = d.pop("stageId")

        stage_project_reference = cls(
            kind=kind,
            stage_id=stage_id,
        )

        return stage_project_reference
