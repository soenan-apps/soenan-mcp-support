from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.preview_read_descriptor import PreviewReadDescriptor


T = TypeVar("T", bound="PreviewReadDescriptorResponse")


@_attrs_define
class PreviewReadDescriptorResponse:
    """
    Attributes:
        ok (bool):
        descriptor (PreviewReadDescriptor):
    """

    ok: bool
    descriptor: PreviewReadDescriptor

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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preview_read_descriptor import PreviewReadDescriptor

        d = dict(src_dict)
        ok = d.pop("ok")

        descriptor = PreviewReadDescriptor.from_dict(d.pop("descriptor"))

        preview_read_descriptor_response = cls(
            ok=ok,
            descriptor=descriptor,
        )

        return preview_read_descriptor_response
