"""Typed, secret-safe observations of the existing Account identity client."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Literal

from soenan.account.crypto.v1 import crypto_pb2 as crypto
from soenan.account.identity.v1 import identity_pb2 as identity
from soenan_account_identity_client._errors import IdentityError


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def flip(value: bytes) -> bytes:
    if not value:
        raise ValueError("missing_ciphertext")
    return bytes([value[0] ^ 1]) + value[1:]


@dataclass(frozen=True)
class EvidenceRequest:
    operation: Literal[
        "observe",
        "pairing",
        "approve",
        "accept",
        "foreign",
        "ciphertext",
        "rollback",
        "code",
        "bootstrap",
    ]
    payload: bytes = b""
    code: bytes = b""

    @classmethod
    def from_wire(cls, value: dict) -> EvidenceRequest:
        operation = value["operation"]
        payload = value.get("payload", "")
        code = value.get("code", "")
        if not isinstance(payload, str) or not isinstance(code, str):
            raise ValueError("invalid_identity_evidence")
        arguments = (
            base64.b64decode(payload, validate=True),
            base64.b64decode(
                code + "=" * (-len(code) % 4), altchars=b"-_", validate=True
            ),
        )
        match operation:
            case (
                "observe"
                | "pairing"
                | "approve"
                | "accept"
                | "foreign"
                | "ciphertext"
                | "rollback"
                | "code"
                | "bootstrap"
            ):
                return cls(operation, *arguments)
            case _:
                raise ValueError("unsupported_identity_evidence")


@dataclass(frozen=True)
class Observation:
    status: str
    state_hash: str
    pin_hash: str
    journal_hash: str
    account_revision: int
    devices_hash: str
    pin_revision: int


@dataclass(frozen=True)
class EvidenceResult:
    slug: str
    before: Observation
    after: Observation
    payload: str = ""


def observe(owner, settings) -> Observation:
    state = owner.snapshot
    state.account_jwks = json.dumps(
        json.loads(state.account_jwks), sort_keys=True, separators=(",", ":")
    )
    statements = [
        identity.IdentityStatement.FromString(record.statement.body)
        for record in settings.bundle.identity_statements
    ]
    current = next(
        item
        for item in statements
        if item.subject == owner.subject
        and item.revision == settings.bundle.identity_revision
    )
    return Observation(
        owner.state,
        digest(state.SerializeToString(deterministic=True)),
        digest(
            b"".join(
                pin.SerializeToString(deterministic=True) for pin in state.trust_anchors
            )
        ),
        digest(
            b"".join(
                op.SerializeToString(deterministic=True)
                for op in state.identity_operations
            )
        ),
        settings.bundle.identity_revision,
        digest(
            b"".join(
                device.SerializeToString(deterministic=True)
                for device in current.devices
            )
        ),
        max(
            (
                pin.identity_revision
                for pin in state.trust_anchors
                if pin.subject == owner.subject
            ),
            default=0,
        ),
    )


def execute_identity_evidence(owner, request: EvidenceRequest) -> EvidenceResult:
    settings = owner.settings()
    before = observe(owner, settings)
    payload = b""
    slug = "accepted"
    try:
        if request.operation == "observe":
            payload = identity.IdentityChangeResponse(
                bundle=settings.bundle, subject=settings.subject
            ).SerializeToString()
        elif request.operation == "pairing":
            payload = owner.pairing_request().SerializeToString()
            owner.synchronize()
        elif request.operation == "approve":
            payload = owner.approve(
                crypto.SignedBytes.FromString(request.payload)
            ).SerializeToString()
        elif request.operation in {"accept", "foreign", "ciphertext", "rollback"}:
            packet = identity.IdentityChangeResponse.FromString(request.payload)
            if request.operation == "ciphertext":
                current = next(
                    statement
                    for record in packet.bundle.identity_statements
                    if (
                        statement := identity.IdentityStatement.FromString(
                            record.statement.body
                        )
                    ).subject
                    == owner.subject
                    and statement.revision == packet.bundle.identity_revision
                )
                delivery = next(
                    signed
                    for signed in packet.bundle.key_deliveries
                    if (
                        decoded := crypto.KeyDeliveryBody.FromString(signed.body)
                    ).recipient.id
                    == owner.device_id
                    and decoded.target == current.receiver.key
                )
                body = crypto.KeyDeliveryBody.FromString(delivery.body)
                body.envelope.ciphertext = flip(body.envelope.ciphertext)
                delivery.body = body.SerializeToString()
            elif request.operation == "rollback":
                revision = before.pin_revision - 1
                if revision < 1:
                    raise ValueError("rollback_requires_existing_pin")
                retained = [
                    record
                    for record in packet.bundle.identity_statements
                    if identity.IdentityStatement.FromString(
                        record.statement.body
                    ).revision
                    <= revision
                ]
                del packet.bundle.identity_statements[:]
                packet.bundle.identity_statements.extend(retained)
                packet.bundle.identity_revision = revision
            owner.accept_approval(packet)
        elif request.operation == "code":
            owner.add_by_key(
                base64.urlsafe_b64encode(request.code).decode().rstrip("=")
            )
        elif request.operation == "bootstrap":
            envelope = crypto.HpkeEnvelope.FromString(settings.sealed_bootstrap)
            envelope.ciphertext = flip(envelope.ciphertext)
            owner.enroll(
                action=identity.ENROLLMENT_ACTION_OPEN_CODE,
                addition_code=request.code,
                sealed_bootstrap=envelope.SerializeToString(),
            )
    except IdentityError as error:
        slug = str(error)
    after = observe(owner, owner.settings())
    return EvidenceResult(slug, before, after, base64.b64encode(payload).decode())


def public_identity_evidence(owner, arguments: dict) -> dict:
    return asdict(
        execute_identity_evidence(owner, EvidenceRequest.from_wire(arguments))
    )
