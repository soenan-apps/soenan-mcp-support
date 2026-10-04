from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_device_certificate import E2EeDeviceCertificate


T = TypeVar("T", bound="E2EeRecoveryPublic")


@_attrs_define
class E2EeRecoveryPublic:
    """
    Attributes:
        recovery_id (str):
        account_subject (str):
        encryption_public_key (str):
        signing_public_key (str):
        generation (int):
        certificates (list[E2EeDeviceCertificate]):
    """

    recovery_id: str
    account_subject: str
    encryption_public_key: str
    signing_public_key: str
    generation: int
    certificates: list[E2EeDeviceCertificate]

    def to_dict(self) -> dict[str, Any]:
        recovery_id = self.recovery_id

        account_subject = self.account_subject

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        generation = self.generation

        certificates = []
        for certificates_item_data in self.certificates:
            certificates_item = certificates_item_data.to_dict()
            certificates.append(certificates_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recovery_id": recovery_id,
                "account_subject": account_subject,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "generation": generation,
                "certificates": certificates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device_certificate import E2EeDeviceCertificate

        d = dict(src_dict)
        recovery_id = d.pop("recovery_id")

        account_subject = d.pop("account_subject")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        generation = d.pop("generation")

        certificates = []
        _certificates = d.pop("certificates")
        for certificates_item_data in _certificates:
            certificates_item = E2EeDeviceCertificate.from_dict(certificates_item_data)

            certificates.append(certificates_item)

        e2_ee_recovery_public = cls(
            recovery_id=recovery_id,
            account_subject=account_subject,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            generation=generation,
            certificates=certificates,
        )

        return e2_ee_recovery_public
