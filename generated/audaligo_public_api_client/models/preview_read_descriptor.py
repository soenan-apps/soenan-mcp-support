from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.preview_read_descriptor_contract import PreviewReadDescriptorContract

if TYPE_CHECKING:
    from ..models.preview_object import PreviewObject
    from ..models.wrapped_data_key import WrappedDataKey


T = TypeVar("T", bound="PreviewReadDescriptor")


@_attrs_define
class PreviewReadDescriptor:
    """
    Attributes:
        v (int):
        contract (PreviewReadDescriptorContract):
        mix_version_id (str):
        preview_id (str):
        wrapped_data_key (WrappedDataKey):
        preview (PreviewObject):
    """

    v: int
    contract: PreviewReadDescriptorContract
    mix_version_id: str
    preview_id: str
    wrapped_data_key: WrappedDataKey
    preview: PreviewObject

    def to_dict(self) -> dict[str, Any]:
        v = self.v

        contract = self.contract.value

        mix_version_id = self.mix_version_id

        preview_id = self.preview_id

        wrapped_data_key = self.wrapped_data_key.to_dict()

        preview = self.preview.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "v": v,
                "contract": contract,
                "mixVersionId": mix_version_id,
                "previewId": preview_id,
                "wrappedDataKey": wrapped_data_key,
                "preview": preview,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preview_object import PreviewObject
        from ..models.wrapped_data_key import WrappedDataKey

        d = dict(src_dict)
        v = d.pop("v")

        contract = PreviewReadDescriptorContract(d.pop("contract"))

        mix_version_id = d.pop("mixVersionId")

        preview_id = d.pop("previewId")

        wrapped_data_key = WrappedDataKey.from_dict(d.pop("wrappedDataKey"))

        preview = PreviewObject.from_dict(d.pop("preview"))

        preview_read_descriptor = cls(
            v=v,
            contract=contract,
            mix_version_id=mix_version_id,
            preview_id=preview_id,
            wrapped_data_key=wrapped_data_key,
            preview=preview,
        )

        return preview_read_descriptor
