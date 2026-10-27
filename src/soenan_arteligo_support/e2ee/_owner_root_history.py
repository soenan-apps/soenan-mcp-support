from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Mapping


from ._crypto import E2eeError, encode, wipe
from ._owner_protocol import ROOT_FIELDS, SignedEvidence, authority_head, bytes32, canonical_digest, object_value
from ._owner_sources import OriginalIssuerAdmission, OwnerSourceEvidence
from ._owner_state import OwnerKey, RootProvenance
from ._trust import _RootIdentity

if TYPE_CHECKING:
    from ._owner_current import VerifiedCurrentDevice
    from ._owner_recovery import OwnerRecovery


@dataclass(frozen=True)
class RootHistoryContext:
    body: Mapping[str, Any]

    def document(self) -> dict[str, Any]:
        return {"v": 1, "domain": "arteligo.owner-custody-backup", "operation": "recovery_rotate",
                "binding": {name: value for name, value in self.body.items()
                            if name not in {"owner_access_snapshot", "public_command"}}}


@dataclass(frozen=True)
class ScopeGenerationReference:
    scope: str
    epoch: int
    digest: str

    @classmethod
    def parse(cls, value: Any) -> ScopeGenerationReference:
        value = object_value(value)
        if (set(value) != {"scope_id", "key_epoch", "generation_digest"}
                or not isinstance(value["scope_id"], str) or not value["scope_id"]
                or type(value["key_epoch"]) is not int or value["key_epoch"] < 1):
            raise E2eeError("invalid_owner_custody_backup")
        bytes32(value["generation_digest"])
        return cls(value["scope_id"], value["key_epoch"], value["generation_digest"])

    def document(self) -> dict[str, Any]:
        return {"scope_id": self.scope, "key_epoch": self.epoch, "generation_digest": self.digest}


@dataclass(frozen=True)
class RootHistorySnapshot:
    envelope: dict[str, str]
    owner_bindings_digest: str


