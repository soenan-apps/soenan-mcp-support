from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.file_preview_read_descriptor import FilePreviewReadDescriptor


T = TypeVar("T", bound="FilePreviewReadDescriptorResponse")


@_attrs_define
class FilePreviewReadDescriptorResponse:
    """
    Attributes:
        ok (bool):
        descriptor (FilePreviewReadDescriptor):
    """

    ok: bool
    descriptor: FilePreviewReadDescriptor

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        descriptor = self.descriptor.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "descriptor": descriptor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.file_preview_read_descriptor import (
            FilePreviewReadDescriptor,
        )

        d = dict(src_dict)
        ok = d.pop("ok")

        descriptor = FilePreviewReadDescriptor.from_dict(d.pop("descriptor"))

        file_preview_read_descriptor_response = cls(
            ok=ok,
            descriptor=descriptor,
        )

        return file_preview_read_descriptor_response
