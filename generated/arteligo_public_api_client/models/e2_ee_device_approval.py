from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot


T = TypeVar("T", bound="E2EeDeviceApproval")


@_attrs_define
class E2EeDeviceApproval:
    """
    Attributes:
        device_id (str):
        encryption_public_key (str):
        signing_public_key (str):
        challenge (str):
        envelopes (list[E2EeEnvelope]):
        recovery_root (E2EeRecoveryRoot | Unset):
    """

    device_id: str
    encryption_public_key: str
    signing_public_key: str
    challenge: str
    envelopes: list[E2EeEnvelope]
    recovery_root: E2EeRecoveryRoot | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        challenge = self.challenge

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        recovery_root: dict[str, Any] | Unset = UNSET
        if not isinstance(self.recovery_root, Unset):
            recovery_root = self.recovery_root.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "device_id": device_id,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "challenge": challenge,
                "envelopes": envelopes,
            }
        )
        if recovery_root is not UNSET:
            field_dict["recovery_root"] = recovery_root

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot

        d = dict(src_dict)
        device_id = d.pop("device_id")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        challenge = d.pop("challenge")

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        _recovery_root = d.pop("recovery_root", UNSET)
        recovery_root: E2EeRecoveryRoot | Unset
        if isinstance(_recovery_root, Unset):
            recovery_root = UNSET
        else:
            recovery_root = E2EeRecoveryRoot.from_dict(_recovery_root)

        e2_ee_device_approval = cls(
            device_id=device_id,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            challenge=challenge,
            envelopes=envelopes,
            recovery_root=recovery_root,
        )

        return e2_ee_device_approval
