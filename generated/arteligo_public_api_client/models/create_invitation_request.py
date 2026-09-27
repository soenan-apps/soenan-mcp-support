from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.create_invitation_request_access_role import (
    CreateInvitationRequestAccessRole,
)

T = TypeVar("T", bound="CreateInvitationRequest")


@_attrs_define
class CreateInvitationRequest:
    """
    Attributes:
        access_role (CreateInvitationRequestAccessRole):
        token (str):
    """

    access_role: CreateInvitationRequestAccessRole
    token: str

    def to_dict(self) -> dict[str, Any]:
        access_role = self.access_role.value

        token = self.token

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "accessRole": access_role,
                "token": token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        access_role = CreateInvitationRequestAccessRole(d.pop("accessRole"))

        token = d.pop("token")

        create_invitation_request = cls(
            access_role=access_role,
            token=token,
        )

        return create_invitation_request
