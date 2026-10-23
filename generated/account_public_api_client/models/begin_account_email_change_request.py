from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="BeginAccountEmailChangeRequest")


@_attrs_define
class BeginAccountEmailChangeRequest:
    """
    Attributes:
        new_email (str):
    """

    new_email: str

    def to_dict(self) -> dict[str, Any]:
        new_email = self.new_email

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "newEmail": new_email,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        new_email = d.pop("newEmail")

        begin_account_email_change_request = cls(
            new_email=new_email,
        )

        return begin_account_email_change_request
