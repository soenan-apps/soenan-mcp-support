from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe
from ._owner_protocol import ROOT_FIELDS


def admission_message(crypto: E2eeCrypto, body: Mapping[str, Any]) -> bytearray:
    canonical = crypto.canonical(body)
    try:
        return bytearray(b"arteligo-e2ee-device-admission-v1\n") + canonical
    finally:
        wipe(canonical)


class AdmissionResult(Enum):
    READY = "ready"
    KEY_ACQUISITION_PENDING = "key_acquisition_pending"


@dataclass
class ScopeAcquisition:
    epoch: int
    state: Literal["pending", "available", "uninitialized"] = "pending"
    reason: str = "key_acquisition_pending"
    signed_command: dict[str, str] | None = None

    def document(self) -> dict[str, Any]:
        value: dict[str, Any] = {"epoch": self.epoch, "state": self.state}
        if self.state == "pending":
            value["reason"] = self.reason
            if self.signed_command is not None:
                value["signed_command"] = self.signed_command
        return value

    @classmethod
    def load(cls, value: Any) -> ScopeAcquisition:
        if not isinstance(value, dict):
            raise E2eeError("invalid_key_admission")
        epoch, state = value.get("epoch"), value.get("state")
        if type(epoch) is not int or epoch < 0 or state not in {
            "pending", "available", "uninitialized",
        }:
            raise E2eeError("invalid_key_admission")
        reason = value.get("reason", "key_acquisition_pending")
        if not isinstance(reason, str):
            raise E2eeError("invalid_key_admission")
        command = value.get("signed_command")
        if command is not None:
            command = _signed_command(command)
        return cls(epoch, state, reason, command)


def _signed_command(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {
        "device_id", "body_bytes", "signature",
    } or any(not isinstance(item, str) or not item for item in value.values()):
        raise E2eeError("invalid_key_admission")
    return dict(value)


@dataclass
class AdmissionAttempt:
    identifier: str
    subject: str
    root: dict[str, Any]
    challenge: str
    signed_command: dict[str, str]
    scopes: dict[str, ScopeAcquisition] = field(default_factory=dict)

    def document(self) -> dict[str, Any]:
        return {
            "attempt_id": self.identifier,
            "account_subject": self.subject,
            "root": {name: self.root[name] for name in ROOT_FIELDS},
            "challenge": self.challenge,
            "signed_command": self.signed_command,
            "scopes": {scope: progress.document() for scope, progress in self.scopes.items()},
        }

    def progress(self) -> dict[str, Any]:
        return {
            "available": sorted(scope for scope, item in self.scopes.items() if item.state == "available"),
            "pending": sorted(scope for scope, item in self.scopes.items() if item.state == "pending"),
            "remaining": {scope: item.reason for scope, item in sorted(self.scopes.items()) if item.state == "pending"},
        }

    def synchronize(self, scopes: list[dict[str, Any]]) -> None:
        current = {}
        for scope in scopes:
            identifier, epoch = scope["project_id"], scope["key_epoch"]
            existing = self.scopes.get(identifier)
            if epoch == 0 and scope["key_state"] == "uninitialized":
                current[identifier] = ScopeAcquisition(epoch, "uninitialized")
            else:
                current[identifier] = (
                    existing if existing is not None and existing.epoch == epoch
                    else ScopeAcquisition(epoch)
                )
        self.scopes = current

    @classmethod
    def load(
        cls, value: Any, crypto: E2eeCrypto, subject: str, device: dict[str, Any]
    ) -> AdmissionAttempt:
        if not isinstance(value, dict) or value.get("account_subject") != subject:
            raise E2eeError("invalid_key_admission")
        identifier, root, challenge = (
            value.get("attempt_id"), value.get("root"), value.get("challenge"),
        )
        if not isinstance(identifier, str) or not identifier or not isinstance(root, dict):
            raise E2eeError("invalid_key_admission")
        if set(root) != set(ROOT_FIELDS) or type(root.get("generation")) is not int or root["generation"] <= 0:
            raise E2eeError("invalid_key_admission")
        if any(not isinstance(root.get(name), str) or not root[name] for name in ROOT_FIELDS if name != "generation"):
            raise E2eeError("invalid_key_admission")
        challenge_bytes = decode(challenge)
        try:
            if len(challenge_bytes) != 32:
                raise E2eeError("invalid_key_admission")
        finally:
            wipe(challenge_bytes)
        command = _signed_command(value.get("signed_command"))
        body = crypto.verify(root["signing_public_key"], "device_add_by_key", command)
        unsigned = {
            "recovery_id": root["recovery_id"], "generation": root["generation"],
            "device": device, "challenge": challenge,
        }
        if command["device_id"] != device["device_id"] or set(body) != {*unsigned, "device_signature"} or any(body.get(name) != item for name, item in unsigned.items()):
            raise E2eeError("invalid_key_admission")
        message = admission_message(crypto, unsigned)
        try:
            crypto.execute({
                "op": "verify_bytes", "public_key": device["signing_public_key"],
                "bytes": encode(message), "signature": body["device_signature"],
            })
        finally:
            wipe(message)
        scopes = value.get("scopes")
        if not isinstance(scopes, dict) or any(not isinstance(scope, str) or not scope for scope in scopes):
            raise E2eeError("invalid_key_admission")
        return cls(identifier, subject, root, challenge, command, {
            scope: ScopeAcquisition.load(progress) for scope, progress in scopes.items()
        })
