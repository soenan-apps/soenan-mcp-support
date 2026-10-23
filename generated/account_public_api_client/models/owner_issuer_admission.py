from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.owner_issuer_admission_root import OwnerIssuerAdmissionRoot
    from ..models.owner_issuer_certificate_reference import (
        OwnerIssuerCertificateReference,
    )


T = TypeVar("T", bound="OwnerIssuerAdmission")


@_attrs_define
class OwnerIssuerAdmission:
    """
    Attributes:
        root (OwnerIssuerAdmissionRoot):
        root_evidence_digest (None | str):
        certificates (list[OwnerIssuerCertificateReference]): Closed original issuer-proof references, sorted by UTF-8
            device_id then certificate_digest. An absent reference cannot be supplemented by a later certificate.
    """

    root: OwnerIssuerAdmissionRoot
    root_evidence_digest: None | str
    certificates: list[OwnerIssuerCertificateReference]

    def to_dict(self) -> dict[str, Any]:
        root = self.root.to_dict()

        root_evidence_digest: None | str
        root_evidence_digest = self.root_evidence_digest

        certificates = []
        for certificates_item_data in self.certificates:
            certificates_item = certificates_item_data.to_dict()
            certificates.append(certificates_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "root": root,
                "root_evidence_digest": root_evidence_digest,
                "certificates": certificates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_issuer_admission_root import OwnerIssuerAdmissionRoot
        from ..models.owner_issuer_certificate_reference import (
            OwnerIssuerCertificateReference,
        )

        d = dict(src_dict)
        root = OwnerIssuerAdmissionRoot.from_dict(d.pop("root"))

        def _parse_root_evidence_digest(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        root_evidence_digest = _parse_root_evidence_digest(
            d.pop("root_evidence_digest")
        )

        certificates = []
        _certificates = d.pop("certificates")
        for certificates_item_data in _certificates:
            certificates_item = OwnerIssuerCertificateReference.from_dict(
                certificates_item_data
            )

            certificates.append(certificates_item)

        owner_issuer_admission = cls(
            root=root,
            root_evidence_digest=root_evidence_digest,
            certificates=certificates,
        )

        return owner_issuer_admission
