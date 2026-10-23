from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

from account_public_api_client.models.owner_transfer_decision import OwnerTransferDecision
from arteligo_public_api_client.models.e2_ee_owner_history_binding import E2EeOwnerHistoryBinding
from arteligo_public_api_client.models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence

from ._crypto import E2eeCrypto, E2eeError
from ._owner_protocol import OwnerManifest, SignedEvidence, bytes32, object_value, parse_model
from ._owner_state import SourceAnchor
from ._trust import _RootIdentity


@dataclass(frozen=True)
class OwnerStoredManifestReference:
    manifest: OwnerManifest
    preparation: SignedEvidence | None
    decision: OwnerTransferDecision | None

    @classmethod
    def parse(cls, crypto: E2eeCrypto, value: Any, organization: str) -> OwnerStoredManifestReference:
        value = object_value(value)
        required = {"signed_command", "manifest_digest", "documents"}
        selected = {"selected_preparation", "selected_decision"}
        if set(value) not in (required, required | selected):
            raise E2eeError("owner_source_manifest_mismatch")
        manifest = OwnerManifest.parse(crypto, value["signed_command"], value["documents"])
        manifest.require_documents()
        if manifest.digest != value["manifest_digest"] or manifest.body.organization_id != organization:
            raise E2eeError("owner_source_manifest_mismatch")
        return cls(manifest,
            SignedEvidence.parse(value["selected_preparation"]) if selected <= value.keys() else None,
            parse_model(OwnerTransferDecision.from_dict, value["selected_decision"]) if selected <= value.keys() else None)

    def document(self) -> dict[str, Any]:
        result = {"signed_command": self.manifest.command.document(), "manifest_digest": self.manifest.digest,
                  "documents": [item.document() for item in self.manifest.require_documents()]}
        if self.preparation is not None and self.decision is not None:
            result.update(selected_preparation=self.preparation.document(), selected_decision=self.decision.to_dict())
        return result


@dataclass(frozen=True)
class OwnerSourceManifestReference:
    manifest_id: str
    manifest_digest: str
    operation_id: str | None = None
    preparation_id: str | None = None

    @classmethod
    def parse(cls, value: Any) -> OwnerSourceManifestReference:
        value = object_value(value)
        required = {"manifest_id", "manifest_digest"}
        if (set(value) not in (required, required | {"operation_id", "preparation_id"})
                or any(not isinstance(item, str) or not item for item in value.values())):
            raise E2eeError("invalid_owner_source_evidence")
        bytes32(value["manifest_digest"])
        return cls(value["manifest_id"], value["manifest_digest"], value.get("operation_id"), value.get("preparation_id"))

    def document(self) -> dict[str, str]:
        value = {"manifest_id": self.manifest_id, "manifest_digest": self.manifest_digest}
        if self.operation_id is not None and self.preparation_id is not None:
            value.update(operation_id=self.operation_id, preparation_id=self.preparation_id)
        return value


@dataclass(frozen=True)
class OriginalAdmissionCertificate:
    device_id: str
    certificate_digest: str

    @classmethod
    def parse(cls, value: Any) -> OriginalAdmissionCertificate:
        value = object_value(value)
        if set(value) != {"device_id", "certificate_digest"} or not isinstance(value["device_id"], str) or not value["device_id"]:
            raise E2eeError("invalid_owner_source_evidence")
        bytes32(value["certificate_digest"])
        return cls(value["device_id"], value["certificate_digest"])

    def document(self) -> dict[str, str]:
        return {"device_id": self.device_id, "certificate_digest": self.certificate_digest}


@dataclass(frozen=True)
class OriginalIssuerAdmission:
    root: _RootIdentity
    root_evidence_digest: str | None
    certificates: tuple[OriginalAdmissionCertificate, ...]

    MAX_CERTIFICATES: ClassVar[int] = 1024

    @classmethod
    def parse(cls, value: Any) -> OriginalIssuerAdmission:
        value = object_value(value)
        if set(value) != {"root", "root_evidence_digest", "certificates"} or not isinstance(value["certificates"], list):
            raise E2eeError("invalid_owner_source_evidence")
        root = object_value(value["root"])
        if set(root) != {"origin", "account_subject", "recovery_id", "generation", "encryption_public_key", "signing_public_key"}:
            raise E2eeError("invalid_owner_source_evidence")
        identity = _RootIdentity.parse(root["origin"], root["account_subject"], root)
        if value["root_evidence_digest"] is not None:
            bytes32(value["root_evidence_digest"])
        certificates = tuple(OriginalAdmissionCertificate.parse(item) for item in value["certificates"])
        if not 1 <= len(certificates) <= cls.MAX_CERTIFICATES or len(set(certificates)) != len(certificates):
            raise E2eeError("invalid_owner_source_evidence")
        return cls(identity, value["root_evidence_digest"], certificates)

    def document(self) -> dict[str, Any]:
        return {"root": self.root.document(), "root_evidence_digest": self.root_evidence_digest,
                "certificates": [item.document() for item in self.certificates]}


