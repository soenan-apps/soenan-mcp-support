from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.owner_device_approval_signed_fields_operation import (
    OwnerDeviceApprovalSignedFieldsOperation,
)

if TYPE_CHECKING:
    from ..models.owner_certificate_recovery_root import OwnerCertificateRecoveryRoot
    from ..models.owner_issuer_admission import OwnerIssuerAdmission


T = TypeVar("T", bound="OwnerDeviceApprovalSignedFields")


@_attrs_define
class OwnerDeviceApprovalSignedFields:
    """
    Attributes:
        operation (OwnerDeviceApprovalSignedFieldsOperation):
        issuer_device_id (str):
        device_id (str):
        account_subject (None | str): The actual signed target account declaration, or null for an original legacy body
            without that field. A present declaration must equal the existing witness subject.
        encryption_public_key (str):
        signing_public_key (str):
        challenge (str):
        recovery_root (None | OwnerCertificateRecoveryRoot): The actual signed declaration, or null when the original
            body had none.
        issuer_admission (None | OwnerIssuerAdmission): The actual signed declaration, or null when acceptance used an
            auxiliary admission. Never a copy of an unsigned witness field.
    """

    operation: OwnerDeviceApprovalSignedFieldsOperation
    issuer_device_id: str
    device_id: str
    account_subject: None | str
    encryption_public_key: str
    signing_public_key: str
    challenge: str
    recovery_root: None | OwnerCertificateRecoveryRoot
    issuer_admission: None | OwnerIssuerAdmission

    def to_dict(self) -> dict[str, Any]:
        from ..models.owner_certificate_recovery_root import (
            OwnerCertificateRecoveryRoot,
        )
        from ..models.owner_issuer_admission import OwnerIssuerAdmission

        operation = self.operation.value

        issuer_device_id = self.issuer_device_id

        device_id = self.device_id

        account_subject: None | str
        account_subject = self.account_subject

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        challenge = self.challenge

        recovery_root: dict[str, Any] | None
        if isinstance(self.recovery_root, OwnerCertificateRecoveryRoot):
            recovery_root = self.recovery_root.to_dict()
        else:
            recovery_root = self.recovery_root

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
                "device_id": device_id,
                "account_subject": account_subject,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "challenge": challenge,
                "recovery_root": recovery_root,
                "issuer_admission": issuer_admission,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_certificate_recovery_root import (
            OwnerCertificateRecoveryRoot,
        )
        from ..models.owner_issuer_admission import OwnerIssuerAdmission

        d = dict(src_dict)
        operation = OwnerDeviceApprovalSignedFieldsOperation(d.pop("operation"))

        issuer_device_id = d.pop("issuer_device_id")

        device_id = d.pop("device_id")

        def _parse_account_subject(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        account_subject = _parse_account_subject(d.pop("account_subject"))

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        challenge = d.pop("challenge")

        def _parse_recovery_root(data: object) -> None | OwnerCertificateRecoveryRoot:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                recovery_root_type_1 = OwnerCertificateRecoveryRoot.from_dict(data)

                return recovery_root_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OwnerCertificateRecoveryRoot, data)

        recovery_root = _parse_recovery_root(d.pop("recovery_root"))

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

        owner_device_approval_signed_fields = cls(
            operation=operation,
            issuer_device_id=issuer_device_id,
            device_id=device_id,
            account_subject=account_subject,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            challenge=challenge,
            recovery_root=recovery_root,
            issuer_admission=issuer_admission,
        )

        return owner_device_approval_signed_fields
