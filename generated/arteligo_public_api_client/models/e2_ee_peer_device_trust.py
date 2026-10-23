from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EePeerDeviceTrust")


@_attrs_define
class E2EePeerDeviceTrust:
    """
    Attributes:
        trusted_device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request.
            Certificates are returned separately in E2eeDevice and are not accepted in this input.
    """

    trusted_device: E2EeSignedDeviceInput

    def to_dict(self) -> dict[str, Any]:
        trusted_device = self.trusted_device.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "trusted_device": trusted_device,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        trusted_device = E2EeSignedDeviceInput.from_dict(d.pop("trusted_device"))

        e2_ee_peer_device_trust = cls(
            trusted_device=trusted_device,
        )

        return e2_ee_peer_device_trust
