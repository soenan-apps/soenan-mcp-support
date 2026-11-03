from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_custody_root_identity_kind import OwnerCustodyRootIdentityKind

T = TypeVar("T", bound="OwnerCustodyRootIdentity")


@_attrs_define
class OwnerCustodyRootIdentity:
    """
    Attributes:
        kind (OwnerCustodyRootIdentityKind):
        account_subject (str):
        recovery_id (str):
        encryption_public_key (str):
        signing_public_key (str):
        generation (int):
    """

    kind: OwnerCustodyRootIdentityKind
    account_subject: str
    recovery_id: str
    encryption_public_key: str
    signing_public_key: str
    generation: int

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        account_subject = self.account_subject

        recovery_id = self.recovery_id

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        generation = self.generation

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "account_subject": account_subject,
                "recovery_id": recovery_id,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "generation": generation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = OwnerCustodyRootIdentityKind(d.pop("kind"))

        account_subject = d.pop("account_subject")

        recovery_id = d.pop("recovery_id")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        generation = d.pop("generation")

        owner_custody_root_identity = cls(
            kind=kind,
            account_subject=account_subject,
            recovery_id=recovery_id,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            generation=generation,
        )

        return owner_custody_root_identity
