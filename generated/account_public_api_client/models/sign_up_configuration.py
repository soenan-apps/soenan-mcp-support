from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.sign_up_configuration_invitation_mode import (
    SignUpConfigurationInvitationMode,
)

T = TypeVar("T", bound="SignUpConfiguration")


@_attrs_define
class SignUpConfiguration:
    """
    Attributes:
        invitation_mode (SignUpConfigurationInvitationMode): Whether the current CSM admission policy hides, accepts, or
            requires an invitation code.
    """

    invitation_mode: SignUpConfigurationInvitationMode

    def to_dict(self) -> dict[str, Any]:
        invitation_mode = self.invitation_mode.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitationMode": invitation_mode,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        invitation_mode = SignUpConfigurationInvitationMode(d.pop("invitationMode"))

        sign_up_configuration = cls(
            invitation_mode=invitation_mode,
        )

        return sign_up_configuration
