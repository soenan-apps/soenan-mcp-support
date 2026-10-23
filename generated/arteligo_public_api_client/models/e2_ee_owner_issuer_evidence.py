from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic


T = TypeVar("T", bound="E2EeOwnerIssuerEvidence")


@_attrs_define
class E2EeOwnerIssuerEvidence:
    """Immutable public issuer proof graph for the selected binding. Includes only exact certificate references frozen by
    its signed issuer_admission and recursively by accepted Account witnesses, plus the corresponding public recovery
    checkpoints. This is not a current device directory and grants no content or key-distribution authority. Fetch on
    demand; retain references rather than embedding full certificate wrappers in private history.

        Attributes:
            devices (list[E2EeDevice]):
            recoveries (list[E2EeRecoveryPublic]):
    """

    devices: list[E2EeDevice]
    recoveries: list[E2EeRecoveryPublic]

    def to_dict(self) -> dict[str, Any]:
        devices = []
        for devices_item_data in self.devices:
            devices_item = devices_item_data.to_dict()
            devices.append(devices_item)

        recoveries = []
        for recoveries_item_data in self.recoveries:
            recoveries_item = recoveries_item_data.to_dict()
            recoveries.append(recoveries_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "devices": devices,
                "recoveries": recoveries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_recovery_public import E2EeRecoveryPublic

        d = dict(src_dict)
        devices = []
        _devices = d.pop("devices")
        for devices_item_data in _devices:
            devices_item = E2EeDevice.from_dict(devices_item_data)

            devices.append(devices_item)

        recoveries = []
        _recoveries = d.pop("recoveries")
        for recoveries_item_data in _recoveries:
            recoveries_item = E2EeRecoveryPublic.from_dict(recoveries_item_data)

            recoveries.append(recoveries_item)

        e2_ee_owner_issuer_evidence = cls(
            devices=devices,
            recoveries=recoveries,
        )

        return e2_ee_owner_issuer_evidence
