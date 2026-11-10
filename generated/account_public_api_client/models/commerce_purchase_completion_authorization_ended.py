from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_purchase_completion_authorization_ended_code import (
    CommercePurchaseCompletionAuthorizationEndedCode,
)
from ..models.commerce_purchase_completion_authorization_ended_kind import (
    CommercePurchaseCompletionAuthorizationEndedKind,
)

T = TypeVar("T", bound="CommercePurchaseCompletionAuthorizationEnded")


@_attrs_define
class CommercePurchaseCompletionAuthorizationEnded:
    """
    Attributes:
        kind (CommercePurchaseCompletionAuthorizationEndedKind):
        code (CommercePurchaseCompletionAuthorizationEndedCode):
    """

    kind: CommercePurchaseCompletionAuthorizationEndedKind
    code: CommercePurchaseCompletionAuthorizationEndedCode

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        code = self.code.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = CommercePurchaseCompletionAuthorizationEndedKind(d.pop("kind"))

        code = CommercePurchaseCompletionAuthorizationEndedCode(d.pop("code"))

        commerce_purchase_completion_authorization_ended = cls(
            kind=kind,
            code=code,
        )

        return commerce_purchase_completion_authorization_ended
