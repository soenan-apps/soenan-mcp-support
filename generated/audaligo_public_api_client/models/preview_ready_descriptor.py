from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.preview_ready_descriptor_kind import PreviewReadyDescriptorKind
from ..models.preview_ready_descriptor_state import PreviewReadyDescriptorState

if TYPE_CHECKING:
    from ..models.preview_playback_loudness_measured import PreviewPlaybackLoudnessMeasured
    from ..models.preview_playback_loudness_unavailable import PreviewPlaybackLoudnessUnavailable
    from ..models.preview_playback_loudness_unmeasurable import PreviewPlaybackLoudnessUnmeasurable


T = TypeVar("T", bound="PreviewReadyDescriptor")


@_attrs_define
class PreviewReadyDescriptor:
    """
    Attributes:
        kind (PreviewReadyDescriptorKind):
        mix_version_id (str):
        preview_id (str):
        state (PreviewReadyDescriptorState):
        playback_loudness (PreviewPlaybackLoudnessMeasured | PreviewPlaybackLoudnessUnavailable |
            PreviewPlaybackLoudnessUnmeasurable):
    """

    kind: PreviewReadyDescriptorKind
    mix_version_id: str
    preview_id: str
    state: PreviewReadyDescriptorState
    playback_loudness: (
        PreviewPlaybackLoudnessMeasured | PreviewPlaybackLoudnessUnavailable | PreviewPlaybackLoudnessUnmeasurable
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.preview_playback_loudness_measured import PreviewPlaybackLoudnessMeasured
        from ..models.preview_playback_loudness_unmeasurable import PreviewPlaybackLoudnessUnmeasurable

        kind = self.kind.value

        mix_version_id = self.mix_version_id

        preview_id = self.preview_id

        state = self.state.value

        playback_loudness: dict[str, Any]
        if isinstance(self.playback_loudness, PreviewPlaybackLoudnessMeasured):
            playback_loudness = self.playback_loudness.to_dict()
        elif isinstance(self.playback_loudness, PreviewPlaybackLoudnessUnmeasurable):
            playback_loudness = self.playback_loudness.to_dict()
        else:
            playback_loudness = self.playback_loudness.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "mixVersionId": mix_version_id,
                "previewId": preview_id,
                "state": state,
                "playbackLoudness": playback_loudness,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preview_playback_loudness_measured import PreviewPlaybackLoudnessMeasured
        from ..models.preview_playback_loudness_unavailable import PreviewPlaybackLoudnessUnavailable
        from ..models.preview_playback_loudness_unmeasurable import PreviewPlaybackLoudnessUnmeasurable

        d = dict(src_dict)
        kind = PreviewReadyDescriptorKind(d.pop("kind"))

        mix_version_id = d.pop("mixVersionId")

        preview_id = d.pop("previewId")

        state = PreviewReadyDescriptorState(d.pop("state"))

        def _parse_playback_loudness(
            data: object,
        ) -> PreviewPlaybackLoudnessMeasured | PreviewPlaybackLoudnessUnavailable | PreviewPlaybackLoudnessUnmeasurable:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_playback_loudness_type_0 = PreviewPlaybackLoudnessMeasured.from_dict(data)

                return componentsschemas_preview_playback_loudness_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_playback_loudness_type_1 = PreviewPlaybackLoudnessUnmeasurable.from_dict(data)

                return componentsschemas_preview_playback_loudness_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_preview_playback_loudness_type_2 = PreviewPlaybackLoudnessUnavailable.from_dict(data)

            return componentsschemas_preview_playback_loudness_type_2

        playback_loudness = _parse_playback_loudness(d.pop("playbackLoudness"))

        preview_ready_descriptor = cls(
            kind=kind,
            mix_version_id=mix_version_id,
            preview_id=preview_id,
            state=state,
            playback_loudness=playback_loudness,
        )

        return preview_ready_descriptor
