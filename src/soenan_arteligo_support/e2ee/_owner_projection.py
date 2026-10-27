from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ._crypto import E2eeCrypto, E2eeError
from ._owner_protocol import ROOT_FIELDS, bytes32, object_value
from ._owner_sources import OriginalIssuerAdmission


@dataclass(frozen=True)
class CertificateProjectionReference:
    certificate_digest: str
    witness_subject: str

    @classmethod
    def parse(cls, value: Mapping[str, Any]) -> CertificateProjectionReference:
        if set(value) != {"operation", "signature_projection"} or value["operation"] != "account_signature_projection":
            raise E2eeError("invalid_certificate")
        reference = object_value(value["signature_projection"])
        if (set(reference) != {"certificate_digest", "witness_subject"}
                or not isinstance(reference["witness_subject"], str) or not reference["witness_subject"]):
            raise E2eeError("invalid_certificate")
        bytes32(reference["certificate_digest"])
        return cls(reference["certificate_digest"], reference["witness_subject"])


@dataclass(frozen=True)
class CertificateSignatureProjection:
    reference: CertificateProjectionReference
    evidence_digest: str
    signing_public_key: str
    operation: str
    device_id: str
    body: dict[str, Any]

    @classmethod
    def parse(cls, value: Any, reference: CertificateProjectionReference) -> CertificateSignatureProjection:
        value = object_value(value)
        if (set(value) != {"format", "account_subject", "certificate_digest", "evidence_digest", "signing_public_key", "signed_fields"}
                or value["format"] != "signature_projection_v1"
                or value["account_subject"] != reference.witness_subject
                or value["certificate_digest"] != reference.certificate_digest):
            raise E2eeError("owner_custody_evidence_mismatch")
        bytes32(value["evidence_digest"])
        bytes32(value["signing_public_key"])
        fields = object_value(value["signed_fields"])
        operation, issuer = fields.get("operation"), fields.get("issuer_device_id")
        if not isinstance(issuer, str) or not issuer:
            raise E2eeError("invalid_certificate")
        if operation == "device_approve":
            expected = {"operation", "issuer_device_id", "account_subject", "device_id", "encryption_public_key",
                        "signing_public_key", "challenge", "recovery_root", "issuer_admission"}
            if set(fields) != expected or fields["account_subject"] not in (None, reference.witness_subject):
                raise E2eeError("owner_custody_evidence_mismatch")
            for name in ("encryption_public_key", "signing_public_key", "challenge"):
                bytes32(fields[name])
            if not isinstance(fields["device_id"], str) or not fields["device_id"]:
                raise E2eeError("invalid_certificate")
            roots = (fields["recovery_root"],)
        elif operation == "envelopes_save":
            if set(fields) != {"operation", "issuer_device_id", "scope_id", "key_epoch", "participation", "issuer_admission"}:
                raise E2eeError("invalid_certificate")
            participation = object_value(fields["participation"])
            if (set(participation) != {"request_command", "approver_recovery"}
                    or not isinstance(fields["scope_id"], str) or not fields["scope_id"]
                    or type(fields["key_epoch"]) is not int or fields["key_epoch"] < 1):
                raise E2eeError("invalid_certificate")
            roots = (participation["approver_recovery"],)
        else:
            raise E2eeError("invalid_certificate")
        for root in roots:
            if root is not None:
                root = object_value(root)
                if set(root) != set(ROOT_FIELDS) or type(root["generation"]) is not int or root["generation"] < 1:
                    raise E2eeError("invalid_certificate")
                bytes32(root["encryption_public_key"])
                bytes32(root["signing_public_key"])
                if not isinstance(root["recovery_id"], str) or not root["recovery_id"]:
                    raise E2eeError("invalid_certificate")
        body = {name: item for name, item in fields.items() if name not in {"operation", "issuer_device_id"}}
        for name in ("issuer_admission", "recovery_root", "account_subject"):
            if body.get(name) is None:
                body.pop(name, None)
        if "issuer_admission" in body:
            OriginalIssuerAdmission.parse(body["issuer_admission"])
        return cls(reference, value["evidence_digest"], value["signing_public_key"], operation, issuer, body)

    def digest(self, crypto: E2eeCrypto, operation: str) -> str:
        if operation != self.operation:
            raise E2eeError("owner_custody_evidence_mismatch")
        return self.evidence_digest

    def verify(self, crypto: E2eeCrypto, public_key: str, operation: str) -> None:
        if operation != self.operation or public_key != self.signing_public_key:
            raise E2eeError("owner_custody_evidence_mismatch")


def original_certificate_digest(crypto: E2eeCrypto, certificate: Mapping[str, Any]) -> str:
    if certificate.get("operation") == "account_signature_projection":
        return CertificateProjectionReference.parse(certificate).certificate_digest
    from ._owner_protocol import canonical_digest

    return canonical_digest(crypto, certificate)
