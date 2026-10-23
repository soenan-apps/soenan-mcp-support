from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.owner_certificate_recovery_root import OwnerCertificateRecoveryRoot
    from ..models.owner_certificate_signed_command import OwnerCertificateSignedCommand


T = TypeVar("T", bound="OwnerCertificateOrganizationParticipation")


@_attrs_define
class OwnerCertificateOrganizationParticipation:
    """
    Attributes:
        request_command (OwnerCertificateSignedCommand): Exact original organization_share_request. Its decoded body is
            closed to scope_id, request_id, account_subject, the five immutable device identity fields, the four recovery
            identity fields, and challenge. No certificate bags are permitted.
        approver_recovery (OwnerCertificateRecoveryRoot):
    """

    request_command: OwnerCertificateSignedCommand
    approver_recovery: OwnerCertificateRecoveryRoot

    def to_dict(self) -> dict[str, Any]:
        request_command = self.request_command.to_dict()

        approver_recovery = self.approver_recovery.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "request_command": request_command,
                "approver_recovery": approver_recovery,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_certificate_recovery_root import (
            OwnerCertificateRecoveryRoot,
        )
        from ..models.owner_certificate_signed_command import (
            OwnerCertificateSignedCommand,
        )

        d = dict(src_dict)
        request_command = OwnerCertificateSignedCommand.from_dict(
            d.pop("request_command")
        )

        approver_recovery = OwnerCertificateRecoveryRoot.from_dict(
            d.pop("approver_recovery")
        )

        owner_certificate_organization_participation = cls(
            request_command=request_command,
            approver_recovery=approver_recovery,
        )

        return owner_certificate_organization_participation
