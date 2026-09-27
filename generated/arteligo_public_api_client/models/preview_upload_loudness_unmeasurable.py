from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_upload_loudness_unmeasurable_kind import (
    PreviewUploadLoudnessUnmeasurableKind,
)

T = TypeVar("T", bound="PreviewUploadLoudnessUnmeasurable")


@_attrs_define
class PreviewUploadLoudnessUnmeasurable:
    """
    Attributes:
        kind (PreviewUploadLoudnessUnmeasurableKind):
    """

    kind: PreviewUploadLoudnessUnmeasurableKind

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = PreviewUploadLoudnessUnmeasurableKind(d.pop("kind"))

        preview_upload_loudness_unmeasurable = cls(
            kind=kind,
        )

        return preview_upload_loudness_unmeasurable
