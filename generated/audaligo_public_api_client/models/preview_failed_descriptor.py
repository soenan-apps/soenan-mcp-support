from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.preview_failed_descriptor_kind import PreviewFailedDescriptorKind
from ..models.preview_failed_descriptor_state import PreviewFailedDescriptorState
from ..models.preview_failure_reason import PreviewFailureReason

T = TypeVar("T", bound="PreviewFailedDescriptor")


@_attrs_define
class PreviewFailedDescriptor:
    """
    Attributes:
        kind (PreviewFailedDescriptorKind):
        mix_version_id (str):
        preview_id (str):
        state (PreviewFailedDescriptorState):
        reason (PreviewFailureReason):
    """

    kind: PreviewFailedDescriptorKind
    mix_version_id: str
    preview_id: str
    state: PreviewFailedDescriptorState
    reason: PreviewFailureReason

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        mix_version_id = self.mix_version_id

        preview_id = self.preview_id

        state = self.state.value

        reason = self.reason.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "mixVersionId": mix_version_id,
                "previewId": preview_id,
                "state": state,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = PreviewFailedDescriptorKind(d.pop("kind"))

        mix_version_id = d.pop("mixVersionId")

        preview_id = d.pop("previewId")

        state = PreviewFailedDescriptorState(d.pop("state"))

        reason = PreviewFailureReason(d.pop("reason"))

        preview_failed_descriptor = cls(
            kind=kind,
            mix_version_id=mix_version_id,
            preview_id=preview_id,
            state=state,
            reason=reason,
        )

        return preview_failed_descriptor
