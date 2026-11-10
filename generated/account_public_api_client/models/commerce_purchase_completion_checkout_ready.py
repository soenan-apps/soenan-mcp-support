from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_purchase_completion_checkout_ready_kind import (
    CommercePurchaseCompletionCheckoutReadyKind,
)

if TYPE_CHECKING:
    from ..models.commerce_attempt_completion_reference import (
        CommerceAttemptCompletionReference,
    )
    from ..models.commerce_contract_reconciliation_reference import (
        CommerceContractReconciliationReference,
    )
    from ..models.commerce_purchase_attempt import CommercePurchaseAttempt


T = TypeVar("T", bound="CommercePurchaseCompletionCheckoutReady")


@_attrs_define
class CommercePurchaseCompletionCheckoutReady:
    """
    Attributes:
        kind (CommercePurchaseCompletionCheckoutReadyKind):
        reference (CommerceAttemptCompletionReference | CommerceContractReconciliationReference):
        attempt (CommercePurchaseAttempt):
    """

    kind: CommercePurchaseCompletionCheckoutReadyKind
    reference: (
        CommerceAttemptCompletionReference | CommerceContractReconciliationReference
    )
    attempt: CommercePurchaseAttempt

    def to_dict(self) -> dict[str, Any]:
        from ..models.commerce_attempt_completion_reference import (
            CommerceAttemptCompletionReference,
        )

        kind = self.kind.value

        reference: dict[str, Any]
        if isinstance(self.reference, CommerceAttemptCompletionReference):
            reference = self.reference.to_dict()
        else:
            reference = self.reference.to_dict()

        attempt = self.attempt.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "reference": reference,
                "attempt": attempt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.commerce_attempt_completion_reference import (
            CommerceAttemptCompletionReference,
        )
        from ..models.commerce_contract_reconciliation_reference import (
            CommerceContractReconciliationReference,
        )
        from ..models.commerce_purchase_attempt import CommercePurchaseAttempt

        d = dict(src_dict)
        kind = CommercePurchaseCompletionCheckoutReadyKind(d.pop("kind"))

        def _parse_reference(
            data: object,
        ) -> (
            CommerceAttemptCompletionReference | CommerceContractReconciliationReference
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_commerce_completion_reference_type_0 = (
                    CommerceAttemptCompletionReference.from_dict(data)
                )

                return componentsschemas_commerce_completion_reference_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_commerce_completion_reference_type_1 = (
                CommerceContractReconciliationReference.from_dict(data)
            )

            return componentsschemas_commerce_completion_reference_type_1

        reference = _parse_reference(d.pop("reference"))

        attempt = CommercePurchaseAttempt.from_dict(d.pop("attempt"))

        commerce_purchase_completion_checkout_ready = cls(
            kind=kind,
            reference=reference,
            attempt=attempt,
        )

        return commerce_purchase_completion_checkout_ready
