from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_owner_issuer_certificate import E2EeOwnerIssuerCertificate
    from ..models.e2_ee_owner_issuer_root import E2EeOwnerIssuerRoot


T = TypeVar("T", bound="E2EeOwnerIssuerAdmission")


@_attrs_define
class E2EeOwnerIssuerAdmission:
    """The original source-root and exact immutable certificate references selected when this command was signed. Later
    certificates cannot qualify or replace this evidence.

        Attributes:
            root (E2EeOwnerIssuerRoot):
            root_evidence_digest (None | str):
            certificates (list[E2EeOwnerIssuerCertificate]):
    """

    root: E2EeOwnerIssuerRoot
    root_evidence_digest: None | str
    certificates: list[E2EeOwnerIssuerCertificate]

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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_issuer_certificate import E2EeOwnerIssuerCertificate
        from ..models.e2_ee_owner_issuer_root import E2EeOwnerIssuerRoot

        d = dict(src_dict)
        root = E2EeOwnerIssuerRoot.from_dict(d.pop("root"))

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
            certificates_item = E2EeOwnerIssuerCertificate.from_dict(
                certificates_item_data
            )

            certificates.append(certificates_item)

        e2_ee_owner_issuer_admission = cls(
            root=root,
            root_evidence_digest=root_evidence_digest,
            certificates=certificates,
        )

        return e2_ee_owner_issuer_admission
