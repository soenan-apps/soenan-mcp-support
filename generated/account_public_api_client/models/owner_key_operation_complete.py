from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OwnerKeyOperationComplete")


@_attrs_define
class OwnerKeyOperationComplete:
    """
    Attributes:
        part_count (int):
        payload_digest (str):
    """

    part_count: int
    payload_digest: str

    def to_dict(self) -> dict[str, Any]:
        part_count = self.part_count

        payload_digest = self.payload_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "part_count": part_count,
                "payload_digest": payload_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        part_count = d.pop("part_count")

        payload_digest = d.pop("payload_digest")

        owner_key_operation_complete = cls(
            part_count=part_count,
            payload_digest=payload_digest,
        )

        return owner_key_operation_complete
