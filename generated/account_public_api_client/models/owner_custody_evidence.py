from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.owner_custody_evidence_operation import OwnerCustodyEvidenceOperation

if TYPE_CHECKING:
    from ..models.owner_custody_device_identity import OwnerCustodyDeviceIdentity
    from ..models.owner_custody_organization_admission import (
        OwnerCustodyOrganizationAdmission,
    )
    from ..models.owner_custody_root_identity import OwnerCustodyRootIdentity
    from ..models.owner_issuer_admission import OwnerIssuerAdmission


T = TypeVar("T", bound="OwnerCustodyEvidence")


@_attrs_define
class OwnerCustodyEvidence:
    """
    Attributes:
        account_subject (str): Actual approving account for envelopes_save organization admission, not the admitted
            member.
        evidence_digest (str):
        operation (OwnerCustodyEvidenceOperation):
        issuer_device_id (str):
        issuer_admission (OwnerIssuerAdmission):
        issuer_root_evidence_digest (None | str): Account's exact latest root witness before this intent was first
            accepted. Null means no earlier Account root fact and requires an independent cryptographic Root anchor, not
            metadata or unwitnessed legacy history. Exact replay never rewrites this reference.
        accepted_custody_revision (int):
        target_identity_digest (str): Unpadded base64url SHA-256 of canonical JSON of the exact target fields, excluding
            kind. Organization admission commits organization_id and the full admitted member recovery_root without a nested
            kind or origin.
        target (OwnerCustodyDeviceIdentity | OwnerCustodyOrganizationAdmission | OwnerCustodyRootIdentity):
    """

    account_subject: str
    evidence_digest: str
    operation: OwnerCustodyEvidenceOperation
    issuer_device_id: str
    issuer_admission: OwnerIssuerAdmission
    issuer_root_evidence_digest: None | str
    accepted_custody_revision: int
    target_identity_digest: str
    target: (
        OwnerCustodyDeviceIdentity
        | OwnerCustodyOrganizationAdmission
        | OwnerCustodyRootIdentity
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.owner_custody_device_identity import OwnerCustodyDeviceIdentity
        from ..models.owner_custody_root_identity import OwnerCustodyRootIdentity

        account_subject = self.account_subject

        evidence_digest = self.evidence_digest

        operation = self.operation.value

        issuer_device_id = self.issuer_device_id

        issuer_admission = self.issuer_admission.to_dict()

        issuer_root_evidence_digest: None | str
        issuer_root_evidence_digest = self.issuer_root_evidence_digest

        accepted_custody_revision = self.accepted_custody_revision

        target_identity_digest = self.target_identity_digest

        target: dict[str, Any]
        if isinstance(self.target, OwnerCustodyDeviceIdentity) or isinstance(
            self.target, OwnerCustodyRootIdentity
        ):
            target = self.target.to_dict()
        else:
            target = self.target.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "account_subject": account_subject,
                "evidence_digest": evidence_digest,
                "operation": operation,
                "issuer_device_id": issuer_device_id,
                "issuer_admission": issuer_admission,
                "issuer_root_evidence_digest": issuer_root_evidence_digest,
                "accepted_custody_revision": accepted_custody_revision,
                "target_identity_digest": target_identity_digest,
                "target": target,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_custody_device_identity import OwnerCustodyDeviceIdentity
        from ..models.owner_custody_organization_admission import (
            OwnerCustodyOrganizationAdmission,
        )
        from ..models.owner_custody_root_identity import OwnerCustodyRootIdentity
        from ..models.owner_issuer_admission import OwnerIssuerAdmission

        d = dict(src_dict)
        account_subject = d.pop("account_subject")

        evidence_digest = d.pop("evidence_digest")

        operation = OwnerCustodyEvidenceOperation(d.pop("operation"))

        issuer_device_id = d.pop("issuer_device_id")

        issuer_admission = OwnerIssuerAdmission.from_dict(d.pop("issuer_admission"))

        def _parse_issuer_root_evidence_digest(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        issuer_root_evidence_digest = _parse_issuer_root_evidence_digest(
            d.pop("issuer_root_evidence_digest")
        )

        accepted_custody_revision = d.pop("accepted_custody_revision")

        target_identity_digest = d.pop("target_identity_digest")

        def _parse_target(
            data: object,
        ) -> (
            OwnerCustodyDeviceIdentity
            | OwnerCustodyOrganizationAdmission
            | OwnerCustodyRootIdentity
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_owner_custody_evidence_target_type_0 = (
                    OwnerCustodyDeviceIdentity.from_dict(data)
                )

                return componentsschemas_owner_custody_evidence_target_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_owner_custody_evidence_target_type_1 = (
                    OwnerCustodyRootIdentity.from_dict(data)
                )

                return componentsschemas_owner_custody_evidence_target_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_owner_custody_evidence_target_type_2 = (
                OwnerCustodyOrganizationAdmission.from_dict(data)
            )

            return componentsschemas_owner_custody_evidence_target_type_2

        target = _parse_target(d.pop("target"))

        owner_custody_evidence = cls(
            account_subject=account_subject,
            evidence_digest=evidence_digest,
            operation=operation,
            issuer_device_id=issuer_device_id,
            issuer_admission=issuer_admission,
            issuer_root_evidence_digest=issuer_root_evidence_digest,
            accepted_custody_revision=accepted_custody_revision,
            target_identity_digest=target_identity_digest,
            target=target,
        )

        return owner_custody_evidence
