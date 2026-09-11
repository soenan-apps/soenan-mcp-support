from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="AcceptInvitationRequest")


@_attrs_define
class AcceptInvitationRequest:
    """
    Attributes:
        invitation_id (str):
        token (str):
    """

    invitation_id: str
    token: str

    def to_dict(self) -> dict[str, Any]:
        invitation_id = self.invitation_id

        token = self.token

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitationId": invitation_id,
                "token": token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        invitation_id = d.pop("invitationId")

        token = d.pop("token")

        accept_invitation_request = cls(
            invitation_id=invitation_id,
            token=token,
        )

        return accept_invitation_request
