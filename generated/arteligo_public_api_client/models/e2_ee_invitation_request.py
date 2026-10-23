from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_command import E2EeSignedCommand
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EeInvitationRequest")


@_attrs_define
class E2EeInvitationRequest:
    """
    Attributes:
        request_id (str):
        invitation_id (str):
        project_id (str):
        invitation_command (E2EeSignedCommand):
        account_subject (str):
        device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request. Certificates are
            returned separately in E2eeDevice and are not accepted in this input.
        recovery (E2EeRecoveryRoot):
        binding_signature (str):
    """

    request_id: str
    invitation_id: str
    project_id: str
    invitation_command: E2EeSignedCommand
    account_subject: str
    device: E2EeSignedDeviceInput
    recovery: E2EeRecoveryRoot
    binding_signature: str

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        invitation_id = self.invitation_id

        project_id = self.project_id

        invitation_command = self.invitation_command.to_dict()

        account_subject = self.account_subject

        device = self.device.to_dict()

        recovery = self.recovery.to_dict()

        binding_signature = self.binding_signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "request_id": request_id,
                "invitation_id": invitation_id,
                "project_id": project_id,
                "invitation_command": invitation_command,
                "account_subject": account_subject,
                "device": device,
                "recovery": recovery,
                "binding_signature": binding_signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_command import E2EeSignedCommand
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        request_id = d.pop("request_id")

        invitation_id = d.pop("invitation_id")

        project_id = d.pop("project_id")

        invitation_command = E2EeSignedCommand.from_dict(d.pop("invitation_command"))

        account_subject = d.pop("account_subject")

        device = E2EeSignedDeviceInput.from_dict(d.pop("device"))

        recovery = E2EeRecoveryRoot.from_dict(d.pop("recovery"))

        binding_signature = d.pop("binding_signature")

        e2_ee_invitation_request = cls(
            request_id=request_id,
            invitation_id=invitation_id,
            project_id=project_id,
            invitation_command=invitation_command,
            account_subject=account_subject,
            device=device,
            recovery=recovery,
            binding_signature=binding_signature,
        )

        return e2_ee_invitation_request
