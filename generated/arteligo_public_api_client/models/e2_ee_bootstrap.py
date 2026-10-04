from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_bundle import E2EeRecoveryBundle


T = TypeVar("T", bound="E2EeBootstrap")


@_attrs_define
class E2EeBootstrap:
    """
    Attributes:
        device (E2EeDevice):
        recovery (E2EeRecoveryBundle):
        root_signature (str):
    """

    device: E2EeDevice
    recovery: E2EeRecoveryBundle
    root_signature: str

    def to_dict(self) -> dict[str, Any]:
        device = self.device.to_dict()

        recovery = self.recovery.to_dict()

        root_signature = self.root_signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "device": device,
                "recovery": recovery,
                "root_signature": root_signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_recovery_bundle import E2EeRecoveryBundle

        d = dict(src_dict)
        device = E2EeDevice.from_dict(d.pop("device"))

        recovery = E2EeRecoveryBundle.from_dict(d.pop("recovery"))

        root_signature = d.pop("root_signature")

        e2_ee_bootstrap = cls(
            device=device,
            recovery=recovery,
            root_signature=root_signature,
        )

        return e2_ee_bootstrap
