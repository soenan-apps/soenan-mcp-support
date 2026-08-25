from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.preview_object_codec import PreviewObjectCodec
from ..models.preview_object_mime_type import PreviewObjectMimeType

if TYPE_CHECKING:
    from ..models.descriptor_chunk import DescriptorChunk
    from ..models.preview_playback_loudness_measured import PreviewPlaybackLoudnessMeasured
    from ..models.preview_playback_loudness_unavailable import PreviewPlaybackLoudnessUnavailable
    from ..models.preview_playback_loudness_unmeasurable import PreviewPlaybackLoudnessUnmeasurable


T = TypeVar("T", bound="PreviewObject")


@_attrs_define
class PreviewObject:
    """
    Attributes:
        preview_id (str):
        project_id (str):
        epoch (int):
        source_object_id (str):
        processing_id (str):
        job_id (str):
        mime_type (PreviewObjectMimeType):
        codec (PreviewObjectCodec):
        bitrate_bps (int):
        playback_loudness (PreviewPlaybackLoudnessMeasured | PreviewPlaybackLoudnessUnavailable |
            PreviewPlaybackLoudnessUnmeasurable):
        nonce_base_b64_u (str):
        chunk_size (int):
        plaintext_size (int):
        ciphertext_size (int):
        chunk_count (int):
        chunks (list[DescriptorChunk]):
    """

    preview_id: str
    project_id: str
    epoch: int
    source_object_id: str
    processing_id: str
    job_id: str
    mime_type: PreviewObjectMimeType
    codec: PreviewObjectCodec
    bitrate_bps: int
    playback_loudness: (
        PreviewPlaybackLoudnessMeasured | PreviewPlaybackLoudnessUnavailable | PreviewPlaybackLoudnessUnmeasurable
    )
    nonce_base_b64_u: str
    chunk_size: int
    plaintext_size: int
    ciphertext_size: int
    chunk_count: int
    chunks: list[DescriptorChunk]

    def to_dict(self) -> dict[str, Any]:
        from ..models.preview_playback_loudness_measured import PreviewPlaybackLoudnessMeasured
        from ..models.preview_playback_loudness_unmeasurable import PreviewPlaybackLoudnessUnmeasurable

        preview_id = self.preview_id

        project_id = self.project_id

        epoch = self.epoch

        source_object_id = self.source_object_id

        processing_id = self.processing_id

        job_id = self.job_id

        mime_type = self.mime_type.value

        codec = self.codec.value

        bitrate_bps = self.bitrate_bps

        playback_loudness: dict[str, Any]
        if isinstance(self.playback_loudness, PreviewPlaybackLoudnessMeasured):
            playback_loudness = self.playback_loudness.to_dict()
        elif isinstance(self.playback_loudness, PreviewPlaybackLoudnessUnmeasurable):
            playback_loudness = self.playback_loudness.to_dict()
        else:
            playback_loudness = self.playback_loudness.to_dict()

        nonce_base_b64_u = self.nonce_base_b64_u

        chunk_size = self.chunk_size

        plaintext_size = self.plaintext_size

        ciphertext_size = self.ciphertext_size

        chunk_count = self.chunk_count

        chunks = []
        for chunks_item_data in self.chunks:
            chunks_item = chunks_item_data.to_dict()
            chunks.append(chunks_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "previewId": preview_id,
                "projectId": project_id,
                "epoch": epoch,
                "sourceObjectId": source_object_id,
                "processingId": processing_id,
                "jobId": job_id,
                "mimeType": mime_type,
                "codec": codec,
                "bitrateBps": bitrate_bps,
                "playbackLoudness": playback_loudness,
                "nonceBaseB64u": nonce_base_b64_u,
                "chunkSize": chunk_size,
                "plaintextSize": plaintext_size,
                "ciphertextSize": ciphertext_size,
                "chunkCount": chunk_count,
                "chunks": chunks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.descriptor_chunk import DescriptorChunk
        from ..models.preview_playback_loudness_measured import PreviewPlaybackLoudnessMeasured
        from ..models.preview_playback_loudness_unavailable import PreviewPlaybackLoudnessUnavailable
        from ..models.preview_playback_loudness_unmeasurable import PreviewPlaybackLoudnessUnmeasurable

        d = dict(src_dict)
        preview_id = d.pop("previewId")

        project_id = d.pop("projectId")

        epoch = d.pop("epoch")

        source_object_id = d.pop("sourceObjectId")

        processing_id = d.pop("processingId")

        job_id = d.pop("jobId")

        mime_type = PreviewObjectMimeType(d.pop("mimeType"))

        codec = PreviewObjectCodec(d.pop("codec"))

        bitrate_bps = d.pop("bitrateBps")

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

        nonce_base_b64_u = d.pop("nonceBaseB64u")

        chunk_size = d.pop("chunkSize")

        plaintext_size = d.pop("plaintextSize")

        ciphertext_size = d.pop("ciphertextSize")

        chunk_count = d.pop("chunkCount")

        chunks = []
        _chunks = d.pop("chunks")
        for chunks_item_data in _chunks:
            chunks_item = DescriptorChunk.from_dict(chunks_item_data)

            chunks.append(chunks_item)

        preview_object = cls(
            preview_id=preview_id,
            project_id=project_id,
            epoch=epoch,
            source_object_id=source_object_id,
            processing_id=processing_id,
            job_id=job_id,
            mime_type=mime_type,
            codec=codec,
            bitrate_bps=bitrate_bps,
            playback_loudness=playback_loudness,
            nonce_base_b64_u=nonce_base_b64_u,
            chunk_size=chunk_size,
            plaintext_size=plaintext_size,
            ciphertext_size=ciphertext_size,
            chunk_count=chunk_count,
            chunks=chunks,
        )

        return preview_object
