from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeEpochLink")


@_attrs_define
class E2EeEpochLink:
    """
    Attributes:
        key_epoch (int):
        previous_key_ciphertext (str):
        signed_command (E2EeSignedCommand):
    """

    key_epoch: int
    previous_key_ciphertext: str
    signed_command: E2EeSignedCommand

    def to_dict(self) -> dict[str, Any]:
        key_epoch = self.key_epoch

        previous_key_ciphertext = self.previous_key_ciphertext

        signed_command = self.signed_command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "key_epoch": key_epoch,
                "previous_key_ciphertext": previous_key_ciphertext,
                "signed_command": signed_command,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        key_epoch = d.pop("key_epoch")

        previous_key_ciphertext = d.pop("previous_key_ciphertext")

        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        e2_ee_epoch_link = cls(
            key_epoch=key_epoch,
            previous_key_ciphertext=previous_key_ciphertext,
            signed_command=signed_command,
        )

        return e2_ee_epoch_link
