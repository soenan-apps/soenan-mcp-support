from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Mapping, TypeVar

from account_public_api_client.models.owner_authority_head import OwnerAuthorityHead
from account_public_api_client.models.owner_authority_head_state import OwnerAuthorityHeadState
from account_public_api_client.models.owner_handoff_gate import OwnerHandoffGate
from account_public_api_client.models.owner_transfer_decision import OwnerTransferDecision
from account_public_api_client.models.owner_transfer_decision_state import OwnerTransferDecisionState
from arteligo_public_api_client.models.e2_ee_owner_candidate_offer import E2EeOwnerCandidateOffer
from arteligo_public_api_client.models.e2_ee_owner_committed_export_reference import E2EeOwnerCommittedExportReference
from arteligo_public_api_client.models.e2_ee_owner_custody import E2EeOwnerCustody
from arteligo_public_api_client.models.e2_ee_owner_key_registration import E2EeOwnerKeyRegistration
from arteligo_public_api_client.models.e2_ee_owner_preparation import E2EeOwnerPreparation
from arteligo_public_api_client.models.e2_ee_owner_source_manifest import E2EeOwnerSourceManifest
from arteligo_public_api_client.models.e2_ee_owner_source_project import E2EeOwnerSourceProject

from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe
from ._trust import public_device

if TYPE_CHECKING:
    from ._owner_sources import OriginalIssuerAdmission


class OwnerOperation(str, Enum):
    REGISTER_KEY = "owner_key_register"
    OFFER = "owner_candidate_offer"
    INVALIDATE = "owner_custody_invalidate"
    KEYRING = "owner_keyring_save"
    MANIFEST = "owner_source_manifest"
    GATE = "owner_gate_create"
    PREPARE = "owner_handoff_prepare"
    ENVELOPES = "owner_envelopes_save"
    ROTATE = "owner_rotate_scope"
    ORDINARY_ENVELOPES = "envelopes_save"

    def __str__(self) -> str:
        return str(self.value)


class OwnerDomain(str, Enum):
    EVIDENCE = "arteligo-owner-evidence-v1"
    KEYRING = "arteligo.owner-keyring"
    INNER = "arteligo.owner-handoff.inner"
    OUTER = "arteligo.owner-handoff.outer"
    PROJECT_KEY = "arteligo-owner-source-project-key-v1"
    SOURCE_DOCUMENT = "arteligo-owner-source-document-v1"

    def __str__(self) -> str:
        return str(self.value)


KEY_BYTES = 32
ROOT_FIELDS = ("recovery_id", "generation", "encryption_public_key", "signing_public_key")
GENERATION_BLOCKERS = frozenset({"owner_key_generation_stale", "owner_generation_proof_missing"})


T = TypeVar("T")


