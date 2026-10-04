from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeObjectChunk")


@_attrs_define
class E2EeObjectChunk:
    """
    Attributes:
        index (int):
        ciphertext_size (int):
        checksum_sha256 (str):
    """

    index: int
    ciphertext_size: int
    checksum_sha256: str

    def to_dict(self) -> dict[str, Any]:
        index = self.index

        ciphertext_size = self.ciphertext_size

        checksum_sha256 = self.checksum_sha256

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "index": index,
                "ciphertext_size": ciphertext_size,
                "checksum_sha256": checksum_sha256,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        index = d.pop("index")

        ciphertext_size = d.pop("ciphertext_size")

        checksum_sha256 = d.pop("checksum_sha256")

        e2_ee_object_chunk = cls(
            index=index,
            ciphertext_size=ciphertext_size,
            checksum_sha256=checksum_sha256,
        )

        return e2_ee_object_chunk
