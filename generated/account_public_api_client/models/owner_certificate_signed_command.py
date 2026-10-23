from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="OwnerCertificateSignedCommand")


@_attrs_define
class OwnerCertificateSignedCommand:
    """Exact original organization_share_request. Its decoded body is closed to scope_id, request_id, account_subject, the
    five immutable device identity fields, the four recovery identity fields, and challenge. No certificate bags are
    permitted.

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

        owner_certificate_signed_command = cls(
            device_id=device_id,
            body_bytes=body_bytes,
            signature=signature,
        )

        return owner_certificate_signed_command
