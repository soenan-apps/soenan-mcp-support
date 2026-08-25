from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.manifest_chunk import ManifestChunk


T = TypeVar("T", bound="ManifestObject")


@_attrs_define
class ManifestObject:
    """
    Attributes:
        chunk_count (int):
        chunk_size (int):
        chunks (list[ManifestChunk]):
        ciphertext_size (int):
        epoch (int):
        file_id (str):
        nonce_base_b64u (str):
        object_id (str):
        plaintext_size (int):
        project_id (str):
        share_id (str):
    """

    chunk_count: int
    chunk_size: int
    chunks: list[ManifestChunk]
    ciphertext_size: int
    epoch: int
    file_id: str
    nonce_base_b64u: str
    object_id: str
    plaintext_size: int
    project_id: str
    share_id: str

    def to_dict(self) -> dict[str, Any]:
        chunk_count = self.chunk_count

        chunk_size = self.chunk_size

        chunks = []
        for chunks_item_data in self.chunks:
            chunks_item = chunks_item_data.to_dict()
            chunks.append(chunks_item)

        ciphertext_size = self.ciphertext_size

        epoch = self.epoch

        file_id = self.file_id

        nonce_base_b64u = self.nonce_base_b64u

        object_id = self.object_id

        plaintext_size = self.plaintext_size

        project_id = self.project_id

        share_id = self.share_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "chunk_count": chunk_count,
                "chunk_size": chunk_size,
                "chunks": chunks,
                "ciphertext_size": ciphertext_size,
                "epoch": epoch,
                "file_id": file_id,
                "nonce_base_b64u": nonce_base_b64u,
                "object_id": object_id,
                "plaintext_size": plaintext_size,
                "project_id": project_id,
                "share_id": share_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.manifest_chunk import ManifestChunk

        d = dict(src_dict)
        chunk_count = d.pop("chunk_count")

        chunk_size = d.pop("chunk_size")

        chunks = []
        _chunks = d.pop("chunks")
        for chunks_item_data in _chunks:
            chunks_item = ManifestChunk.from_dict(chunks_item_data)

            chunks.append(chunks_item)

        ciphertext_size = d.pop("ciphertext_size")

        epoch = d.pop("epoch")

        file_id = d.pop("file_id")

        nonce_base_b64u = d.pop("nonce_base_b64u")

        object_id = d.pop("object_id")

        plaintext_size = d.pop("plaintext_size")

        project_id = d.pop("project_id")

        share_id = d.pop("share_id")

        manifest_object = cls(
            chunk_count=chunk_count,
            chunk_size=chunk_size,
            chunks=chunks,
            ciphertext_size=ciphertext_size,
            epoch=epoch,
            file_id=file_id,
            nonce_base_b64u=nonce_base_b64u,
            object_id=object_id,
            plaintext_size=plaintext_size,
            project_id=project_id,
            share_id=share_id,
        )

        return manifest_object
