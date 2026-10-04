from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_object_chunk import E2EeObjectChunk


T = TypeVar("T", bound="E2EeObjectManifest")


@_attrs_define
class E2EeObjectManifest:
    """
    Attributes:
        scope_id (str):
        object_id (str):
        key_epoch (int):
        chunks (list[E2EeObjectChunk]):
        ciphertext_size (int):
    """

    scope_id: str
    object_id: str
    key_epoch: int
    chunks: list[E2EeObjectChunk]
    ciphertext_size: int

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        object_id = self.object_id

        key_epoch = self.key_epoch

        chunks = []
        for chunks_item_data in self.chunks:
            chunks_item = chunks_item_data.to_dict()
            chunks.append(chunks_item)

        ciphertext_size = self.ciphertext_size

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "object_id": object_id,
                "key_epoch": key_epoch,
                "chunks": chunks,
                "ciphertext_size": ciphertext_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_object_chunk import E2EeObjectChunk

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        object_id = d.pop("object_id")

        key_epoch = d.pop("key_epoch")

        chunks = []
        _chunks = d.pop("chunks")
        for chunks_item_data in _chunks:
            chunks_item = E2EeObjectChunk.from_dict(chunks_item_data)

            chunks.append(chunks_item)

        ciphertext_size = d.pop("ciphertext_size")

        e2_ee_object_manifest = cls(
            scope_id=scope_id,
            object_id=object_id,
            key_epoch=key_epoch,
            chunks=chunks,
            ciphertext_size=ciphertext_size,
        )

        return e2_ee_object_manifest
