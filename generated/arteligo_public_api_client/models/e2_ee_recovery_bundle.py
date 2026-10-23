from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device_certificate import E2EeDeviceCertificate
    from ..models.e2_ee_device_root_proof import E2EeDeviceRootProof
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_owner_binding_reference import E2EeOwnerBindingReference
    from ..models.e2_ee_owner_capsule import E2EeOwnerCapsule
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeRecoveryBundle")


@_attrs_define
class E2EeRecoveryBundle:
    """
    Attributes:
        recovery_id (str):
        encryption_public_key (str):
        signing_public_key (str):
        encrypted_bundle (str):
        generation (int):
        public_command (E2EeSignedCommand):
        certificates (list[E2EeDeviceCertificate] | Unset):
        device_roots (list[E2EeDeviceRootProof] | Unset):
        envelopes (list[E2EeEnvelope] | Unset): Current readable scope keys sealed to the replacement recovery root.
            Required for recovery_rotate and saved atomically with the root; omitted from stored recovery responses.
        owner_access_snapshot (E2EeOwnerCapsule | Unset):
        owner_access_snapshot_command (E2EeSignedCommand | Unset):
        owner_access_history (list[E2EeOwnerBindingReference] | Unset): All immutable Account-selected binding
            references originally owned by the authenticated subject, including retired selections and organizations the
            subject has left. These references grant only historical public proof and own custody-backup access, never
            current project content or envelopes.
    """

    recovery_id: str
    encryption_public_key: str
    signing_public_key: str
    encrypted_bundle: str
    generation: int
    public_command: E2EeSignedCommand
    certificates: list[E2EeDeviceCertificate] | Unset = UNSET
    device_roots: list[E2EeDeviceRootProof] | Unset = UNSET
    envelopes: list[E2EeEnvelope] | Unset = UNSET
    owner_access_snapshot: E2EeOwnerCapsule | Unset = UNSET
    owner_access_snapshot_command: E2EeSignedCommand | Unset = UNSET
    owner_access_history: list[E2EeOwnerBindingReference] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        recovery_id = self.recovery_id

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        encrypted_bundle = self.encrypted_bundle

        generation = self.generation

        public_command = self.public_command.to_dict()

        certificates: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.certificates, Unset):
            certificates = []
            for certificates_item_data in self.certificates:
                certificates_item = certificates_item_data.to_dict()
                certificates.append(certificates_item)

        device_roots: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.device_roots, Unset):
            device_roots = []
            for device_roots_item_data in self.device_roots:
                device_roots_item = device_roots_item_data.to_dict()
                device_roots.append(device_roots_item)

        envelopes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.envelopes, Unset):
            envelopes = []
            for envelopes_item_data in self.envelopes:
                envelopes_item = envelopes_item_data.to_dict()
                envelopes.append(envelopes_item)

        owner_access_snapshot: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_access_snapshot, Unset):
            owner_access_snapshot = self.owner_access_snapshot.to_dict()

        owner_access_snapshot_command: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_access_snapshot_command, Unset):
            owner_access_snapshot_command = self.owner_access_snapshot_command.to_dict()

        owner_access_history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.owner_access_history, Unset):
            owner_access_history = []
            for owner_access_history_item_data in self.owner_access_history:
                owner_access_history_item = owner_access_history_item_data.to_dict()
                owner_access_history.append(owner_access_history_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recovery_id": recovery_id,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "encrypted_bundle": encrypted_bundle,
                "generation": generation,
                "public_command": public_command,
            }
        )
        if certificates is not UNSET:
            field_dict["certificates"] = certificates
        if device_roots is not UNSET:
            field_dict["device_roots"] = device_roots
        if envelopes is not UNSET:
            field_dict["envelopes"] = envelopes
        if owner_access_snapshot is not UNSET:
            field_dict["owner_access_snapshot"] = owner_access_snapshot
        if owner_access_snapshot_command is not UNSET:
            field_dict["owner_access_snapshot_command"] = owner_access_snapshot_command
        if owner_access_history is not UNSET:
            field_dict["owner_access_history"] = owner_access_history

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device_certificate import E2EeDeviceCertificate
        from ..models.e2_ee_device_root_proof import E2EeDeviceRootProof
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_owner_binding_reference import E2EeOwnerBindingReference
        from ..models.e2_ee_owner_capsule import E2EeOwnerCapsule
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        recovery_id = d.pop("recovery_id")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        encrypted_bundle = d.pop("encrypted_bundle")

        generation = d.pop("generation")

        public_command = E2EeSignedCommand.from_dict(d.pop("public_command"))

        _certificates = d.pop("certificates", UNSET)
        certificates: list[E2EeDeviceCertificate] | Unset = UNSET
        if _certificates is not UNSET:
            certificates = []
            for certificates_item_data in _certificates:
                certificates_item = E2EeDeviceCertificate.from_dict(
                    certificates_item_data
                )

                certificates.append(certificates_item)

        _device_roots = d.pop("device_roots", UNSET)
        device_roots: list[E2EeDeviceRootProof] | Unset = UNSET
        if _device_roots is not UNSET:
            device_roots = []
            for device_roots_item_data in _device_roots:
                device_roots_item = E2EeDeviceRootProof.from_dict(
                    device_roots_item_data
                )

                device_roots.append(device_roots_item)

        _envelopes = d.pop("envelopes", UNSET)
        envelopes: list[E2EeEnvelope] | Unset = UNSET
        if _envelopes is not UNSET:
            envelopes = []
            for envelopes_item_data in _envelopes:
                envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

                envelopes.append(envelopes_item)

        _owner_access_snapshot = d.pop("owner_access_snapshot", UNSET)
        owner_access_snapshot: E2EeOwnerCapsule | Unset
        if isinstance(_owner_access_snapshot, Unset):
            owner_access_snapshot = UNSET
        else:
            owner_access_snapshot = E2EeOwnerCapsule.from_dict(_owner_access_snapshot)

        _owner_access_snapshot_command = d.pop("owner_access_snapshot_command", UNSET)
        owner_access_snapshot_command: E2EeSignedCommand | Unset
        if isinstance(_owner_access_snapshot_command, Unset):
            owner_access_snapshot_command = UNSET
        else:
            owner_access_snapshot_command = E2EeSignedCommand.from_dict(
                _owner_access_snapshot_command
            )

        _owner_access_history = d.pop("owner_access_history", UNSET)
        owner_access_history: list[E2EeOwnerBindingReference] | Unset = UNSET
        if _owner_access_history is not UNSET:
            owner_access_history = []
            for owner_access_history_item_data in _owner_access_history:
                owner_access_history_item = E2EeOwnerBindingReference.from_dict(
                    owner_access_history_item_data
                )

                owner_access_history.append(owner_access_history_item)

        e2_ee_recovery_bundle = cls(
            recovery_id=recovery_id,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            encrypted_bundle=encrypted_bundle,
            generation=generation,
            public_command=public_command,
            certificates=certificates,
            device_roots=device_roots,
            envelopes=envelopes,
            owner_access_snapshot=owner_access_snapshot,
            owner_access_snapshot_command=owner_access_snapshot_command,
            owner_access_history=owner_access_history,
        )

        return e2_ee_recovery_bundle
