from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_upload_media_codecs import PreviewUploadMediaCodecs
from ..models.preview_upload_media_mime_type import PreviewUploadMediaMimeType
from ..models.preview_upload_media_sample_rate import PreviewUploadMediaSampleRate

if TYPE_CHECKING:
    from ..models.preview_upload_loudness_measured import PreviewUploadLoudnessMeasured
    from ..models.preview_upload_loudness_unmeasurable import (
        PreviewUploadLoudnessUnmeasurable,
    )


T = TypeVar("T", bound="PreviewUploadMedia")


@_attrs_define
class PreviewUploadMedia:
    """
    Attributes:
        duration_seconds (float):
        mime_type (PreviewUploadMediaMimeType):
        codecs (PreviewUploadMediaCodecs):
        sample_rate (PreviewUploadMediaSampleRate):
        channels (int):
        bitrate (int): Rounded effective bitrate of serialized plaintext WebM, in bits per second: round(plaintextSize *
            8 / durationSeconds). This is observed output, not a requested encoder target; Opus uses variable bitrate.
        playback_loudness (PreviewUploadLoudnessMeasured | PreviewUploadLoudnessUnmeasurable): Client-reported
            measurement only; playback policy and gain are server-derived.
    """

    duration_seconds: float
    mime_type: PreviewUploadMediaMimeType
    codecs: PreviewUploadMediaCodecs
    sample_rate: PreviewUploadMediaSampleRate
    channels: int
    bitrate: int
    playback_loudness: PreviewUploadLoudnessMeasured | PreviewUploadLoudnessUnmeasurable

    def to_dict(self) -> dict[str, Any]:
        from ..models.preview_upload_loudness_measured import (
            PreviewUploadLoudnessMeasured,
        )

        duration_seconds = self.duration_seconds

        mime_type = self.mime_type.value

        codecs = self.codecs.value

        sample_rate = self.sample_rate.value

        channels = self.channels

        bitrate = self.bitrate

        playback_loudness: dict[str, Any]
        if isinstance(self.playback_loudness, PreviewUploadLoudnessMeasured):
            playback_loudness = self.playback_loudness.to_dict()
        else:
            playback_loudness = self.playback_loudness.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "durationSeconds": duration_seconds,
                "mimeType": mime_type,
                "codecs": codecs,
                "sampleRate": sample_rate,
                "channels": channels,
                "bitrate": bitrate,
                "playbackLoudness": playback_loudness,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.preview_upload_loudness_measured import (
            PreviewUploadLoudnessMeasured,
        )
        from ..models.preview_upload_loudness_unmeasurable import (
            PreviewUploadLoudnessUnmeasurable,
        )

        d = dict(src_dict)
        duration_seconds = d.pop("durationSeconds")

        mime_type = PreviewUploadMediaMimeType(d.pop("mimeType"))

        codecs = PreviewUploadMediaCodecs(d.pop("codecs"))

        sample_rate = PreviewUploadMediaSampleRate(d.pop("sampleRate"))

        channels = d.pop("channels")

        bitrate = d.pop("bitrate")

        def _parse_playback_loudness(
            data: object,
        ) -> PreviewUploadLoudnessMeasured | PreviewUploadLoudnessUnmeasurable:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_upload_loudness_type_0 = (
                    PreviewUploadLoudnessMeasured.from_dict(data)
                )

                return componentsschemas_preview_upload_loudness_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_preview_upload_loudness_type_1 = (
                PreviewUploadLoudnessUnmeasurable.from_dict(data)
            )

            return componentsschemas_preview_upload_loudness_type_1

        playback_loudness = _parse_playback_loudness(d.pop("playbackLoudness"))

        preview_upload_media = cls(
            duration_seconds=duration_seconds,
            mime_type=mime_type,
            codecs=codecs,
            sample_rate=sample_rate,
            channels=channels,
            bitrate=bitrate,
            playback_loudness=playback_loudness,
        )

        return preview_upload_media
