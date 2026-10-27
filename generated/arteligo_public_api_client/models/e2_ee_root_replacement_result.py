from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_root_replacement_result_phase import E2EeRootReplacementResultPhase
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_recovery_bundle import E2EeRecoveryBundle
    from ..models.e2_ee_root_replacement_owner import E2EeRootReplacementOwner
    from ..models.e2_ee_root_replacement_pending_effect import (
        E2EeRootReplacementPendingEffect,
    )
    from ..models.e2_ee_root_replacement_scope import E2EeRootReplacementScope


T = TypeVar("T", bound="E2EeRootReplacementResult")


@_attrs_define
class E2EeRootReplacementResult:
    """
    Attributes:
        operation_id (str):
        request_digest (str):
        phase (E2EeRootReplacementResultPhase): rejected is returned only from a durable operation that never dispatched
            an Account apply. Transport errors never imply rejection.
        pending_effects (list[E2EeRootReplacementPendingEffect]):
        account_receipt (str | Unset): Exact Account-owned public receipt bytes. Authenticate independently before
            completing local journals.
        receipt_digest (str | Unset):
        recovery (E2EeRecoveryBundle | Unset):
        issuer_device (E2EeDevice | Unset):
        settled_scopes (list[E2EeRootReplacementScope] | Unset):
        settled_owners (list[E2EeRootReplacementOwner] | Unset):
        devices (list[E2EeDevice] | Unset):
    """

    operation_id: str
    request_digest: str
    phase: E2EeRootReplacementResultPhase
    pending_effects: list[E2EeRootReplacementPendingEffect]
    account_receipt: str | Unset = UNSET
    receipt_digest: str | Unset = UNSET
    recovery: E2EeRecoveryBundle | Unset = UNSET
    issuer_device: E2EeDevice | Unset = UNSET
    settled_scopes: list[E2EeRootReplacementScope] | Unset = UNSET
    settled_owners: list[E2EeRootReplacementOwner] | Unset = UNSET
    devices: list[E2EeDevice] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        request_digest = self.request_digest

        phase = self.phase.value

        pending_effects = []
        for pending_effects_item_data in self.pending_effects:
            pending_effects_item = pending_effects_item_data.to_dict()
            pending_effects.append(pending_effects_item)

        account_receipt = self.account_receipt

        receipt_digest = self.receipt_digest

        recovery: dict[str, Any] | Unset = UNSET
        if not isinstance(self.recovery, Unset):
            recovery = self.recovery.to_dict()

        issuer_device: dict[str, Any] | Unset = UNSET
        if not isinstance(self.issuer_device, Unset):
            issuer_device = self.issuer_device.to_dict()

        settled_scopes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.settled_scopes, Unset):
            settled_scopes = []
            for settled_scopes_item_data in self.settled_scopes:
                settled_scopes_item = settled_scopes_item_data.to_dict()
                settled_scopes.append(settled_scopes_item)

        settled_owners: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.settled_owners, Unset):
            settled_owners = []
            for settled_owners_item_data in self.settled_owners:
                settled_owners_item = settled_owners_item_data.to_dict()
                settled_owners.append(settled_owners_item)

        devices: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.devices, Unset):
            devices = []
            for devices_item_data in self.devices:
                devices_item = devices_item_data.to_dict()
                devices.append(devices_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "request_digest": request_digest,
                "phase": phase,
                "pending_effects": pending_effects,
            }
        )
        if account_receipt is not UNSET:
            field_dict["account_receipt"] = account_receipt
        if receipt_digest is not UNSET:
            field_dict["receipt_digest"] = receipt_digest
        if recovery is not UNSET:
            field_dict["recovery"] = recovery
        if issuer_device is not UNSET:
            field_dict["issuer_device"] = issuer_device
        if settled_scopes is not UNSET:
            field_dict["settled_scopes"] = settled_scopes
        if settled_owners is not UNSET:
            field_dict["settled_owners"] = settled_owners
        if devices is not UNSET:
            field_dict["devices"] = devices

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_recovery_bundle import E2EeRecoveryBundle
        from ..models.e2_ee_root_replacement_owner import E2EeRootReplacementOwner
        from ..models.e2_ee_root_replacement_pending_effect import (
            E2EeRootReplacementPendingEffect,
        )
        from ..models.e2_ee_root_replacement_scope import E2EeRootReplacementScope

        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        request_digest = d.pop("request_digest")

        phase = E2EeRootReplacementResultPhase(d.pop("phase"))

        pending_effects = []
        _pending_effects = d.pop("pending_effects")
        for pending_effects_item_data in _pending_effects:
            pending_effects_item = E2EeRootReplacementPendingEffect.from_dict(
                pending_effects_item_data
            )

            pending_effects.append(pending_effects_item)

        account_receipt = d.pop("account_receipt", UNSET)

        receipt_digest = d.pop("receipt_digest", UNSET)

        _recovery = d.pop("recovery", UNSET)
        recovery: E2EeRecoveryBundle | Unset
        if isinstance(_recovery, Unset):
            recovery = UNSET
        else:
            recovery = E2EeRecoveryBundle.from_dict(_recovery)

        _issuer_device = d.pop("issuer_device", UNSET)
        issuer_device: E2EeDevice | Unset
        if isinstance(_issuer_device, Unset):
            issuer_device = UNSET
        else:
            issuer_device = E2EeDevice.from_dict(_issuer_device)

        _settled_scopes = d.pop("settled_scopes", UNSET)
        settled_scopes: list[E2EeRootReplacementScope] | Unset = UNSET
        if _settled_scopes is not UNSET:
            settled_scopes = []
            for settled_scopes_item_data in _settled_scopes:
                settled_scopes_item = E2EeRootReplacementScope.from_dict(
                    settled_scopes_item_data
                )

                settled_scopes.append(settled_scopes_item)

        _settled_owners = d.pop("settled_owners", UNSET)
        settled_owners: list[E2EeRootReplacementOwner] | Unset = UNSET
        if _settled_owners is not UNSET:
            settled_owners = []
            for settled_owners_item_data in _settled_owners:
                settled_owners_item = E2EeRootReplacementOwner.from_dict(
                    settled_owners_item_data
                )

                settled_owners.append(settled_owners_item)

        _devices = d.pop("devices", UNSET)
        devices: list[E2EeDevice] | Unset = UNSET
        if _devices is not UNSET:
            devices = []
            for devices_item_data in _devices:
                devices_item = E2EeDevice.from_dict(devices_item_data)

                devices.append(devices_item)

        e2_ee_root_replacement_result = cls(
            operation_id=operation_id,
            request_digest=request_digest,
            phase=phase,
            pending_effects=pending_effects,
            account_receipt=account_receipt,
            receipt_digest=receipt_digest,
            recovery=recovery,
            issuer_device=issuer_device,
            settled_scopes=settled_scopes,
            settled_owners=settled_owners,
            devices=devices,
        )

        return e2_ee_root_replacement_result
