from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from account_public_api_client.models.owner_transfer_decision import OwnerTransferDecision
from arteligo_public_api_client.models.e2_ee_owner_custody import E2EeOwnerCustody

from ._crypto import E2eeError
from ._owner_protocol import (
    OwnerAuthorityHead, OwnerBinding, OwnerCapsuleCrypto, OwnerManifest, OwnerOperation, OwnerSourceDocument,
    SignedEvidence, authority_head, object_value, parse_model,
)
from ._signed_commands import AcceptedCommand, RejectedCommand, SavedCommand, UncertainCommand
from ._trust import _RootIdentity

if TYPE_CHECKING:
    from ._session import DeviceSession


@dataclass(frozen=True)
class OwnerKey:
    key_id: str
    key_epoch: int
    public_key: str
    binding_digest: str
    secret_key: str = field(repr=False)
    binding: OwnerBinding = field(repr=False)

    @classmethod
    def parse(cls, value: Any, organization: str, crypto: OwnerCapsuleCrypto) -> OwnerKey:
        value = object_value(value)
        try:
            binding = OwnerBinding.parse(value["binding_command"])
            if (set(value) != {"key_id", "key_epoch", "public_key", "secret_key", "binding_digest", "binding_command"}
                    or type(value["key_epoch"]) is not int or value["key_epoch"] < 1
                    or crypto.public_key(value["secret_key"]) != value["public_key"]
                    or binding.body.organization_id != organization
                    or binding.body.key_id != value["key_id"] or binding.body.public_key != value["public_key"]
                    or binding.command.digest(crypto.crypto, binding.operation) != value["binding_digest"]):
                raise E2eeError("owner_keyring_mismatch")
            return cls(value["key_id"], value["key_epoch"], value["public_key"],
                       value["binding_digest"], value["secret_key"], binding)
        except (KeyError, TypeError):
            raise E2eeError("owner_keyring_mismatch") from None

    def public_binding(self) -> dict[str, Any]:
        return {"key_id": self.key_id, "key_epoch": self.key_epoch,
                "public_key": self.public_key, "binding_digest": self.binding_digest}

    def document(self) -> dict[str, Any]:
        return {**self.public_binding(), "secret_key": self.secret_key,
                "binding_command": self.binding.command.document()}


@dataclass
class CandidateSecret:
    secret_key: str = field(repr=False)
    custody: E2EeOwnerCustody
    binding: OwnerBinding
    registered: bool = False

    @classmethod
    def parse(cls, value: Any) -> CandidateSecret:
        value = object_value(value)
        try:
            binding = OwnerBinding.parse(value["offer"])
            if binding.operation != OwnerOperation.OFFER or not isinstance(value["secret_key"], str):
                raise E2eeError("invalid_owner_state")
            return cls(value["secret_key"], parse_model(E2EeOwnerCustody.from_dict, value["custody"]),
                       binding, value.get("registered") is True)
        except (KeyError, TypeError):
            raise E2eeError("invalid_owner_state") from None

    def document(self) -> dict[str, Any]:
        return {"secret_key": self.secret_key, "custody": self.custody.to_dict(),
                "offer": self.binding.command.document(), "registered": self.registered}


@dataclass(frozen=True)
class SourceAnchor:
    command: SignedEvidence
    device: dict[str, Any]
    root: dict[str, Any]

    @classmethod
    def parse(cls, value: Any) -> SourceAnchor:
        value = object_value(value)
        try:
            command = SignedEvidence.parse(value["command"])
            device, root = object_value(value["device"]), object_value(value["root"])
            if command.body.get("trusted_device") != device or command.body.get("recovery_root") != root:
                raise E2eeError("invalid_owner_state")
            return cls(command, device, root)
        except (KeyError, TypeError):
            raise E2eeError("invalid_owner_state") from None

    def document(self) -> dict[str, Any]:
        return {"command": self.command.document(), "device": self.device, "root": self.root}


@dataclass(frozen=True)
class ManifestSelection:
    source_binding: dict[str, Any]
    preparation: SignedEvidence
    decision: OwnerTransferDecision



