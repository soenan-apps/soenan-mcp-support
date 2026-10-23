from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission


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
        owner_access_snapshot_digest (str | Unset): SHA-256 of the exact canonical two-field Owner snapshot capsule
            bytes.
        owner_bindings_digest (str | Unset): SHA-256 of the JCS bare array of all originally-own immutable selected
            binding references, including retired selections, sorted by organization_id then binding_digest. Required for
            new recovery replacements.
        issuer_admission (E2EeOwnerIssuerAdmission | Unset): The original source-root and exact immutable certificate
            references selected when this command was signed. Later certificates cannot qualify or replace this evidence.
    """

    recovery_id: str
    encryption_public_key: str
    signing_public_key: str
    generation: int
    account_subject: str
    owner_access_snapshot_digest: str | Unset = UNSET
    owner_bindings_digest: str | Unset = UNSET
    issuer_admission: E2EeOwnerIssuerAdmission | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        recovery_id = self.recovery_id

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        generation = self.generation

        account_subject = self.account_subject

        owner_access_snapshot_digest = self.owner_access_snapshot_digest

        owner_bindings_digest = self.owner_bindings_digest

        issuer_admission: dict[str, Any] | Unset = UNSET
        if not isinstance(self.issuer_admission, Unset):
            issuer_admission = self.issuer_admission.to_dict()

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
        if owner_access_snapshot_digest is not UNSET:
            field_dict["owner_access_snapshot_digest"] = owner_access_snapshot_digest
        if owner_bindings_digest is not UNSET:
            field_dict["owner_bindings_digest"] = owner_bindings_digest
        if issuer_admission is not UNSET:
            field_dict["issuer_admission"] = issuer_admission

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission

        d = dict(src_dict)
        recovery_id = d.pop("recovery_id")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        generation = d.pop("generation")

        account_subject = d.pop("account_subject")

        owner_access_snapshot_digest = d.pop("owner_access_snapshot_digest", UNSET)

        owner_bindings_digest = d.pop("owner_bindings_digest", UNSET)

        _issuer_admission = d.pop("issuer_admission", UNSET)
        issuer_admission: E2EeOwnerIssuerAdmission | Unset
        if isinstance(_issuer_admission, Unset):
            issuer_admission = UNSET
        else:
            issuer_admission = E2EeOwnerIssuerAdmission.from_dict(_issuer_admission)

        e2_ee_recovery_statement = cls(
            recovery_id=recovery_id,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            generation=generation,
            account_subject=account_subject,
            owner_access_snapshot_digest=owner_access_snapshot_digest,
            owner_bindings_digest=owner_bindings_digest,
            issuer_admission=issuer_admission,
        )

        return e2_ee_recovery_statement
