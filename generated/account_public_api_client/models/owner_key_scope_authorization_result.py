from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_dependency_outcome import OwnerKeyDependencyOutcome

if TYPE_CHECKING:
    from ..models.owner_key_scope_authorization_target import (
        OwnerKeyScopeAuthorizationTarget,
    )


T = TypeVar("T", bound="OwnerKeyScopeAuthorizationResult")


@_attrs_define
class OwnerKeyScopeAuthorizationResult:
    """
    Attributes:
        target (OwnerKeyScopeAuthorizationTarget):
        outcome (OwnerKeyDependencyOutcome):
    """

    target: OwnerKeyScopeAuthorizationTarget
    outcome: OwnerKeyDependencyOutcome

    def to_dict(self) -> dict[str, Any]:
        target = self.target.to_dict()

        outcome = self.outcome.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "target": target,
                "outcome": outcome,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_key_scope_authorization_target import (
            OwnerKeyScopeAuthorizationTarget,
        )

        d = dict(src_dict)
        target = OwnerKeyScopeAuthorizationTarget.from_dict(d.pop("target"))

        outcome = OwnerKeyDependencyOutcome(d.pop("outcome"))

        owner_key_scope_authorization_result = cls(
            target=target,
            outcome=outcome,
        )

        return owner_key_scope_authorization_result
