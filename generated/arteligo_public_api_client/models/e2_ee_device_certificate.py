from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_certificate_signature_projection_reference import (
        E2EeCertificateSignatureProjectionReference,
    )
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_command import E2EeSignedCommand
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EeDeviceCertificate")


@_attrs_define
class E2EeDeviceCertificate:
    """
    Attributes:
        operation (str):
        signed_command (E2EeSignedCommand | Unset):
        root_signature (str | Unset):
        public_device (E2EeSignedDeviceInput | Unset): Immutable public device snapshot bound into a signed request.
            Certificates are returned separately in E2eeDevice and are not accepted in this input.
        recovery_root (E2EeRecoveryRoot | Unset):
        signature_projection (E2EeCertificateSignatureProjectionReference | Unset): Resolve directly at Account. The
            digest identifies the original full certificate, never this reference wrapper.
    """

    operation: str
    signed_command: E2EeSignedCommand | Unset = UNSET
    root_signature: str | Unset = UNSET
    public_device: E2EeSignedDeviceInput | Unset = UNSET
    recovery_root: E2EeRecoveryRoot | Unset = UNSET
    signature_projection: E2EeCertificateSignatureProjectionReference | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        operation = self.operation

        signed_command: dict[str, Any] | Unset = UNSET
        if not isinstance(self.signed_command, Unset):
            signed_command = self.signed_command.to_dict()

        root_signature = self.root_signature

        public_device: dict[str, Any] | Unset = UNSET
        if not isinstance(self.public_device, Unset):
            public_device = self.public_device.to_dict()

        recovery_root: dict[str, Any] | Unset = UNSET
        if not isinstance(self.recovery_root, Unset):
            recovery_root = self.recovery_root.to_dict()

        signature_projection: dict[str, Any] | Unset = UNSET
        if not isinstance(self.signature_projection, Unset):
            signature_projection = self.signature_projection.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation": operation,
            }
        )
        if signed_command is not UNSET:
            field_dict["signed_command"] = signed_command
        if root_signature is not UNSET:
            field_dict["root_signature"] = root_signature
        if public_device is not UNSET:
            field_dict["public_device"] = public_device
        if recovery_root is not UNSET:
            field_dict["recovery_root"] = recovery_root
        if signature_projection is not UNSET:
            field_dict["signature_projection"] = signature_projection

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_certificate_signature_projection_reference import (
            E2EeCertificateSignatureProjectionReference,
        )
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_command import E2EeSignedCommand
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        operation = d.pop("operation")

        _signed_command = d.pop("signed_command", UNSET)
        signed_command: E2EeSignedCommand | Unset
        if isinstance(_signed_command, Unset):
            signed_command = UNSET
        else:
            signed_command = E2EeSignedCommand.from_dict(_signed_command)

        root_signature = d.pop("root_signature", UNSET)

        _public_device = d.pop("public_device", UNSET)
        public_device: E2EeSignedDeviceInput | Unset
        if isinstance(_public_device, Unset):
            public_device = UNSET
        else:
            public_device = E2EeSignedDeviceInput.from_dict(_public_device)

        _recovery_root = d.pop("recovery_root", UNSET)
        recovery_root: E2EeRecoveryRoot | Unset
        if isinstance(_recovery_root, Unset):
            recovery_root = UNSET
        else:
            recovery_root = E2EeRecoveryRoot.from_dict(_recovery_root)

        _signature_projection = d.pop("signature_projection", UNSET)
        signature_projection: E2EeCertificateSignatureProjectionReference | Unset
        if isinstance(_signature_projection, Unset):
            signature_projection = UNSET
        else:
            signature_projection = (
                E2EeCertificateSignatureProjectionReference.from_dict(
                    _signature_projection
                )
            )

        e2_ee_device_certificate = cls(
            operation=operation,
            signed_command=signed_command,
            root_signature=root_signature,
            public_device=public_device,
            recovery_root=recovery_root,
            signature_projection=signature_projection,
        )

        return e2_ee_device_certificate
