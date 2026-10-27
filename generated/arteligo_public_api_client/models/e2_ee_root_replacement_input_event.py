from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_root_replacement_input_event_kind import (
    E2EeRootReplacementInputEventKind,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_key_operation_pending_command import (
        E2EeKeyOperationPendingCommand,
    )
    from ..models.e2_ee_key_operation_protected_source import (
        E2EeKeyOperationProtectedSource,
    )
    from ..models.e2_ee_key_operation_reference import E2EeKeyOperationReference
    from ..models.e2_ee_owner_binding_reference import E2EeOwnerBindingReference
    from ..models.e2_ee_owner_issuer_root import E2EeOwnerIssuerRoot
    from ..models.e2_ee_owner_source_submission import E2EeOwnerSourceSubmission
    from ..models.e2_ee_root_replacement_scope_command import (
        E2EeRootReplacementScopeCommand,
    )
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeRootReplacementInputEvent")


@_attrs_define
class E2EeRootReplacementInputEvent:
    """Finite typed input. Header is first. Each item appears once. Complete binds the count and SHA-256 over uint64 big-
    endian byte length followed by exact UTF-8 bytes of each preceding NDJSON line, excluding its newline. Fragment
    events carry at most 16384 decoded bytes of one original input event and use its sequence, ordered fragment_index,
    and fragment_final. The digest covers reconstructed original events, never fragment wrappers.

        Attributes:
            operation_id (str):
            sequence (int):
            kind (E2EeRootReplacementInputEventKind):
            issuer_device_id (str | Unset):
            expected_root (E2EeOwnerIssuerRoot | Unset):
            preparation_digest (str | Unset):
            read_set_digest (str | Unset):
            reference (E2EeKeyOperationReference | Unset):
            retained_binding (E2EeOwnerBindingReference | Unset):
            protected_source (E2EeKeyOperationProtectedSource | Unset):
            pending_command (E2EeKeyOperationPendingCommand | Unset):
            command (E2EeSignedCommand | Unset):
            scope_command (E2EeRootReplacementScopeCommand | Unset):
            source_submission (E2EeOwnerSourceSubmission | Unset):
            fragment_index (int | Unset):
            fragment_final (bool | Unset):
            fragment_data (str | Unset):
            event_count (int | Unset):
            payload_digest (str | Unset):
    """

    operation_id: str
    sequence: int
    kind: E2EeRootReplacementInputEventKind
    issuer_device_id: str | Unset = UNSET
    expected_root: E2EeOwnerIssuerRoot | Unset = UNSET
    preparation_digest: str | Unset = UNSET
    read_set_digest: str | Unset = UNSET
    reference: E2EeKeyOperationReference | Unset = UNSET
    retained_binding: E2EeOwnerBindingReference | Unset = UNSET
    protected_source: E2EeKeyOperationProtectedSource | Unset = UNSET
    pending_command: E2EeKeyOperationPendingCommand | Unset = UNSET
    command: E2EeSignedCommand | Unset = UNSET
    scope_command: E2EeRootReplacementScopeCommand | Unset = UNSET
    source_submission: E2EeOwnerSourceSubmission | Unset = UNSET
    fragment_index: int | Unset = UNSET
    fragment_final: bool | Unset = UNSET
    fragment_data: str | Unset = UNSET
    event_count: int | Unset = UNSET
    payload_digest: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        sequence = self.sequence

        kind = self.kind.value

        issuer_device_id = self.issuer_device_id

        expected_root: dict[str, Any] | Unset = UNSET
        if not isinstance(self.expected_root, Unset):
            expected_root = self.expected_root.to_dict()

        preparation_digest = self.preparation_digest

        read_set_digest = self.read_set_digest

        reference: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reference, Unset):
            reference = self.reference.to_dict()

        retained_binding: dict[str, Any] | Unset = UNSET
        if not isinstance(self.retained_binding, Unset):
            retained_binding = self.retained_binding.to_dict()

        protected_source: dict[str, Any] | Unset = UNSET
        if not isinstance(self.protected_source, Unset):
            protected_source = self.protected_source.to_dict()

        pending_command: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pending_command, Unset):
            pending_command = self.pending_command.to_dict()

        command: dict[str, Any] | Unset = UNSET
        if not isinstance(self.command, Unset):
            command = self.command.to_dict()

        scope_command: dict[str, Any] | Unset = UNSET
        if not isinstance(self.scope_command, Unset):
            scope_command = self.scope_command.to_dict()

        source_submission: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source_submission, Unset):
            source_submission = self.source_submission.to_dict()

        fragment_index = self.fragment_index

        fragment_final = self.fragment_final

        fragment_data = self.fragment_data

        event_count = self.event_count

        payload_digest = self.payload_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "sequence": sequence,
                "kind": kind,
            }
        )
        if issuer_device_id is not UNSET:
            field_dict["issuer_device_id"] = issuer_device_id
        if expected_root is not UNSET:
            field_dict["expected_root"] = expected_root
        if preparation_digest is not UNSET:
            field_dict["preparation_digest"] = preparation_digest
        if read_set_digest is not UNSET:
            field_dict["read_set_digest"] = read_set_digest
        if reference is not UNSET:
            field_dict["reference"] = reference
        if retained_binding is not UNSET:
            field_dict["retained_binding"] = retained_binding
        if protected_source is not UNSET:
            field_dict["protected_source"] = protected_source
        if pending_command is not UNSET:
            field_dict["pending_command"] = pending_command
        if command is not UNSET:
            field_dict["command"] = command
        if scope_command is not UNSET:
            field_dict["scope_command"] = scope_command
        if source_submission is not UNSET:
            field_dict["source_submission"] = source_submission
        if fragment_index is not UNSET:
            field_dict["fragment_index"] = fragment_index
        if fragment_final is not UNSET:
            field_dict["fragment_final"] = fragment_final
        if fragment_data is not UNSET:
            field_dict["fragment_data"] = fragment_data
        if event_count is not UNSET:
            field_dict["event_count"] = event_count
        if payload_digest is not UNSET:
            field_dict["payload_digest"] = payload_digest

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
        from ..models.e2_ee_owner_issuer_root import E2EeOwnerIssuerRoot
        from ..models.e2_ee_owner_source_submission import E2EeOwnerSourceSubmission
        from ..models.e2_ee_root_replacement_scope_command import (
            E2EeRootReplacementScopeCommand,
        )
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        sequence = d.pop("sequence")

        kind = E2EeRootReplacementInputEventKind(d.pop("kind"))

        issuer_device_id = d.pop("issuer_device_id", UNSET)

        _expected_root = d.pop("expected_root", UNSET)
        expected_root: E2EeOwnerIssuerRoot | Unset
        if isinstance(_expected_root, Unset):
            expected_root = UNSET
        else:
            expected_root = E2EeOwnerIssuerRoot.from_dict(_expected_root)

        preparation_digest = d.pop("preparation_digest", UNSET)

        read_set_digest = d.pop("read_set_digest", UNSET)

        _reference = d.pop("reference", UNSET)
        reference: E2EeKeyOperationReference | Unset
        if isinstance(_reference, Unset):
            reference = UNSET
        else:
            reference = E2EeKeyOperationReference.from_dict(_reference)

        _retained_binding = d.pop("retained_binding", UNSET)
        retained_binding: E2EeOwnerBindingReference | Unset
        if isinstance(_retained_binding, Unset):
            retained_binding = UNSET
        else:
            retained_binding = E2EeOwnerBindingReference.from_dict(_retained_binding)

        _protected_source = d.pop("protected_source", UNSET)
        protected_source: E2EeKeyOperationProtectedSource | Unset
        if isinstance(_protected_source, Unset):
            protected_source = UNSET
        else:
            protected_source = E2EeKeyOperationProtectedSource.from_dict(
                _protected_source
            )

        _pending_command = d.pop("pending_command", UNSET)
        pending_command: E2EeKeyOperationPendingCommand | Unset
        if isinstance(_pending_command, Unset):
            pending_command = UNSET
        else:
            pending_command = E2EeKeyOperationPendingCommand.from_dict(_pending_command)

        _command = d.pop("command", UNSET)
        command: E2EeSignedCommand | Unset
        if isinstance(_command, Unset):
            command = UNSET
        else:
            command = E2EeSignedCommand.from_dict(_command)

        _scope_command = d.pop("scope_command", UNSET)
        scope_command: E2EeRootReplacementScopeCommand | Unset
        if isinstance(_scope_command, Unset):
            scope_command = UNSET
        else:
            scope_command = E2EeRootReplacementScopeCommand.from_dict(_scope_command)

        _source_submission = d.pop("source_submission", UNSET)
        source_submission: E2EeOwnerSourceSubmission | Unset
        if isinstance(_source_submission, Unset):
            source_submission = UNSET
        else:
            source_submission = E2EeOwnerSourceSubmission.from_dict(_source_submission)

        fragment_index = d.pop("fragment_index", UNSET)

        fragment_final = d.pop("fragment_final", UNSET)

        fragment_data = d.pop("fragment_data", UNSET)

        event_count = d.pop("event_count", UNSET)

        payload_digest = d.pop("payload_digest", UNSET)

        e2_ee_root_replacement_input_event = cls(
            operation_id=operation_id,
            sequence=sequence,
            kind=kind,
            issuer_device_id=issuer_device_id,
            expected_root=expected_root,
            preparation_digest=preparation_digest,
            read_set_digest=read_set_digest,
            reference=reference,
            retained_binding=retained_binding,
            protected_source=protected_source,
            pending_command=pending_command,
            command=command,
            scope_command=scope_command,
            source_submission=source_submission,
            fragment_index=fragment_index,
            fragment_final=fragment_final,
            fragment_data=fragment_data,
            event_count=event_count,
            payload_digest=payload_digest,
        )

        return e2_ee_root_replacement_input_event
