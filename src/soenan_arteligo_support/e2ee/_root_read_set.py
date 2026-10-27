from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Mapping

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_protocol import SignedEvidence, authority_head, bytes32, canonical_digest, object_value
from ._owner_sources import OwnerIssuerEvidence
from ._trust import public_device

if TYPE_CHECKING:
    from ._session import DeviceSession


CONTEXT_READS = frozenset({
    "e2eeGetRecovery", "e2eeListDevices", "e2eeGetMemberDevices", "e2eeGetScope",
    "e2eeGetRecipients", "e2eeGetScopeRecoveryRoots", "e2eeGetEnvelopes", "e2eeGetEpochs",
    "e2eeGetScopeParticipantProofs", "e2eeGetOwnerGeneration", "e2eeGetTrust",
    "e2eeGetOwnerAuthority", "e2eeGetOwnerBinding", "e2eeGetOwnerCustody",
    "e2eeGetOwnerInventory", "e2eeGetOwnerCandidates", "e2eeGetOwnerKeyring",
    "e2eeGetOwnerManifest", "e2eeGetOwnerManifestDocuments", "e2eeGetProjectOwnerSourceEvidence",
    "e2eeGetOwnerPreparation",
})


@dataclass(frozen=True)
class RootReadSet:
    operation_id: str
    key_state_digest: str
    read_set_digest: str
    preparation_digest: str
    dependency_manifest: dict[str, Any]
    recovery: dict[str, Any]
    devices: tuple[dict[str, Any], ...]
    scopes: Mapping[str, dict[str, Any]]
    owners: Mapping[str, dict[str, Any]]
    proof_context: str
    prior_recoveries: tuple[dict[str, Any], ...] = ()
    issuer_evidence: dict[str, Any] = field(default_factory=lambda: {"devices": [], "recoveries": []})
    actor_subject: str = ""

    @classmethod
    def receive(cls, operation_id: str, events: Iterable[dict[str, Any]]) -> RootReadSet:
        digest = hashlib.sha256()
        header = recovery = proof = complete = None
        devices: dict[str, dict[str, Any]] = {}
        scopes: dict[str, dict[str, Any]] = {}
        owners: dict[str, dict[str, Any]] = {}
        graph: dict[str, dict[str, dict[str, Any]]] = {"devices": {}, "recoveries": {}}
        count = 0
        for event in events:
            if (complete is not None or event.get("operation_id") != operation_id
                    or type(event.get("sequence")) is not int or event["sequence"] != count):
                raise E2eeError("invalid_key_operation_stream")
            kind = event.get("kind")
            if kind == "complete":
                complete = event
                if event.get("event_count") != count or event.get("read_set_digest") != encode(digest.digest()):
                    raise E2eeError("invalid_key_operation_stream")
                continue
            raw = decode(event.get("event_bytes"))
            try:
                if json.loads(raw) != {key: value for key, value in event.items() if key != "event_bytes"}:
                    raise E2eeError("invalid_key_operation_stream")
                digest.update(raw)
            finally:
                wipe(raw)
            if count == 0 and kind != "header":
                raise E2eeError("invalid_key_operation_stream")
            if kind == "header" and header is None:
                header = event
            elif kind == "recovery" and recovery is None:
                recovery = object_value(event.get("recovery"))
            elif kind == "proof_context" and proof is None:
                proof = event
            elif kind == "device":
                device = object_value(event.get("device"))
                identifier = device["device_id"]
                if identifier in devices:
                    raise E2eeError("invalid_key_operation_stream")
                devices[identifier] = device
            elif kind == "scope":
                scope = object_value(event.get("scope"))
                identifier = object_value(scope.get("scope"))["project_id"]
                if identifier in scopes:
                    raise E2eeError("invalid_key_operation_stream")
                scopes[identifier] = scope
            elif kind == "owner":
                owner = object_value(event.get("owner"))
                identifier = owner["organization_id"]
                if identifier in owners:
                    raise E2eeError("invalid_key_operation_stream")
                owners[identifier] = owner
            elif kind == "issuer_evidence":
                evidence = object_value(event.get("issuer_evidence"))
                for name, key in (("devices", "device_id"), ("recoveries", "recovery_id")):
                    for value in evidence[name]:
                        previous = graph[name].get(value[key])
                        if previous is not None and previous != value:
                            raise E2eeError("invalid_key_operation_stream")
                        graph[name][value[key]] = value
            else:
                raise E2eeError("invalid_key_operation_stream")
            count += 1
        if any(item is None for item in (header, recovery, proof, complete)):
            raise E2eeError("incomplete_key_operation_stream")
        for value in (header["key_state_digest"], complete["read_set_digest"], proof["preparation_digest"]):
            bytes32(value)
        return cls(operation_id, header["key_state_digest"], complete["read_set_digest"],
                   proof["preparation_digest"], object_value(header["dependency_manifest"]), recovery,
                   tuple(devices.values()), scopes, owners, proof["proof_context"],
                   issuer_evidence={name: list(value.values()) for name, value in graph.items()})

    def document(self) -> dict[str, Any]:
        return {"operation_id": self.operation_id, "key_state_digest": self.key_state_digest,
                "read_set_digest": self.read_set_digest, "preparation_digest": self.preparation_digest,
                "dependency_manifest": self.dependency_manifest, "recovery": self.recovery,
                "devices": list(self.devices), "scopes": dict(self.scopes), "owners": dict(self.owners),
                "proof_context": self.proof_context, "prior_recoveries": list(self.prior_recoveries),
                "issuer_evidence": self.issuer_evidence, "actor_subject": self.actor_subject}

    @classmethod
    def parse(cls, value: Any) -> RootReadSet:
        value = object_value(value)
        return cls(value["operation_id"], value["key_state_digest"], value["read_set_digest"],
                   value["preparation_digest"], value["dependency_manifest"], value["recovery"],
                   tuple(value["devices"]), value["scopes"], value["owners"], value["proof_context"],
                   tuple(value.get("prior_recoveries", [])), value.get("issuer_evidence", {"devices": [], "recoveries": []}),
                   value.get("actor_subject", ""))

    @classmethod
    def from_context(cls, session: DeviceSession, value: Any) -> RootReadSet:
        from ._key_operation_proof import OperationProofContext

        value = object_value(value)
        if value.get("actor_subject") != session.subject:
            raise E2eeError("operation_proof_context_mismatch")
        for name in ("read_set_digest", "key_state_digest"):
            bytes32(value.get(name))
        scopes, owners, devices = {}, {}, {}
        for collection, scope_field, target in (("scopes", "scope", scopes), ("owners", None, owners), ("devices", None, devices)):
            items = value.get(collection)
            if not isinstance(items, list):
                raise E2eeError("operation_proof_context_missing")
            for item in items:
                item = object_value(item)
                identifier = (object_value(item.get(scope_field))["project_id"] if scope_field else
                              item["organization_id"] if collection == "owners" else item["device_id"])
                if identifier in target:
                    raise E2eeError("operation_proof_context_mismatch")
                target[identifier] = item
        wire = value.get("proof_context", "")
        proof = OperationProofContext.from_wire(session, wire) if wire else None
        if proof is not None:
            proof.require_identity(session, value["operation_id"])
            if proof.context.get("key_state_digest") != value["key_state_digest"]:
                raise E2eeError("operation_proof_context_mismatch")
        manifest = object_value(value.get("manifest", {}))
        if proof is not None and proof.context.get("manifest_digest") != canonical_digest(session.crypto, manifest):
            raise E2eeError("operation_proof_context_mismatch")
        return cls(value["operation_id"], value["key_state_digest"], value["read_set_digest"],
                   proof.digest if proof is not None else "", manifest, value.get("recovery", {}),
                   tuple(devices.values()), scopes, owners, wire,
                   issuer_evidence=value.get("issuer_evidence", {"devices": [], "recoveries": []}),
                   actor_subject=value["actor_subject"])

    @cached_property
    def historical_evidence(self) -> OwnerIssuerEvidence:
        devices: dict[str, dict[str, Any]] = {}
        roots: dict[str, dict[str, Any]] = {}
        graphs = [self.issuer_evidence, *(
            proof["issuer_evidence"] for owner in self.owners.values() for proof in owner["bindings"]
        ), *({"devices": scope["devices"], "recoveries": scope["recoveries"]} for scope in self.scopes.values()),
            {"devices": self.devices, "recoveries": [*self.prior_recoveries, *([self.recovery] if self.recovery else [])]}]
        for graph in graphs:
            for value in graph["devices"]:
                identifier = value["device_id"]
                previous = devices.get(identifier)
                if previous is not None:
                    if public_device(previous) != public_device(value):
                        raise E2eeError("device_key_changed")
                    certificates = list(previous.get("certificates", []))
                    certificates.extend(item for item in value.get("certificates", []) if item not in certificates)
                    value = {**value, "certificates": certificates}
                devices[identifier] = value
            for value in graph["recoveries"]:
                identifier = value["recovery_id"]
                previous = roots.get(identifier)
                if previous is not None and any(previous.get(name) != value.get(name)
                    for name in ("generation", "encryption_public_key", "signing_public_key")):
                    raise E2eeError("recovery_key_changed")
                if previous is not None:
                    if (previous.get("account_subject") is not None and value.get("account_subject") is not None
                            and previous["account_subject"] != value["account_subject"]):
                        raise E2eeError("recovery_subject_mismatch")
                    certificates = list(previous.get("certificates", []))
                    certificates.extend(item for item in value.get("certificates", []) if item not in certificates)
                    value = {**value, "certificates": certificates}
                roots[identifier] = value
        return OwnerIssuerEvidence(devices, roots)

    def settled(self, result: Mapping[str, Any]) -> RootReadSet:
        if any(not isinstance(result.get(name), list) for name in ("devices", "settled_scopes", "settled_owners")):
            raise E2eeError("recovery_replacement_pending")
        scopes = {value["scope"]["project_id"]: value for value in result["settled_scopes"]}
        owners = {value["organization_id"]: value for value in result["settled_owners"]}
        devices = {value["device_id"]: value for value in result["devices"]}
        if (len(scopes) != len(result["settled_scopes"]) or len(owners) != len(result["settled_owners"])
                or len(devices) != len(result["devices"])):
            raise E2eeError("invalid_key_operation_stream")
        return replace(self, recovery=object_value(result.get("recovery")), devices=tuple(devices.values()),
                       scopes=scopes, owners=owners, prior_recoveries=(*self.prior_recoveries, self.recovery))

    def remember(self, session: DeviceSession, proof: Any) -> None:
        if proof is not None:
            for subject, value in proof.subjects.items():
                if value["outcome"] == "available":
                    session.trust.observe_custody_revocations(subject, value["revoked_device_ids"])
        session._remember_device_material(None, list(self.devices))
        for identifier, value in self.scopes.items():
            session._participants.forget_scope(identifier)
            session._adopt_scope(identifier, session._scope_owner(identifier), value["scope"])
            session._key_bundles[identifier] = {"envelopes": value["envelopes"], "epochs": value["epoch_links"]}
            session._remember_device_material(identifier, value["devices"])
            session.trust.remember_recoveries(value["recoveries"], identifier)
            for participant in value["participant_proofs"]:
                subject = participant.get("account_subject")
                if subject is not None:
                    session._participants._proofs.setdefault((identifier, subject), []).append(participant)

    @contextmanager
    def use(self, session: DeviceSession, proof: Any) -> Iterator[None]:
        if session._root_read_set is not None:
            raise E2eeError("root_replacement_in_progress")
        session._proof_read_set = None
        session._root_read_set = self
        session.owner_access.reads._operation = proof
        try:
            yield
        finally:
            session._root_read_set = None
            session.owner_access.reads._operation = None
            for identifier in self.scopes:
                session._participants.forget_scope(identifier)

    def device(self, scope: str | None, identifier: str) -> dict[str, Any]:
        values = self.devices if scope is None else self.scope(scope)["devices"]
        selected = next((value for value in values if value["device_id"] == identifier), None)
        if selected is None:
            raise E2eeError("root_replacement_dependency_missing")
        return selected

    def root(self, scope: str | None, identifier: str) -> dict[str, Any]:
        roots = ([self.recovery, *self.historical_evidence.recoveries.values()]
                 if scope is None else [*self.scope(scope)["recoveries"], *self.historical_evidence.recoveries.values()])
        subject = self.actor_subject or (self.devices[0]["account_subject"] if self.devices else self.recovery.get("account_subject"))
        selected = next((value for value in roots if value.get("recovery_id") == identifier
                         and (scope is not None or value.get("account_subject", subject) == subject)), None)
        if selected is None:
            raise E2eeError("root_replacement_dependency_missing")
        return selected

    def scope(self, identifier: str) -> dict[str, Any]:
        if identifier not in self.scopes:
            raise E2eeError("root_replacement_dependency_missing")
        return self.scopes[identifier]

    def owner(self, identifier: str) -> dict[str, Any]:
        if identifier not in self.owners:
            raise E2eeError("root_replacement_dependency_missing")
        return self.owners[identifier]

    def read(self, operation: str, **parameters: Any) -> dict[str, Any]:
        scope = parameters.get("scope_id")
        organization = parameters.get("organization_id")
        if operation == "e2eeGetRecovery":
            return self.recovery
        if operation in {"e2eeListOrganizations", "e2eeListProjects"}:
            organization_only = operation == "e2eeListOrganizations"
            return {"projects": [value["scope"] for key, value in self.scopes.items()
                                 if (key == value["scope"].get("owner_org")) == organization_only]}
        if operation in {"e2eeListDevices", "e2eeGetMemberDevices"}:
            values = self.devices if scope is None else self.scope(scope)["devices"]
            identifier = parameters.get("device_id")
            return {"devices": [value for value in values if identifier is None or value["device_id"] == identifier]}
        if operation == "e2eeGetScope":
            return self.scope(scope)["scope"]
        if operation == "e2eeGetRecipients":
            return self.scope(scope)["recipients"]
        if operation == "e2eeGetScopeRecoveryRoots":
            identifier = parameters.get("recovery_id")
            return {"recoveries": [value for value in self.scope(scope)["recoveries"]
                                   if identifier is None or value["recovery_id"] == identifier]}
        if operation == "e2eeGetEnvelopes":
            fields = {"epoch": "key_epoch", "recipient_id": "recipient_id", "recipient_kind": "recipient_kind"}
            return {"envelopes": [value for value in self.scope(scope)["envelopes"]
                                  if all(value.get(field) == parameters[name] for name, field in fields.items()
                                         if parameters.get(name) is not None)]}
        if operation == "e2eeGetEpochs":
            return {"epochs": [value for value in self.scope(scope)["epoch_links"]
                               if value["key_epoch"] > parameters.get("after_epoch", 0)]}
        if operation == "e2eeGetScopeParticipantProofs":
            value = self.scope(scope)
            source = value.get("participant_source")
            source_scope = parameters.get("source_scope_id")
            if source_scope is not None:
                if not isinstance(source, dict) or source.get("scope_id") != source_scope:
                    raise E2eeError("participant_scope_mismatch")
                proofs = value.get("source_participant_proofs")
                if not isinstance(proofs, list):
                    raise E2eeError("root_replacement_dependency_missing")
            else:
                proofs = value["participant_proofs"]
            after = parameters.get("after_request_id")
            limit = parameters.get("limit", 256)
            if type(limit) is not int or limit < 1:
                raise E2eeError("invalid_cursor")
            selected = sorted((proof for proof in proofs
                if proof.get("account_subject") == parameters.get("account_subject")
                and (after is None or proof["request_id"] > after)), key=lambda proof: proof["request_id"])
            page = selected[:limit]
            return {"proofs": page, "next_after": page[-1]["request_id"] if len(selected) > limit else None,
                    **({"source": source} if source is not None else {})}
        if operation == "e2eeGetOwnerGeneration":
            value = next((value for value in self.scope(scope)["generations"]
                          if value["key_epoch"] == parameters["epoch"]), None)
            if value is None:
                raise E2eeError("owner_generation_proof_missing")
            return value
        if operation == "e2eeGetTrust":
            return {"statements": [value for item in self.scopes.values() for value in item["trust_statements"]]}
        if operation in {"e2eeGetOwnerAuthority", "e2eeGetOwnerBinding"}:
            owner = self.owner(organization)
            head = authority_head(owner["authority"], organization)
            digest = parameters.get("binding_digest", head.binding_digest)
            value = next((value for value in owner["bindings"]
                          if value["owner_authority"]["binding_digest"] == digest), None)
            if value is None:
                if not digest:
                    return {"owner_authority": head.to_dict()}
                raise E2eeError("root_replacement_dependency_missing")
            return value
        if operation == "e2eeGetOwnerInventory":
            return self.owner(organization)["inventory"]
        if operation == "e2eeGetOwnerCandidates":
            return {"candidates": self.owner(organization)["candidates"]}
        if operation == "e2eeGetOwnerKeyring":
            return self.owner(organization)["keyring"]
        if operation in {"e2eeGetOwnerManifest", "e2eeGetOwnerManifestDocuments"}:
            collection = "manifests" if operation == "e2eeGetOwnerManifest" else "manifest_bundles"
            values = self.owner(organization).get(collection, [])
            if operation == "e2eeGetOwnerManifestDocuments":
                value = next((value["bundle"] for value in values if value["manifest_id"] == parameters["manifest_id"]), None)
            else:
                value = next((value for value in values
                              if SignedEvidence.parse(value["signed_command"]).body["manifest_id"] == parameters["manifest_id"]), None)
            if value is not None:
                return value
        if operation == "e2eeGetProjectOwnerSourceEvidence":
            value = next((value for owner in self.owners.values() for value in owner["sources"]
                          if value["manifest_id"] == parameters["manifest_id"]
                          and self._source_scope(value) == scope), None)
            if value is not None:
                return value
        if operation == "e2eeGetOwnerPreparation":
            value = next((value for value in self.owner(organization)["preparations"]
                          if SignedEvidence.parse(value["signed_command"]).body["preparation_id"] == parameters["preparation_id"]), None)
            if value is not None:
                return value
        raise E2eeError("root_replacement_dependency_missing")

    @staticmethod
    def _source_scope(value: Mapping[str, Any]) -> str:
        raw = decode(value["document"]["document_bytes"])
        try:
            return object_value(json.loads(raw))["project_id"]
        finally:
            wipe(raw)
