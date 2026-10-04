from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeInvitationInfo")


@_attrs_define
class E2EeInvitationInfo:
    """
    Attributes:
        invitation_id (str):
        project_id (str):
        role (str):
        expires_at (int):
        binding_public_key (str):
        binding_signature (str):
        creator_device (E2EeDevice):
        signed_command (E2EeSignedCommand):
        state (str):
    """

    invitation_id: str
    project_id: str
    role: str
    expires_at: int
    binding_public_key: str
    binding_signature: str
    creator_device: E2EeDevice
    signed_command: E2EeSignedCommand
    state: str

    def to_dict(self) -> dict[str, Any]:
        invitation_id = self.invitation_id

        project_id = self.project_id

        role = self.role

        expires_at = self.expires_at

        binding_public_key = self.binding_public_key

        binding_signature = self.binding_signature

        creator_device = self.creator_device.to_dict()

        signed_command = self.signed_command.to_dict()

        state = self.state

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitation_id": invitation_id,
                "project_id": project_id,
                "role": role,
                "expires_at": expires_at,
                "binding_public_key": binding_public_key,
                "binding_signature": binding_signature,
                "creator_device": creator_device,
                "signed_command": signed_command,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        invitation_id = d.pop("invitation_id")

        project_id = d.pop("project_id")

        role = d.pop("role")

        expires_at = d.pop("expires_at")

        binding_public_key = d.pop("binding_public_key")

        binding_signature = d.pop("binding_signature")

        creator_device = E2EeDevice.from_dict(d.pop("creator_device"))

        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        state = d.pop("state")

        e2_ee_invitation_info = cls(
            invitation_id=invitation_id,
            project_id=project_id,
            role=role,
            expires_at=expires_at,
            binding_public_key=binding_public_key,
            binding_signature=binding_signature,
            creator_device=creator_device,
            signed_command=signed_command,
            state=state,
        )

        return e2_ee_invitation_info
