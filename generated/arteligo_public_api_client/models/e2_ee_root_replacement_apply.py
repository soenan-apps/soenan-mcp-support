from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_owner_source_submission import E2EeOwnerSourceSubmission
    from ..models.e2_ee_root_replacement_scope_command import (
        E2EeRootReplacementScopeCommand,
    )
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeRootReplacementApply")


@_attrs_define
class E2EeRootReplacementApply:
    """
    Attributes:
        preparation_digest (str):
        read_set_digest (str):
        root_command (E2EeSignedCommand):
        companion_admission (E2EeSignedCommand):
        owner_key_commands (list[E2EeSignedCommand]):
        owner_candidate_commands (list[E2EeSignedCommand]):
        scope_commands (list[E2EeRootReplacementScopeCommand]):
        source_submissions (list[E2EeOwnerSourceSubmission]):
        keyring_commands (list[E2EeSignedCommand]):
        gate_commands (list[E2EeSignedCommand]):
        preparation_commands (list[E2EeSignedCommand]):
    """

    preparation_digest: str
    read_set_digest: str
    root_command: E2EeSignedCommand
    companion_admission: E2EeSignedCommand
    owner_key_commands: list[E2EeSignedCommand]
    owner_candidate_commands: list[E2EeSignedCommand]
    scope_commands: list[E2EeRootReplacementScopeCommand]
    source_submissions: list[E2EeOwnerSourceSubmission]
    keyring_commands: list[E2EeSignedCommand]
    gate_commands: list[E2EeSignedCommand]
    preparation_commands: list[E2EeSignedCommand]

    def to_dict(self) -> dict[str, Any]:
        preparation_digest = self.preparation_digest

        read_set_digest = self.read_set_digest

        root_command = self.root_command.to_dict()

        companion_admission = self.companion_admission.to_dict()

        owner_key_commands = []
        for owner_key_commands_item_data in self.owner_key_commands:
            owner_key_commands_item = owner_key_commands_item_data.to_dict()
            owner_key_commands.append(owner_key_commands_item)

        owner_candidate_commands = []
        for owner_candidate_commands_item_data in self.owner_candidate_commands:
            owner_candidate_commands_item = owner_candidate_commands_item_data.to_dict()
            owner_candidate_commands.append(owner_candidate_commands_item)

        scope_commands = []
        for scope_commands_item_data in self.scope_commands:
            scope_commands_item = scope_commands_item_data.to_dict()
            scope_commands.append(scope_commands_item)

        source_submissions = []
        for source_submissions_item_data in self.source_submissions:
            source_submissions_item = source_submissions_item_data.to_dict()
            source_submissions.append(source_submissions_item)

        keyring_commands = []
        for keyring_commands_item_data in self.keyring_commands:
            keyring_commands_item = keyring_commands_item_data.to_dict()
            keyring_commands.append(keyring_commands_item)

        gate_commands = []
        for gate_commands_item_data in self.gate_commands:
            gate_commands_item = gate_commands_item_data.to_dict()
            gate_commands.append(gate_commands_item)

        preparation_commands = []
        for preparation_commands_item_data in self.preparation_commands:
            preparation_commands_item = preparation_commands_item_data.to_dict()
            preparation_commands.append(preparation_commands_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "preparation_digest": preparation_digest,
                "read_set_digest": read_set_digest,
                "root_command": root_command,
                "companion_admission": companion_admission,
                "owner_key_commands": owner_key_commands,
                "owner_candidate_commands": owner_candidate_commands,
                "scope_commands": scope_commands,
                "source_submissions": source_submissions,
                "keyring_commands": keyring_commands,
                "gate_commands": gate_commands,
                "preparation_commands": preparation_commands,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_source_submission import E2EeOwnerSourceSubmission
        from ..models.e2_ee_root_replacement_scope_command import (
            E2EeRootReplacementScopeCommand,
        )
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        preparation_digest = d.pop("preparation_digest")

        read_set_digest = d.pop("read_set_digest")

        root_command = E2EeSignedCommand.from_dict(d.pop("root_command"))

        companion_admission = E2EeSignedCommand.from_dict(d.pop("companion_admission"))

        owner_key_commands = []
        _owner_key_commands = d.pop("owner_key_commands")
        for owner_key_commands_item_data in _owner_key_commands:
            owner_key_commands_item = E2EeSignedCommand.from_dict(
                owner_key_commands_item_data
            )

            owner_key_commands.append(owner_key_commands_item)

        owner_candidate_commands = []
        _owner_candidate_commands = d.pop("owner_candidate_commands")
        for owner_candidate_commands_item_data in _owner_candidate_commands:
            owner_candidate_commands_item = E2EeSignedCommand.from_dict(
                owner_candidate_commands_item_data
            )

            owner_candidate_commands.append(owner_candidate_commands_item)

        scope_commands = []
        _scope_commands = d.pop("scope_commands")
        for scope_commands_item_data in _scope_commands:
            scope_commands_item = E2EeRootReplacementScopeCommand.from_dict(
                scope_commands_item_data
            )

            scope_commands.append(scope_commands_item)

        source_submissions = []
        _source_submissions = d.pop("source_submissions")
        for source_submissions_item_data in _source_submissions:
            source_submissions_item = E2EeOwnerSourceSubmission.from_dict(
                source_submissions_item_data
            )

            source_submissions.append(source_submissions_item)

        keyring_commands = []
        _keyring_commands = d.pop("keyring_commands")
        for keyring_commands_item_data in _keyring_commands:
            keyring_commands_item = E2EeSignedCommand.from_dict(
                keyring_commands_item_data
            )

            keyring_commands.append(keyring_commands_item)

        gate_commands = []
        _gate_commands = d.pop("gate_commands")
        for gate_commands_item_data in _gate_commands:
            gate_commands_item = E2EeSignedCommand.from_dict(gate_commands_item_data)

            gate_commands.append(gate_commands_item)

        preparation_commands = []
        _preparation_commands = d.pop("preparation_commands")
        for preparation_commands_item_data in _preparation_commands:
            preparation_commands_item = E2EeSignedCommand.from_dict(
                preparation_commands_item_data
            )

            preparation_commands.append(preparation_commands_item)

        e2_ee_root_replacement_apply = cls(
            preparation_digest=preparation_digest,
            read_set_digest=read_set_digest,
            root_command=root_command,
            companion_admission=companion_admission,
            owner_key_commands=owner_key_commands,
            owner_candidate_commands=owner_candidate_commands,
            scope_commands=scope_commands,
            source_submissions=source_submissions,
            keyring_commands=keyring_commands,
            gate_commands=gate_commands,
            preparation_commands=preparation_commands,
        )

        return e2_ee_root_replacement_apply