def object_value(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise E2eeError("invalid_owner_evidence")
    return value


def parse_model(parser: Callable[[Mapping[str, Any]], T], value: Any) -> T:
    try:
        return parser(object_value(value))
    except (KeyError, TypeError, ValueError, AttributeError):
        raise E2eeError("invalid_owner_evidence") from None


def bytes32(value: Any) -> None:
    if not isinstance(value, str):
        raise E2eeError("invalid_owner_evidence")
    raw = decode(value)
    try:
        if len(raw) != KEY_BYTES or encode(raw) != value:
            raise E2eeError("invalid_owner_evidence")
    finally:
        wipe(raw)


def canonical_digest(crypto: E2eeCrypto, value: Any) -> str:
    raw = crypto.canonical(value)
    try:
        return encode(hashlib.sha256(raw).digest())
    finally:
        wipe(raw)


@dataclass(frozen=True)
class SignedEvidence:
    device_id: str
    body_bytes: str
    signature: str
    body: dict[str, Any]

    @classmethod
    def parse(cls, value: Any) -> SignedEvidence:
        document = object_value(value)
        if set(document) != {"device_id", "body_bytes", "signature"} or any(
            not isinstance(item, str) or not item for item in document.values()
        ):
            raise E2eeError("invalid_owner_evidence")
        raw = decode(document["body_bytes"])
        try:
            body = object_value(json.loads(raw))
        except (ValueError, TypeError):
            raise E2eeError("invalid_owner_evidence") from None
        finally:
            wipe(raw)
        return cls(document["device_id"], document["body_bytes"], document["signature"], body)

    def document(self) -> dict[str, str]:
        return {"device_id": self.device_id, "body_bytes": self.body_bytes, "signature": self.signature}

    def digest(self, crypto: E2eeCrypto, operation: str) -> str:
        raw = crypto.canonical(self.document())
        try:
            prefix = f"{OwnerDomain.EVIDENCE}\n{operation}\n".encode()
            return encode(hashlib.sha256(prefix + raw).digest())
        finally:
            wipe(raw)

    def verify(self, crypto: E2eeCrypto, public_key: str, operation: str) -> None:
        crypto.verify(public_key, operation, self.document())


def authority_head(value: Any, organization: str) -> OwnerAuthorityHead:
    head = parse_model(OwnerAuthorityHead.from_dict, value)
    if (head.organization_id != organization
            or type(head.ownership_revision) is not int or head.ownership_revision < 0
            or type(head.key_epoch) is not int or head.key_epoch < 0
            or not isinstance(head.owner_subject, str) or not head.owner_subject
            or not isinstance(head.read_capability, str) or not head.read_capability):
        raise E2eeError("invalid_owner_authority")
    if head.state != OwnerAuthorityHeadState.UNPROVISIONED:
        bytes32(head.public_key)
        bytes32(head.binding_digest)
        if not isinstance(head.key_id, str) or not head.key_id or head.key_epoch < 1:
            raise E2eeError("invalid_owner_authority")
    return head


def require_active(head: OwnerAuthorityHead) -> OwnerAuthorityHead:
    if head.state != OwnerAuthorityHeadState.ACTIVE:
        raise E2eeError("owner_rotation_required")
    return head


def custody(value: Any) -> E2EeOwnerCustody:
    result = parse_model(E2EeOwnerCustody.from_dict, value)
    if (not isinstance(result.recovery_id, str) or not result.recovery_id
            or any(type(number) is not int or number < 1 for number in (
                result.recovery_generation, result.root_revision,
            )) or type(result.custody_revision) is not int or result.custody_revision < 0
            or result.root_revision != result.recovery_generation):
        raise E2eeError("owner_custody_changed")
    return result


@dataclass(frozen=True)
class OwnerBinding:
    command: SignedEvidence
    body: E2EeOwnerCandidateOffer | E2EeOwnerKeyRegistration
    operation: OwnerOperation
    original_admission: OriginalIssuerAdmission

    @classmethod
    def parse(cls, value: Any) -> OwnerBinding:
        from ._owner_sources import OriginalIssuerAdmission

        command = SignedEvidence.parse(value)
        if "candidate_id" in command.body:
            operation = OwnerOperation.OFFER
            body = parse_model(E2EeOwnerCandidateOffer.from_dict, command.body)
            numbers = (body.recovery_generation, body.root_revision)
            subject = body.account_subject
            if body.root_revision != body.recovery_generation:
                raise E2eeError("invalid_owner_evidence")
        else:
            operation = OwnerOperation.REGISTER_KEY
            body = parse_model(E2EeOwnerKeyRegistration.from_dict, command.body)
            numbers = (body.recovery_generation,)
            subject = body.device.account_subject
            if (type(body.expected_ownership_revision) is not int or body.expected_ownership_revision < 0
                    or type(body.expected_key_epoch) is not int or body.expected_key_epoch < 0):
                raise E2eeError("invalid_owner_evidence")
        device = public_device(body.device.to_dict())
        root = body.recovery_root
        if (command.device_id != device["device_id"] or device["account_subject"] != subject
                or body.recovery_id != root.recovery_id or body.recovery_generation != root.generation
                or type(body.custody_revision) is not int or body.custody_revision < 0
                or any(type(number) is not int or number < 1 for number in numbers)
                or not isinstance(body.organization_id, str) or not body.organization_id
                or not isinstance(body.key_id, str) or not body.key_id):
            raise E2eeError("invalid_owner_evidence")
        bytes32(body.public_key)
        if "issuer_admission" not in command.body:
            raise E2eeError("unsupported_owner_binding_proof")
        admission = OriginalIssuerAdmission.parse(command.body["issuer_admission"])
        if (admission.root.subject != subject
                or any(admission.root.document()[name] != root.to_dict()[name] for name in ROOT_FIELDS)):
            raise E2eeError("owner_custody_evidence_mismatch")
        return cls(command, body, operation, admission)


@dataclass(frozen=True)
class OwnerSourceDocument:
    document_bytes: str
    project: E2EeOwnerSourceProject
    project_key: str
    digest: str

    @staticmethod
    def key(project_id: str) -> str:
        return encode(hashlib.sha256(f"{OwnerDomain.PROJECT_KEY}\n{project_id}".encode()).digest())

    @classmethod
    def parse(cls, crypto: E2eeCrypto, value: Any) -> OwnerSourceDocument:
        value = object_value(value)
        if set(value) != {"document_bytes"} or not isinstance(value["document_bytes"], str):
            raise E2eeError("owner_source_manifest_mismatch")
        raw = decode(value["document_bytes"])
        canonical = bytearray()
        try:
            document = object_value(json.loads(raw))
            if set(document) != {"project_id", "creation_command", "peer_trust", "owner_confirmations", "command_issuers"}:
                raise E2eeError("owner_project_source_mismatch")
            project = parse_model(E2EeOwnerSourceProject.from_dict, document)
            if not isinstance(project.project_id, str) or not project.project_id:
                raise E2eeError("owner_project_source_mismatch")
            canonical = crypto.canonical(document)
            if raw != canonical or encode(raw) != value["document_bytes"]:
                raise E2eeError("owner_source_manifest_mismatch")
            digest = encode(hashlib.sha256(f"{OwnerDomain.SOURCE_DOCUMENT}\n".encode() + raw).digest())
            return cls(value["document_bytes"], project, cls.key(project.project_id), digest)
        except (ValueError, TypeError):
            raise E2eeError("owner_source_manifest_mismatch") from None
        finally:
            wipe(raw)
            wipe(canonical)

    @classmethod
    def create(cls, crypto: E2eeCrypto, value: dict[str, Any]) -> OwnerSourceDocument:
        raw = crypto.canonical(value)
        try:
            return cls.parse(crypto, {"document_bytes": encode(raw)})
        finally:
            wipe(raw)

    def document(self) -> dict[str, str]:
        return {"document_bytes": self.document_bytes}

    def entry(self) -> dict[str, str]:
        return {"project_key": self.project_key, "document_digest": self.digest}


@dataclass(frozen=True)
class OwnerManifest:
    command: SignedEvidence
    body: E2EeOwnerSourceManifest
    digest: str
    documents: tuple[OwnerSourceDocument, ...] = ()

    @classmethod
    def parse(cls, crypto: E2eeCrypto, value: Any, documents: Any = ()) -> OwnerManifest:
        command = SignedEvidence.parse(value)
        body = parse_model(E2EeOwnerSourceManifest.from_dict, command.body)
        authority_head(body.owner_authority.to_dict(), body.organization_id)
        if (set(command.body) != {"format", "organization_id", "manifest_id", "owner_authority", "issuer_admission", "entries"}
                or command.body["format"] != "project_index_v1"
                or not isinstance(body.manifest_id, str) or not body.manifest_id
                or not isinstance(command.body["entries"], list)):
            raise E2eeError("owner_source_manifest_mismatch")
        from ._owner_sources import OriginalIssuerAdmission

        OriginalIssuerAdmission.parse(command.body["issuer_admission"])
        previous = None
        entries = {}
        for item in command.body["entries"]:
            item = object_value(item)
            if set(item) != {"project_key", "document_digest"}:
                raise E2eeError("owner_source_manifest_mismatch")
            bytes32(item["project_key"])
            bytes32(item["document_digest"])
            raw = decode(item["project_key"])
            try:
                key = bytes(raw)
            finally:
                wipe(raw)
            if previous is not None and previous >= key:
                raise E2eeError("owner_source_manifest_mismatch")
            previous = key
            entries[item["project_key"]] = item["document_digest"]
        if not isinstance(documents, (list, tuple)):
            raise E2eeError("owner_source_manifest_mismatch")
        parsed = tuple(OwnerSourceDocument.parse(crypto, item) for item in documents)
        if len({item.project_key for item in parsed}) != len(parsed) or any(
            entries.get(item.project_key) != item.digest for item in parsed
        ):
            raise E2eeError("owner_source_manifest_mismatch")
        return cls(command, body, command.digest(crypto, OwnerOperation.MANIFEST), parsed)

    def entries(self) -> dict[str, str]:
        return {item["project_key"]: item["document_digest"] for item in self.command.body["entries"]}

    def require_documents(self) -> tuple[OwnerSourceDocument, ...]:
        if {item.project_key: item.digest for item in self.documents} != self.entries():
            raise E2eeError("owner_source_document_missing")
        return self.documents

    def submission(self) -> dict[str, Any]:
        return {"signed_command": self.command.document(),
                "documents": [item.document() for item in self.require_documents()]}


@dataclass(frozen=True)
class OwnerPreparation:
    command: SignedEvidence
    body: E2EeOwnerPreparation
    original_admission: OriginalIssuerAdmission

    @classmethod
    def parse(cls, value: Any) -> OwnerPreparation:
        from ._owner_sources import OriginalIssuerAdmission

        command = SignedEvidence.parse(value)
        body = parse_model(E2EeOwnerPreparation.from_dict, command.body)
        authority_head(body.owner_authority.to_dict(), body.organization_id)
        for value in (body.offer_digest, body.source_manifest_digest, body.capsule_digest):
            bytes32(value)
        if "issuer_admission" not in command.body:
            raise E2eeError("unsupported_owner_preparation_proof")
        admission = OriginalIssuerAdmission.parse(command.body["issuer_admission"])
        return cls(command, body, admission)

    def context(self) -> dict[str, Any]:
        value = dict(self.command.body)
        del value["capsule"]
        del value["capsule_digest"]
        return value


def gate_descriptor(value: Any) -> OwnerHandoffGate:
    gate = parse_model(OwnerHandoffGate.from_dict, value)
    if (any(not isinstance(item, str) or not item for item in (
        gate.gate_id, gate.organization_id, gate.preparation_id, gate.candidate_id, gate.source_manifest_id,
    )) or type(gate.ownership_revision) is not int or gate.ownership_revision < 0
            or type(gate.source_key_epoch) is not int or gate.source_key_epoch < 1):
        raise E2eeError("owner_gate_mismatch")
    for item in (gate.public_key, gate.source_binding_digest, gate.offer_digest,
                 gate.source_manifest_digest, gate.history_manifest_digest):
        bytes32(item)
    return gate


def committed_decision(value: OwnerTransferDecision, organization: str) -> OwnerTransferDecision:
    if (value.organization_id != organization or value.state != OwnerTransferDecisionState.COMMITTED
            or not isinstance(value.operation_id, str) or not value.operation_id
            or value.no_content is not False or not isinstance(value.head, OwnerAuthorityHead)):
        raise E2eeError("owner_receipt_mismatch")
    authority_head(value.head.to_dict(), organization)
    return value


def committed_export_references(value: Any) -> tuple[E2EeOwnerCommittedExportReference, ...]:
    if not isinstance(value, list):
        raise E2eeError("owner_export_discovery_unavailable")
    references = []
    operations = set()
    fields = {"operation_id", "successor_binding_digest", "source_manifest_id", "source_manifest_digest"}
    for item in value:
        item = object_value(item)
        if set(item) != fields or any(not isinstance(field, str) or not field for field in item.values()):
            raise E2eeError("invalid_owner_evidence")
        bytes32(item["successor_binding_digest"])
        bytes32(item["source_manifest_digest"])
        reference = parse_model(E2EeOwnerCommittedExportReference.from_dict, item)
        if reference.operation_id in operations:
            raise E2eeError("invalid_owner_evidence")
        operations.add(reference.operation_id)
        references.append(reference)
    return tuple(references)


class OwnerCapsuleCrypto:
    def __init__(self, crypto: E2eeCrypto):
        self.crypto = crypto

    def public_key(self, secret: str) -> str:
        bytes32(secret)
        return self.crypto.execute({
            "op": "public_keys", "encryption_secret_key": secret,
            "signing_secret_key": encode(bytes(KEY_BYTES)),
        })["encryption_public_key"]

    def seal(self, sender_secret: str, recipient: str, plaintext: bytearray,
             preparation: Mapping[str, Any], domain: OwnerDomain) -> dict[str, str]:
        context = self.crypto.canonical({"v": 1, "domain": domain, **preparation})
        try:
            sealed = self.crypto.execute({
                "op": "hpke_auth_seal", "sender_secret_key": sender_secret,
                "recipient_public_key": recipient, "plaintext": encode(plaintext),
                "info": encode(context), "aad": encode(context),
            })
            return {"encapsulated_key": sealed["enc"], "ciphertext": sealed["ciphertext"]}
        finally:
            wipe(context)

    def open(self, secret: str, sender: Mapping[str, Any], envelope: Mapping[str, Any],
             preparation: Mapping[str, Any], domain: OwnerDomain) -> bytearray:
        context = self.crypto.canonical({"v": 1, "domain": domain, **preparation})
        try:
            return decode(self.crypto.execute({
                "op": "hpke_auth_open", "recipient_secret_key": secret,
                "sender_public_key": sender["encryption_public_key"],
                "info": encode(context), "aad": encode(context),
                "envelope": {"v": 1, "suite": "HPKE-Auth-X25519-HKDF-SHA256-AES256GCM",
                             "enc": envelope["encapsulated_key"], "ciphertext": envelope["ciphertext"]},
            })["plaintext"])
        except (KeyError, TypeError):
            raise E2eeError("invalid_owner_handoff") from None
        finally:
            wipe(context)
