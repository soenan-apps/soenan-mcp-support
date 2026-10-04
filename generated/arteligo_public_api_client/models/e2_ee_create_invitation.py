from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeCreateInvitation")


@_attrs_define
class E2EeCreateInvitation:
    """
    Attributes:
        invitation_id (str):
        project_id (str):
        role (str):
        expires_at (int):
        binding_public_key (str):
        binding_signature (str):
    """

    invitation_id: str
    project_id: str
    role: str
    expires_at: int
    binding_public_key: str
    binding_signature: str

    def to_dict(self) -> dict[str, Any]:
        invitation_id = self.invitation_id

        project_id = self.project_id

        role = self.role

        expires_at = self.expires_at

        binding_public_key = self.binding_public_key

        binding_signature = self.binding_signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
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
        d = dict(src_dict)
        invitation_id = d.pop("invitation_id")

        project_id = d.pop("project_id")

        role = d.pop("role")

        expires_at = d.pop("expires_at")

        binding_public_key = d.pop("binding_public_key")

        binding_signature = d.pop("binding_signature")

        e2_ee_create_invitation = cls(
            invitation_id=invitation_id,
            project_id=project_id,
            role=role,
            expires_at=expires_at,
            binding_public_key=binding_public_key,
            binding_signature=binding_signature,
        )

        return e2_ee_create_invitation
