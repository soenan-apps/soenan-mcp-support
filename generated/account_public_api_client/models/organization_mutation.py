from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.idempotent_mutation_outcome import IdempotentMutationOutcome

T = TypeVar("T", bound="OrganizationMutation")


@_attrs_define
class OrganizationMutation:
    """
    Attributes:
        outcome (IdempotentMutationOutcome):
    """

    outcome: IdempotentMutationOutcome

    def to_dict(self) -> dict[str, Any]:
        outcome = self.outcome.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "outcome": outcome,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        outcome = IdempotentMutationOutcome(d.pop("outcome"))

        organization_mutation = cls(
            outcome=outcome,
        )

        return organization_mutation
