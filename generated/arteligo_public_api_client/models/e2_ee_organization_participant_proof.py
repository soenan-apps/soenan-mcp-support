from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_organization_participant_proof_kind import (
    E2EeOrganizationParticipantProofKind,
)

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOrganizationParticipantProof")


@_attrs_define
class E2EeOrganizationParticipantProof:
    """
    Attributes:
        kind (E2EeOrganizationParticipantProofKind):
        scope_id (str):
        request_id (str):
        account_subject (str):
        request_command (E2EeSignedCommand):
        approval_command (E2EeSignedCommand):
        approver_device (E2EeDevice):
    """

    kind: E2EeOrganizationParticipantProofKind
    scope_id: str
    request_id: str
    account_subject: str
    request_command: E2EeSignedCommand
    approval_command: E2EeSignedCommand
    approver_device: E2EeDevice

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        scope_id = self.scope_id

        request_id = self.request_id

        account_subject = self.account_subject

        request_command = self.request_command.to_dict()

        approval_command = self.approval_command.to_dict()

        approver_device = self.approver_device.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "scope_id": scope_id,
                "request_id": request_id,
                "account_subject": account_subject,
                "request_command": request_command,
                "approval_command": approval_command,
                "approver_device": approver_device,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        kind = E2EeOrganizationParticipantProofKind(d.pop("kind"))

        scope_id = d.pop("scope_id")

        request_id = d.pop("request_id")

        account_subject = d.pop("account_subject")

        request_command = E2EeSignedCommand.from_dict(d.pop("request_command"))

        approval_command = E2EeSignedCommand.from_dict(d.pop("approval_command"))

        approver_device = E2EeDevice.from_dict(d.pop("approver_device"))

        e2_ee_organization_participant_proof = cls(
            kind=kind,
            scope_id=scope_id,
            request_id=request_id,
            account_subject=account_subject,
            request_command=request_command,
            approval_command=approval_command,
            approver_device=approver_device,
        )

        return e2_ee_organization_participant_proof
