from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeOwnerIssuerCertificate")


@_attrs_define
class E2EeOwnerIssuerCertificate:
    """
    Attributes:
        device_id (str):
        certificate_digest (str):
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
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        certificate_digest = d.pop("certificate_digest")

        e2_ee_owner_issuer_certificate = cls(
            device_id=device_id,
            certificate_digest=certificate_digest,
        )

        return e2_ee_owner_issuer_certificate
