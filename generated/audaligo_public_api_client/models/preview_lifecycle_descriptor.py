from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.preview_lifecycle_descriptor_kind import PreviewLifecycleDescriptorKind
from ..models.preview_lifecycle_descriptor_state import PreviewLifecycleDescriptorState

T = TypeVar("T", bound="PreviewLifecycleDescriptor")


@_attrs_define
class PreviewLifecycleDescriptor:
    """
    Attributes:
        kind (PreviewLifecycleDescriptorKind):
        mix_version_id (str):
        preview_id (str):
        state (PreviewLifecycleDescriptorState):
    """

    kind: PreviewLifecycleDescriptorKind
    mix_version_id: str
    preview_id: str
    state: PreviewLifecycleDescriptorState

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        mix_version_id = self.mix_version_id

        preview_id = self.preview_id

        state = self.state.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "mixVersionId": mix_version_id,
                "previewId": preview_id,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = PreviewLifecycleDescriptorKind(d.pop("kind"))

        mix_version_id = d.pop("mixVersionId")

        preview_id = d.pop("previewId")

        state = PreviewLifecycleDescriptorState(d.pop("state"))

        preview_lifecycle_descriptor = cls(
            kind=kind,
            mix_version_id=mix_version_id,
            preview_id=preview_id,
            state=state,
        )

        return preview_lifecycle_descriptor
