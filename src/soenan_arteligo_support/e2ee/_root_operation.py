from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeCrypto, E2eeError, decode, wipe
from ._owner_projection import original_certificate_digest
from ._owner_protocol import ROOT_FIELDS, SignedEvidence, canonical_digest, object_value
from ._owner_sources import OriginalAdmissionCertificate, OriginalIssuerAdmission
from ._root_admission import RootAdmissionProof
from ._trust import _RootIdentity, public_device

if TYPE_CHECKING:
    from ._session import DeviceSession


@dataclass(frozen=True)
class ProposedRootReplacement:
    root: _RootIdentity
    admission: OriginalIssuerAdmission
    custody_revision: int

    @classmethod
    def create(
        cls, crypto: E2eeCrypto, previous: _RootIdentity, root: Mapping[str, Any],
        public: SignedEvidence, companion: RootAdmissionProof, device: Mapping[str, Any],
        custody_revision: int,
    ) -> ProposedRootReplacement:
        proposed = _RootIdentity.parse(previous.origin, previous.subject, dict(root))
        if (previous.generation >= 2**63 - 1 or proposed.generation != previous.generation + 1
                or proposed.identifier == previous.identifier
                or proposed.encryption_key == previous.encryption_key
                or proposed.signing_key == previous.signing_key
                or type(custody_revision) is not int or not 0 <= custody_revision < 2**63 - 1):
            raise E2eeError("owner_custody_changed")
        identity = public_device(device)
        if (identity["account_subject"] != previous.subject or public.device_id != identity["device_id"]
                or public.body.get("account_subject") != previous.subject
                or any(public.body.get(name) != root[name] for name in ROOT_FIELDS)
                or companion.root != {name: root[name] for name in ROOT_FIELDS}
                or companion.command.body.get("device") != identity):
            raise E2eeError("invalid_recovery_replacement")
        public.verify(crypto, identity["signing_public_key"], "recovery_public")
        certificates = tuple(sorted({
            OriginalAdmissionCertificate(identity["device_id"], original_certificate_digest(crypto, {
                "operation": "recovery_public", "signed_command": public.document(),
            })),
            OriginalAdmissionCertificate(identity["device_id"], original_certificate_digest(crypto, {
                "operation": "device_add_by_key", "signed_command": companion.command.document(),
            })),
        }, key=lambda item: (item.device_id, item.certificate_digest)))
        return cls(proposed, OriginalIssuerAdmission(proposed, public.digest(crypto, "recovery_public"), certificates),
                   custody_revision + 1)

    def custody_fields(self) -> dict[str, Any]:
        return {"recovery_id": self.root.identifier, "recovery_generation": self.root.generation,
                "root_revision": self.root.generation, "custody_revision": self.custody_revision}


