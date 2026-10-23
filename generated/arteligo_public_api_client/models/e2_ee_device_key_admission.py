from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EeDeviceKeyAdmission")


@_attrs_define
class E2EeDeviceKeyAdmission:
    """
    Attributes:
        recovery_id (str):
        generation (int):
        device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request. Certificates are
            returned separately in E2eeDevice and are not accepted in this input.
        challenge (str):
        device_signature (str):
    """

    recovery_id: str
    generation: int
    device: E2EeSignedDeviceInput
    challenge: str
    device_signature: str

    def to_dict(self) -> dict[str, Any]:
        recovery_id = self.recovery_id

        generation = self.generation

        device = self.device.to_dict()

        challenge = self.challenge

        device_signature = self.device_signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recovery_id": recovery_id,
                "generation": generation,
                "device": device,
                "challenge": challenge,
                "device_signature": device_signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        recovery_id = d.pop("recovery_id")

        generation = d.pop("generation")

        device = E2EeSignedDeviceInput.from_dict(d.pop("device"))

        challenge = d.pop("challenge")

        device_signature = d.pop("device_signature")

        e2_ee_device_key_admission = cls(
            recovery_id=recovery_id,
            generation=generation,
            device=device,
            challenge=challenge,
            device_signature=device_signature,
        )

        return e2_ee_device_key_admission
