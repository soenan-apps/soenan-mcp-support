from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_key_claim import FileKeyClaim
    from ..models.preview_intent import PreviewIntent


T = TypeVar("T", bound="UploadSessionResponse")


@_attrs_define
class UploadSessionResponse:
    """
    Attributes:
        upload_id (str):
        key_epoch (int):
        key_claim (FileKeyClaim):
        transfer_continuation (str | Unset):
        preview_intent (PreviewIntent | Unset):
    """

    upload_id: str
    key_epoch: int
    key_claim: FileKeyClaim
    transfer_continuation: str | Unset = UNSET
    preview_intent: PreviewIntent | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        upload_id = self.upload_id

        key_epoch = self.key_epoch

        key_claim = self.key_claim.to_dict()

        transfer_continuation = self.transfer_continuation

        preview_intent: dict[str, Any] | Unset = UNSET
        if not isinstance(self.preview_intent, Unset):
            preview_intent = self.preview_intent.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "uploadId": upload_id,
                "keyEpoch": key_epoch,
                "keyClaim": key_claim,
            }
        )
        if transfer_continuation is not UNSET:
            field_dict["transferContinuation"] = transfer_continuation
        if preview_intent is not UNSET:
            field_dict["previewIntent"] = preview_intent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_key_claim import FileKeyClaim
        from ..models.preview_intent import PreviewIntent

        d = dict(src_dict)
        upload_id = d.pop("uploadId")

        key_epoch = d.pop("keyEpoch")

        key_claim = FileKeyClaim.from_dict(d.pop("keyClaim"))
        transfer_continuation = d.pop("transferContinuation", UNSET)

        _preview_intent = d.pop("previewIntent", UNSET)
        preview_intent: PreviewIntent | Unset
        if isinstance(_preview_intent, Unset):
            preview_intent = UNSET
        else:
            preview_intent = PreviewIntent.from_dict(_preview_intent)

        upload_session_response = cls(
            upload_id=upload_id,
            key_epoch=key_epoch,
            key_claim=key_claim,
            transfer_continuation=transfer_continuation,
            preview_intent=preview_intent,
        )

        return upload_session_response
