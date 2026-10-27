from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CloseAccountRequest")


@_attrs_define
class CloseAccountRequest:
    """
    Attributes:
        current_password (str):
    """

    current_password: str

    def to_dict(self) -> dict[str, Any]:
        current_password = self.current_password

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "currentPassword": current_password,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_password = d.pop("currentPassword")

        close_account_request = cls(
            current_password=current_password,
        )

        return close_account_request
