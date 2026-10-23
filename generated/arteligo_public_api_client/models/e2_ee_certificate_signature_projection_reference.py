from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeCertificateSignatureProjectionReference")


@_attrs_define
class E2EeCertificateSignatureProjectionReference:
    """Resolve directly at Account. The digest identifies the original full certificate, never this reference wrapper.

    Attributes:
        certificate_digest (str):
        witness_subject (str):
    """

    certificate_digest: str
    witness_subject: str

    def to_dict(self) -> dict[str, Any]:
        certificate_digest = self.certificate_digest

        witness_subject = self.witness_subject

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "certificate_digest": certificate_digest,
                "witness_subject": witness_subject,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        certificate_digest = d.pop("certificate_digest")

        witness_subject = d.pop("witness_subject")

        e2_ee_certificate_signature_projection_reference = cls(
            certificate_digest=certificate_digest,
            witness_subject=witness_subject,
        )

        return e2_ee_certificate_signature_projection_reference
