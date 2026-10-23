from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOrganizationParticipation")


@_attrs_define
class E2EeOrganizationParticipation:
    """
    Attributes:
        request_command (E2EeSignedCommand):
        approver_recovery (E2EeRecoveryRoot):
    """

    request_command: E2EeSignedCommand
    approver_recovery: E2EeRecoveryRoot

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
        from ..models.e2_ee_recovery_root import E2EeRecoveryRoot
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        request_command = E2EeSignedCommand.from_dict(d.pop("request_command"))

        approver_recovery = E2EeRecoveryRoot.from_dict(d.pop("approver_recovery"))

        e2_ee_organization_participation = cls(
            request_command=request_command,
            approver_recovery=approver_recovery,
        )

        return e2_ee_organization_participation
