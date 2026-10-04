from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice


T = TypeVar("T", bound="E2EeDeviceRootProof")


@_attrs_define
class E2EeDeviceRootProof:
    """
    Attributes:
        public_device (E2EeDevice):
        root_signature (str):
    """

    public_device: E2EeDevice
    root_signature: str

    def to_dict(self) -> dict[str, Any]:
        public_device = self.public_device.to_dict()

        root_signature = self.root_signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "public_device": public_device,
                "root_signature": root_signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_device import E2EeDevice

        d = dict(src_dict)
        public_device = E2EeDevice.from_dict(d.pop("public_device"))

        root_signature = d.pop("root_signature")

        e2_ee_device_root_proof = cls(
            public_device=public_device,
            root_signature=root_signature,
        )

        return e2_ee_device_root_proof
