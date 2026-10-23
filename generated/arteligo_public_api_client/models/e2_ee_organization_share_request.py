from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EeOrganizationShareRequest")


@_attrs_define
class E2EeOrganizationShareRequest:
    """
    Attributes:
        scope_id (str):
        request_id (str):
        account_subject (str):
        device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request. Certificates are
            returned separately in E2eeDevice and are not accepted in this input.
        recovery (E2EeRecoveryRoot):
        challenge (str):
    """

    scope_id: str
    request_id: str
    account_subject: str
    device: E2EeSignedDeviceInput
    recovery: E2EeRecoveryRoot
    challenge: str

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        request_id = self.request_id

        account_subject = self.account_subject

        device = self.device.to_dict()

        recovery = self.recovery.to_dict()

        challenge = self.challenge

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "request_id": request_id,
                "account_subject": account_subject,
                "device": device,
                "recovery": recovery,
                "challenge": challenge,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        request_id = d.pop("request_id")

        account_subject = d.pop("account_subject")

        device = E2EeSignedDeviceInput.from_dict(d.pop("device"))

        recovery = E2EeRecoveryRoot.from_dict(d.pop("recovery"))

        challenge = d.pop("challenge")

        e2_ee_organization_share_request = cls(
            scope_id=scope_id,
            request_id=request_id,
            account_subject=account_subject,
            device=device,
            recovery=recovery,
            challenge=challenge,
        )

        return e2_ee_organization_share_request
