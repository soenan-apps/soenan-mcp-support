from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="E2EeSignedDeviceInput")


@_attrs_define
class E2EeSignedDeviceInput:
    """Immutable public device snapshot bound into a signed request. Certificates are returned separately in E2eeDevice and
    are not accepted in this input.

        Attributes:
            device_id (str):
            account_subject (str):
            encryption_public_key (str):
            signing_public_key (str):
            state (str):
    """

    device_id: str
    account_subject: str
    encryption_public_key: str
    signing_public_key: str
    state: str

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        account_subject = self.account_subject

        encryption_public_key = self.encryption_public_key

        signing_public_key = self.signing_public_key

        state = self.state

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "device_id": device_id,
                "account_subject": account_subject,
                "encryption_public_key": encryption_public_key,
                "signing_public_key": signing_public_key,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        account_subject = d.pop("account_subject")

        encryption_public_key = d.pop("encryption_public_key")

        signing_public_key = d.pop("signing_public_key")

        state = d.pop("state")

        e2_ee_signed_device_input = cls(
            device_id=device_id,
            account_subject=account_subject,
            encryption_public_key=encryption_public_key,
            signing_public_key=signing_public_key,
            state=state,
        )

        return e2_ee_signed_device_input
