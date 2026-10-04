from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot


T = TypeVar("T", bound="E2EeInvitationRequest")


@_attrs_define
class E2EeInvitationRequest:
    """
    Attributes:
        request_id (str):
        invitation_id (str):
        account_subject (str):
        device (E2EeDevice):
        recovery (E2EeRecoveryRoot):
        binding_signature (str):
    """

    request_id: str
    invitation_id: str
    account_subject: str
    device: E2EeDevice
    recovery: E2EeRecoveryRoot
    binding_signature: str

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        invitation_id = self.invitation_id

        account_subject = self.account_subject

        device = self.device.to_dict()

        recovery = self.recovery.to_dict()

        binding_signature = self.binding_signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "request_id": request_id,
                "invitation_id": invitation_id,
                "account_subject": account_subject,
                "device": device,
                "recovery": recovery,
                "binding_signature": binding_signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot

        d = dict(src_dict)
        request_id = d.pop("request_id")

        invitation_id = d.pop("invitation_id")

        account_subject = d.pop("account_subject")

        device = E2EeDevice.from_dict(d.pop("device"))

        recovery = E2EeRecoveryRoot.from_dict(d.pop("recovery"))

        binding_signature = d.pop("binding_signature")

        e2_ee_invitation_request = cls(
            request_id=request_id,
            invitation_id=invitation_id,
            account_subject=account_subject,
            device=device,
            recovery=recovery,
            binding_signature=binding_signature,
        )

        return e2_ee_invitation_request
