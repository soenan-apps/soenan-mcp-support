from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.commerce_right_state import CommerceRightState

T = TypeVar("T", bound="CommerceVerifyResponse")


@_attrs_define
class CommerceVerifyResponse:
    """
    Attributes:
        purchase_id (UUID):
        state (CommerceRightState):
        revision (int):
        may_finish_transaction (bool):
        manual_contract_conflict (bool):
    """

    purchase_id: UUID
    state: CommerceRightState
    revision: int
    may_finish_transaction: bool
    manual_contract_conflict: bool

    def to_dict(self) -> dict[str, Any]:
        purchase_id = str(self.purchase_id)

        state = self.state.value

        revision = self.revision

        may_finish_transaction = self.may_finish_transaction

        manual_contract_conflict = self.manual_contract_conflict

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "purchaseId": purchase_id,
                "state": state,
                "revision": revision,
                "mayFinishTransaction": may_finish_transaction,
                "manualContractConflict": manual_contract_conflict,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        purchase_id = UUID(d.pop("purchaseId"))

        state = CommerceRightState(d.pop("state"))

        revision = d.pop("revision")

        may_finish_transaction = d.pop("mayFinishTransaction")

        manual_contract_conflict = d.pop("manualContractConflict")

        commerce_verify_response = cls(
            purchase_id=purchase_id,
            state=state,
            revision=revision,
            may_finish_transaction=may_finish_transaction,
            manual_contract_conflict=manual_contract_conflict,
        )

        return commerce_verify_response
