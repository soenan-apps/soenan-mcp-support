from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.preview_failed_descriptor import PreviewFailedDescriptor
    from ..models.preview_lifecycle_descriptor import PreviewLifecycleDescriptor
    from ..models.preview_ready_descriptor import PreviewReadyDescriptor


T = TypeVar("T", bound="PreviewDescriptorResponse")


@_attrs_define
class PreviewDescriptorResponse:
    """
    Attributes:
        ok (bool):
        descriptor (PreviewFailedDescriptor | PreviewLifecycleDescriptor | PreviewReadyDescriptor):
    """

    ok: bool
    descriptor: PreviewFailedDescriptor | PreviewLifecycleDescriptor | PreviewReadyDescriptor

    def to_dict(self) -> dict[str, Any]:
        from ..models.preview_failed_descriptor import PreviewFailedDescriptor
        from ..models.preview_lifecycle_descriptor import PreviewLifecycleDescriptor

        ok = self.ok

        descriptor: dict[str, Any]
        if isinstance(self.descriptor, PreviewLifecycleDescriptor):
            descriptor = self.descriptor.to_dict()
        elif isinstance(self.descriptor, PreviewFailedDescriptor):
            descriptor = self.descriptor.to_dict()
        else:
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
        from ..models.preview_failed_descriptor import PreviewFailedDescriptor
        from ..models.preview_lifecycle_descriptor import PreviewLifecycleDescriptor
        from ..models.preview_ready_descriptor import PreviewReadyDescriptor

        d = dict(src_dict)
        ok = d.pop("ok")

        def _parse_descriptor(
            data: object,
        ) -> PreviewFailedDescriptor | PreviewLifecycleDescriptor | PreviewReadyDescriptor:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_descriptor_type_0 = PreviewLifecycleDescriptor.from_dict(data)

                return componentsschemas_preview_descriptor_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_preview_descriptor_type_1 = PreviewFailedDescriptor.from_dict(data)

                return componentsschemas_preview_descriptor_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_preview_descriptor_type_2 = PreviewReadyDescriptor.from_dict(data)

            return componentsschemas_preview_descriptor_type_2

        descriptor = _parse_descriptor(d.pop("descriptor"))

        preview_descriptor_response = cls(
            ok=ok,
            descriptor=descriptor,
        )

        return preview_descriptor_response