@dataclass(frozen=True)
class OwnerIssuerEvidence:
    devices: Mapping[str, dict[str, Any]]
    recoveries: Mapping[str, dict[str, Any]]

    @classmethod
    def parse(cls, value: Any) -> OwnerIssuerEvidence:
        model = parse_model(E2EeOwnerIssuerEvidence.from_dict, object_value(value))
        devices = {item.device_id: item.to_dict() for item in model.devices}
        roots = {item.recovery_id: item.to_dict() for item in model.recoveries}
        if (len(devices) != len(model.devices) or len(roots) != len(model.recoveries)
                or sum(len(item.get("certificates", [])) for item in devices.values()) + len(roots)
                > OriginalIssuerAdmission.MAX_CERTIFICATES):
            raise E2eeError("invalid_owner_evidence")
        return cls(devices, roots)

    def device(self, identifier: str) -> dict[str, Any]:
        if identifier not in self.devices:
            raise E2eeError("owner_device_proof_missing")
        return self.devices[identifier]

    def recovery(self, identifier: str) -> dict[str, Any]:
        if identifier not in self.recoveries:
            raise E2eeError("owner_root_proof_missing")
        return self.recoveries[identifier]


@dataclass(frozen=True)
class OwnerSourceEvidence:
    anchor: SourceAnchor | None
    confirmations: tuple[SourceAnchor, ...]
    self_roots: tuple[_RootIdentity, ...]
    manifests: tuple[OwnerSourceManifestReference, ...]
    receipts: tuple[str, ...]
    key_bindings: tuple[E2EeOwnerHistoryBinding, ...]
    issuer_admission: OriginalIssuerAdmission
    root_snapshot_digest: str | None = None

    @classmethod
    def parse(cls, crypto: E2eeCrypto, value: Any, organization: str) -> OwnerSourceEvidence:
        value = object_value(value)
        lists = {"self_roots", "confirmed_sources", "manifests", "receipts", "key_bindings"}
        required = lists | {"issuer_admission"}
        if not required <= value.keys() or value.keys() - required - {"source_anchor", "root_snapshot_digest"} or any(
            not isinstance(value[name], list) for name in lists
        ):
            raise E2eeError("invalid_owner_source_evidence")
        if "root_snapshot_digest" in value:
            bytes32(value["root_snapshot_digest"])
        anchor = SourceAnchor.parse(value["source_anchor"]) if "source_anchor" in value else None
        confirmations = tuple(SourceAnchor.parse(item) for item in value["confirmed_sources"])
        for statement in (*confirmations, *((anchor,) if anchor is not None else ())):
            if not isinstance(statement.command.body.get("scope_id"), str):
                raise E2eeError("invalid_owner_source_evidence")
        if anchor is not None and anchor.command.body["scope_id"] != organization:
            raise E2eeError("invalid_owner_source_evidence")
        if any(not isinstance(item, str) or not item for item in value["receipts"]):
            raise E2eeError("invalid_owner_source_evidence")
        roots = []
        for item in value["self_roots"]:
            item = object_value(item)
            if set(item) != {"origin", "account_subject", "recovery_id", "generation", "encryption_public_key", "signing_public_key"}:
                raise E2eeError("invalid_owner_source_evidence")
            roots.append(_RootIdentity.parse(item["origin"], item["account_subject"], item))
        bindings = []
        for item in value["key_bindings"]:
            item = object_value(item)
            if (set(item) != {"key_id", "key_epoch", "public_key", "binding_digest"}
                    or not isinstance(item["key_id"], str) or not item["key_id"]
                    or type(item["key_epoch"]) is not int or item["key_epoch"] < 1):
                raise E2eeError("invalid_owner_source_evidence")
            bytes32(item["public_key"])
            bytes32(item["binding_digest"])
            bindings.append(parse_model(E2EeOwnerHistoryBinding.from_dict, item))
        return cls(anchor, confirmations, tuple(roots),
            tuple(OwnerSourceManifestReference.parse(item) for item in value["manifests"]),
            tuple(value["receipts"]), tuple(bindings), OriginalIssuerAdmission.parse(value["issuer_admission"]),
            value.get("root_snapshot_digest"))

    def document(self) -> dict[str, Any]:
        value = {"self_roots": [root.document() for root in self.self_roots],
                 "confirmed_sources": [item.document() for item in self.confirmations],
                 "manifests": [item.document() for item in self.manifests],
                 "receipts": list(self.receipts),
                 "key_bindings": [item.to_dict() for item in self.key_bindings],
                 "issuer_admission": self.issuer_admission.document()}
        if self.anchor is not None:
            value["source_anchor"] = self.anchor.document()
        if self.root_snapshot_digest is not None:
            value["root_snapshot_digest"] = self.root_snapshot_digest
        return value
