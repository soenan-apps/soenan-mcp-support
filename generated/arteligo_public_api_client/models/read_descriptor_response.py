from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.read_descriptor import ReadDescriptor


T = TypeVar("T", bound="ReadDescriptorResponse")


@_attrs_define
class ReadDescriptorResponse:
    """
    Attributes:
        ok (bool):
        descriptor (ReadDescriptor):
    """

    ok: bool
    descriptor: ReadDescriptor

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
        from ..models.read_descriptor import ReadDescriptor

        d = dict(src_dict)
        ok = d.pop("ok")

        descriptor = ReadDescriptor.from_dict(d.pop("descriptor"))

        read_descriptor_response = cls(
            ok=ok,
            descriptor=descriptor,
        )

        return read_descriptor_response
