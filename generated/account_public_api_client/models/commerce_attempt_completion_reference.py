from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

from ..models.commerce_attempt_completion_reference_kind import (
    CommerceAttemptCompletionReferenceKind,
)

T = TypeVar("T", bound="CommerceAttemptCompletionReference")


@_attrs_define
class CommerceAttemptCompletionReference:
    """
    Attributes:
        kind (CommerceAttemptCompletionReferenceKind):
        attempt_id (UUID):
    """

    kind: CommerceAttemptCompletionReferenceKind
    attempt_id: UUID

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        attempt_id = str(self.attempt_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "attemptId": attempt_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = CommerceAttemptCompletionReferenceKind(d.pop("kind"))

        attempt_id = UUID(d.pop("attemptId"))

        commerce_attempt_completion_reference = cls(
            kind=kind,
            attempt_id=attempt_id,
        )

        return commerce_attempt_completion_reference
