from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OwnerIssuerAdmissionRoot")


@_attrs_define
class OwnerIssuerAdmissionRoot:
    """
    Attributes:
        origin (str): Frozen provenance label only, never a cryptographic identity anchor.
        account_subject (str):
        recovery_id (str):
        generation (int):
        encryption_public_key (str):
        signing_public_key (str):
    """

    origin: str
    account_subject: str
    recovery_id: str
    generation: int
    encryption_public_key: str
    signing_public_key: str

    def to_dict(self) -> dict[str, Any]:
        origin = self.origin

        account_subject = self.account_subject

        recovery_id = self.recovery_id

        generation = self.generation

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "origin": origin,
                "account_subject": account_subject,
                "recovery_id": recovery_id,
                "generation": generation,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        origin = d.pop("origin")

        account_subject = d.pop("account_subject")

        recovery_id = d.pop("recovery_id")

        generation = d.pop("generation")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        owner_issuer_admission_root = cls(
            origin=origin,
            account_subject=account_subject,
            recovery_id=recovery_id,
            generation=generation,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
        )

        return owner_issuer_admission_root
