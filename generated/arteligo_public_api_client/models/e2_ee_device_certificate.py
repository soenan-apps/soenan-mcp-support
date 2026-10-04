from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeDeviceCertificate")


@_attrs_define
class E2EeDeviceCertificate:
    """
    Attributes:
        operation (str):
        signed_command (E2EeSignedCommand | Unset):
        root_signature (str | Unset):
        public_device (E2EeDevice | Unset):
        recovery_root (E2EeRecoveryRoot | Unset):
    """

    operation: str
    signed_command: E2EeSignedCommand | Unset = UNSET
    root_signature: str | Unset = UNSET
    public_device: E2EeDevice | Unset = UNSET
    recovery_root: E2EeRecoveryRoot | Unset = UNSET

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

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_command import E2EeSignedCommand

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
        public_device: E2EeDevice | Unset
        if isinstance(_public_device, Unset):
            public_device = UNSET
        else:
            public_device = E2EeDevice.from_dict(_public_device)

        _recovery_root = d.pop("recovery_root", UNSET)
        recovery_root: E2EeRecoveryRoot | Unset
        if isinstance(_recovery_root, Unset):
            recovery_root = UNSET
        else:
            recovery_root = E2EeRecoveryRoot.from_dict(_recovery_root)

        e2_ee_device_certificate = cls(
            operation=operation,
            signed_command=signed_command,
            root_signature=root_signature,
            public_device=public_device,
            recovery_root=recovery_root,
        )

        return e2_ee_device_certificate
