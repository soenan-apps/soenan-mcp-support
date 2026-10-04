from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device_certificate import E2EeDeviceCertificate


T = TypeVar("T", bound="E2EeDevice")


@_attrs_define
class E2EeDevice:
    """
    Attributes:
        device_id (str):
        account_subject (str):
        encryption_public_key (str):
        signing_public_key (str):
        state (str):
        certificates (list[E2EeDeviceCertificate] | Unset):
    """

    device_id: str
    account_subject: str
    encryption_public_key: str
    signing_public_key: str
    state: str
    certificates: list[E2EeDeviceCertificate] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        account_subject = self.account_subject

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        state = self.state

        certificates: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.certificates, Unset):
            certificates = []
            for certificates_item_data in self.certificates:
                certificates_item = certificates_item_data.to_dict()
                certificates.append(certificates_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "device_id": device_id,
                "account_subject": account_subject,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "state": state,
            }
        )
        if certificates is not UNSET:
            field_dict["certificates"] = certificates

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device_certificate import E2EeDeviceCertificate

        d = dict(src_dict)
        device_id = d.pop("device_id")

        account_subject = d.pop("account_subject")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        state = d.pop("state")

        _certificates = d.pop("certificates", UNSET)
        certificates: list[E2EeDeviceCertificate] | Unset = UNSET
        if _certificates is not UNSET:
            certificates = []
            for certificates_item_data in _certificates:
                certificates_item = E2EeDeviceCertificate.from_dict(
                    certificates_item_data
                )

                certificates.append(certificates_item)

        e2_ee_device = cls(
            device_id=device_id,
            account_subject=account_subject,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            state=state,
            certificates=certificates,
        )

        return e2_ee_device
