from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.descriptor_chunk import DescriptorChunk
    from ..models.file_preview_media import FilePreviewMedia
    from ..models.preview_init_segment import PreviewInitSegment


T = TypeVar("T", bound="FilePreviewObject")


@_attrs_define
class FilePreviewObject:
    """
    Attributes:
        preview_id (str):
        project_id (str):
        file_id (str):
        source_object_id (str):
        processing_id (str):
        job_id (str):
        media (FilePreviewMedia):
        epoch (int):
        nonce_base_b64_u (str):
        chunk_size (int):
        plaintext_size (int):
        ciphertext_size (int):
        chunk_count (int):
        chunks (list[DescriptorChunk]):
        init_segment (None | PreviewInitSegment):
    """

    preview_id: str
    project_id: str
    file_id: str
    source_object_id: str
    processing_id: str
    job_id: str
    media: FilePreviewMedia
    epoch: int
    nonce_base_b64_u: str
    chunk_size: int
    plaintext_size: int
    ciphertext_size: int
    chunk_count: int
    chunks: list[DescriptorChunk]
    init_segment: None | PreviewInitSegment

    def to_dict(self) -> dict[str, Any]:
        from ..models.preview_init_segment import PreviewInitSegment

        preview_id = self.preview_id

        project_id = self.project_id

        file_id = self.file_id

        source_object_id = self.source_object_id

        processing_id = self.processing_id

        job_id = self.job_id

        media = self.media.to_dict()

        epoch = self.epoch

        nonce_base_b64_u = self.nonce_base_b64_u

        chunk_size = self.chunk_size

        plaintext_size = self.plaintext_size

        ciphertext_size = self.ciphertext_size

        chunk_count = self.chunk_count

        chunks = []
        for chunks_item_data in self.chunks:
            chunks_item = chunks_item_data.to_dict()
            chunks.append(chunks_item)

        init_segment: dict[str, Any] | None
        if isinstance(self.init_segment, PreviewInitSegment):
            init_segment = self.init_segment.to_dict()
        else:
            init_segment = self.init_segment

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "previewId": preview_id,
                "projectId": project_id,
                "fileId": file_id,
                "sourceObjectId": source_object_id,
                "processingId": processing_id,
                "jobId": job_id,
                "media": media,
                "epoch": epoch,
                "nonceBaseB64u": nonce_base_b64_u,
                "chunkSize": chunk_size,
                "plaintextSize": plaintext_size,
                "ciphertextSize": ciphertext_size,
                "chunkCount": chunk_count,
                "chunks": chunks,
                "initSegment": init_segment,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.descriptor_chunk import DescriptorChunk
        from ..models.file_preview_media import FilePreviewMedia
        from ..models.preview_init_segment import PreviewInitSegment

        d = dict(src_dict)
        preview_id = d.pop("previewId")

        project_id = d.pop("projectId")

        file_id = d.pop("fileId")

        source_object_id = d.pop("sourceObjectId")

        processing_id = d.pop("processingId")

        job_id = d.pop("jobId")

        media = FilePreviewMedia.from_dict(d.pop("media"))

        epoch = d.pop("epoch")

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

        file_preview_object = cls(
            preview_id=preview_id,
            project_id=project_id,
            file_id=file_id,
            source_object_id=source_object_id,
            processing_id=processing_id,
            job_id=job_id,
            media=media,
            epoch=epoch,
            nonce_base_b64_u=nonce_base_b64_u,
            chunk_size=chunk_size,
            plaintext_size=plaintext_size,
            ciphertext_size=ciphertext_size,
            chunk_count=chunk_count,
            chunks=chunks,
            init_segment=init_segment,
        )

        return file_preview_object
