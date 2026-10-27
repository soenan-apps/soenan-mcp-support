from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_root_replacement_event_fragment_kind import (
    E2EeRootReplacementEventFragmentKind,
)
from ..models.e2_ee_root_replacement_event_kind import E2EeRootReplacementEventKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_device import E2EeDevice
    from ..models.e2_ee_key_operation_dependency_manifest import (
        E2EeKeyOperationDependencyManifest,
    )
    from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
    from ..models.e2_ee_recovery_bundle import E2EeRecoveryBundle
    from ..models.e2_ee_root_replacement_owner import E2EeRootReplacementOwner
    from ..models.e2_ee_root_replacement_scope import E2EeRootReplacementScope


T = TypeVar("T", bound="E2EeRootReplacementEvent")


@_attrs_define
class E2EeRootReplacementEvent:
    """Typed finite stream. Each kind has exactly its named payload. The complete digest is SHA-256 over concatenated
    decoded event_bytes of preceding logical events in sequence order. event_bytes is the exact UTF-8 JSON payload
    without that field. Oversized logical events are transported as fragment events with the same sequence, ordered
    fragment_index, fragment_final and at most 16384 decoded fragment_data bytes. Reassemble and validate the original
    typed event before hashing or using it. event_count counts logical events and excludes fragment wrappers.

        Attributes:
            operation_id (str):
            sequence (int):
            kind (E2EeRootReplacementEventKind):
            event_bytes (str | Unset):
            key_state_digest (str | Unset):
            dependency_manifest (E2EeKeyOperationDependencyManifest | Unset):
            issuer_evidence (E2EeOwnerIssuerEvidence | Unset): Immutable public issuer proof graph for the selected binding.
                Includes only exact certificate references frozen by its signed issuer_admission and recursively by accepted
                Account witnesses, plus the corresponding public recovery checkpoints. This is not a current device directory
                and grants no content or key-distribution authority. Fetch on demand; retain references rather than embedding
                full certificate wrappers in private history.
            recovery (E2EeRecoveryBundle | Unset):
            device (E2EeDevice | Unset):
            scope (E2EeRootReplacementScope | Unset):
            owner (E2EeRootReplacementOwner | Unset):
            account_preparation (str | Unset): Exact Account-owned public preparation bytes. Authenticate independently at
                the Account preparation endpoint.
            preparation_digest (str | Unset):
            read_set_digest (str | Unset):
            event_count (int | Unset):
            fragment_kind (E2EeRootReplacementEventFragmentKind | Unset):
            fragment_index (int | Unset):
            fragment_final (bool | Unset):
            fragment_data (str | Unset):
    """

    operation_id: str
    sequence: int
    kind: E2EeRootReplacementEventKind
    event_bytes: str | Unset = UNSET
    key_state_digest: str | Unset = UNSET
    dependency_manifest: E2EeKeyOperationDependencyManifest | Unset = UNSET
    issuer_evidence: E2EeOwnerIssuerEvidence | Unset = UNSET
    recovery: E2EeRecoveryBundle | Unset = UNSET
    device: E2EeDevice | Unset = UNSET
    scope: E2EeRootReplacementScope | Unset = UNSET
    owner: E2EeRootReplacementOwner | Unset = UNSET
    account_preparation: str | Unset = UNSET
    preparation_digest: str | Unset = UNSET
    read_set_digest: str | Unset = UNSET
    event_count: int | Unset = UNSET
    fragment_kind: E2EeRootReplacementEventFragmentKind | Unset = UNSET
    fragment_index: int | Unset = UNSET
    fragment_final: bool | Unset = UNSET
    fragment_data: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        sequence = self.sequence

        kind = self.kind.value

        event_bytes = self.event_bytes

        key_state_digest = self.key_state_digest

        dependency_manifest: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dependency_manifest, Unset):
            dependency_manifest = self.dependency_manifest.to_dict()

        issuer_evidence: dict[str, Any] | Unset = UNSET
        if not isinstance(self.issuer_evidence, Unset):
            issuer_evidence = self.issuer_evidence.to_dict()

        recovery: dict[str, Any] | Unset = UNSET
        if not isinstance(self.recovery, Unset):
            recovery = self.recovery.to_dict()

        device: dict[str, Any] | Unset = UNSET
        if not isinstance(self.device, Unset):
            device = self.device.to_dict()

        scope: dict[str, Any] | Unset = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope.to_dict()

        owner: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner, Unset):
            owner = self.owner.to_dict()

        account_preparation = self.account_preparation

        preparation_digest = self.preparation_digest

        read_set_digest = self.read_set_digest

        event_count = self.event_count

        fragment_kind: str | Unset = UNSET
        if not isinstance(self.fragment_kind, Unset):
            fragment_kind = self.fragment_kind.value

        fragment_index = self.fragment_index

        fragment_final = self.fragment_final

        fragment_data = self.fragment_data

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "sequence": sequence,
                "kind": kind,
            }
        )
        if event_bytes is not UNSET:
            field_dict["event_bytes"] = event_bytes
        if key_state_digest is not UNSET:
            field_dict["key_state_digest"] = key_state_digest
        if dependency_manifest is not UNSET:
            field_dict["dependency_manifest"] = dependency_manifest
        if issuer_evidence is not UNSET:
            field_dict["issuer_evidence"] = issuer_evidence
        if recovery is not UNSET:
            field_dict["recovery"] = recovery
        if device is not UNSET:
            field_dict["device"] = device
        if scope is not UNSET:
            field_dict["scope"] = scope
        if owner is not UNSET:
            field_dict["owner"] = owner
        if account_preparation is not UNSET:
            field_dict["account_preparation"] = account_preparation
        if preparation_digest is not UNSET:
            field_dict["preparation_digest"] = preparation_digest
        if read_set_digest is not UNSET:
            field_dict["read_set_digest"] = read_set_digest
        if event_count is not UNSET:
            field_dict["event_count"] = event_count
        if fragment_kind is not UNSET:
            field_dict["fragment_kind"] = fragment_kind
        if fragment_index is not UNSET:
            field_dict["fragment_index"] = fragment_index
        if fragment_final is not UNSET:
            field_dict["fragment_final"] = fragment_final
        if fragment_data is not UNSET:
            field_dict["fragment_data"] = fragment_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_device import E2EeDevice
        from ..models.e2_ee_key_operation_dependency_manifest import (
            E2EeKeyOperationDependencyManifest,
        )
        from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
        from ..models.e2_ee_recovery_bundle import E2EeRecoveryBundle
        from ..models.e2_ee_root_replacement_owner import E2EeRootReplacementOwner
        from ..models.e2_ee_root_replacement_scope import E2EeRootReplacementScope

        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        sequence = d.pop("sequence")

        kind = E2EeRootReplacementEventKind(d.pop("kind"))

        event_bytes = d.pop("event_bytes", UNSET)

        key_state_digest = d.pop("key_state_digest", UNSET)

        _dependency_manifest = d.pop("dependency_manifest", UNSET)
        dependency_manifest: E2EeKeyOperationDependencyManifest | Unset
        if isinstance(_dependency_manifest, Unset):
            dependency_manifest = UNSET
        else:
            dependency_manifest = E2EeKeyOperationDependencyManifest.from_dict(
                _dependency_manifest
            )

        _issuer_evidence = d.pop("issuer_evidence", UNSET)
        issuer_evidence: E2EeOwnerIssuerEvidence | Unset
        if isinstance(_issuer_evidence, Unset):
            issuer_evidence = UNSET
        else:
            issuer_evidence = E2EeOwnerIssuerEvidence.from_dict(_issuer_evidence)

        _recovery = d.pop("recovery", UNSET)
        recovery: E2EeRecoveryBundle | Unset
        if isinstance(_recovery, Unset):
            recovery = UNSET
        else:
            recovery = E2EeRecoveryBundle.from_dict(_recovery)

        _device = d.pop("device", UNSET)
        device: E2EeDevice | Unset
        if isinstance(_device, Unset):
            device = UNSET
        else:
            device = E2EeDevice.from_dict(_device)

        _scope = d.pop("scope", UNSET)
        scope: E2EeRootReplacementScope | Unset
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = E2EeRootReplacementScope.from_dict(_scope)

        _owner = d.pop("owner", UNSET)
        owner: E2EeRootReplacementOwner | Unset
        if isinstance(_owner, Unset):
            owner = UNSET
        else:
            owner = E2EeRootReplacementOwner.from_dict(_owner)

        account_preparation = d.pop("account_preparation", UNSET)

        preparation_digest = d.pop("preparation_digest", UNSET)

        read_set_digest = d.pop("read_set_digest", UNSET)

        event_count = d.pop("event_count", UNSET)

        _fragment_kind = d.pop("fragment_kind", UNSET)
        fragment_kind: E2EeRootReplacementEventFragmentKind | Unset
        if isinstance(_fragment_kind, Unset):
            fragment_kind = UNSET
        else:
            fragment_kind = E2EeRootReplacementEventFragmentKind(_fragment_kind)

        fragment_index = d.pop("fragment_index", UNSET)

        fragment_final = d.pop("fragment_final", UNSET)

        fragment_data = d.pop("fragment_data", UNSET)

        e2_ee_root_replacement_event = cls(
            operation_id=operation_id,
            sequence=sequence,
            kind=kind,
            event_bytes=event_bytes,
            key_state_digest=key_state_digest,
            dependency_manifest=dependency_manifest,
            issuer_evidence=issuer_evidence,
            recovery=recovery,
            device=device,
            scope=scope,
            owner=owner,
            account_preparation=account_preparation,
            preparation_digest=preparation_digest,
            read_set_digest=read_set_digest,
            event_count=event_count,
            fragment_kind=fragment_kind,
            fragment_index=fragment_index,
            fragment_final=fragment_final,
            fragment_data=fragment_data,
        )

        return e2_ee_root_replacement_event
