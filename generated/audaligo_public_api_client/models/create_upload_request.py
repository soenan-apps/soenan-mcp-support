from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.preview_intent import PreviewIntent


T = TypeVar("T", bound="CreateUploadRequest")


@_attrs_define
class CreateUploadRequest:
    """
    Attributes:
        preview_intent (PreviewIntent | Unset):
    """

    preview_intent: PreviewIntent | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        preview_intent: dict[str, Any] | Unset = UNSET
        if not isinstance(self.preview_intent, Unset):
            preview_intent = self.preview_intent.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if preview_intent is not UNSET:
            field_dict["previewIntent"] = preview_intent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preview_intent import PreviewIntent

        d = dict(src_dict)
        _preview_intent = d.pop("previewIntent", UNSET)
        preview_intent: PreviewIntent | Unset
        if isinstance(_preview_intent, Unset):
            preview_intent = UNSET
        else:
            preview_intent = PreviewIntent.from_dict(_preview_intent)

        create_upload_request = cls(
            preview_intent=preview_intent,
        )

        return create_upload_request
