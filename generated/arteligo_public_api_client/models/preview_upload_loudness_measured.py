from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_upload_loudness_measured_kind import (
    PreviewUploadLoudnessMeasuredKind,
)

T = TypeVar("T", bound="PreviewUploadLoudnessMeasured")


@_attrs_define
class PreviewUploadLoudnessMeasured:
    """
    Attributes:
        kind (PreviewUploadLoudnessMeasuredKind):
        integrated_lufs_x100 (int):
        true_peak_dbtp_x100 (int):
        loudness_range_lu_x100 (int):
    """

    kind: PreviewUploadLoudnessMeasuredKind
    integrated_lufs_x100: int
    true_peak_dbtp_x100: int
    loudness_range_lu_x100: int

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        integrated_lufs_x100 = self.integrated_lufs_x100

        true_peak_dbtp_x100 = self.true_peak_dbtp_x100

        loudness_range_lu_x100 = self.loudness_range_lu_x100

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "integratedLufsX100": integrated_lufs_x100,
                "truePeakDbtpX100": true_peak_dbtp_x100,
                "loudnessRangeLuX100": loudness_range_lu_x100,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = PreviewUploadLoudnessMeasuredKind(d.pop("kind"))

        integrated_lufs_x100 = d.pop("integratedLufsX100")

        true_peak_dbtp_x100 = d.pop("truePeakDbtpX100")

        loudness_range_lu_x100 = d.pop("loudnessRangeLuX100")

        preview_upload_loudness_measured = cls(
            kind=kind,
            integrated_lufs_x100=integrated_lufs_x100,
            true_peak_dbtp_x100=true_peak_dbtp_x100,
            loudness_range_lu_x100=loudness_range_lu_x100,
        )

        return preview_upload_loudness_measured
