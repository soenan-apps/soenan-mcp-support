from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot


T = TypeVar("T", bound="E2EePeerTrust")


@_attrs_define
class E2EePeerTrust:
    """
    Attributes:
        trusted_device (E2EeDevice):
        recovery_root (E2EeRecoveryRoot | Unset):
    """

    trusted_device: E2EeDevice
    recovery_root: E2EeRecoveryRoot | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        trusted_device = self.trusted_device.to_dict()

        recovery_root: dict[str, Any] | Unset = UNSET
        if not isinstance(self.recovery_root, Unset):
            recovery_root = self.recovery_root.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "trusted_device": trusted_device,
            }
        )
        if recovery_root is not UNSET:
            field_dict["recovery_root"] = recovery_root

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot

        d = dict(src_dict)
        trusted_device = E2EeDevice.from_dict(d.pop("trusted_device"))

        _recovery_root = d.pop("recovery_root", UNSET)
        recovery_root: E2EeRecoveryRoot | Unset
        if isinstance(_recovery_root, Unset):
            recovery_root = UNSET
        else:
            recovery_root = E2EeRecoveryRoot.from_dict(_recovery_root)

        e2_ee_peer_trust = cls(
            trusted_device=trusted_device,
            recovery_root=recovery_root,
        )

        return e2_ee_peer_trust
