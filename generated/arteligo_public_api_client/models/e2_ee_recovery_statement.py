from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeRecoveryStatement")


@_attrs_define
class E2EeRecoveryStatement:
    """
    Attributes:
        recovery_id (str):
        encryption_public_key (str):
        signing_public_key (str):
        generation (int):
        account_subject (str):
    """

    recovery_id: str
    encryption_public_key: str
    signing_public_key: str
    generation: int
    account_subject: str

    def to_dict(self) -> dict[str, Any]:
        recovery_id = self.recovery_id

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        generation = self.generation

        account_subject = self.account_subject

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recovery_id": recovery_id,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "generation": generation,
                "account_subject": account_subject,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        recovery_id = d.pop("recovery_id")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        generation = d.pop("generation")

        account_subject = d.pop("account_subject")

        e2_ee_recovery_statement = cls(
            recovery_id=recovery_id,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            generation=generation,
            account_subject=account_subject,
        )

        return e2_ee_recovery_statement