class ManifestOrigin(str, Enum):
    LOCAL = "local_export"
    FROZEN = "frozen_custody"
    DATA = "unqualified_history"

@dataclass(frozen=True)
class SavedManifest:
    manifest: OwnerManifest
    selection: ManifestSelection | None = None
    origin: ManifestOrigin = ManifestOrigin.LOCAL

    def document(self) -> dict[str, Any]:
        result = {"signed_command": self.manifest.command.document(), "manifest_digest": self.manifest.digest,
                  "documents": [item.document() for item in self.manifest.require_documents()],
                  "origin": self.origin.value}
        if self.selection is not None:
            result.update(source_binding=self.selection.source_binding,
                          selected_preparation=self.selection.preparation.document(),
                          selected_decision=self.selection.decision.to_dict())
        return result


@dataclass(frozen=True)
class PreparationStamp:
    authority: OwnerAuthorityHead
    offer_digest: str
    manifest_digest: str

    def document(self) -> dict[str, Any]:
        return {"head": self.authority.to_dict(), "offer_digest": self.offer_digest,
                "manifest_digest": self.manifest_digest}


@dataclass(frozen=True)
class RootProvenance:
    self_roots: tuple[_RootIdentity, ...] = ()

    @classmethod
    def parse(cls, value: Any, origin: str, subject: str) -> RootProvenance:
        value = object_value(value)
        if set(value) != {"v", "self_roots"} or value["v"] != 1 or not isinstance(value["self_roots"], list):
            raise E2eeError("invalid_owner_state")
        roots = tuple(_RootIdentity.parse(origin, subject, object_value(item)) for item in value["self_roots"])
        return cls().merged(roots)

    def merged(self, roots: tuple[_RootIdentity, ...]) -> RootProvenance:
        values = {root.identifier: root for root in self.self_roots}
        generations = {root.generation: root for root in self.self_roots}
        for root in roots:
            if (root.identifier in values and values[root.identifier] != root
                    or root.generation in generations and generations[root.generation] != root):
                raise E2eeError("recovery_key_changed")
            values[root.identifier], generations[root.generation] = root, root
        return RootProvenance(tuple(sorted(values.values(), key=lambda root: (root.generation, root.identifier))))

    def partition(self, authenticated: frozenset[_RootIdentity]) -> tuple[tuple[_RootIdentity, ...], tuple[_RootIdentity, ...]]:
        known = RootProvenance().merged(tuple(authenticated))
        generations = {root.generation: root for root in known.self_roots}
        identifiers = {root.identifier: root for root in known.self_roots}
        trusted, provisional = [], []
        for root in self.self_roots:
            if (root.generation in generations and generations[root.generation] != root
                    or root.identifier in identifiers and identifiers[root.identifier] != root):
                raise E2eeError("recovery_key_changed")
            (trusted if root in authenticated else provisional).append(root)
        return tuple(trusted), tuple(provisional)

    def document(self) -> dict[str, Any]:
        return {"v": 1, "self_roots": [root.document() for root in self.self_roots]}


@dataclass
class OwnerState:
    keys: list[OwnerKey] = field(default_factory=list, repr=False)
    journal: dict[str, SavedCommand] = field(default_factory=dict, repr=False)
    manifests: dict[str, SavedManifest] = field(default_factory=dict)
    source_anchor: SourceAnchor | None = None
    confirmed_sources: list[SourceAnchor] = field(default_factory=list)
    observed_head: OwnerAuthorityHead | None = None
    candidate: CandidateSecret | None = field(default=None, repr=False)
    retired_candidates: list[CandidateSecret] = field(default_factory=list, repr=False)
    registration: SavedCommand | None = field(default=None, repr=False)
    custody: E2EeOwnerCustody | None = None
    prepared: dict[str, PreparationStamp] = field(default_factory=dict)
    pending_import: dict[str, str] | None = field(default=None, repr=False)
    receipts: dict[str, OwnerTransferDecision] = field(default_factory=dict)
    completed_imports: set[str] = field(default_factory=set)


