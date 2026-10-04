from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeSignedCommand")


@_attrs_define
class E2EeSignedCommand:
    """
    Attributes:
        device_id (str):
        body_bytes (str):
        signature (str):
    """

    device_id: str
    body_bytes: str
    signature: str

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        body_bytes = self.body_bytes

        signature = self.signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "device_id": device_id,
                "body_bytes": body_bytes,
                "signature": signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        body_bytes = d.pop("body_bytes")

        signature = d.pop("signature")

        e2_ee_signed_command = cls(
            device_id=device_id,
            body_bytes=body_bytes,
            signature=signature,
        )

        return e2_ee_signed_command
