from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_playback_loudness_measured_kind import (
    PreviewPlaybackLoudnessMeasuredKind,
)
from ..models.preview_playback_loudness_measured_policy_version import (
    PreviewPlaybackLoudnessMeasuredPolicyVersion,
)

T = TypeVar("T", bound="PreviewPlaybackLoudnessMeasured")


@_attrs_define
class PreviewPlaybackLoudnessMeasured:
    """
    Attributes:
        kind (PreviewPlaybackLoudnessMeasuredKind):
        policy_version (PreviewPlaybackLoudnessMeasuredPolicyVersion):
        integrated_loudness_lufs (float):
        true_peak_dbtp (float):
        loudness_range_lu (float):
        target_integrated_loudness_lufs (float):
        maximum_true_peak_dbtp (float):
        maximum_boost_db (float):
        recommended_gain_db (float):
    """

    kind: PreviewPlaybackLoudnessMeasuredKind
    policy_version: PreviewPlaybackLoudnessMeasuredPolicyVersion
    integrated_loudness_lufs: float
    true_peak_dbtp: float
    loudness_range_lu: float
    target_integrated_loudness_lufs: float
    maximum_true_peak_dbtp: float
    maximum_boost_db: float
    recommended_gain_db: float

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        policy_version = self.policy_version.value

        integrated_loudness_lufs = self.integrated_loudness_lufs

        true_peak_dbtp = self.true_peak_dbtp

        loudness_range_lu = self.loudness_range_lu

        target_integrated_loudness_lufs = self.target_integrated_loudness_lufs

        maximum_true_peak_dbtp = self.maximum_true_peak_dbtp

        maximum_boost_db = self.maximum_boost_db

        recommended_gain_db = self.recommended_gain_db

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "policyVersion": policy_version,
                "integratedLoudnessLufs": integrated_loudness_lufs,
                "truePeakDbtp": true_peak_dbtp,
                "loudnessRangeLu": loudness_range_lu,
                "targetIntegratedLoudnessLufs": target_integrated_loudness_lufs,
                "maximumTruePeakDbtp": maximum_true_peak_dbtp,
                "maximumBoostDb": maximum_boost_db,
                "recommendedGainDb": recommended_gain_db,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = PreviewPlaybackLoudnessMeasuredKind(d.pop("kind"))

        policy_version = PreviewPlaybackLoudnessMeasuredPolicyVersion(
            d.pop("policyVersion")
        )

        integrated_loudness_lufs = d.pop("integratedLoudnessLufs")

        true_peak_dbtp = d.pop("truePeakDbtp")

        loudness_range_lu = d.pop("loudnessRangeLu")

        target_integrated_loudness_lufs = d.pop("targetIntegratedLoudnessLufs")

        maximum_true_peak_dbtp = d.pop("maximumTruePeakDbtp")

        maximum_boost_db = d.pop("maximumBoostDb")

        recommended_gain_db = d.pop("recommendedGainDb")

        preview_playback_loudness_measured = cls(
            kind=kind,
            policy_version=policy_version,
            integrated_loudness_lufs=integrated_loudness_lufs,
            true_peak_dbtp=true_peak_dbtp,
            loudness_range_lu=loudness_range_lu,
            target_integrated_loudness_lufs=target_integrated_loudness_lufs,
            maximum_true_peak_dbtp=maximum_true_peak_dbtp,
            maximum_boost_db=maximum_boost_db,
            recommended_gain_db=recommended_gain_db,
        )

        return preview_playback_loudness_measured