class OwnerStateStore:
    def __init__(self, session: DeviceSession, crypto: OwnerCapsuleCrypto):
        self.session, self.crypto = session, crypto
        self._device: dict[str, Any] | None = None
        self._states: dict[str, OwnerState] = {}
        self._roots = RootProvenance()
        self._source_observations: dict[str, tuple[str, OwnerSourceDocument]] = {}

    def _load(self) -> None:
        self.session.require_approved()
        if self._device is self.session._device:
            return
        device = self.session._device
        values = (device or {}).get("owner_access", {})
        states = {organization: self._parse(organization, object_value(value)) for organization, value in values.items()}
        roots = RootProvenance.parse((device or {}).get("owner_root_provenance", {"v": 1, "self_roots": []}),
                                    self.session.trust.origin, self.session.subject)
        roots = roots.merged(tuple(_RootIdentity.parse(self.session.trust.origin, self.session.subject, item)
                                   for value in values.values() for item in value.get("self_roots", [])))
        observations = {}
        for scope, value in object_value((device or {}).get("owner_source_observations", {})).items():
            value = object_value(value)
            if set(value) != {"organization_id", "document"} or not isinstance(value["organization_id"], str):
                raise E2eeError("invalid_owner_state")
            document = OwnerSourceDocument.parse(self.crypto.crypto, value["document"])
            if document.project.project_id != scope:
                raise E2eeError("invalid_owner_state")
            observations[scope] = (value["organization_id"], document)
        self._source_observations = observations
        self._device, self._states, self._roots = device, states, roots

    def _parse(self, organization: str, value: dict[str, Any]) -> OwnerState:
        try:
            state = OwnerState()
            state.keys = [OwnerKey.parse(item, organization, self.crypto) for item in value.get("keys", [])]
            state.journal = {slot: SavedCommand.parse(item, OwnerOperation(item["operation"]))
                             for slot, item in value.get("journal", {}).items()}
            for identifier, saved in value.get("manifests", {}).items():
                manifest = OwnerManifest.parse(self.crypto.crypto, saved["signed_command"], saved.get("documents", []))
                if manifest.digest != saved["manifest_digest"] or manifest.body.manifest_id != identifier:
                    raise E2eeError("owner_source_manifest_mismatch")
                selection = None
                if "selected_decision" in saved:
                    selection = ManifestSelection(object_value(saved["source_binding"]),
                        SignedEvidence.parse(saved["selected_preparation"]),
                        parse_model(OwnerTransferDecision.from_dict, saved["selected_decision"]))
                origin = ManifestOrigin(saved.get("origin", ManifestOrigin.DATA.value))
                state.manifests[identifier] = SavedManifest(manifest, selection, origin)
            if value.get("source_anchor") is not None:
                state.source_anchor = SourceAnchor.parse(value["source_anchor"])
            state.confirmed_sources = [SourceAnchor.parse(item) for item in value.get("confirmed_sources", [])]
            if value.get("observed_head") is not None:
                state.observed_head = authority_head(value["observed_head"], organization)
            if value.get("candidate") is not None:
                state.candidate = CandidateSecret.parse(value["candidate"])
            state.retired_candidates = [CandidateSecret.parse(item) for item in value.get("retired_candidates", [])]
            if value.get("key_registration") is not None:
                pending = value["key_registration"]
                state.registration = SavedCommand.parse(pending, OwnerOperation.REGISTER_KEY)
                state.registration.key = pending.get("key", pending.get("secret_key"))
            if value.get("custody") is not None:
                state.custody = parse_model(E2EeOwnerCustody.from_dict, value["custody"])
            state.prepared = {identifier: PreparationStamp(authority_head(item["head"], organization),
                item["offer_digest"], item["manifest_digest"]) for identifier, item in value.get("prepared", {}).items()}
            if value.get("pending_import") is not None:
                state.pending_import = object_value(value["pending_import"])
            state.receipts = {identifier: parse_model(OwnerTransferDecision.from_dict, item)
                              for identifier, item in value.get("receipts", {}).items()}
            state.completed_imports = set(value.get("completed_imports", []))
            return state
        except (KeyError, TypeError, ValueError):
            raise E2eeError("invalid_owner_state") from None

    def get(self, organization: str) -> OwnerState:
        self._load()
        return self._states.setdefault(organization, OwnerState())

    def find(self, organization: str) -> OwnerState | None:
        self._load()
        return self._states.get(organization)

    def organizations(self) -> tuple[str, ...]:
        self._load()
        return tuple(self._states)

    def self_roots(self) -> tuple[_RootIdentity, ...]:
        self._load()
        return self._roots.self_roots

    def source_namespace(self, scope: str, organization: str | None) -> None:
        self._load()
        previous = self._source_observations.get(scope)
        if previous is not None and previous[0] != organization:
            raise E2eeError("owner_project_source_mismatch")

    def observe_source(self, scope: str, organization: str, document: OwnerSourceDocument | None) -> None:
        self.source_namespace(scope, organization)
        previous = self._source_observations.get(scope)
        if previous is not None:
            if document is None or previous[1].document_bytes != document.document_bytes:
                raise E2eeError("owner_project_source_mismatch")
            return
        if document is not None:
            self._source_observations[scope] = (organization, document)
            self._device.setdefault("owner_source_observations", {})[scope] = {
                "organization_id": organization, "document": document.document(),
            }
            self.session._persist()

    def retain_roots(self, roots: tuple[_RootIdentity, ...]) -> None:
        self._load()
        if any(root.origin != self.session.trust.origin or root.subject != self.session.subject for root in roots):
            raise E2eeError("account_mismatch")
        self._roots = self._roots.merged(roots)
        self._device["owner_root_provenance"] = self._roots.document()
        for value in self._device.get("owner_access", {}).values():
            value.pop("self_roots", None)
        self.session._persist()

    def save(self, organization: str) -> None:
        state = self.get(organization)
        value = {
            "keys": [key.document() for key in state.keys],
            "journal": {slot: saved.document() for slot, saved in state.journal.items()},
            "manifests": {identifier: saved.document() for identifier, saved in state.manifests.items()},
            "confirmed_sources": [anchor.document() for anchor in state.confirmed_sources],
            "retired_candidates": [candidate.document() for candidate in state.retired_candidates],
            "prepared": {identifier: stamp.document() for identifier, stamp in state.prepared.items()},
            "receipts": {identifier: receipt.to_dict() for identifier, receipt in state.receipts.items()},
            "completed_imports": sorted(state.completed_imports),
        }
        if state.source_anchor is not None:
            value["source_anchor"] = state.source_anchor.document()
        if state.observed_head is not None:
            value["observed_head"] = state.observed_head.to_dict()
        if state.candidate is not None:
            value["candidate"] = state.candidate.document()
        if state.custody is not None:
            value["custody"] = state.custody.to_dict()
        if state.registration is not None:
            value["key_registration"] = state.registration.document()
        if state.pending_import is not None:
            value["pending_import"] = state.pending_import
        self._device.setdefault("owner_access", {})[organization] = value
        self._device["owner_root_provenance"] = self._roots.document()
        for saved in self._device["owner_access"].values():
            saved.pop("self_roots", None)
        try:
            self.session._persist()
        except BaseException:
            self.session.lock()
            raise

    def command(self, organization: str, slot: str, operation: OwnerOperation,
                body: dict[str, Any] | None = None) -> SavedCommand:
        state = self.get(organization)
        saved = state.journal.get(slot)
        if saved is None:
            if body is None:
                raise E2eeError("owner_command_not_pending")
            saved = SavedCommand(operation, UncertainCommand(SignedEvidence.parse(self.session.sign(operation, body))))
            state.journal[slot] = saved
            self.save(organization)
        elif saved.operation != operation:
            raise E2eeError("owner_command_pending")
        return saved

    def finish(self, organization: str, slot: str) -> None:
        state = self.get(organization)
        saved = state.journal.get(slot)
        if saved is not None:
            if not isinstance(saved.outcome, (AcceptedCommand, RejectedCommand)):
                raise E2eeError("owner_command_uncertain")
            del state.journal[slot]
            self.save(organization)

    def clear(self) -> None:
        self._states.clear()
        self._roots = RootProvenance()
        self._source_observations.clear()
        self._device = None
