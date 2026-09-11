from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_playback_loudness_unmeasurable_kind import (
    PreviewPlaybackLoudnessUnmeasurableKind,
)
from ..models.preview_playback_loudness_unmeasurable_policy_version import (
    PreviewPlaybackLoudnessUnmeasurablePolicyVersion,
)

T = TypeVar("T", bound="PreviewPlaybackLoudnessUnmeasurable")


@_attrs_define
class PreviewPlaybackLoudnessUnmeasurable:
    """
    Attributes:
        kind (PreviewPlaybackLoudnessUnmeasurableKind):
        policy_version (PreviewPlaybackLoudnessUnmeasurablePolicyVersion):
        target_integrated_loudness_lufs (float):
        maximum_true_peak_dbtp (float):
        maximum_boost_db (float):
        recommended_gain_db (float):
    """

    kind: PreviewPlaybackLoudnessUnmeasurableKind
    policy_version: PreviewPlaybackLoudnessUnmeasurablePolicyVersion
    target_integrated_loudness_lufs: float
    maximum_true_peak_dbtp: float
    maximum_boost_db: float
    recommended_gain_db: float

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        policy_version = self.policy_version.value

        target_integrated_loudness_lufs = self.target_integrated_loudness_lufs

        maximum_true_peak_dbtp = self.maximum_true_peak_dbtp

        maximum_boost_db = self.maximum_boost_db

        recommended_gain_db = self.recommended_gain_db

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "policyVersion": policy_version,
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
        kind = PreviewPlaybackLoudnessUnmeasurableKind(d.pop("kind"))

        policy_version = PreviewPlaybackLoudnessUnmeasurablePolicyVersion(
            d.pop("policyVersion")
        )

        target_integrated_loudness_lufs = d.pop("targetIntegratedLoudnessLufs")

        maximum_true_peak_dbtp = d.pop("maximumTruePeakDbtp")

        maximum_boost_db = d.pop("maximumBoostDb")

        recommended_gain_db = d.pop("recommendedGainDb")

        preview_playback_loudness_unmeasurable = cls(
            kind=kind,
            policy_version=policy_version,
            target_integrated_loudness_lufs=target_integrated_loudness_lufs,
            maximum_true_peak_dbtp=maximum_true_peak_dbtp,
            maximum_boost_db=maximum_boost_db,
            recommended_gain_db=recommended_gain_db,
        )

        return preview_playback_loudness_unmeasurable
