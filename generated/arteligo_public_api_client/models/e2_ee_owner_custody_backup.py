from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeOwnerCustodyBackup")


@_attrs_define
class E2EeOwnerCustodyBackup:
    """An opaque HPKE Auth backup for the owner's own recovery root or the approved target device. The complete encrypted
    backup is bound by the original device-signed command and is never decrypted by a server.

        Attributes:
            encapsulated_key (str):
            ciphertext (str):
    """

    encapsulated_key: str
    ciphertext: str

    def to_dict(self) -> dict[str, Any]:
        encapsulated_key = self.encapsulated_key

        ciphertext = self.ciphertext

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "encapsulated_key": encapsulated_key,
                "ciphertext": ciphertext,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        encapsulated_key = d.pop("encapsulated_key")

        ciphertext = d.pop("ciphertext")

        e2_ee_owner_custody_backup = cls(
            encapsulated_key=encapsulated_key,
            ciphertext=ciphertext,
        )

        return e2_ee_owner_custody_backup
