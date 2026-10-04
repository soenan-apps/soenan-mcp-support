from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic


T = TypeVar("T", bound="E2EeRecipients")


@_attrs_define
class E2EeRecipients:
    """
    Attributes:
        devices (list[E2EeDevice]):
        recoveries (list[E2EeRecoveryPublic]):
        organization_id (str | Unset):
        organization_epoch (int | Unset):
    """

    devices: list[E2EeDevice]
    recoveries: list[E2EeRecoveryPublic]
    organization_id: str | Unset = UNSET
    organization_epoch: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        devices = []
        for devices_item_data in self.devices:
            devices_item = devices_item_data.to_dict()
            devices.append(devices_item)

        recoveries = []
        for recoveries_item_data in self.recoveries:
            recoveries_item = recoveries_item_data.to_dict()
            recoveries.append(recoveries_item)

        organization_id = self.organization_id

        organization_epoch = self.organization_epoch

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "devices": devices,
                "recoveries": recoveries,
            }
        )
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if organization_epoch is not UNSET:
            field_dict["organization_epoch"] = organization_epoch

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

        organization_id = d.pop("organization_id", UNSET)

        organization_epoch = d.pop("organization_epoch", UNSET)

        e2_ee_recipients = cls(
            devices=devices,
            recoveries=recoveries,
            organization_id=organization_id,
            organization_epoch=organization_epoch,
        )

        return e2_ee_recipients