class ProtectedRootDependencies:
    def __init__(self, crypto: E2eeCrypto, subject: str):
        self.crypto, self.subject = crypto, subject
        self.targets: dict[str, dict[str, Any]] = {}
        self.references: dict[str, dict[str, Any]] = {}
        self._visited: set[tuple[str, str | None, str | None, str]] = set()
        self._subjects: dict[str, str] = {}

    @classmethod
    def _public_reference(cls, value: Any) -> Any:
        if isinstance(value, Mapping):
            private = {"secret", "secret_key", "encryption_secret_key", "signing_secret_key", "gate_private_key", "key", "code"}
            return {name: cls._public_reference(item) for name, item in value.items() if name not in private}
        if isinstance(value, (list, tuple)):
            return [cls._public_reference(item) for item in value]
        return value

    def _index_devices(self, value: Any) -> None:
        if isinstance(value, (list, tuple)):
            for item in value:
                self._index_devices(item)
        elif isinstance(value, Mapping):
            if isinstance(value.get("device_id"), str) and isinstance(value.get("account_subject"), str):
                previous = self._subjects.get(value["device_id"])
                if previous is not None and previous != value["account_subject"]:
                    raise E2eeError("account_mismatch")
                self._subjects[value["device_id"]] = value["account_subject"]
            encoded = "body_bytes" if set(value) == {"device_id", "body_bytes", "signature"} else (
                "document_bytes" if set(value) == {"document_bytes"} else None)
            if encoded is not None:
                raw = decode(value[encoded])
                try:
                    self._index_devices(json.loads(raw))
                finally:
                    wipe(raw)
            else:
                for item in value.values():
                    self._index_devices(item)

    def _put(self, collection: dict[str, dict[str, Any]], value: dict[str, Any]) -> None:
        collection[canonical_digest(self.crypto, value)] = value

    def target(self, subject: str, organization: str | None, scope: str | None,
               purpose: str, origin: str) -> None:
        if not subject:
            raise E2eeError("invalid_owner_evidence")
        self._put(self.targets, {"account_subject": subject, "organization_id": organization,
                  "scope_id": scope, "purpose": purpose, "origin_reference": origin})

    def reference(self, kind: str, subject: str, organization: str | None, digest: str,
                  origin: str, **fields: Any) -> None:
        if not isinstance(digest, str) or not digest:
            raise E2eeError("invalid_owner_evidence")
        self._put(self.references, {"kind": kind, "account_subject": subject,
                  "organization_id": organization, "digest": digest, "origin_reference": origin, **fields})

    def collect(self, value: Any, *, organization: str | None = None, scope: str | None = None,
                purpose: str = "retained_binding_issuer", subject: str | None = None) -> None:
        if isinstance(value, (list, tuple)):
            for item in value:
                self.collect(item, organization=organization, scope=scope, purpose=purpose, subject=subject)
            return
        if not isinstance(value, Mapping):
            return
        value = dict(value)
        organization = value.get("organization_id", value.get("owner_org", organization))
        scope = value.get("scope_id", value.get("project_id", scope))
        subject = value.get("account_subject", subject)
        if set(value) == {"device_id", "body_bytes", "signature"}:
            signed = SignedEvidence.parse(value)
            issuer = self._subjects.get(signed.device_id, subject or self.subject)
            origin = canonical_digest(self.crypto, signed.document())
            self.target(issuer, organization, scope, purpose, origin)
            self.collect(signed.body, organization=organization, scope=scope, purpose=purpose, subject=issuer)
            return
        if set(value) == {"document_bytes"}:
            raw = decode(value["document_bytes"])
            try:
                self.collect(object_value(json.loads(raw)), organization=organization, scope=scope,
                             purpose="source_creator", subject=subject)
            except (ValueError, TypeError):
                raise E2eeError("invalid_owner_evidence") from None
            finally:
                wipe(raw)
            return
        origin = canonical_digest(self.crypto, self._public_reference(value))
        identity = (origin, organization, scope, purpose)
        if identity in self._visited:
            return
        self._visited.add(identity)
        if isinstance(subject, str) and subject:
            if isinstance(value.get("device_id"), str):
                self._subjects[value["device_id"]] = subject
            self.target(subject, organization, scope, purpose, origin)
        for name in ("root_evidence_digest", "issuer_root_evidence_digest", "evidence_digest"):
            if isinstance(value.get(name), str):
                self.reference("custody_evidence", subject or self.subject, organization, value[name], origin)
        for name in ("binding_digest", "source_binding_digest", "successor_binding_digest"):
            if organization and isinstance(value.get(name), str) and value[name]:
                self.reference("selected_binding", subject or self.subject, organization, value[name], origin)
        if organization:
            receipts = value.get("receipts", ())
            if isinstance(receipts, (list, tuple, dict)):
                for identifier in receipts:
                    if isinstance(identifier, str):
                        self.reference("transfer_decision", subject or self.subject, organization, identifier, origin)
            if isinstance(value.get("operation_id"), str) and (
                "source_manifest_id" in value or "manifest_id" in value or "candidate_offer_digest" in value
            ):
                self.reference("transfer_decision", subject or self.subject, organization, value["operation_id"], origin)
        if value.get("operation") == "account_signature_projection":
            projection = object_value(value.get("signature_projection"))
            self.reference("certificate_projection", projection["witness_subject"], organization,
                           projection["certificate_digest"], origin)
        elif value.get("operation") in {"bootstrap", "device_approve", "device_add_by_key", "recovery_public", "envelopes_save"} and "signed_command" in value:
            signed = SignedEvidence.parse(value["signed_command"])
            issuer = self._subjects.get(signed.device_id, subject or self.subject)
            self.reference("certificate_projection", issuer, organization,
                           original_certificate_digest(self.crypto, value), origin,
                           original_certificate=value)
        for certificate in value.get("certificates", []):
            if isinstance(certificate, Mapping) and "certificate_digest" in certificate:
                self.reference("certificate_projection", self._subjects.get(certificate.get("device_id"), subject or self.subject),
                               organization, certificate["certificate_digest"], origin)
        for name, item in value.items():
            if name in {"secret_key", "encryption_secret_key", "signing_secret_key", "key", "code"}:
                continue
            selected = ("source_creator" if name in {"creator_device", "creator", "creation_command"} else
                        "peer_trust_issuer" if name in {"peer_trust", "owner_confirmations", "confirmed_sources", "source_anchor"} else
                        "pending_command_issuer" if name in {"journal", "saved_command", "key_registration"} else purpose)
            self.collect(item, organization=organization, scope=scope, purpose=selected, subject=subject)

    def document(self) -> dict[str, Any]:
        references = []
        for key in sorted(self.targets):
            target = self.targets[key]
            references.append({**{name: value for name, value in target.items()
                                  if name != "purpose" and value is not None}, "kind": target["purpose"]})
        retained = {}
        for key in sorted(self.references):
            reference = self.references[key]
            if reference["kind"] == "selected_binding":
                value = {"organization_id": reference["organization_id"], "binding_digest": reference["digest"]}
                retained[(value["organization_id"], value["binding_digest"])] = value
                continue
            field = {"custody_evidence": "root_evidence_digest", "transfer_decision": "transfer_operation_id",
                     "certificate_projection": "certificate_digest"}.get(reference["kind"])
            if field is not None:
                value = {"kind": "retained_binding_issuer", "account_subject": reference["account_subject"],
                         "origin_reference": reference["origin_reference"], field: reference["digest"]}
                if reference["organization_id"] is not None:
                    value["organization_id"] = reference["organization_id"]
                references.append(value)
        return {"references": references, "retained_bindings": list(retained.values()),
                "protected_sources": [], "pending_commands": []}

    @classmethod
    def for_session(cls, session: DeviceSession) -> dict[str, Any]:
        manifest = cls(session.crypto, session.subject)
        manifest._index_devices(session._device)
        manifest._index_devices(session.trust._state)
        manifest._index_devices(list(session._devices.values()))
        manifest._index_devices(list(session._scope_device_material.values()))
        manifest.target(session.subject, None, None, "actor", session.device_id)
        manifest.collect(session.public, purpose="actor")
        manifest.collect(session.recovery, purpose="actor")
        for device in session._devices.values():
            manifest.collect(device)
        manifest.collect(session.trust._state)
        manifest.collect(session.trust._endorsements, purpose="peer_trust_issuer")
        manifest.collect((session._device or {}).get("owner_source_observations", {}), purpose="source_creator")
        sources, pending = [], []
        known_devices = {value["device_id"]: value for value in (*session._devices.values(), *session._scope_device_material.values())}
        known_roots = {value["recovery_id"]: value for value in session.trust._recovery_proofs.values()}
        if session.recovery is not None:
            known_roots[session.recovery["recovery_id"]] = session.recovery
        for value in known_devices.values():
            manifest.collect(value)
        for value in known_roots.values():
            manifest.collect(value)
        for organization in session.owner_access.store.organizations():
            state = session.owner_access.store.get(organization)
            raw = (session._device or {}).get("owner_access", {}).get(organization, {})
            manifest.collect(raw, organization=organization)
            for saved in state.manifests.values():
                evidence = (saved.issuer_evidence.document() if saved.issuer_evidence is not None else
                            {"devices": list(known_devices.values()), "recoveries": list(known_roots.values())})
                for document in saved.manifest.require_documents():
                    sources.append({"organization_id": organization, "manifest_id": saved.manifest.body.manifest_id,
                                    "manifest_digest": saved.manifest.digest, "document": document.document(),
                                    "issuer_evidence": evidence})
            for command in (*state.journal.values(), *((state.registration,) if state.registration is not None else ())):
                pending.append({"operation": command.operation, "signed_command": command.command.document()})
        device = session._device or {}
        for collection in ("scope_rotations", "root_device_history"):
            for value in device.get(collection, {}).values():
                operation = value.get("operation", "rotate_scope" if collection == "scope_rotations" else "envelopes_save")
                command = SignedEvidence.parse(value.get("command"))
                pending.append({"operation": operation, "signed_command": command.document()})
                manifest.collect(command.document(), purpose="pending_command_issuer", subject=session.subject)
        replacement = device.get("recovery_replacement")
        if replacement is not None:
            manifest.collect(replacement, purpose="pending_command_issuer", subject=session.subject)
            pending.extend((
                {"operation": "recovery_rotate", "signed_command": replacement["saved_command"]["command"]},
                {"operation": "device_add_by_key", "signed_command": replacement["root_admission"]["signed_command"]},
            ))
        result = manifest.document()
        result["protected_sources"] = sources
        result["pending_commands"] = pending
        return result
