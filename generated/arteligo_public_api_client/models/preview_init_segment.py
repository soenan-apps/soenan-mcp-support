from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="PreviewInitSegment")


@_attrs_define
class PreviewInitSegment:
    """
    Attributes:
        plaintext_offset (int):
        plaintext_length (int):
    """

    plaintext_offset: int
    plaintext_length: int

    def to_dict(self) -> dict[str, Any]:
        plaintext_offset = self.plaintext_offset

        plaintext_length = self.plaintext_length

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "plaintextOffset": plaintext_offset,
                "plaintextLength": plaintext_length,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        plaintext_offset = d.pop("plaintextOffset")

        plaintext_length = d.pop("plaintextLength")

        preview_init_segment = cls(
            plaintext_offset=plaintext_offset,
            plaintext_length=plaintext_length,
        )

        return preview_init_segment
