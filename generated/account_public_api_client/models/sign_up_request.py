from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="SignUpRequest")


@_attrs_define
class SignUpRequest:
    """
    Attributes:
        email (str):
        password (str):
        terms_version_id (UUID):
        display_name (str | Unset):
        invitation_code (str | Unset): Optional CSM-issued signup invitation. Runtime policy decides whether it is
            required.
        redirect_url (str | Unset): Optional safe same-origin continuation. Never contains the email-link token.
    """

    email: str
    password: str
    terms_version_id: UUID
    display_name: str | Unset = UNSET
    invitation_code: str | Unset = UNSET
    redirect_url: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        password = self.password

        terms_version_id = str(self.terms_version_id)

        display_name = self.display_name

        invitation_code = self.invitation_code

        redirect_url = self.redirect_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "email": email,
                "password": password,
                "termsVersionId": terms_version_id,
            }
        )
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if invitation_code is not UNSET:
            field_dict["invitationCode"] = invitation_code
        if redirect_url is not UNSET:
            field_dict["redirectUrl"] = redirect_url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        email = d.pop("email")

        password = d.pop("password")

        terms_version_id = UUID(d.pop("termsVersionId"))

        display_name = d.pop("displayName", UNSET)

        invitation_code = d.pop("invitationCode", UNSET)

        redirect_url = d.pop("redirectUrl", UNSET)

        sign_up_request = cls(
            email=email,
            password=password,
            terms_version_id=terms_version_id,
            display_name=display_name,
            invitation_code=invitation_code,
            redirect_url=redirect_url,
        )

        return sign_up_request
