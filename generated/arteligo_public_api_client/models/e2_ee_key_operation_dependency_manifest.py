from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_key_operation_pending_command import (
        E2EeKeyOperationPendingCommand,
    )
    from ..models.e2_ee_key_operation_protected_source import (
        E2EeKeyOperationProtectedSource,
    )
    from ..models.e2_ee_key_operation_reference import E2EeKeyOperationReference
    from ..models.e2_ee_owner_binding_reference import E2EeOwnerBindingReference


T = TypeVar("T", bound="E2EeKeyOperationDependencyManifest")


@_attrs_define
class E2EeKeyOperationDependencyManifest:
    """
    Attributes:
        references (list[E2EeKeyOperationReference]):
        retained_bindings (list[E2EeOwnerBindingReference]):
        protected_sources (list[E2EeKeyOperationProtectedSource]):
        pending_commands (list[E2EeKeyOperationPendingCommand]):
    """

    references: list[E2EeKeyOperationReference]
    retained_bindings: list[E2EeOwnerBindingReference]
    protected_sources: list[E2EeKeyOperationProtectedSource]
    pending_commands: list[E2EeKeyOperationPendingCommand]

    def to_dict(self) -> dict[str, Any]:
        references = []
        for references_item_data in self.references:
            references_item = references_item_data.to_dict()
            references.append(references_item)

        retained_bindings = []
        for retained_bindings_item_data in self.retained_bindings:
            retained_bindings_item = retained_bindings_item_data.to_dict()
            retained_bindings.append(retained_bindings_item)

        protected_sources = []
        for protected_sources_item_data in self.protected_sources:
            protected_sources_item = protected_sources_item_data.to_dict()
            protected_sources.append(protected_sources_item)

        pending_commands = []
        for pending_commands_item_data in self.pending_commands:
            pending_commands_item = pending_commands_item_data.to_dict()
            pending_commands.append(pending_commands_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "references": references,
                "retained_bindings": retained_bindings,
                "protected_sources": protected_sources,
                "pending_commands": pending_commands,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_key_operation_pending_command import (
            E2EeKeyOperationPendingCommand,
        )
        from ..models.e2_ee_key_operation_protected_source import (
            E2EeKeyOperationProtectedSource,
        )
        from ..models.e2_ee_key_operation_reference import E2EeKeyOperationReference
        from ..models.e2_ee_owner_binding_reference import E2EeOwnerBindingReference

        d = dict(src_dict)
        references = []
        _references = d.pop("references")
        for references_item_data in _references:
            references_item = E2EeKeyOperationReference.from_dict(references_item_data)

            references.append(references_item)

        retained_bindings = []
        _retained_bindings = d.pop("retained_bindings")
        for retained_bindings_item_data in _retained_bindings:
            retained_bindings_item = E2EeOwnerBindingReference.from_dict(
                retained_bindings_item_data
            )

            retained_bindings.append(retained_bindings_item)

        protected_sources = []
        _protected_sources = d.pop("protected_sources")
        for protected_sources_item_data in _protected_sources:
            protected_sources_item = E2EeKeyOperationProtectedSource.from_dict(
                protected_sources_item_data
            )

            protected_sources.append(protected_sources_item)

        pending_commands = []
        _pending_commands = d.pop("pending_commands")
        for pending_commands_item_data in _pending_commands:
            pending_commands_item = E2EeKeyOperationPendingCommand.from_dict(
                pending_commands_item_data
            )

            pending_commands.append(pending_commands_item)

        e2_ee_key_operation_dependency_manifest = cls(
            references=references,
            retained_bindings=retained_bindings,
            protected_sources=protected_sources,
            pending_commands=pending_commands,
        )

        return e2_ee_key_operation_dependency_manifest
