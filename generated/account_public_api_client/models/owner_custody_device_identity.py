from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_custody_device_identity_kind import OwnerCustodyDeviceIdentityKind

T = TypeVar("T", bound="OwnerCustodyDeviceIdentity")


@_attrs_define
class OwnerCustodyDeviceIdentity:
    """
    Attributes:
        kind (OwnerCustodyDeviceIdentityKind):
        device_id (str):
        encryption_public_key (str):
        signing_public_key (str):
        challenge (str):
    """

    kind: OwnerCustodyDeviceIdentityKind
    device_id: str
    encryption_public_key: str
    signing_public_key: str
    challenge: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        device_id = self.device_id

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        challenge = self.challenge

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "device_id": device_id,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "challenge": challenge,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = OwnerCustodyDeviceIdentityKind(d.pop("kind"))

        device_id = d.pop("device_id")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        challenge = d.pop("challenge")

        owner_custody_device_identity = cls(
            kind=kind,
            device_id=device_id,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            challenge=challenge,
        )

        return owner_custody_device_identity
