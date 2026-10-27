from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_key_scope_authorization_target_basis import (
    OwnerKeyScopeAuthorizationTargetBasis,
)
from ..models.owner_key_scope_authorization_target_operation_class import (
    OwnerKeyScopeAuthorizationTargetOperationClass,
)

T = TypeVar("T", bound="OwnerKeyScopeAuthorizationTarget")


@_attrs_define
class OwnerKeyScopeAuthorizationTarget:
    """
    Attributes:
        actor_subject (str):
        organization_id (str):
        scope_id (str):
        basis (OwnerKeyScopeAuthorizationTargetBasis):
        operation_class (OwnerKeyScopeAuthorizationTargetOperationClass):
    """

    actor_subject: str
    organization_id: str
    scope_id: str
    basis: OwnerKeyScopeAuthorizationTargetBasis
    operation_class: OwnerKeyScopeAuthorizationTargetOperationClass

    def to_dict(self) -> dict[str, Any]:
        actor_subject = self.actor_subject

        organization_id = self.organization_id

        scope_id = self.scope_id

        basis = self.basis.value

        operation_class = self.operation_class.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "actor_subject": actor_subject,
                "organization_id": organization_id,
                "scope_id": scope_id,
                "basis": basis,
                "operation_class": operation_class,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        actor_subject = d.pop("actor_subject")

        organization_id = d.pop("organization_id")

        scope_id = d.pop("scope_id")

        basis = OwnerKeyScopeAuthorizationTargetBasis(d.pop("basis"))

        operation_class = OwnerKeyScopeAuthorizationTargetOperationClass(
            d.pop("operation_class")
        )

        owner_key_scope_authorization_target = cls(
            actor_subject=actor_subject,
            organization_id=organization_id,
            scope_id=scope_id,
            basis=basis,
            operation_class=operation_class,
        )

        return owner_key_scope_authorization_target
