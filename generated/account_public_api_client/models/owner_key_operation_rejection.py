from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_operation_rejection_reason import (
    OwnerKeyOperationRejectionReason,
)

T = TypeVar("T", bound="OwnerKeyOperationRejection")


@_attrs_define
class OwnerKeyOperationRejection:
    """
    Attributes:
        operation_id (str):
        actor_subject (str):
        preparation_digest (str):
        request_digest (str):
        reason (OwnerKeyOperationRejectionReason):
    """

    operation_id: str
    actor_subject: str
    preparation_digest: str
    request_digest: str
    reason: OwnerKeyOperationRejectionReason

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        actor_subject = self.actor_subject

        preparation_digest = self.preparation_digest

        request_digest = self.request_digest

        reason = self.reason.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "actor_subject": actor_subject,
                "preparation_digest": preparation_digest,
                "request_digest": request_digest,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        actor_subject = d.pop("actor_subject")

        preparation_digest = d.pop("preparation_digest")

        request_digest = d.pop("request_digest")

        reason = OwnerKeyOperationRejectionReason(d.pop("reason"))

        owner_key_operation_rejection = cls(
            operation_id=operation_id,
            actor_subject=actor_subject,
            preparation_digest=preparation_digest,
            request_digest=request_digest,
            reason=reason,
        )

        return owner_key_operation_rejection
