from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_owner_source_command_issuer_operation import (
    E2EeOwnerSourceCommandIssuerOperation,
)

if TYPE_CHECKING:
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
    from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput


T = TypeVar("T", bound="E2EeOwnerSourceCommandIssuer")


@_attrs_define
class E2EeOwnerSourceCommandIssuer:
    """
    Attributes:
        operation (E2EeOwnerSourceCommandIssuerOperation):
        command_digest (str):
        device (E2EeSignedDeviceInput): Immutable public device snapshot bound into a signed request. Certificates are
            returned separately in E2eeDevice and are not accepted in this input.
        issuer_admission (E2EeOwnerIssuerAdmission): The original source-root and exact immutable certificate references
            selected when this command was signed. Later certificates cannot qualify or replace this evidence.
    """

    operation: E2EeOwnerSourceCommandIssuerOperation
    command_digest: str
    device: E2EeSignedDeviceInput
    issuer_admission: E2EeOwnerIssuerAdmission

    def to_dict(self) -> dict[str, Any]:
        operation = self.operation.value

        command_digest = self.command_digest

        device = self.device.to_dict()

        issuer_admission = self.issuer_admission.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation": operation,
                "command_digest": command_digest,
                "device": device,
                "issuer_admission": issuer_admission,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
        from ..models.e2_ee_signed_device_input import E2EeSignedDeviceInput

        d = dict(src_dict)
        operation = E2EeOwnerSourceCommandIssuerOperation(d.pop("operation"))

        command_digest = d.pop("command_digest")

        device = E2EeSignedDeviceInput.from_dict(d.pop("device"))

        issuer_admission = E2EeOwnerIssuerAdmission.from_dict(d.pop("issuer_admission"))

        e2_ee_owner_source_command_issuer = cls(
            operation=operation,
            command_digest=command_digest,
            device=device,
            issuer_admission=issuer_admission,
        )

        return e2_ee_owner_source_command_issuer
