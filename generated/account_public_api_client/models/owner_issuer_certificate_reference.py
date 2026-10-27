from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OwnerIssuerCertificateReference")


@_attrs_define
class OwnerIssuerCertificateReference:
    """
    Attributes:
        device_id (str):
        certificate_digest (str): Unpadded base64url SHA-256 of JCS of the entire original immutable public certificate.
    """

    device_id: str
    certificate_digest: str

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        certificate_digest = self.certificate_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "device_id": device_id,
                "certificate_digest": certificate_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        certificate_digest = d.pop("certificate_digest")

        owner_issuer_certificate_reference = cls(
            device_id=device_id,
            certificate_digest=certificate_digest,
        )

        return owner_issuer_certificate_reference
