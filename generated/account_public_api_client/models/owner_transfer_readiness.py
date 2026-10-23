from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.owner_transfer_blocker import OwnerTransferBlocker
from ..models.owner_transfer_readiness_state import OwnerTransferReadinessState

T = TypeVar("T", bound="OwnerTransferReadiness")


@_attrs_define
class OwnerTransferReadiness:
    """
    Attributes:
        ownership_revision (int):
        state (OwnerTransferReadinessState):
        blocker (OwnerTransferBlocker):
    """

    ownership_revision: int
    state: OwnerTransferReadinessState
    blocker: OwnerTransferBlocker

    def to_dict(self) -> dict[str, Any]:
        ownership_revision = self.ownership_revision

        state = self.state.value

        blocker = self.blocker.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ownershipRevision": ownership_revision,
                "state": state,
                "blocker": blocker,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ownership_revision = d.pop("ownershipRevision")

        state = OwnerTransferReadinessState(d.pop("state"))

        blocker = OwnerTransferBlocker(d.pop("blocker"))

        owner_transfer_readiness = cls(
            ownership_revision=ownership_revision,
            state=state,
            blocker=blocker,
        )

        return owner_transfer_readiness
