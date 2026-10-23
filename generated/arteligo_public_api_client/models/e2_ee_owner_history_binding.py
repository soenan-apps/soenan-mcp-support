from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeOwnerHistoryBinding")


@_attrs_define
class E2EeOwnerHistoryBinding:
    """
    Attributes:
        key_id (str):
        key_epoch (int):
        public_key (str):
        binding_digest (str):
    """

    key_id: str
    key_epoch: int
    public_key: str
    binding_digest: str

    def to_dict(self) -> dict[str, Any]:
        key_id = self.key_id

        key_epoch = self.key_epoch

        public_key = self.public_key

        binding_digest = self.binding_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "key_id": key_id,
                "key_epoch": key_epoch,
                "public_key": public_key,
                "binding_digest": binding_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        key_id = d.pop("key_id")

        key_epoch = d.pop("key_epoch")

        public_key = d.pop("public_key")

        binding_digest = d.pop("binding_digest")

        e2_ee_owner_history_binding = cls(
            key_id=key_id,
            key_epoch=key_epoch,
            public_key=public_key,
            binding_digest=binding_digest,
        )

        return e2_ee_owner_history_binding
