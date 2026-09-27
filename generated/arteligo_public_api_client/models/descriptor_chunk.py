from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="DescriptorChunk")


@_attrs_define
class DescriptorChunk:
    """
    Attributes:
        chunk_index (int):
        plaintext_offset (int):
        plaintext_size (int):
        ciphertext_offset (int):
        ciphertext_size (int):
        ciphertext_sha_256b64_u (str):
        final_chunk (bool):
    """

    chunk_index: int
    plaintext_offset: int
    plaintext_size: int
    ciphertext_offset: int
    ciphertext_size: int
    ciphertext_sha_256b64_u: str
    final_chunk: bool

    def to_dict(self) -> dict[str, Any]:
        chunk_index = self.chunk_index

        plaintext_offset = self.plaintext_offset

        plaintext_size = self.plaintext_size

        ciphertext_offset = self.ciphertext_offset

        ciphertext_size = self.ciphertext_size

        ciphertext_sha_256b64_u = self.ciphertext_sha_256b64_u

        final_chunk = self.final_chunk

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "chunkIndex": chunk_index,
                "plaintextOffset": plaintext_offset,
                "plaintextSize": plaintext_size,
                "ciphertextOffset": ciphertext_offset,
                "ciphertextSize": ciphertext_size,
                "ciphertextSha256B64u": ciphertext_sha_256b64_u,
                "finalChunk": final_chunk,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        chunk_index = d.pop("chunkIndex")

        plaintext_offset = d.pop("plaintextOffset")

        plaintext_size = d.pop("plaintextSize")

        ciphertext_offset = d.pop("ciphertextOffset")

        ciphertext_size = d.pop("ciphertextSize")

        ciphertext_sha_256b64_u = d.pop("ciphertextSha256B64u")

        final_chunk = d.pop("finalChunk")

        descriptor_chunk = cls(
            chunk_index=chunk_index,
            plaintext_offset=plaintext_offset,
            plaintext_size=plaintext_size,
            ciphertext_offset=ciphertext_offset,
            ciphertext_size=ciphertext_size,
            ciphertext_sha_256b64_u=ciphertext_sha_256b64_u,
            final_chunk=final_chunk,
        )

        return descriptor_chunk
