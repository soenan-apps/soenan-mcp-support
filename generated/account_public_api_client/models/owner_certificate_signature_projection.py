from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.owner_certificate_signature_projection_format import (
    OwnerCertificateSignatureProjectionFormat,
)

if TYPE_CHECKING:
    from ..models.owner_device_approval_signed_fields import (
        OwnerDeviceApprovalSignedFields,
    )
    from ..models.owner_organization_admission_signed_fields import (
        OwnerOrganizationAdmissionSignedFields,
    )


T = TypeVar("T", bound="OwnerCertificateSignatureProjection")


@_attrs_define
class OwnerCertificateSignatureProjection:
    """
    Attributes:
        format_ (OwnerCertificateSignatureProjectionFormat):
        account_subject (str):
        certificate_digest (str): SHA-256 of JCS of the entire original immutable certificate wrapper, never of this
            projection.
        evidence_digest (str): Exact original operation-domain signed-command digest linking the existing immutable
            Account witness.
        signing_public_key (str): The key used for the original Ed25519 signature computation, not an Account identity
            assignment.
        signed_fields (OwnerDeviceApprovalSignedFields | OwnerOrganizationAdmissionSignedFields):
    """

    format_: OwnerCertificateSignatureProjectionFormat
    account_subject: str
    certificate_digest: str
    evidence_digest: str
    signing_public_key: str
    signed_fields: (
        OwnerDeviceApprovalSignedFields | OwnerOrganizationAdmissionSignedFields
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.owner_device_approval_signed_fields import (
            OwnerDeviceApprovalSignedFields,
        )

        format_ = self.format_.value

        account_subject = self.account_subject

        certificate_digest = self.certificate_digest

        evidence_digest = self.evidence_digest

        signing_public_key = self.signing_public_key

        signed_fields: dict[str, Any]
        if isinstance(self.signed_fields, OwnerDeviceApprovalSignedFields):
            signed_fields = self.signed_fields.to_dict()
        else:
            signed_fields = self.signed_fields.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "format": format_,
                "account_subject": account_subject,
                "certificate_digest": certificate_digest,
                "evidence_digest": evidence_digest,
                "signing_public_key": signing_public_key,
                "signed_fields": signed_fields,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_device_approval_signed_fields import (
            OwnerDeviceApprovalSignedFields,
        )
        from ..models.owner_organization_admission_signed_fields import (
            OwnerOrganizationAdmissionSignedFields,
        )

        d = dict(src_dict)
        format_ = OwnerCertificateSignatureProjectionFormat(d.pop("format"))

        account_subject = d.pop("account_subject")

        certificate_digest = d.pop("certificate_digest")

        evidence_digest = d.pop("evidence_digest")

        signing_public_key = d.pop("signing_public_key")

        def _parse_signed_fields(
            data: object,
        ) -> OwnerDeviceApprovalSignedFields | OwnerOrganizationAdmissionSignedFields:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_owner_certificate_signed_fields_type_0 = (
                    OwnerDeviceApprovalSignedFields.from_dict(data)
                )

                return componentsschemas_owner_certificate_signed_fields_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_owner_certificate_signed_fields_type_1 = (
                OwnerOrganizationAdmissionSignedFields.from_dict(data)
            )

            return componentsschemas_owner_certificate_signed_fields_type_1

        signed_fields = _parse_signed_fields(d.pop("signed_fields"))

        owner_certificate_signature_projection = cls(
            format_=format_,
            account_subject=account_subject,
            certificate_digest=certificate_digest,
            evidence_digest=evidence_digest,
            signing_public_key=signing_public_key,
            signed_fields=signed_fields,
        )

        return owner_certificate_signature_projection
