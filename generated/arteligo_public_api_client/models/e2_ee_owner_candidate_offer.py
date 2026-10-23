from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_custody_backup import E2EeOwnerCustodyBackup
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_command import E2EeSignedCommand
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EeOwnerCandidateOffer")


@_attrs_define
class E2EeOwnerCandidateOffer:
    """
    Attributes:
        organization_id (str):
        candidate_id (str):
        account_subject (str):
        key_id (str):
        public_key (str):
        recovery_id (str):
        recovery_generation (int):
        root_revision (int):
        custody_revision (int):
        device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request. Certificates are
            returned separately in E2eeDevice and are not accepted in this input.
        recovery_root (E2EeRecoveryRoot):
        source_anchor (E2EeSignedCommand):
        custody_backup (E2EeOwnerCustodyBackup): An opaque HPKE Auth backup for the owner's own recovery root or the
            approved target device. The complete encrypted backup is bound by the original device-signed command and is
            never decrypted by a server.
        issuer_admission (E2EeOwnerIssuerAdmission): The original source-root and exact immutable certificate references
            selected when this command was signed. Later certificates cannot qualify or replace this evidence.
    """

    organization_id: str
    candidate_id: str
    account_subject: str
    key_id: str
    public_key: str
    recovery_id: str
    recovery_generation: int
    root_revision: int
    custody_revision: int
    device: E2EeSignedDeviceInput
    recovery_root: E2EeRecoveryRoot
    source_anchor: E2EeSignedCommand
    custody_backup: E2EeOwnerCustodyBackup
    issuer_admission: E2EeOwnerIssuerAdmission

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        candidate_id = self.candidate_id

        account_subject = self.account_subject

        key_id = self.key_id

        public_key = self.public_key

        recovery_id = self.recovery_id

        recovery_generation = self.recovery_generation

        root_revision = self.root_revision

        custody_revision = self.custody_revision

        device = self.device.to_dict()

        recovery_root = self.recovery_root.to_dict()

        source_anchor = self.source_anchor.to_dict()

        custody_backup = self.custody_backup.to_dict()

        issuer_admission = self.issuer_admission.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "candidate_id": candidate_id,
                "account_subject": account_subject,
                "key_id": key_id,
                "public_key": public_key,
                "recovery_id": recovery_id,
                "recovery_generation": recovery_generation,
                "root_revision": root_revision,
                "custody_revision": custody_revision,
                "device": device,
                "recovery_root": recovery_root,
                "source_anchor": source_anchor,
                "custody_backup": custody_backup,
                "issuer_admission": issuer_admission,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_custody_backup import E2EeOwnerCustodyBackup
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_command import E2EeSignedCommand
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        candidate_id = d.pop("candidate_id")

        account_subject = d.pop("account_subject")

        key_id = d.pop("key_id")

        public_key = d.pop("public_key")

        recovery_id = d.pop("recovery_id")

        recovery_generation = d.pop("recovery_generation")

        root_revision = d.pop("root_revision")

        custody_revision = d.pop("custody_revision")

        device = E2EeSignedDeviceInput.from_dict(d.pop("device"))

        recovery_root = E2EeRecoveryRoot.from_dict(d.pop("recovery_root"))

        source_anchor = E2EeSignedCommand.from_dict(d.pop("source_anchor"))

        custody_backup = E2EeOwnerCustodyBackup.from_dict(d.pop("custody_backup"))

        issuer_admission = E2EeOwnerIssuerAdmission.from_dict(d.pop("issuer_admission"))

        e2_ee_owner_candidate_offer = cls(
            organization_id=organization_id,
            candidate_id=candidate_id,
            account_subject=account_subject,
            key_id=key_id,
            public_key=public_key,
            recovery_id=recovery_id,
            recovery_generation=recovery_generation,
            root_revision=root_revision,
            custody_revision=custody_revision,
            device=device,
            recovery_root=recovery_root,
            source_anchor=source_anchor,
            custody_backup=custody_backup,
            issuer_admission=issuer_admission,
        )

        return e2_ee_owner_candidate_offer
