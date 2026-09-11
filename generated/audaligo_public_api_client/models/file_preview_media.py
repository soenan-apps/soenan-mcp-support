from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.preview_init_segment import PreviewInitSegment
    from ..models.preview_playback_loudness_measured import (
        PreviewPlaybackLoudnessMeasured,
    )
    from ..models.preview_playback_loudness_unavailable import (
        PreviewPlaybackLoudnessUnavailable,
    )
    from ..models.preview_playback_loudness_unmeasurable import (
        PreviewPlaybackLoudnessUnmeasurable,
    )


T = TypeVar("T", bound="FilePreviewMedia")


@_attrs_define
class FilePreviewMedia:
    """
    Attributes:
        duration_seconds (float | None):
        mime_type (str):
        codecs (str):
        width (int | None):
        height (int | None):
        frame_rate (float | None):
        has_audio (bool | None):
        init_segment (None | PreviewInitSegment):
        playback_loudness (None | PreviewPlaybackLoudnessMeasured | PreviewPlaybackLoudnessUnavailable |
            PreviewPlaybackLoudnessUnmeasurable):
    """

    duration_seconds: float | None
    mime_type: str
    codecs: str
    width: int | None
    height: int | None
    frame_rate: float | None
    has_audio: bool | None
    init_segment: None | PreviewInitSegment
    playback_loudness: (
        None
        | PreviewPlaybackLoudnessMeasured
        | PreviewPlaybackLoudnessUnavailable
        | PreviewPlaybackLoudnessUnmeasurable
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.preview_init_segment import PreviewInitSegment
        from ..models.preview_playback_loudness_measured import (
            PreviewPlaybackLoudnessMeasured,
        )
        from ..models.preview_playback_loudness_unavailable import (
            PreviewPlaybackLoudnessUnavailable,
        )
        from ..models.preview_playback_loudness_unmeasurable import (
            PreviewPlaybackLoudnessUnmeasurable,
        )

        duration_seconds: float | None
        duration_seconds = self.duration_seconds

        mime_type = self.mime_type

        codecs = self.codecs

        width: int | None
        width = self.width

        height: int | None
        height = self.height

        frame_rate: float | None
        frame_rate = self.frame_rate

        has_audio: bool | None
        has_audio = self.has_audio

        init_segment: dict[str, Any] | None
        if isinstance(self.init_segment, PreviewInitSegment):
            init_segment = self.init_segment.to_dict()
        else:
            init_segment = self.init_segment

        playback_loudness: dict[str, Any] | None
        if (
            isinstance(self.playback_loudness, PreviewPlaybackLoudnessMeasured)
            or isinstance(self.playback_loudness, PreviewPlaybackLoudnessUnmeasurable)
            or isinstance(self.playback_loudness, PreviewPlaybackLoudnessUnavailable)
        ):
            playback_loudness = self.playback_loudness.to_dict()
        else:
            playback_loudness = self.playback_loudness

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "durationSeconds": duration_seconds,
                "mimeType": mime_type,
                "codecs": codecs,
                "width": width,
                "height": height,
                "frameRate": frame_rate,
                "hasAudio": has_audio,
                "initSegment": init_segment,
                "playbackLoudness": playback_loudness,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.preview_init_segment import PreviewInitSegment
        from ..models.preview_playback_loudness_measured import (
            PreviewPlaybackLoudnessMeasured,
        )
        from ..models.preview_playback_loudness_unavailable import (
            PreviewPlaybackLoudnessUnavailable,
        )
        from ..models.preview_playback_loudness_unmeasurable import (
            PreviewPlaybackLoudnessUnmeasurable,
        )

        d = dict(src_dict)

        def _parse_duration_seconds(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        duration_seconds = _parse_duration_seconds(d.pop("durationSeconds"))

        mime_type = d.pop("mimeType")

        codecs = d.pop("codecs")

        def _parse_width(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        width = _parse_width(d.pop("width"))

        def _parse_height(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        height = _parse_height(d.pop("height"))

        def _parse_frame_rate(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        frame_rate = _parse_frame_rate(d.pop("frameRate"))

        def _parse_has_audio(data: object) -> bool | None:
            if data is None:
                return data
            return cast(bool | None, data)

        has_audio = _parse_has_audio(d.pop("hasAudio"))

        def _parse_init_segment(data: object) -> None | PreviewInitSegment:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                init_segment_type_1 = PreviewInitSegment.from_dict(data)

                return init_segment_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PreviewInitSegment, data)

        init_segment = _parse_init_segment(d.pop("initSegment"))

        def _parse_playback_loudness(
            data: object,
        ) -> (
            None
            | PreviewPlaybackLoudnessMeasured
            | PreviewPlaybackLoudnessUnavailable
            | PreviewPlaybackLoudnessUnmeasurable
        ):
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_playback_loudness_type_0 = (
                    PreviewPlaybackLoudnessMeasured.from_dict(data)
                )

                return componentsschemas_preview_playback_loudness_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_playback_loudness_type_1 = (
                    PreviewPlaybackLoudnessUnmeasurable.from_dict(data)
                )

                return componentsschemas_preview_playback_loudness_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_playback_loudness_type_2 = (
                    PreviewPlaybackLoudnessUnavailable.from_dict(data)
                )

                return componentsschemas_preview_playback_loudness_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None
                | PreviewPlaybackLoudnessMeasured
                | PreviewPlaybackLoudnessUnavailable
                | PreviewPlaybackLoudnessUnmeasurable,
                data,
            )

        playback_loudness = _parse_playback_loudness(d.pop("playbackLoudness"))

        file_preview_media = cls(
            duration_seconds=duration_seconds,
            mime_type=mime_type,
            codecs=codecs,
            width=width,
            height=height,
            frame_rate=frame_rate,
            has_audio=has_audio,
            init_segment=init_segment,
            playback_loudness=playback_loudness,
        )

        return file_preview_media
