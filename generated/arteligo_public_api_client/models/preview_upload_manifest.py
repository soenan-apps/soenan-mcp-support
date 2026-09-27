from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_upload_manifest_chunk_size import PreviewUploadManifestChunkSize

if TYPE_CHECKING:
    from ..models.descriptor_chunk import DescriptorChunk
    from ..models.preview_upload_media import PreviewUploadMedia


T = TypeVar("T", bound="PreviewUploadManifest")


@_attrs_define
class PreviewUploadManifest:
    """Client-encrypted Opus WebM sidecar metadata for a committed source file; identity and epoch must match the source-
    bound preview reservation.

        Attributes:
            source_object_id (str):
            preview_id (str):
            processing_id (str):
            job_id (str):
            epoch (int):
            nonce_base_b64_u (str):
            plaintext_size (int): Encoded WebM plaintext size, at most 536870912 bytes (512 MiB).
            ciphertext_size (int): Plaintext size plus 16 bytes per encrypted chunk; storage quota applies to ciphertext.
            chunk_size (PreviewUploadManifestChunkSize):
            chunks (list[DescriptorChunk]):
            media (PreviewUploadMedia):
    """

    source_object_id: str
    preview_id: str
    processing_id: str
    job_id: str
    epoch: int
    nonce_base_b64_u: str
    plaintext_size: int
    ciphertext_size: int
    chunk_size: PreviewUploadManifestChunkSize
    chunks: list[DescriptorChunk]
    media: PreviewUploadMedia

    def to_dict(self) -> dict[str, Any]:
        source_object_id = self.source_object_id

        preview_id = self.preview_id

        processing_id = self.processing_id

        job_id = self.job_id

        epoch = self.epoch

        nonce_base_b64_u = self.nonce_base_b64_u

        plaintext_size = self.plaintext_size

        ciphertext_size = self.ciphertext_size

        chunk_size = self.chunk_size.value

        chunks = []
        for chunks_item_data in self.chunks:
            chunks_item = chunks_item_data.to_dict()
            chunks.append(chunks_item)

        media = self.media.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sourceObjectId": source_object_id,
                "previewId": preview_id,
                "processingId": processing_id,
                "jobId": job_id,
                "epoch": epoch,
                "nonceBaseB64u": nonce_base_b64_u,
                "plaintextSize": plaintext_size,
                "ciphertextSize": ciphertext_size,
                "chunkSize": chunk_size,
                "chunks": chunks,
                "media": media,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.descriptor_chunk import DescriptorChunk
        from ..models.preview_upload_media import PreviewUploadMedia

        d = dict(src_dict)
        source_object_id = d.pop("sourceObjectId")

        preview_id = d.pop("previewId")

        processing_id = d.pop("processingId")

        job_id = d.pop("jobId")

        epoch = d.pop("epoch")

        nonce_base_b64_u = d.pop("nonceBaseB64u")

        plaintext_size = d.pop("plaintextSize")

        ciphertext_size = d.pop("ciphertextSize")

        chunk_size = PreviewUploadManifestChunkSize(d.pop("chunkSize"))

        chunks = []
        _chunks = d.pop("chunks")
        for chunks_item_data in _chunks:
            chunks_item = DescriptorChunk.from_dict(chunks_item_data)

            chunks.append(chunks_item)

        media = PreviewUploadMedia.from_dict(d.pop("media"))

        preview_upload_manifest = cls(
            source_object_id=source_object_id,
            preview_id=preview_id,
            processing_id=processing_id,
            job_id=job_id,
            epoch=epoch,
            nonce_base_b64_u=nonce_base_b64_u,
            plaintext_size=plaintext_size,
            ciphertext_size=ciphertext_size,
            chunk_size=chunk_size,
            chunks=chunks,
            media=media,
        )

        return preview_upload_manifest
