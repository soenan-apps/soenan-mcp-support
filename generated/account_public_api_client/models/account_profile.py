from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.account_profile_email_verification_state import (
    AccountProfileEmailVerificationState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AccountProfile")


@_attrs_define
class AccountProfile:
    """
    Attributes:
        email_verification_state (AccountProfileEmailVerificationState):
        primary_email (None | str | Unset):
        display_name (None | str | Unset):
    """

    email_verification_state: AccountProfileEmailVerificationState
    primary_email: None | str | Unset = UNSET
    display_name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        email_verification_state = self.email_verification_state.value

        primary_email: None | str | Unset
        if isinstance(self.primary_email, Unset):
            primary_email = UNSET
        else:
            primary_email = self.primary_email

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "emailVerificationState": email_verification_state,
            }
        )
        if primary_email is not UNSET:
            field_dict["primaryEmail"] = primary_email
        if display_name is not UNSET:
            field_dict["displayName"] = display_name

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        email_verification_state = AccountProfileEmailVerificationState(
            d.pop("emailVerificationState")
        )

        def _parse_primary_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        primary_email = _parse_primary_email(d.pop("primaryEmail", UNSET))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("displayName", UNSET))

        account_profile = cls(
            email_verification_state=email_verification_state,
            primary_email=primary_email,
            display_name=display_name,
        )

        return account_profile
