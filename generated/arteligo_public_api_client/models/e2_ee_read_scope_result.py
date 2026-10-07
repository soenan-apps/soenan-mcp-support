from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_read_scope_result_error import E2EeReadScopeResultError
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_epoch_link import E2EeEpochLink
    from ..models.e2_ee_project import E2EeProject
    from ..models.e2_ee_record_reference import E2EeRecordReference
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic


T = TypeVar("T", bound="E2EeReadScopeResult")


@_attrs_define
class E2EeReadScopeResult:
    """
    Attributes:
        scope_id (str):
        records (list[E2EeRecordReference]):
        remaining_record_ids (list[str]):
        missing_record_ids (list[str]):
        envelopes (list[E2EeEnvelope]):
        devices (list[E2EeDevice]):
        recoveries (list[E2EeRecoveryPublic]):
        epochs (list[E2EeEpochLink]):
        metadata (E2EeProject | Unset):
        error (E2EeReadScopeResultError | Unset):
    """

    scope_id: str
    records: list[E2EeRecordReference]
    remaining_record_ids: list[str]
    missing_record_ids: list[str]
    envelopes: list[E2EeEnvelope]
    devices: list[E2EeDevice]
    recoveries: list[E2EeRecoveryPublic]
    epochs: list[E2EeEpochLink]
    metadata: E2EeProject | Unset = UNSET
    error: E2EeReadScopeResultError | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()
            records.append(records_item)

        remaining_record_ids = self.remaining_record_ids

        missing_record_ids = self.missing_record_ids

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        devices = []
        for devices_item_data in self.devices:
            devices_item = devices_item_data.to_dict()
            devices.append(devices_item)

        recoveries = []
        for recoveries_item_data in self.recoveries:
            recoveries_item = recoveries_item_data.to_dict()
            recoveries.append(recoveries_item)

        epochs = []
        for epochs_item_data in self.epochs:
            epochs_item = epochs_item_data.to_dict()
            epochs.append(epochs_item)

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        error: str | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "records": records,
                "remaining_record_ids": remaining_record_ids,
                "missing_record_ids": missing_record_ids,
                "envelopes": envelopes,
                "devices": devices,
                "recoveries": recoveries,
                "epochs": epochs,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_epoch_link import E2EeEpochLink
        from ..models.e2_ee_project import E2EeProject
        from ..models.e2_ee_record_reference import E2EeRecordReference
        from ..models.e2_ee_recovery_public import E2EeRecoveryPublic

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = E2EeRecordReference.from_dict(records_item_data)

            records.append(records_item)

        remaining_record_ids = cast(list[str], d.pop("remaining_record_ids"))

        missing_record_ids = cast(list[str], d.pop("missing_record_ids"))

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

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

        epochs = []
        _epochs = d.pop("epochs")
        for epochs_item_data in _epochs:
            epochs_item = E2EeEpochLink.from_dict(epochs_item_data)

            epochs.append(epochs_item)

        _metadata = d.pop("metadata", UNSET)
        metadata: E2EeProject | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = E2EeProject.from_dict(_metadata)

        _error = d.pop("error", UNSET)
        error: E2EeReadScopeResultError | Unset
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = E2EeReadScopeResultError(_error)

        e2_ee_read_scope_result = cls(
            scope_id=scope_id,
            records=records,
            remaining_record_ids=remaining_record_ids,
            missing_record_ids=missing_record_ids,
            envelopes=envelopes,
            devices=devices,
            recoveries=recoveries,
            epochs=epochs,
            metadata=metadata,
            error=error,
        )

        return e2_ee_read_scope_result
