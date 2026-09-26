from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_upload_session_state import PreviewUploadSessionState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.preview_upload_key_claim import PreviewUploadKeyClaim
    from ..models.wrapped_data_key import WrappedDataKey


T = TypeVar("T", bound="PreviewUploadSession")


@_attrs_define
class PreviewUploadSession:
    """Source-bound sidecar begun only after the source file is committed. Browser sessions receive wrappedDataKey;
    delegated transfers instead receive a one-time preview-specific keyClaim. Never return both to a delegated caller.

        Attributes:
            preview_id (str):
            source_object_id (str):
            processing_id (str):
            job_id (str):
            epoch (int):
            nonce_base_b64_u (str):
            state (PreviewUploadSessionState): Reserved before a manifest, waiting for encrypted chunks, or fully ready.
            wrapped_data_key (WrappedDataKey | Unset):
            key_claim (PreviewUploadKeyClaim | Unset):
    """

    preview_id: str
    source_object_id: str
    processing_id: str
    job_id: str
    epoch: int
    nonce_base_b64_u: str
    state: PreviewUploadSessionState
    wrapped_data_key: WrappedDataKey | Unset = UNSET
    key_claim: PreviewUploadKeyClaim | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        preview_id = self.preview_id

        source_object_id = self.source_object_id

        processing_id = self.processing_id

        job_id = self.job_id

        epoch = self.epoch

        nonce_base_b64_u = self.nonce_base_b64_u

        state = self.state.value

        wrapped_data_key: dict[str, Any] | Unset = UNSET
        if not isinstance(self.wrapped_data_key, Unset):
            wrapped_data_key = self.wrapped_data_key.to_dict()

        key_claim: dict[str, Any] | Unset = UNSET
        if not isinstance(self.key_claim, Unset):
            key_claim = self.key_claim.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "previewId": preview_id,
                "sourceObjectId": source_object_id,
                "processingId": processing_id,
                "jobId": job_id,
                "epoch": epoch,
                "nonceBaseB64u": nonce_base_b64_u,
                "state": state,
            }
        )
        if wrapped_data_key is not UNSET:
            field_dict["wrappedDataKey"] = wrapped_data_key
        if key_claim is not UNSET:
            field_dict["keyClaim"] = key_claim

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.preview_upload_key_claim import PreviewUploadKeyClaim
        from ..models.wrapped_data_key import WrappedDataKey

        d = dict(src_dict)
        preview_id = d.pop("previewId")

        source_object_id = d.pop("sourceObjectId")

        processing_id = d.pop("processingId")

        job_id = d.pop("jobId")

        epoch = d.pop("epoch")

        nonce_base_b64_u = d.pop("nonceBaseB64u")

        state = PreviewUploadSessionState(d.pop("state"))

        _wrapped_data_key = d.pop("wrappedDataKey", UNSET)
        wrapped_data_key: WrappedDataKey | Unset
        if isinstance(_wrapped_data_key, Unset):
            wrapped_data_key = UNSET
        else:
            wrapped_data_key = WrappedDataKey.from_dict(_wrapped_data_key)

        _key_claim = d.pop("keyClaim", UNSET)
        key_claim: PreviewUploadKeyClaim | Unset
        if isinstance(_key_claim, Unset):
            key_claim = UNSET
        else:
            key_claim = PreviewUploadKeyClaim.from_dict(_key_claim)

        preview_upload_session = cls(
            preview_id=preview_id,
            source_object_id=source_object_id,
            processing_id=processing_id,
            job_id=job_id,
            epoch=epoch,
            nonce_base_b64_u=nonce_base_b64_u,
            state=state,
            wrapped_data_key=wrapped_data_key,
            key_claim=key_claim,
        )

        return preview_upload_session
