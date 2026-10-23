from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_source_command_issuer import E2EeOwnerSourceCommandIssuer
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerSourceProject")


@_attrs_define
class E2EeOwnerSourceProject:
    """
    Attributes:
        project_id (str):
        creation_command (E2EeSignedCommand):
        peer_trust (list[E2EeSignedCommand]):
        owner_confirmations (list[E2EeSignedCommand]):
        command_issuers (list[E2EeOwnerSourceCommandIssuer]):
    """

    project_id: str
    creation_command: E2EeSignedCommand
    peer_trust: list[E2EeSignedCommand]
    owner_confirmations: list[E2EeSignedCommand]
    command_issuers: list[E2EeOwnerSourceCommandIssuer]

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        creation_command = self.creation_command.to_dict()

        peer_trust = []
        for peer_trust_item_data in self.peer_trust:
            peer_trust_item = peer_trust_item_data.to_dict()
            peer_trust.append(peer_trust_item)

        owner_confirmations = []
        for owner_confirmations_item_data in self.owner_confirmations:
            owner_confirmations_item = owner_confirmations_item_data.to_dict()
            owner_confirmations.append(owner_confirmations_item)

        command_issuers = []
        for command_issuers_item_data in self.command_issuers:
            command_issuers_item = command_issuers_item_data.to_dict()
            command_issuers.append(command_issuers_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_id": project_id,
                "creation_command": creation_command,
                "peer_trust": peer_trust,
                "owner_confirmations": owner_confirmations,
                "command_issuers": command_issuers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_source_command_issuer import (
            E2EeOwnerSourceCommandIssuer,
        )
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        project_id = d.pop("project_id")

        creation_command = E2EeSignedCommand.from_dict(d.pop("creation_command"))

        peer_trust = []
        _peer_trust = d.pop("peer_trust")
        for peer_trust_item_data in _peer_trust:
            peer_trust_item = E2EeSignedCommand.from_dict(peer_trust_item_data)

            peer_trust.append(peer_trust_item)

        owner_confirmations = []
        _owner_confirmations = d.pop("owner_confirmations")
        for owner_confirmations_item_data in _owner_confirmations:
            owner_confirmations_item = E2EeSignedCommand.from_dict(
                owner_confirmations_item_data
            )

            owner_confirmations.append(owner_confirmations_item)

        command_issuers = []
        _command_issuers = d.pop("command_issuers")
        for command_issuers_item_data in _command_issuers:
            command_issuers_item = E2EeOwnerSourceCommandIssuer.from_dict(
                command_issuers_item_data
            )

            command_issuers.append(command_issuers_item)

        e2_ee_owner_source_project = cls(
            project_id=project_id,
            creation_command=creation_command,
            peer_trust=peer_trust,
            owner_confirmations=owner_confirmations,
            command_issuers=command_issuers,
        )

        return e2_ee_owner_source_project
