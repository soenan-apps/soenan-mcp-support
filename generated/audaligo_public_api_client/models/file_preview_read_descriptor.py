from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.file_preview_read_descriptor_contract import (
    FilePreviewReadDescriptorContract,
)

if TYPE_CHECKING:
    from ..models.file_preview_object import FilePreviewObject
    from ..models.wrapped_data_key import WrappedDataKey


T = TypeVar("T", bound="FilePreviewReadDescriptor")


@_attrs_define
class FilePreviewReadDescriptor:
    """
    Attributes:
        v (int):
        contract (FilePreviewReadDescriptorContract):
        file_id (str):
        preview_id (str):
        wrapped_data_key (WrappedDataKey):
        preview (FilePreviewObject):
    """

    v: int
    contract: FilePreviewReadDescriptorContract
    file_id: str
    preview_id: str
    wrapped_data_key: WrappedDataKey
    preview: FilePreviewObject

    def to_dict(self) -> dict[str, Any]:
        v = self.v

        contract = self.contract.value

        file_id = self.file_id

        preview_id = self.preview_id

        wrapped_data_key = self.wrapped_data_key.to_dict()

        preview = self.preview.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "v": v,
                "contract": contract,
                "fileId": file_id,
                "previewId": preview_id,
                "wrappedDataKey": wrapped_data_key,
                "preview": preview,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.file_preview_object import FilePreviewObject
        from ..models.wrapped_data_key import WrappedDataKey

        d = dict(src_dict)
        v = d.pop("v")

        contract = FilePreviewReadDescriptorContract(d.pop("contract"))

        file_id = d.pop("fileId")

        preview_id = d.pop("previewId")

        wrapped_data_key = WrappedDataKey.from_dict(d.pop("wrappedDataKey"))

        preview = FilePreviewObject.from_dict(d.pop("preview"))

        file_preview_read_descriptor = cls(
            v=v,
            contract=contract,
            file_id=file_id,
            preview_id=preview_id,
            wrapped_data_key=wrapped_data_key,
            preview=preview,
        )

        return file_preview_read_descriptor
