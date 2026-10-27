from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SignUpConfiguration")


@_attrs_define
class SignUpConfiguration:
    """
    Attributes:
        invitation_code_required (bool): Whether the current CSM admission policy requires an invitation code.
    """

    invitation_code_required: bool

    def to_dict(self) -> dict[str, Any]:
        invitation_code_required = self.invitation_code_required

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitationCodeRequired": invitation_code_required,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        invitation_code_required = d.pop("invitationCodeRequired")

        sign_up_configuration = cls(
            invitation_code_required=invitation_code_required,
        )

        return sign_up_configuration
