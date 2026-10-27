from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_root_replacement_pending_effect_reason import (
    E2EeRootReplacementPendingEffectReason,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="E2EeRootReplacementPendingEffect")


@_attrs_define
class E2EeRootReplacementPendingEffect:
    """
    Attributes:
        operation (str):
        command_digest (str):
        reason (E2EeRootReplacementPendingEffectReason):
        scope_id (str | Unset):
    """

    operation: str
    command_digest: str
    reason: E2EeRootReplacementPendingEffectReason
    scope_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        operation = self.operation

        command_digest = self.command_digest

        reason = self.reason.value

        scope_id = self.scope_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation": operation,
                "command_digest": command_digest,
                "reason": reason,
            }
        )
        if scope_id is not UNSET:
            field_dict["scope_id"] = scope_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        operation = d.pop("operation")

        command_digest = d.pop("command_digest")

        reason = E2EeRootReplacementPendingEffectReason(d.pop("reason"))

        scope_id = d.pop("scope_id", UNSET)

        e2_ee_root_replacement_pending_effect = cls(
            operation=operation,
            command_digest=command_digest,
            reason=reason,
            scope_id=scope_id,
        )

        return e2_ee_root_replacement_pending_effect
