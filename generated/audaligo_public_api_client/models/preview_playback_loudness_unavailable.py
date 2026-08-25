from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.preview_playback_loudness_unavailable_kind import PreviewPlaybackLoudnessUnavailableKind
from ..models.take_audio_role import TakeAudioRole

T = TypeVar("T", bound="PreviewPlaybackLoudnessUnavailable")


@_attrs_define
class PreviewPlaybackLoudnessUnavailable:
    """
    Attributes:
        kind (PreviewPlaybackLoudnessUnavailableKind):
        audio_role (TakeAudioRole):
    """

    kind: PreviewPlaybackLoudnessUnavailableKind
    audio_role: TakeAudioRole

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        audio_role = self.audio_role.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "audioRole": audio_role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = PreviewPlaybackLoudnessUnavailableKind(d.pop("kind"))

        audio_role = TakeAudioRole(d.pop("audioRole"))

        preview_playback_loudness_unavailable = cls(
            kind=kind,
            audio_role=audio_role,
        )

        return preview_playback_loudness_unavailable
