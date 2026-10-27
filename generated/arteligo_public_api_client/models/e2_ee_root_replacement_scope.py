from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_epoch_link import E2EeEpochLink
    from ..models.e2_ee_invitation_participant_proof import (
        E2EeInvitationParticipantProof,
    )
    from ..models.e2_ee_organization_participant_proof import (
        E2EeOrganizationParticipantProof,
    )
    from ..models.e2_ee_owner_generation import E2EeOwnerGeneration
    from ..models.e2_ee_participant_source import E2EeParticipantSource
    from ..models.e2_ee_project import E2EeProject
    from ..models.e2_ee_recipients import E2EeRecipients
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeRootReplacementScope")


@_attrs_define
class E2EeRootReplacementScope:
    """
    Attributes:
        scope (E2EeProject):
        retained_epochs (list[int]):
        envelopes (list[E2EeEnvelope]):
        epoch_links (list[E2EeEpochLink]):
        generations (list[E2EeOwnerGeneration]):
        recipients (E2EeRecipients):
        devices (list[E2EeDevice]):
        recoveries (list[E2EeRecoveryPublic]):
        participant_proofs (list[E2EeInvitationParticipantProof | E2EeOrganizationParticipantProof]):
        trust_statements (list[E2EeSignedCommand]):
        participant_source (E2EeParticipantSource | Unset):
        creation_command (E2EeSignedCommand | Unset):
    """

    scope: E2EeProject
    retained_epochs: list[int]
    envelopes: list[E2EeEnvelope]
    epoch_links: list[E2EeEpochLink]
    generations: list[E2EeOwnerGeneration]
    recipients: E2EeRecipients
    devices: list[E2EeDevice]
    recoveries: list[E2EeRecoveryPublic]
    participant_proofs: list[
        E2EeInvitationParticipantProof | E2EeOrganizationParticipantProof
    ]
    trust_statements: list[E2EeSignedCommand]
    participant_source: E2EeParticipantSource | Unset = UNSET
    creation_command: E2EeSignedCommand | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.e2_ee_invitation_participant_proof import (
            E2EeInvitationParticipantProof,
        )

        scope = self.scope.to_dict()

        retained_epochs = self.retained_epochs

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        epoch_links = []
        for epoch_links_item_data in self.epoch_links:
            epoch_links_item = epoch_links_item_data.to_dict()
            epoch_links.append(epoch_links_item)

        generations = []
        for generations_item_data in self.generations:
            generations_item = generations_item_data.to_dict()
            generations.append(generations_item)

        recipients = self.recipients.to_dict()

        devices = []
        for devices_item_data in self.devices:
            devices_item = devices_item_data.to_dict()
            devices.append(devices_item)

        recoveries = []
        for recoveries_item_data in self.recoveries:
            recoveries_item = recoveries_item_data.to_dict()
            recoveries.append(recoveries_item)

        participant_proofs = []
        for participant_proofs_item_data in self.participant_proofs:
            participant_proofs_item: dict[str, Any]
            if isinstance(participant_proofs_item_data, E2EeInvitationParticipantProof):
                participant_proofs_item = participant_proofs_item_data.to_dict()
            else:
                participant_proofs_item = participant_proofs_item_data.to_dict()

            participant_proofs.append(participant_proofs_item)

        trust_statements = []
        for trust_statements_item_data in self.trust_statements:
            trust_statements_item = trust_statements_item_data.to_dict()
            trust_statements.append(trust_statements_item)

        participant_source: dict[str, Any] | Unset = UNSET
        if not isinstance(self.participant_source, Unset):
            participant_source = self.participant_source.to_dict()

        creation_command: dict[str, Any] | Unset = UNSET
        if not isinstance(self.creation_command, Unset):
            creation_command = self.creation_command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope": scope,
                "retained_epochs": retained_epochs,
                "envelopes": envelopes,
                "epoch_links": epoch_links,
                "generations": generations,
                "recipients": recipients,
                "devices": devices,
                "recoveries": recoveries,
                "participant_proofs": participant_proofs,
                "trust_statements": trust_statements,
            }
        )
        if participant_source is not UNSET:
            field_dict["participant_source"] = participant_source
        if creation_command is not UNSET:
            field_dict["creation_command"] = creation_command

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_epoch_link import E2EeEpochLink
        from ..models.e2_ee_invitation_participant_proof import (
            E2EeInvitationParticipantProof,
        )
        from ..models.e2_ee_organization_participant_proof import (
            E2EeOrganizationParticipantProof,
        )
        from ..models.e2_ee_owner_generation import E2EeOwnerGeneration
        from ..models.e2_ee_participant_source import E2EeParticipantSource
        from ..models.e2_ee_project import E2EeProject
        from ..models.e2_ee_recipients import E2EeRecipients
        from ..models.e2_ee_recovery_public import E2EeRecoveryPublic
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        scope = E2EeProject.from_dict(d.pop("scope"))

        retained_epochs = cast(list[int], d.pop("retained_epochs"))

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        epoch_links = []
        _epoch_links = d.pop("epoch_links")
        for epoch_links_item_data in _epoch_links:
            epoch_links_item = E2EeEpochLink.from_dict(epoch_links_item_data)

            epoch_links.append(epoch_links_item)

        generations = []
        _generations = d.pop("generations")
        for generations_item_data in _generations:
            generations_item = E2EeOwnerGeneration.from_dict(generations_item_data)

            generations.append(generations_item)

        recipients = E2EeRecipients.from_dict(d.pop("recipients"))

        devices = []
        _devices = d.pop("devices")
        for devices_item_data in _devices:
            devices_item = E2EeDevice.from_dict(devices_item_data)

            devices.append(devices_item)

        recoveries = []
        _recoveries = d.pop("recoveries")
        for recoveries_item_data in _recoveries:
            recoveries_item = E2EeRecoveryPublic.from_dict(recoveries_item_data)

            recoveries.append(recoveries_item)

        participant_proofs = []
        _participant_proofs = d.pop("participant_proofs")
        for participant_proofs_item_data in _participant_proofs:

            def _parse_participant_proofs_item(
                data: object,
            ) -> E2EeInvitationParticipantProof | E2EeOrganizationParticipantProof:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_e2_ee_scope_participant_proof_type_0 = (
                        E2EeInvitationParticipantProof.from_dict(data)
                    )

                    return componentsschemas_e2_ee_scope_participant_proof_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_e2_ee_scope_participant_proof_type_1 = (
                    E2EeOrganizationParticipantProof.from_dict(data)
                )

                return componentsschemas_e2_ee_scope_participant_proof_type_1

            participant_proofs_item = _parse_participant_proofs_item(
                participant_proofs_item_data
            )

            participant_proofs.append(participant_proofs_item)

        trust_statements = []
        _trust_statements = d.pop("trust_statements")
        for trust_statements_item_data in _trust_statements:
            trust_statements_item = E2EeSignedCommand.from_dict(
                trust_statements_item_data
            )

            trust_statements.append(trust_statements_item)

        _participant_source = d.pop("participant_source", UNSET)
        participant_source: E2EeParticipantSource | Unset
        if isinstance(_participant_source, Unset):
            participant_source = UNSET
        else:
            participant_source = E2EeParticipantSource.from_dict(_participant_source)

        _creation_command = d.pop("creation_command", UNSET)
        creation_command: E2EeSignedCommand | Unset
        if isinstance(_creation_command, Unset):
            creation_command = UNSET
        else:
            creation_command = E2EeSignedCommand.from_dict(_creation_command)

        e2_ee_root_replacement_scope = cls(
            scope=scope,
            retained_epochs=retained_epochs,
            envelopes=envelopes,
            epoch_links=epoch_links,
            generations=generations,
            recipients=recipients,
            devices=devices,
            recoveries=recoveries,
            participant_proofs=participant_proofs,
            trust_statements=trust_statements,
            participant_source=participant_source,
            creation_command=creation_command,
        )

        return e2_ee_root_replacement_scope
