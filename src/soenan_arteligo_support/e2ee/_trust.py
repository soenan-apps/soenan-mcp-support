from __future__ import annotations

from collections.abc import Callable, Mapping
import json
from typing import Any

from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe
from ._storage import SecureStore

_DEVICE_FIELDS = (
    "device_id",
    "account_subject",
    "encryption_public_key",
    "signing_public_key",
)


def public_device(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or any(
        not isinstance(value.get(field), str) or not value[field]
        for field in _DEVICE_FIELDS
    ):
        raise E2eeError("invalid_device")
    return {**{field: value[field] for field in _DEVICE_FIELDS}, "state": "approved"}


class KeyTrust:
    """Trust starts at local keys, recovery-code keys, or an explicit QR/link proof."""

    def __init__(
        self,
        crypto: E2eeCrypto,
        store: SecureStore,
        subject: str,
        *,
        owner_subject: str | None = None,
    ):
        self.crypto = crypto
        self.store = store
        self.name = f"trust:{subject}"
        self._state = {"devices": {}, "recovery": {}}
        self.owner_subject = owner_subject or subject
        self._endorsements: list[dict[str, Any]] = []

    def set_endorsements(self, statements: list[dict[str, Any]]) -> None:
        if len(statements) > 1024:
            raise E2eeError("trust_limit_exceeded")
        self._endorsements = statements

    def _endorsed(
        self, lookup: Callable[[str], Mapping[str, Any]], visiting: frozenset[str]
    ):
        for command in self._endorsements:
            identifier = command.get("device_id")
            if not isinstance(identifier, str) or identifier in visiting:
                continue
            issuer = lookup(identifier)
            if issuer.get("account_subject") != self.owner_subject:
                continue
            try:
                checked = self.verify_device(issuer, lookup, visiting)
            except E2eeError as error:
                if error.code == "untrusted_device":
                    continue
                raise
            yield self.crypto.verify(
                checked["signing_public_key"], "peer_trust", command
            )

    def _load(self, kind: str, identifier: str) -> dict[str, Any] | None:
        if identifier not in self._state[kind]:
            saved = self.store.read(f"{self.name}:{kind}:{identifier}")
            if saved:
                self._state[kind][identifier] = json.loads(saved)
        return self._state[kind].get(identifier)

    def _save(self, kind: str, identifier: str, value: dict[str, Any]) -> None:
        self.store.write(
            f"{self.name}:{kind}:{identifier}", json.dumps(value, separators=(",", ":"))
        )
        self._state[kind][identifier] = value

    def pin_device(self, device: Mapping[str, Any]) -> dict[str, Any]:
        value = public_device(device)
        previous = self._load("devices", value["device_id"])
        if previous is not None and previous != value:
            raise E2eeError("device_key_changed")
        self._save("devices", value["device_id"], value)
        return value

    def pin_recovery(self, subject: str, recovery: Mapping[str, Any]) -> None:
        value = {
            "account_subject": subject,
            "recovery_id": recovery["recovery_id"],
            "signing_public_key": recovery["signing_public_key"],
            "encryption_public_key": recovery["encryption_public_key"],
        }
        previous = self._load("recovery", value["recovery_id"])
        if previous is not None and previous != value:
            raise E2eeError("recovery_key_changed")
        self._save("recovery", value["recovery_id"], value)

    def verify_recovery(
        self,
        subject: str,
        recovery: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
    ) -> dict[str, Any]:
        identifier = recovery.get("recovery_id")
        if not isinstance(identifier, str):
            raise E2eeError("invalid_recovery")
        previous = self._load("recovery", identifier)
        if previous is not None:
            self.pin_recovery(subject, recovery)
            return dict(recovery)
        for certificate in recovery.get("certificates", []):
            operation = certificate.get("operation")
            if operation != "recovery_public":
                continue
            command = certificate.get("signed_command", {})
            issuer = self.verify_device(lookup(command.get("device_id")), lookup)
            if issuer["account_subject"] != subject:
                raise E2eeError("invalid_recovery")
            body = self.crypto.verify(issuer["signing_public_key"], operation, command)
            if body.get("account_subject") == subject and all(
                body.get(field) == recovery.get(field)
                for field in (
                    "recovery_id",
                    "encryption_public_key",
                    "signing_public_key",
                    "generation",
                )
            ):
                self.pin_recovery(subject, recovery)
                return dict(recovery)
        for body in self._endorsed(lookup, frozenset()):
            peer = body.get("trusted_device", {})
            root = body.get("recovery_root", {})
            if peer.get("account_subject") == subject and all(
                root.get(field) == recovery.get(field)
                for field in (
                    "recovery_id",
                    "encryption_public_key",
                    "signing_public_key",
                    "generation",
                )
            ):
                self.pin_recovery(subject, recovery)
                return dict(recovery)
        raise E2eeError("untrusted_recovery")

    def verify_device(
        self,
        device: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
        visiting: frozenset[str] = frozenset(),
    ) -> dict[str, Any]:
        identifier = device.get("device_id")
        if (
            not isinstance(identifier, str)
            or identifier in visiting
            or len(visiting) >= 32
        ):
            raise E2eeError("untrusted_device")
        previous = self._load("devices", identifier)
        if previous is not None:
            if previous != public_device(device):
                raise E2eeError("device_key_changed")
            return previous
        for body in self._endorsed(lookup, visiting | {identifier}):
            if public_device(body.get("trusted_device", {})) == public_device(device):
                return self.pin_device(device)
        certificates = device.get("certificates")
        if not isinstance(certificates, list):
            raise E2eeError("untrusted_device")
        for certificate in certificates:
            if not isinstance(certificate, dict):
                continue
            operation = certificate.get("operation")
            command = certificate.get("signed_command")
            if operation != "bootstrap" and not isinstance(command, dict):
                continue
            if operation == "device_approve":
                issuer_id = command.get("device_id")
                if not isinstance(issuer_id, str) or issuer_id == identifier:
                    continue
                try:
                    issuer = self.verify_device(
                        lookup(issuer_id), lookup, visiting | {identifier}
                    )
                except E2eeError as error:
                    if error.code == "untrusted_device":
                        continue
                    raise
                body = self.crypto.verify(
                    issuer["signing_public_key"], operation, command
                )
                if issuer["account_subject"] != device.get("account_subject"):
                    raise E2eeError("untrusted_device")
                if any(
                    body.get(field) != device.get(field)
                    for field in (
                        "device_id",
                        "encryption_public_key",
                        "signing_public_key",
                    )
                ):
                    raise E2eeError("invalid_certificate")
                return self.pin_device(device)
            if operation == "bootstrap":
                recovery = certificate.get("recovery_root", {})
                root = self._load("recovery", recovery.get("recovery_id"))
                if root is None:
                    continue
                if root["account_subject"] != device.get("account_subject") or any(
                    root[field] != recovery.get(field)
                    for field in ("signing_public_key", "encryption_public_key")
                ):
                    raise E2eeError("invalid_certificate")
                if public_device(certificate.get("public_device", {})) != public_device(
                    device
                ):
                    raise E2eeError("invalid_certificate")
                canonical = self.crypto.canonical(public_device(device))
                message = bytearray(b"arteligo-e2ee-device-root-v1\n") + canonical
                try:
                    self.crypto.execute(
                        {
                            "op": "verify_bytes",
                            "public_key": root["signing_public_key"],
                            "bytes": encode(message),
                            "signature": certificate.get("root_signature"),
                        }
                    )
                finally:
                    wipe(canonical)
                    wipe(message)
                return self.pin_device(device)
            if operation == "recovery_restore":
                decoded = decode(command.get("body_bytes"))
                try:
                    body = json.loads(decoded)
                finally:
                    wipe(decoded)
                root = self._load("recovery", body.get("recovery_id"))
                if root is None:
                    continue
                body = self.crypto.verify(
                    root["signing_public_key"], operation, command
                )
                if root["account_subject"] != device.get(
                    "account_subject"
                ) or public_device(body.get("device", {})) != public_device(device):
                    raise E2eeError("invalid_certificate")
                return self.pin_device(device)
        raise E2eeError("untrusted_device")
