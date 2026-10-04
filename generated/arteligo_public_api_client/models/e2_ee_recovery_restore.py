from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice


T = TypeVar("T", bound="E2EeRecoveryRestore")


@_attrs_define
class E2EeRecoveryRestore:
    """
    Attributes:
        recovery_id (str):
        device (E2EeDevice):
        challenge (str):
    """

    recovery_id: str
    device: E2EeDevice
    challenge: str

    def to_dict(self) -> dict[str, Any]:
        recovery_id = self.recovery_id

        device = self.device.to_dict()

        challenge = self.challenge

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recovery_id": recovery_id,
                "device": device,
                "challenge": challenge,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice

        d = dict(src_dict)
        recovery_id = d.pop("recovery_id")

        device = E2EeDevice.from_dict(d.pop("device"))

        challenge = d.pop("challenge")

        e2_ee_recovery_restore = cls(
            recovery_id=recovery_id,
            device=device,
            challenge=challenge,
        )

        return e2_ee_recovery_restore
