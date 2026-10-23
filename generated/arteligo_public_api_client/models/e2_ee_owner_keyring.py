from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority


T = TypeVar("T", bound="E2EeOwnerKeyring")


@_attrs_define
class E2EeOwnerKeyring:
    """
    Attributes:
        organization_id (str):
        owner_authority (E2EeOwnerAuthority):
        ciphertext (str):
    """

    organization_id: str
    owner_authority: E2EeOwnerAuthority
    ciphertext: str

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        owner_authority = self.owner_authority.to_dict()

        ciphertext = self.ciphertext

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "owner_authority": owner_authority,
                "ciphertext": ciphertext,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        ciphertext = d.pop("ciphertext")

        e2_ee_owner_keyring = cls(
            organization_id=organization_id,
            owner_authority=owner_authority,
            ciphertext=ciphertext,
        )

        return e2_ee_owner_keyring
