from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="FilePreviewSegment")


@_attrs_define
class FilePreviewSegment:
    """
    Attributes:
        ordinal (int):
        start_seconds (float):
        end_seconds (float):
        plaintext_offset (int):
        plaintext_length (int):
    """

    ordinal: int
    start_seconds: float
    end_seconds: float
    plaintext_offset: int
    plaintext_length: int

    def to_dict(self) -> dict[str, Any]:
        ordinal = self.ordinal

        start_seconds = self.start_seconds

        end_seconds = self.end_seconds

        plaintext_offset = self.plaintext_offset

        plaintext_length = self.plaintext_length

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ordinal": ordinal,
                "startSeconds": start_seconds,
                "endSeconds": end_seconds,
                "plaintextOffset": plaintext_offset,
                "plaintextLength": plaintext_length,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ordinal = d.pop("ordinal")

        start_seconds = d.pop("startSeconds")

        end_seconds = d.pop("endSeconds")

        plaintext_offset = d.pop("plaintextOffset")

        plaintext_length = d.pop("plaintextLength")

        file_preview_segment = cls(
            ordinal=ordinal,
            start_seconds=start_seconds,
            end_seconds=end_seconds,
            plaintext_offset=plaintext_offset,
            plaintext_length=plaintext_length,
        )

        return file_preview_segment
