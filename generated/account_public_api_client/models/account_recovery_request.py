from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccountRecoveryRequest")


@_attrs_define
class AccountRecoveryRequest:
    """
    Attributes:
        email (str):
        redirect_url (str | Unset): Optional safe same-origin continuation. Never contains the recovery-link token.
    """

    email: str
    redirect_url: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        redirect_url = self.redirect_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "email": email,
            }
        )
        if redirect_url is not UNSET:
            field_dict["redirectUrl"] = redirect_url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        email = d.pop("email")

        redirect_url = d.pop("redirectUrl", UNSET)

        account_recovery_request = cls(
            email=email,
            redirect_url=redirect_url,
        )

        return account_recovery_request
