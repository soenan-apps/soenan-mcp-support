from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ResetPreviewUploadRequest")


@_attrs_define
class ResetPreviewUploadRequest:
    """
    Attributes:
        expected_preview_id (str):
    """

    expected_preview_id: str

    def to_dict(self) -> dict[str, Any]:
        expected_preview_id = self.expected_preview_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expectedPreviewId": expected_preview_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        expected_preview_id = d.pop("expectedPreviewId")

        reset_preview_upload_request = cls(
            expected_preview_id=expected_preview_id,
        )

        return reset_preview_upload_request
