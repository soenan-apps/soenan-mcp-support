from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.passkey_view import PasskeyView


T = TypeVar("T", bound="PasskeyList")


@_attrs_define
class PasskeyList:
    """
    Attributes:
        passkeys (list[PasskeyView]):
    """

    passkeys: list[PasskeyView]

    def to_dict(self) -> dict[str, Any]:
        passkeys = []
        for passkeys_item_data in self.passkeys:
            passkeys_item = passkeys_item_data.to_dict()
            passkeys.append(passkeys_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "passkeys": passkeys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.passkey_view import PasskeyView

        d = dict(src_dict)
        passkeys = []
        _passkeys = d.pop("passkeys")
        for passkeys_item_data in _passkeys:
            passkeys_item = PasskeyView.from_dict(passkeys_item_data)

            passkeys.append(passkeys_item)

        passkey_list = cls(
            passkeys=passkeys,
        )

        return passkey_list
