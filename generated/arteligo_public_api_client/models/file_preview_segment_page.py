from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.file_preview_segment import FilePreviewSegment


T = TypeVar("T", bound="FilePreviewSegmentPage")


@_attrs_define
class FilePreviewSegmentPage:
    """
    Attributes:
        preview_id (str):
        segments (list[FilePreviewSegment]):
        next_cursor (None | str):
    """

    preview_id: str
    segments: list[FilePreviewSegment]
    next_cursor: None | str

    def to_dict(self) -> dict[str, Any]:
        preview_id = self.preview_id

        segments = []
        for segments_item_data in self.segments:
            segments_item = segments_item_data.to_dict()
            segments.append(segments_item)

        next_cursor: None | str
        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "previewId": preview_id,
                "segments": segments,
                "nextCursor": next_cursor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.file_preview_segment import FilePreviewSegment

        d = dict(src_dict)
        preview_id = d.pop("previewId")

        segments = []
        _segments = d.pop("segments")
        for segments_item_data in _segments:
            segments_item = FilePreviewSegment.from_dict(segments_item_data)

            segments.append(segments_item)

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("nextCursor"))

        file_preview_segment_page = cls(
            preview_id=preview_id,
            segments=segments,
            next_cursor=next_cursor,
        )

        return file_preview_segment_page
