from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_dependency_outcome import OwnerKeyDependencyOutcome

if TYPE_CHECKING:
    from ..models.owner_key_custody_target import OwnerKeyCustodyTarget


T = TypeVar("T", bound="OwnerKeyTargetResult")


@_attrs_define
class OwnerKeyTargetResult:
    """Outcome is evaluated for the target purpose and scope. Project recipients use current sponsored access, independent
    of organization membership or seats. Historical references do not grant current eligibility.

        Attributes:
            target (OwnerKeyCustodyTarget):
            outcome (OwnerKeyDependencyOutcome):
            can_manage_organization_keys (bool):
            can_receive_organization_keys (bool):
    """

    target: OwnerKeyCustodyTarget
    outcome: OwnerKeyDependencyOutcome
    can_manage_organization_keys: bool
    can_receive_organization_keys: bool

    def to_dict(self) -> dict[str, Any]:
        target = self.target.to_dict()

        outcome = self.outcome.value

        can_manage_organization_keys = self.can_manage_organization_keys

        can_receive_organization_keys = self.can_receive_organization_keys

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "target": target,
                "outcome": outcome,
                "can_manage_organization_keys": can_manage_organization_keys,
                "can_receive_organization_keys": can_receive_organization_keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_key_custody_target import OwnerKeyCustodyTarget

        d = dict(src_dict)
        target = OwnerKeyCustodyTarget.from_dict(d.pop("target"))

        outcome = OwnerKeyDependencyOutcome(d.pop("outcome"))

        can_manage_organization_keys = d.pop("can_manage_organization_keys")

        can_receive_organization_keys = d.pop("can_receive_organization_keys")

        owner_key_target_result = cls(
            target=target,
            outcome=outcome,
            can_manage_organization_keys=can_manage_organization_keys,
            can_receive_organization_keys=can_receive_organization_keys,
        )

        return owner_key_target_result
