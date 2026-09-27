from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ManifestChunk")


@_attrs_define
class ManifestChunk:
    """
    Attributes:
        chunk_index (int):
        ciphertext_offset (int):
        ciphertext_sha256_b64u (str):
        ciphertext_size (int):
        final_chunk (bool):
        plaintext_offset (int):
        plaintext_size (int):
    """

    chunk_index: int
    ciphertext_offset: int
    ciphertext_sha256_b64u: str
    ciphertext_size: int
    final_chunk: bool
    plaintext_offset: int
    plaintext_size: int

    def to_dict(self) -> dict[str, Any]:
        chunk_index = self.chunk_index

        ciphertext_offset = self.ciphertext_offset

        ciphertext_sha256_b64u = self.ciphertext_sha256_b64u

        ciphertext_size = self.ciphertext_size

        final_chunk = self.final_chunk

        plaintext_offset = self.plaintext_offset

        plaintext_size = self.plaintext_size

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "chunk_index": chunk_index,
                "ciphertext_offset": ciphertext_offset,
                "ciphertext_sha256_b64u": ciphertext_sha256_b64u,
                "ciphertext_size": ciphertext_size,
                "final_chunk": final_chunk,
                "plaintext_offset": plaintext_offset,
                "plaintext_size": plaintext_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        chunk_index = d.pop("chunk_index")

        ciphertext_offset = d.pop("ciphertext_offset")

        ciphertext_sha256_b64u = d.pop("ciphertext_sha256_b64u")

        ciphertext_size = d.pop("ciphertext_size")

        final_chunk = d.pop("final_chunk")

        plaintext_offset = d.pop("plaintext_offset")

        plaintext_size = d.pop("plaintext_size")

        manifest_chunk = cls(
            chunk_index=chunk_index,
            ciphertext_offset=ciphertext_offset,
            ciphertext_sha256_b64u=ciphertext_sha256_b64u,
            ciphertext_size=ciphertext_size,
            final_chunk=final_chunk,
            plaintext_offset=plaintext_offset,
            plaintext_size=plaintext_size,
        )

        return manifest_chunk
