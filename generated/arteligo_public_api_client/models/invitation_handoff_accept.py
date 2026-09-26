from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="InvitationHandoffAccept")


@_attrs_define
class InvitationHandoffAccept:
    """
    Attributes:
        invitation_id (str):
    """

    invitation_id: str

    def to_dict(self) -> dict[str, Any]:
        invitation_id = self.invitation_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitationId": invitation_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        invitation_id = d.pop("invitationId")

        invitation_handoff_accept = cls(
            invitation_id=invitation_id,
        )

        return invitation_handoff_accept
