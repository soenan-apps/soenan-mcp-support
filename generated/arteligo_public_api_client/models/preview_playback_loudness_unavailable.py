from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_playback_loudness_unavailable_kind import (
    PreviewPlaybackLoudnessUnavailableKind,
)

T = TypeVar("T", bound="PreviewPlaybackLoudnessUnavailable")


@_attrs_define
class PreviewPlaybackLoudnessUnavailable:
    """
    Attributes:
        kind (PreviewPlaybackLoudnessUnavailableKind):
    """

    kind: PreviewPlaybackLoudnessUnavailableKind

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
        kind = PreviewPlaybackLoudnessUnavailableKind(d.pop("kind"))

        preview_playback_loudness_unavailable = cls(
            kind=kind,
        )

        return preview_playback_loudness_unavailable
