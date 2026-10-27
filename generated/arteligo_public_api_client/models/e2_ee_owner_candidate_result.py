from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerCandidateResult")


@_attrs_define
class E2EeOwnerCandidateResult:
    """
    Attributes:
        offer (E2EeSignedCommand):
        offer_digest (str):
        state (str):
        device (E2EeDevice):
        recovery (E2EeRecoveryPublic):
    """

    offer: E2EeSignedCommand
    offer_digest: str
    state: str
    device: E2EeDevice
    recovery: E2EeRecoveryPublic

    def to_dict(self) -> dict[str, Any]:
        offer = self.offer.to_dict()

        offer_digest = self.offer_digest

        state = self.state

        device = self.device.to_dict()

        recovery = self.recovery.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "offer": offer,
                "offer_digest": offer_digest,
                "state": state,
                "device": device,
                "recovery": recovery,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_recovery_public import E2EeRecoveryPublic
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        offer = E2EeSignedCommand.from_dict(d.pop("offer"))

        offer_digest = d.pop("offer_digest")

        state = d.pop("state")

        device = E2EeDevice.from_dict(d.pop("device"))

        recovery = E2EeRecoveryPublic.from_dict(d.pop("recovery"))

        e2_ee_owner_candidate_result = cls(
            offer=offer,
            offer_digest=offer_digest,
            state=state,
            device=device,
            recovery=recovery,
        )

        return e2_ee_owner_candidate_result
