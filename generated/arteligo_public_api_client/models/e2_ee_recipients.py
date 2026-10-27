from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_recipient_purpose import E2EeRecipientPurpose
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic


T = TypeVar("T", bound="E2EeRecipients")


@_attrs_define
class E2EeRecipients:
    """
    Attributes:
        purpose (E2EeRecipientPurpose):
        devices (list[E2EeDevice]):
        recoveries (list[E2EeRecoveryPublic]):
        organization_id (str | Unset):
        organization_epoch (int | Unset):
        owner_authority (E2EeOwnerAuthority | Unset):
    """

    purpose: E2EeRecipientPurpose
    devices: list[E2EeDevice]
    recoveries: list[E2EeRecoveryPublic]
    organization_id: str | Unset = UNSET
    organization_epoch: int | Unset = UNSET
    owner_authority: E2EeOwnerAuthority | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        purpose = self.purpose.value

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

        owner_authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_authority, Unset):
            owner_authority = self.owner_authority.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "purpose": purpose,
                "devices": devices,
                "recoveries": recoveries,
            }
        )
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if organization_epoch is not UNSET:
            field_dict["organization_epoch"] = organization_epoch
        if owner_authority is not UNSET:
            field_dict["owner_authority"] = owner_authority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_recovery_public import E2EeRecoveryPublic

        d = dict(src_dict)
        purpose = E2EeRecipientPurpose(d.pop("purpose"))

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

        _owner_authority = d.pop("owner_authority", UNSET)
        owner_authority: E2EeOwnerAuthority | Unset
        if isinstance(_owner_authority, Unset):
            owner_authority = UNSET
        else:
            owner_authority = E2EeOwnerAuthority.from_dict(_owner_authority)

        e2_ee_recipients = cls(
            purpose=purpose,
            devices=devices,
            recoveries=recoveries,
            organization_id=organization_id,
            organization_epoch=organization_epoch,
            owner_authority=owner_authority,
        )

        return e2_ee_recipients
