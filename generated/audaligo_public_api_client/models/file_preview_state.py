from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.file_preview_state_state import FilePreviewStateState

if TYPE_CHECKING:
    from ..models.file_preview_media import FilePreviewMedia


T = TypeVar("T", bound="FilePreviewState")


@_attrs_define
class FilePreviewState:
    """
    Attributes:
        file_id (str):
        preview_id (str):
        state (FilePreviewStateState):
        reason (None | str):
        media (FilePreviewMedia | None):
    """

    file_id: str
    preview_id: str
    state: FilePreviewStateState
    reason: None | str
    media: FilePreviewMedia | None

    def to_dict(self) -> dict[str, Any]:
        from ..models.file_preview_media import FilePreviewMedia

        file_id = self.file_id

        preview_id = self.preview_id

        state = self.state.value

        reason: None | str
        reason = self.reason

        media: dict[str, Any] | None
        if isinstance(self.media, FilePreviewMedia):
            media = self.media.to_dict()
        else:
            media = self.media

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "fileId": file_id,
                "previewId": preview_id,
                "state": state,
                "reason": reason,
                "media": media,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.file_preview_media import FilePreviewMedia

        d = dict(src_dict)
        file_id = d.pop("fileId")

        preview_id = d.pop("previewId")

        state = FilePreviewStateState(d.pop("state"))

        def _parse_reason(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        reason = _parse_reason(d.pop("reason"))

        def _parse_media(data: object) -> FilePreviewMedia | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                media_type_1 = FilePreviewMedia.from_dict(data)

                return media_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FilePreviewMedia | None, data)

        media = _parse_media(d.pop("media"))

        file_preview_state = cls(
            file_id=file_id,
            preview_id=preview_id,
            state=state,
            reason=reason,
            media=media,
        )

        return file_preview_state
