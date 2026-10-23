from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EeCreateInvitation")


@_attrs_define
class E2EeCreateInvitation:
    """
    Attributes:
        creator_device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request.
            Certificates are returned separately in E2eeDevice and are not accepted in this input.
        creator_recovery (E2EeRecoveryRoot):
        invitation_id (str):
        project_id (str):
        role (str):
        expires_at (int):
        binding_public_key (str):
        binding_signature (str):
    """

    creator_device: E2EeSignedDeviceInput
    creator_recovery: E2EeRecoveryRoot
    invitation_id: str
    project_id: str
    role: str
    expires_at: int
    binding_public_key: str
    binding_signature: str

    def to_dict(self) -> dict[str, Any]:
        creator_device = self.creator_device.to_dict()

        creator_recovery = self.creator_recovery.to_dict()

        invitation_id = self.invitation_id

        project_id = self.project_id

        role = self.role

        expires_at = self.expires_at

        binding_public_key = self.binding_public_key

        binding_signature = self.binding_signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "creator_device": creator_device,
                "creator_recovery": creator_recovery,
                "invitation_id": invitation_id,
                "project_id": project_id,
                "role": role,
                "expires_at": expires_at,
                "binding_public_key": binding_public_key,
                "binding_signature": binding_signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        creator_device = E2EeSignedDeviceInput.from_dict(d.pop("creator_device"))

        creator_recovery = E2EeRecoveryRoot.from_dict(d.pop("creator_recovery"))

        invitation_id = d.pop("invitation_id")

        project_id = d.pop("project_id")

        role = d.pop("role")

        expires_at = d.pop("expires_at")

        binding_public_key = d.pop("binding_public_key")

        binding_signature = d.pop("binding_signature")

        e2_ee_create_invitation = cls(
            creator_device=creator_device,
            creator_recovery=creator_recovery,
            invitation_id=invitation_id,
            project_id=project_id,
            role=role,
            expires_at=expires_at,
            binding_public_key=binding_public_key,
            binding_signature=binding_signature,
        )

        return e2_ee_create_invitation
