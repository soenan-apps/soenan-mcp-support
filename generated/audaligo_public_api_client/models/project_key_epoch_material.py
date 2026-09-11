from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ProjectKeyEpochMaterial")


@_attrs_define
class ProjectKeyEpochMaterial:
    """
    Attributes:
        epoch (int):
        key_b64_u (str): Unpadded base64url encoding of exactly 32 bytes. Clear project keys may be retained only in
            bounded process memory. A browser may persist one only after sealing it with its non-extractable origin key.
    """

    epoch: int
    key_b64_u: str

    def to_dict(self) -> dict[str, Any]:
        epoch = self.epoch

        key_b64_u = self.key_b64_u

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "epoch": epoch,
                "keyB64u": key_b64_u,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        epoch = d.pop("epoch")

        key_b64_u = d.pop("keyB64u")

        project_key_epoch_material = cls(
            epoch=epoch,
            key_b64_u=key_b64_u,
        )

        return project_key_epoch_material
