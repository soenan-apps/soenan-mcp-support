from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_owner_custody_backup import E2EeOwnerCustodyBackup
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot


T = TypeVar("T", bound="E2EeDeviceApproval")


@_attrs_define
class E2EeDeviceApproval:
    """
    Attributes:
        device_id (str):
        encryption_public_key (str):
        signing_public_key (str):
        challenge (str):
        envelopes (list[E2EeEnvelope]):
        account_subject (str | Unset): Signed target Account subject when present. Historical commands without this
            field retain their original bytes.
        state (str | Unset): Original signed device state retained by legacy commands. This metadata does not grant
            current approval or override the stored device state.
        recovery_root (E2EeRecoveryRoot | Unset):
        owner_access_backup (E2EeOwnerCustodyBackup | Unset): An opaque HPKE Auth backup for the owner's own recovery
            root or the approved target device. The complete encrypted backup is bound by the original device-signed command
            and is never decrypted by a server.
        issuer_admission (E2EeOwnerIssuerAdmission | Unset): The original source-root and exact immutable certificate
            references selected when this command was signed. Later certificates cannot qualify or replace this evidence.
    """

    device_id: str
    encryption_public_key: str
    signing_public_key: str
    challenge: str
    envelopes: list[E2EeEnvelope]
    account_subject: str | Unset = UNSET
    state: str | Unset = UNSET
    recovery_root: E2EeRecoveryRoot | Unset = UNSET
    owner_access_backup: E2EeOwnerCustodyBackup | Unset = UNSET
    issuer_admission: E2EeOwnerIssuerAdmission | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        challenge = self.challenge

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        account_subject = self.account_subject

        state = self.state

        recovery_root: dict[str, Any] | Unset = UNSET
        if not isinstance(self.recovery_root, Unset):
            recovery_root = self.recovery_root.to_dict()

        owner_access_backup: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_access_backup, Unset):
            owner_access_backup = self.owner_access_backup.to_dict()

        issuer_admission: dict[str, Any] | Unset = UNSET
        if not isinstance(self.issuer_admission, Unset):
            issuer_admission = self.issuer_admission.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "device_id": device_id,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "challenge": challenge,
                "envelopes": envelopes,
            }
        )
        if account_subject is not UNSET:
            field_dict["account_subject"] = account_subject
        if state is not UNSET:
            field_dict["state"] = state
        if recovery_root is not UNSET:
            field_dict["recovery_root"] = recovery_root
        if owner_access_backup is not UNSET:
            field_dict["owner_access_backup"] = owner_access_backup
        if issuer_admission is not UNSET:
            field_dict["issuer_admission"] = issuer_admission

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_owner_custody_backup import E2EeOwnerCustodyBackup
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot

        d = dict(src_dict)
        device_id = d.pop("device_id")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        challenge = d.pop("challenge")

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        account_subject = d.pop("account_subject", UNSET)

        state = d.pop("state", UNSET)

        _recovery_root = d.pop("recovery_root", UNSET)
        recovery_root: E2EeRecoveryRoot | Unset
        if isinstance(_recovery_root, Unset):
            recovery_root = UNSET
        else:
            recovery_root = E2EeRecoveryRoot.from_dict(_recovery_root)

        _owner_access_backup = d.pop("owner_access_backup", UNSET)
        owner_access_backup: E2EeOwnerCustodyBackup | Unset
        if isinstance(_owner_access_backup, Unset):
            owner_access_backup = UNSET
        else:
            owner_access_backup = E2EeOwnerCustodyBackup.from_dict(_owner_access_backup)

        _issuer_admission = d.pop("issuer_admission", UNSET)
        issuer_admission: E2EeOwnerIssuerAdmission | Unset
        if isinstance(_issuer_admission, Unset):
            issuer_admission = UNSET
        else:
            issuer_admission = E2EeOwnerIssuerAdmission.from_dict(_issuer_admission)

        e2_ee_device_approval = cls(
            device_id=device_id,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            challenge=challenge,
            envelopes=envelopes,
            account_subject=account_subject,
            state=state,
            recovery_root=recovery_root,
            owner_access_backup=owner_access_backup,
            issuer_admission=issuer_admission,
        )

        return e2_ee_device_approval
