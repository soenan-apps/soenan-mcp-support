from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

from ..models.commerce_contract_reconciliation_reference_kind import (
    CommerceContractReconciliationReferenceKind,
)

T = TypeVar("T", bound="CommerceContractReconciliationReference")


@_attrs_define
class CommerceContractReconciliationReference:
    """
    Attributes:
        kind (CommerceContractReconciliationReferenceKind):
        reconciliation_id (UUID):
    """

    kind: CommerceContractReconciliationReferenceKind
    reconciliation_id: UUID

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        reconciliation_id = str(self.reconciliation_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "reconciliationId": reconciliation_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = CommerceContractReconciliationReferenceKind(d.pop("kind"))

        reconciliation_id = UUID(d.pop("reconciliationId"))

        commerce_contract_reconciliation_reference = cls(
            kind=kind,
            reconciliation_id=reconciliation_id,
        )

        return commerce_contract_reconciliation_reference
