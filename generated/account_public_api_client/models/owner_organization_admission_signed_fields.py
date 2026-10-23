from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.owner_organization_admission_signed_fields_operation import (
    OwnerOrganizationAdmissionSignedFieldsOperation,
)

if TYPE_CHECKING:
    from ..models.owner_certificate_organization_participation import (
        OwnerCertificateOrganizationParticipation,
    )
    from ..models.owner_issuer_admission import OwnerIssuerAdmission


T = TypeVar("T", bound="OwnerOrganizationAdmissionSignedFields")


@_attrs_define
class OwnerOrganizationAdmissionSignedFields:
    """
    Attributes:
        operation (OwnerOrganizationAdmissionSignedFieldsOperation):
        issuer_device_id (str):
        scope_id (str):
        key_epoch (int):
        participation (OwnerCertificateOrganizationParticipation):
        issuer_admission (None | OwnerIssuerAdmission): Only the original signed declaration. Null never imports an
            auxiliary witness admission into the signed fields.
    """

    operation: OwnerOrganizationAdmissionSignedFieldsOperation
    issuer_device_id: str
    scope_id: str
    key_epoch: int
    participation: OwnerCertificateOrganizationParticipation
    issuer_admission: None | OwnerIssuerAdmission

    def to_dict(self) -> dict[str, Any]:
        from ..models.owner_issuer_admission import OwnerIssuerAdmission

        operation = self.operation.value

        issuer_device_id = self.issuer_device_id

        scope_id = self.scope_id

        key_epoch = self.key_epoch

        participation = self.participation.to_dict()

        issuer_admission: dict[str, Any] | None
        if isinstance(self.issuer_admission, OwnerIssuerAdmission):
            issuer_admission = self.issuer_admission.to_dict()
        else:
            issuer_admission = self.issuer_admission

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation": operation,
                "issuer_device_id": issuer_device_id,
                "scope_id": scope_id,
                "key_epoch": key_epoch,
                "participation": participation,
                "issuer_admission": issuer_admission,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_certificate_organization_participation import (
            OwnerCertificateOrganizationParticipation,
        )
        from ..models.owner_issuer_admission import OwnerIssuerAdmission

        d = dict(src_dict)
        operation = OwnerOrganizationAdmissionSignedFieldsOperation(d.pop("operation"))

        issuer_device_id = d.pop("issuer_device_id")

        scope_id = d.pop("scope_id")

        key_epoch = d.pop("key_epoch")

        participation = OwnerCertificateOrganizationParticipation.from_dict(
            d.pop("participation")
        )

        def _parse_issuer_admission(data: object) -> None | OwnerIssuerAdmission:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                issuer_admission_type_1 = OwnerIssuerAdmission.from_dict(data)

                return issuer_admission_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OwnerIssuerAdmission, data)

        issuer_admission = _parse_issuer_admission(d.pop("issuer_admission"))

        owner_organization_admission_signed_fields = cls(
            operation=operation,
            issuer_device_id=issuer_device_id,
            scope_id=scope_id,
            key_epoch=key_epoch,
            participation=participation,
            issuer_admission=issuer_admission,
        )

        return owner_organization_admission_signed_fields