class OwnerRootHistory:
    def __init__(self, recovery: OwnerRecovery):
        self.recovery, self.owner, self.session, self.crypto = recovery, recovery.owner, recovery.session, recovery.crypto

    def _root(self, body: Mapping[str, Any]) -> dict[str, Any]:
        return {"origin": self.session.trust.origin, "account_subject": self.session.subject,
                **{name: body[name] for name in ROOT_FIELDS}}

    def roots(self) -> list[dict[str, Any]]:
        roots = {root.identifier: root for root in self.owner.store.self_roots()}
        for value in self.session.trust._state["recovery"].values():
            if value["account_subject"] == self.session.subject:
                root = self.owner.verifier.root(value, self.session.subject)
                roots[root.identifier] = root
        if self.session.recovery is not None:
            root = self.owner.verifier.root(self.session.recovery, self.session.subject)
            roots[root.identifier] = root
        return [root.document() for root in sorted(roots.values(), key=lambda value: (value.generation, value.identifier))]

    def qualified(self) -> VerifiedCurrentDevice | None:
        organizations = {
            scope["owner_org"] for scope in self.session.scopes()
            if scope.get("owner_org") and scope["key_epoch"] > 0
            and scope["key_state"] in {"ready", "rekey_required"}
            and scope["lifecycle"] in {"active", "archived"}
        }
        for reference in (self.session.recovery or {}).get("owner_access_history", []):
            organization, digest = reference["organization_id"], reference["binding_digest"]
            self.selected(organization, digest)
        if not organizations:
            return None
        organization = sorted(organizations)[0]
        head = self.owner.reads.authority(organization, self.owner.reads.capability(organization))
        root = self.owner.verifier.root(self.session.recovery, self.session.subject)
        anchor = self.owner.current.independent_root(organization, self.session.public)
        return self.owner.current.qualify(organization, self.session.public, anchor, head, expected_root=root)

    def selected(self, organization: str, digest: str):
        proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=digest)
        head = authority_head(proof.get("owner_authority"), organization)
        return self.owner.reads.selected(organization, digest, capability=head.read_capability), proof

    def digest(self) -> str | None:
        root = self.session.recovery
        if root is None or root.get("owner_access_snapshot_command") is None:
            return None
        signed = SignedEvidence.parse(root["owner_access_snapshot_command"])
        public = SignedEvidence.parse(signed.body.get("public_command"))
        digest = canonical_digest(self.crypto, signed.body.get("owner_access_snapshot"))
        if (any(signed.body.get(name) != root[name] for name in ROOT_FIELDS)
                or public.body.get("owner_access_snapshot_digest") != digest):
            raise E2eeError("invalid_owner_custody_backup")
        return digest


    def verify_reference(self, root: _RootIdentity, digest: str) -> None:
        material = self.session._recovery_material(None, root.identifier)
        if material is None or self.owner.verifier.root(material, self.session.subject) != root:
            raise E2eeError("owner_root_proof_missing")
        public = None
        for certificate in material.get("certificates", []):
            if certificate.get("operation") != "recovery_public":
                continue
            candidate = SignedEvidence.parse(certificate["signed_command"])
            if (candidate.body.get("owner_access_snapshot_digest") == digest
                    and all(candidate.body.get(name) == root.document()[name] for name in ROOT_FIELDS)):
                public = candidate
                break
        if public is None:
            raise E2eeError("invalid_owner_custody_backup")
        admission = OriginalIssuerAdmission.parse(public.body.get("issuer_admission"))
        self.owner.current.historical_event("recovery_public", public, {
            "account_subject": self.session.subject, **{name: material[name] for name in ROOT_FIELDS}},
            admission.root)

    def _bindings(self, organizations: list[dict[str, Any]]) -> list[dict[str, str]]:
        values = {(item["organization_id"], key["binding_digest"])
                  for item in organizations for key in item["keys"]
                  if SignedEvidence.parse(key["binding_command"]).body["device"]["account_subject"] == self.session.subject}
        return [{"organization_id": organization, "binding_digest": digest}
                for organization, digest in sorted(values, key=lambda value: (value[0].encode(), value[1].encode()))]

    def seal(self, body: dict[str, Any], keys: Mapping[str, str], admission: OriginalIssuerAdmission,
             references: list[ScopeGenerationReference], qualified: VerifiedCurrentDevice | None) -> RootHistorySnapshot:
        organizations = []
        for organization in self.owner.store.organizations():
            state = self.owner.store.get(organization)
            if not state.keys:
                continue
            for key in state.keys:
                selected, _ = self.selected(organization, key.binding_digest)
                if key.public_binding() != {name: selected.head.to_dict()[name] for name in key.public_binding()}:
                    raise E2eeError("owner_keyring_mismatch")
            sources = self.recovery.source_evidence(organization, qualified=qualified)
            organizations.append({"organization_id": organization, "keys": [key.document() for key in state.keys],
                                  "source_evidence": sources.document()})
        bindings = self._bindings(organizations)
        digest = canonical_digest(self.crypto, bindings)
        if qualified is not None and digest != qualified.custody.owner_bindings_digest:
            raise E2eeError("owner_history_unavailable")
        payload = self.crypto.canonical({"v": 1, "account_subject": self.session.subject, "root": self._root(body),
            "self_roots": self.roots(), "issuer_admission": admission.document(), "owner_bindings": bindings,
            "organizations": organizations, "scope_generations": [reference.document() for reference in references]})
        aad = self.crypto.canonical(RootHistoryContext(body).document())
        try:
            sealed = self.crypto.execute({"op": "hpke_auth_seal", "sender_secret_key": keys["encryption_secret_key"],
                "recipient_public_key": body["encryption_public_key"], "plaintext": encode(payload),
                "info": encode(aad), "aad": encode(aad)})
            return RootHistorySnapshot({"encapsulated_key": sealed["enc"], "ciphertext": sealed["ciphertext"]}, digest)
        finally:
            wipe(payload)
            wipe(aad)

    def open(self, root: Mapping[str, Any], secret: str) -> tuple[SignedEvidence, SignedEvidence, dict[str, Any]]:
        signed = SignedEvidence.parse(root.get("owner_access_snapshot_command"))
        body, public = signed.body, SignedEvidence.parse(signed.body.get("public_command"))
        envelope = object_value(body.get("owner_access_snapshot"))
        if (any(body.get(name) != root[name] for name in ROOT_FIELDS)
                or public.device_id != signed.device_id or public.body.get("account_subject") != self.session.subject
                or any(public.body.get(name) != root[name] for name in ROOT_FIELDS)
                or public.body.get("owner_access_snapshot_digest") != canonical_digest(self.crypto, envelope)):
            raise E2eeError("invalid_owner_custody_backup")
        payload = self.recovery.open_custody(RootHistoryContext(body), envelope, secret, root["encryption_public_key"])
        required = {"v", "account_subject", "root", "self_roots", "issuer_admission", "owner_bindings", "organizations", "scope_generations"}
        if (set(payload) != required or payload["v"] != 1 or payload["account_subject"] != self.session.subject
                or payload["root"] != self._root(root) or any(not isinstance(payload[name], list)
                    for name in ("self_roots", "owner_bindings", "organizations", "scope_generations"))):
            raise E2eeError("invalid_owner_custody_backup")
        if (payload["issuer_admission"] != public.body.get("issuer_admission")
                or payload["owner_bindings"] != self._bindings(payload["organizations"])
                or canonical_digest(self.crypto, payload["owner_bindings"]) != public.body.get("owner_bindings_digest")):
            raise E2eeError("owner_history_unavailable")
        return signed, public, payload

    def restore(self, root_secret: str) -> None:
        root = self.session.recovery
        if root is None or root.get("owner_access_snapshot_command") is None:
            return
        signed, public, payload = self.open(root, root_secret)
        own_roots = RootProvenance.parse({"v": 1, "self_roots": payload["self_roots"]},
            self.session.trust.origin, self.session.subject).self_roots
        if any(value.generation >= root["generation"] for value in own_roots):
            raise E2eeError("invalid_owner_custody_backup")
        admission = OriginalIssuerAdmission.parse(payload["issuer_admission"])
        target = {"account_subject": self.session.subject, **{name: root[name] for name in ROOT_FIELDS}}
        verified = self.owner.current.historical_event("recovery_public", public, target, admission.root)
        if OriginalIssuerAdmission.parse(verified.evidence.issuer_admission.to_dict()) != admission:
            raise E2eeError("owner_custody_evidence_mismatch")
        trusted, provisional = RootProvenance(own_roots).partition(verified.authenticated_roots)
        staged, organizations = [], set()
        for item in payload["organizations"]:
            value = object_value(item)
            if set(value) != {"organization_id", "keys", "source_evidence"} or not isinstance(value["keys"], list):
                raise E2eeError("invalid_owner_custody_backup")
            organization = value["organization_id"]
            if not isinstance(organization, str) or not organization or organization in organizations:
                raise E2eeError("owner_keyring_mismatch")
            organizations.add(organization)
            keys = [OwnerKey.parse(key, organization, self.owner.capsules) for key in value["keys"]]
            if len({key.key_id for key in keys}) != len(keys) or len({key.key_epoch for key in keys}) != len(keys):
                raise E2eeError("owner_keyring_mismatch")
            sources = OwnerSourceEvidence.parse(self.crypto, value["source_evidence"], organization,
                origin=self.session.trust.origin)
            source_roots, source_provisional = RootProvenance(sources.self_roots).partition(verified.authenticated_roots)
            sources = replace(sources, self_roots=source_roots)
            trusted += source_roots
            provisional += source_provisional
            if [key.public_binding() for key in keys] != [reference.to_dict() for reference in sources.key_bindings]:
                raise E2eeError("owner_keyring_mismatch")
            for key in keys:
                selected, _ = self.selected(organization, key.binding_digest)
                if key.public_binding() != {name: selected.head.to_dict()[name] for name in key.public_binding()}:
                    raise E2eeError("owner_keyring_mismatch")
            staged.append((organization, keys, sources))
        references = [ScopeGenerationReference.parse(value) for value in payload["scope_generations"]]
        if len({(value.scope, value.epoch) for value in references}) != len(references):
            raise E2eeError("invalid_owner_custody_backup")
        issuer = self.session._historical_device_material(None, signed.device_id)
        if issuer["account_subject"] != self.session.subject:
            raise E2eeError("account_mismatch")
        signed.verify(self.crypto, issuer["signing_public_key"], "recovery_rotate")
        public.verify(self.crypto, issuer["signing_public_key"], "recovery_public")
        self.owner.store.retain_roots(trusted)
        for organization, keys, sources in staged:
            self.recovery.restore_frozen_sources(organization, sources, admission.root.document())
            for key in keys:
                selected, proof = self.selected(organization, key.binding_digest)
                self.owner.verifier.binding(organization, proof, selected.head, sources=sources)
            self.owner.keyring.merge(organization, keys)
        self.recovery._retain_provisional_roots(provisional)
        self.session._device["root_scope_generations"] = {"root": self._root(root),
            "operation": "recovery_rotate", "evidence_digest": signed.digest(self.crypto, "recovery_rotate"),
            "references": [reference.document() for reference in references]}
        self.session._persist()

    def matches_generation(self, generation, command: SignedEvidence, operation: str) -> bool:
        saved = (self.session._device or {}).get("root_scope_generations")
        if (saved is None or self.session.recovery is None or saved["root"] != self._root(self.session.recovery)
                or saved.get("operation") != operation
                or saved.get("evidence_digest") != command.digest(self.crypto, operation)):
            return False
        digest = canonical_digest(self.crypto, {"operation": generation.operation, "signed_command": generation.command.document()})
        return ScopeGenerationReference(generation.scope, generation.epoch, digest).document() in saved["references"]
