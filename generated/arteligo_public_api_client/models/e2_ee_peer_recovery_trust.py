from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EePeerRecoveryTrust")


@_attrs_define
class E2EePeerRecoveryTrust:
    """
    Attributes:
        trusted_device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request.
            Certificates are returned separately in E2eeDevice and are not accepted in this input.
        recovery_root (E2EeRecoveryRoot):
    """

    trusted_device: E2EeSignedDeviceInput
    recovery_root: E2EeRecoveryRoot

    def to_dict(self) -> dict[str, Any]:
        trusted_device = self.trusted_device.to_dict()

        recovery_root = self.recovery_root.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "trusted_device": trusted_device,
                "recovery_root": recovery_root,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        trusted_device = E2EeSignedDeviceInput.from_dict(d.pop("trusted_device"))

        recovery_root = E2EeRecoveryRoot.from_dict(d.pop("recovery_root"))

        e2_ee_peer_recovery_trust = cls(
            trusted_device=trusted_device,
            recovery_root=recovery_root,
        )

        return e2_ee_peer_recovery_trust
