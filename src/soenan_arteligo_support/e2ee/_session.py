from __future__ import annotations

import hashlib
import json
import secrets
from collections.abc import Mapping
from typing import Any

from ._api import E2eeAPI
from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe
from ._storage import SecureStore
from ._trust import KeyTrust, public_device


class DeviceSession:
    def __init__(
        self,
        api: E2eeAPI,
        crypto: E2eeCrypto,
        store: SecureStore,
        *,
        origin: str,
        subject: str,
    ):
        self.api, self.crypto, self.store = api, crypto, store
        self.subject = subject
        namespace = hashlib.sha256((origin + "\n" + subject).encode()).hexdigest()
        self._storage_key = "device:" + namespace
        self.trust = KeyTrust(crypto, store, namespace, owner_subject=subject)
        self._device: dict[str, Any] | None = None
        self._devices: dict[str, dict[str, Any]] = {}
        self._scope_keys: dict[tuple[str, int], bytearray] = {}
        self._restoring_recovery: tuple[str, bytearray] | None = None
        self.recovery: dict[str, Any] | None = None
        self.state = "needs_setup"

    @property
    def device_id(self) -> str:
        return self._device["device_id"] if self._device else ""

    @property
    def public(self) -> dict[str, Any]:
        if self._device is None:
            raise E2eeError("device_approval_required")
        return public_device({**self._device, "account_subject": self.subject})

    def _new_device(self) -> dict[str, Any]:
        return {**self.crypto.keypair(), "device_id": secrets.token_urlsafe(24)}

    def _persist(self) -> None:
        self.store.write(
            self._storage_key, json.dumps(self._device, separators=(",", ":"))
        )

    def refresh(self) -> str:
        self.state = "pending_approval"
        saved = self.store.read(self._storage_key)
        if saved is not None:
            self._device = json.loads(saved)
            derived = self.crypto.execute(
                {
                    "op": "public_keys",
                    "encryption_secret_key": self._device["encryption_secret_key"],
                    "signing_secret_key": self._device["signing_secret_key"],
                }
            )
            if any(derived[field] != self._device[field] for field in derived):
                raise E2eeError("device_key_changed")
            self.trust.pin_device(self.public)
        try:
            self.recovery = self.api.call("e2eeGetRecovery")
        except E2eeError as error:
            if error.code != "not_found":
                raise
            self.recovery = None
        if self.recovery is not None:
            self.trust.set_endorsements(self.api.call("e2eeGetTrust")["statements"])
        if self._device is None:
            self.state = "needs_setup" if self.recovery is None else "pending_approval"
            return self.state
        values = self.api.call("e2eeListDevices")["devices"]
        self._devices = {value["device_id"]: value for value in values}
        current = self._devices.get(self.device_id)
        if current is None:
            self.state = "needs_setup" if self.recovery is None else "pending_approval"
        else:
            if public_device(current) != self.public:
                raise E2eeError("device_key_changed")
            self.state = current["state"]
        observed_state = self.state
        self.state = (
            "pending_approval" if observed_state == "approved" else observed_state
        )
        if observed_state != "approved":
            self._clear_keys()
        elif self.recovery is not None:
            try:
                self.trust.verify_recovery(
                    self.subject,
                    self.recovery,
                    lambda identifier: self._devices[identifier],
                )
            except E2eeError as error:
                if (
                    error.code not in {"untrusted_device", "untrusted_recovery"}
                    or not self._device.get("challenge")
                    or self._device.get("paired") is True
                ):
                    raise
                self.state = "pending_approval"
                self._clear_keys()
                return self.state
            self.state = "approved"
        if self._device.get("recovery_restore") is not None and self.state != "revoked":
            self.state = "recovery_pending"
        return self.state

    def require_approved(self) -> None:
        if self.state != "approved" or self._device is None:
            raise E2eeError("device_approval_required")

    def endorse(
        self, device: dict[str, Any], recovery: dict[str, Any] | None = None
    ) -> None:
        """Persist public trust only after the caller completed an out-of-band proof."""
        self.require_approved()
        body: dict[str, Any] = {"trusted_device": public_device(device)}
        if recovery is not None:
            body["recovery_root"] = {
                field: recovery[field]
                for field in (
                    "recovery_id",
                    "encryption_public_key",
                    "signing_public_key",
                    "generation",
                )
            }
        self.command("e2eeSaveTrust", "peer_trust", body)
        self.trust.pin_device(device)
        if recovery is not None:
            self.trust.pin_recovery(device["account_subject"], recovery)

    def sign(
        self, operation: str, body: Mapping[str, Any], *, secret_key: str | None = None
    ) -> dict[str, str]:
        if self._device is None:
            raise E2eeError("device_approval_required")
        return self.crypto.sign(
            secret_key or self._device["signing_secret_key"],
            operation,
            body,
            self.device_id,
        )

    def command(
        self,
        api_operation: str,
        operation: str,
        body: dict[str, Any],
        *,
        secret_key: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        return self.api.call(
            api_operation,
            body=self.sign(operation, body, secret_key=secret_key),
            **parameters,
        )

    def prepare_setup(self) -> dict[str, Any]:
        if self.recovery is not None:
            raise E2eeError("already_initialized")
        device = self._new_device()
        recovery = self.crypto.keypair()
        identifier = secrets.token_urlsafe(24)
        code = self.crypto.execute({"op": "recovery_generate"})["code"]
        context = self.crypto.canonical(
            {
                "v": 1,
                "domain": "arteligo.recovery",
                "account_subject": self.subject,
                "recovery_id": identifier,
                "generation": 1,
            }
        )
        plaintext = self.crypto.canonical(recovery)
        try:
            sealed = self.crypto.execute(
                {
                    "op": "recovery_seal",
                    "code": code,
                    "plaintext": encode(plaintext),
                    "aad": encode(context),
                }
            )
            public = public_device({**device, "account_subject": self.subject})
            root_bytes = bytearray(
                b"arteligo-e2ee-device-root-v1\n"
            ) + self.crypto.canonical(public)
            try:
                root_signature = self.crypto.execute(
                    {
                        "op": "sign_bytes",
                        "secret_key": recovery["signing_secret_key"],
                        "bytes": encode(root_bytes),
                    }
                )["signature"]
            finally:
                wipe(root_bytes)
            return {
                "code": code,
                "device": device,
                "root_signature": root_signature,
                "recovery": {
                    "recovery_id": identifier,
                    "generation": 1,
                    "encryption_public_key": recovery["encryption_public_key"],
                    "signing_public_key": recovery["signing_public_key"],
                    "encrypted_bundle": encode(
                        json.dumps(sealed, separators=(",", ":")).encode()
                    ),
                    "public_command": self.crypto.sign(
                        device["signing_secret_key"],
                        "recovery_public",
                        {
                            "recovery_id": identifier,
                            "generation": 1,
                            "encryption_public_key": recovery["encryption_public_key"],
                            "signing_public_key": recovery["signing_public_key"],
                            "account_subject": self.subject,
                        },
                        device["device_id"],
                    ),
                },
            }
        finally:
            wipe(plaintext)
            wipe(context)
            recovery.clear()

    def finish_setup(self, draft: dict[str, Any]) -> None:
        self._device = draft["device"]
        self._persist()
        self.command(
            "e2eeBootstrap",
            "bootstrap",
            {
                "device": self.public,
                "recovery": draft["recovery"],
                "root_signature": draft["root_signature"],
            },
        )
        self.recovery = draft["recovery"]
        self.trust.pin_device(self.public)
        self.trust.pin_recovery(self.subject, self.recovery)
        self._devices[self.device_id] = self.public
        self.state = "approved"

    def enroll(self) -> dict[str, Any]:
        if self.state == "approved":
            raise E2eeError("already_approved")
        if self._device is None or self.state == "revoked":
            self._device = self._new_device()
        self._device.setdefault("challenge", secrets.token_urlsafe(32))
        self._persist()
        pairing = {**self.public, "challenge": self._device["challenge"]}
        self.command("e2eeEnrollDevice", "device_enroll", {**pairing, "envelopes": []})
        self.state = "pending_approval"
        return pairing

    def scopes(self) -> list[dict[str, Any]]:
        self.require_approved()
        projects = self.api.call("e2eeListProjects")["projects"]
        organizations = self.api.call("e2eeListOrganizations")["projects"]
        return organizations + projects

    def prepare_recovery_replacement(self) -> dict[str, Any]:
        self.require_approved()
        if self.recovery is None:
            raise E2eeError("recovery_missing")
        keys = self.crypto.keypair()
        identifier = secrets.token_urlsafe(24)
        generation = self.recovery["generation"] + 1
        code = self.crypto.execute({"op": "recovery_generate"})["code"]
        context = self.crypto.canonical(
            {
                "v": 1,
                "domain": "arteligo.recovery",
                "account_subject": self.subject,
                "recovery_id": identifier,
                "generation": generation,
            }
        )
        plaintext = self.crypto.canonical(keys)
        try:
            sealed = self.crypto.execute(
                {
                    "op": "recovery_seal",
                    "code": code,
                    "plaintext": encode(plaintext),
                    "aad": encode(context),
                }
            )
            public = {
                "recovery_id": identifier,
                "generation": generation,
                "encryption_public_key": keys["encryption_public_key"],
                "signing_public_key": keys["signing_public_key"],
            }
            devices = self.api.call("e2eeListDevices")["devices"]
            self._devices.update({device["device_id"]: device for device in devices})
            roots = []
            for device in devices:
                if device["state"] not in {"approved", "revoked"}:
                    continue
                if device["account_subject"] != self.subject:
                    raise E2eeError("account_mismatch")
                checked = self.trust.verify_device(
                    device, lambda value: self._devices[value]
                )
                message = bytearray(
                    b"arteligo-e2ee-device-root-v1\n"
                ) + self.crypto.canonical(checked)
                try:
                    signature = self.crypto.execute(
                        {
                            "op": "sign_bytes",
                            "secret_key": keys["signing_secret_key"],
                            "bytes": encode(message),
                        }
                    )["signature"]
                finally:
                    wipe(message)
                roots.append({"public_device": checked, "root_signature": signature})
            return {
                "code": code,
                "recovery": {
                    **public,
                    "encrypted_bundle": encode(
                        json.dumps(sealed, separators=(",", ":")).encode()
                    ),
                    "public_command": self.sign(
                        "recovery_public", {**public, "account_subject": self.subject}
                    ),
                    "device_roots": roots,
                },
            }
        finally:
            keys.clear()
            wipe(context)
            wipe(plaintext)

    def replace_recovery(self, draft: dict[str, Any]) -> None:
        self.require_approved()
        self.command("e2eeRotateRecovery", "recovery_rotate", draft["recovery"])
        self.recovery = draft["recovery"]
        self.trust.pin_recovery(self.subject, self.recovery)
        self.reconcile_keys()

    def reconcile_keys(self) -> None:
        for _ in range(3):
            pending = [
                scope
                for scope in self.scopes()
                if scope.get("lifecycle") == "rekey_required"
                and scope.get("role") in {"owner", "editor", "admin"}
            ]
            if not pending:
                return
            for scope in pending:
                try:
                    self.rotate_scope(scope)
                except E2eeError as error:
                    if error.code != "revision_conflict":
                        raise
        if any(
            scope.get("lifecycle") == "rekey_required"
            and scope.get("role") in {"owner", "editor", "admin"}
            for scope in self.scopes()
        ):
            raise E2eeError("rekey_required")

    def rotate_scope(self, scope: dict[str, Any]) -> None:
        self.require_approved()
        identifier, epoch = scope["project_id"], scope["key_epoch"]
        key = self.crypto.key()
        previous = bytearray()
        try:
            body: dict[str, Any] = {"scope_id": identifier, "expected_epoch": epoch}
            if identifier != scope.get("owner_org"):
                previous = self.scope_key(identifier, epoch)
                aad = self.crypto.canonical(
                    {
                        "v": 1,
                        "domain": "arteligo.previous-project-key",
                        "scope_id": identifier,
                        "key_epoch": epoch + 1,
                        "previous_epoch": epoch,
                    }
                )
                try:
                    body["previous_key_ciphertext"] = encode(
                        json.dumps(
                            self.crypto.seal(key, previous, aad), separators=(",", ":")
                        ).encode()
                    )
                finally:
                    wipe(aad)
            audience = self.api.call("e2eeGetRecipients", scope_id=identifier)
            self._devices.update(
                {device["device_id"]: device for device in audience["devices"]}
            )
            envelopes = []
            for device in audience["devices"]:
                checked = self.trust.verify_device(
                    device, lambda value: self._devices[value]
                )
                envelopes.append(
                    self.wrap_key(
                        identifier,
                        epoch + 1,
                        key,
                        recipient=checked["device_id"],
                        kind="device",
                        public_key=checked["encryption_public_key"],
                    )
                )
            for recovery in audience["recoveries"]:
                self.trust.verify_recovery(
                    recovery["account_subject"],
                    recovery,
                    lambda value: self._devices[value],
                )
                envelopes.append(
                    self.wrap_key(
                        identifier,
                        epoch + 1,
                        key,
                        recipient=recovery["recovery_id"],
                        kind="recovery",
                        public_key=recovery["encryption_public_key"],
                    )
                )
            if audience.get("organization_id") is not None:
                organization = audience["organization_id"]
                org_key = self.scope_key(organization, audience["organization_epoch"])
                try:
                    public = self.crypto.execute(
                        {
                            "op": "public_keys",
                            "encryption_secret_key": encode(org_key),
                            "signing_secret_key": encode(bytes(32)),
                        }
                    )
                    envelopes.append(
                        self.wrap_key(
                            identifier,
                            epoch + 1,
                            key,
                            recipient=organization,
                            kind="organization",
                            public_key=public["encryption_public_key"],
                            organization_epoch=audience["organization_epoch"],
                        )
                    )
                finally:
                    wipe(org_key)
            body["envelopes"] = envelopes
            self.command("e2eeRotateScope", "rotate_scope", body, scope_id=identifier)
            self._remember(identifier, epoch + 1, key)
        finally:
            wipe(key)
            wipe(previous)

    def approve(self, pairing: dict[str, Any]) -> dict[str, Any]:
        self.require_approved()
        if pairing.get("account_subject") != self.subject:
            raise E2eeError("account_mismatch")
        public_device(pairing)
        envelopes = []
        for scope in self.scopes():
            key = self.scope_key(scope["project_id"], scope["key_epoch"])
            try:
                envelopes.append(
                    self.wrap_key(
                        scope["project_id"],
                        scope["key_epoch"],
                        key,
                        recipient=pairing["device_id"],
                        kind="device",
                        public_key=pairing["encryption_public_key"],
                    )
                )
            finally:
                wipe(key)
        if self.recovery is None:
            raise E2eeError("recovery_missing")
        recovery_root = {
            key: self.recovery[key]
            for key in (
                "recovery_id",
                "encryption_public_key",
                "signing_public_key",
                "generation",
            )
        }
        approved = self.command(
            "e2eeApproveDevice",
            "device_approve",
            {**pairing, "recovery_root": recovery_root, "envelopes": envelopes},
            device_id=pairing["device_id"],
        )
        self.trust.pin_device(pairing)
        return {
            "trusted_device": self.public,
            "recovery_root": recovery_root,
            "approved_device": public_device(approved),
            "challenge": pairing["challenge"],
        }

    def accept_approval(self, receipt: dict[str, Any]) -> None:
        if self._device is None or receipt.get("challenge") != self._device.get(
            "challenge"
        ):
            raise E2eeError("pairing_mismatch")
        approver, approved, recovery = (
            receipt["trusted_device"],
            receipt["approved_device"],
            receipt["recovery_root"],
        )
        if (
            public_device(approved) != self.public
            or approver.get("account_subject") != self.subject
        ):
            raise E2eeError("pairing_mismatch")
        registered = next(
            (
                device
                for device in self.api.call("e2eeListDevices")["devices"]
                if device["device_id"] == self.device_id
            ),
            None,
        )
        if (
            registered is None
            or public_device(registered) != self.public
            or registered.get("state") != "approved"
        ):
            raise E2eeError("pairing_mismatch")
        certificates = registered.get("certificates", [])
        matching = []
        for certificate in certificates:
            if certificate.get("operation") != "device_approve":
                continue
            signed = certificate.get("signed_command", {})
            if signed.get("device_id") != approver.get("device_id"):
                continue
            body = self.crypto.verify(
                approver["signing_public_key"], "device_approve", signed
            )
            if (
                body.get("challenge") == receipt["challenge"]
                and all(
                    body.get(field) == self.public.get(field)
                    for field in (
                        "device_id",
                        "encryption_public_key",
                        "signing_public_key",
                    )
                )
                and body.get("recovery_root") == recovery
            ):
                matching.append(body)
        if not matching:
            raise E2eeError("invalid_certificate")
        self.trust.pin_device(approver)
        self.trust.pin_recovery(self.subject, recovery)
        self._devices[approver["device_id"]] = approver
        self._devices[self.device_id] = approved
        self._device["paired"] = True
        self._persist()
        self.refresh()
        self.endorse(approver, recovery)

    def restore(self, code: str) -> None:
        recovery = self.recovery
        if recovery is None:
            raise E2eeError("recovery_missing")
        context = self.crypto.canonical(
            {
                "v": 1,
                "domain": "arteligo.recovery",
                "account_subject": self.subject,
                "recovery_id": recovery["recovery_id"],
                "generation": recovery["generation"],
            }
        )
        plaintext = bytearray()
        keys: dict[str, str] = {}
        try:
            opened = self.crypto.execute(
                {
                    "op": "recovery_open",
                    "code": code,
                    "envelope": json.loads(decode(recovery["encrypted_bundle"])),
                    "aad": encode(context),
                }
            )
            plaintext = decode(opened["plaintext"])
            keys = json.loads(plaintext)
            derived = self.crypto.execute(
                {
                    "op": "public_keys",
                    "encryption_secret_key": keys["encryption_secret_key"],
                    "signing_secret_key": keys["signing_secret_key"],
                }
            )
            if any(derived[field] != recovery[field] for field in derived):
                raise E2eeError("recovery_key_changed")
            self._restoring_recovery = (
                recovery["recovery_id"],
                decode(keys["encryption_secret_key"]),
            )
            self.trust.pin_recovery(self.subject, recovery)
            pending = self._device.get("recovery_restore") if self._device else None
            if (
                pending is None
                or pending.get("recovery_id") != recovery["recovery_id"]
                or pending.get("generation") != recovery["generation"]
                or self.state == "revoked"
            ):
                self._clear_keys()
                self._device = self._new_device()
                pending = {
                    "recovery_id": recovery["recovery_id"],
                    "generation": recovery["generation"],
                    "challenge": secrets.token_urlsafe(32),
                }
                self._device["recovery_restore"] = pending
                self._persist()
            self.state = "recovery_pending"
            devices = self.api.call("e2eeListDevices")["devices"]
            registered = next(
                (device for device in devices if device["device_id"] == self.device_id),
                None,
            )
            if registered is None or registered["state"] != "approved":
                self.command(
                    "e2eeRestoreRecovery",
                    "recovery_restore",
                    {
                        "recovery_id": recovery["recovery_id"],
                        "device": self.public,
                        "challenge": pending["challenge"],
                    },
                    secret_key=keys["signing_secret_key"],
                )
            elif public_device(registered) != self.public:
                raise E2eeError("device_key_changed")
            self.trust.pin_device(self.public)
            self._devices[self.device_id] = self.public
            self._devices.update(
                {
                    device["device_id"]: device
                    for device in self.api.call("e2eeListDevices")["devices"]
                }
            )
            self.state = "approved"
            for scope in self.scopes():
                identifier, epoch = scope["project_id"], scope["key_epoch"]
                if epoch == 0 and scope.get("lifecycle") == "uninitialized":
                    continue
                try:
                    key = self._read_key(
                        identifier,
                        epoch,
                        recipient=recovery["recovery_id"],
                        kind="recovery",
                        secret_key=keys["encryption_secret_key"],
                    )
                except E2eeError as error:
                    if (
                        error.code != "key_redistribution_required"
                        or scope.get("participation_policy") != "organization"
                    ):
                        raise
                    key = self.scope_key(identifier, epoch)
                try:
                    self._remember(identifier, epoch, key)
                    envelope = self.wrap_key(
                        identifier,
                        epoch,
                        key,
                        recipient=self.device_id,
                        kind="device",
                        public_key=self.public["encryption_public_key"],
                    )
                    self.command(
                        "e2eeSaveEnvelopes",
                        "envelopes_save",
                        {
                            "scope_id": identifier,
                            "key_epoch": epoch,
                            "envelopes": [envelope],
                        },
                        scope_id=identifier,
                    )
                finally:
                    wipe(key)
            self.reconcile_keys()
            self._device.pop("recovery_restore")
            self._persist()
        finally:
            if self._restoring_recovery is not None:
                wipe(self._restoring_recovery[1])
                self._restoring_recovery = None
            if self._device is not None and self._device.get("recovery_restore"):
                self.state = "recovery_pending"
            wipe(context)
            wipe(plaintext)
            keys.clear()

    def wrap_key(
        self,
        scope: str,
        epoch: int,
        key: bytearray,
        *,
        recipient: str,
        kind: str,
        public_key: str,
        organization_epoch: int | None = None,
    ) -> dict[str, Any]:
        self.require_approved()
        fields = {
            "scope_id": scope,
            "key_epoch": epoch,
            "sender_device_id": self.device_id,
            "recipient_id": recipient,
            "recipient_kind": kind,
        }
        if kind == "organization":
            if (
                type(organization_epoch) is not int
                or not 1 <= organization_epoch <= 2**63 - 1
            ):
                raise E2eeError("invalid_envelope")
            fields["organization_epoch"] = organization_epoch
        elif organization_epoch is not None:
            raise E2eeError("invalid_envelope")
        context = self.crypto.canonical(
            {"v": 1, "domain": "arteligo.scope-key", **fields}
        )
        try:
            sealed = self.crypto.execute(
                {
                    "op": "hpke_auth_seal",
                    "sender_secret_key": self._device["encryption_secret_key"],
                    "recipient_public_key": public_key,
                    "plaintext": encode(key),
                    "info": encode(context),
                    "aad": encode(context),
                }
            )
            return {
                **fields,
                "encapsulated_key": sealed["enc"],
                "ciphertext": sealed["ciphertext"],
            }
        finally:
            wipe(context)

    def device(self, scope: str, identifier: str) -> dict[str, Any]:
        if identifier not in self._devices:
            values = self.api.call("e2eeGetMemberDevices", scope_id=scope)["devices"]
            self._devices.update({item["device_id"]: item for item in values})

        def lookup(value: str) -> dict[str, Any]:
            if value not in self._devices:
                raise E2eeError("untrusted_device")
            return self._devices[value]

        return self.trust.verify_device(lookup(identifier), lookup)

    def _read_key(
        self,
        scope: str,
        epoch: int,
        *,
        recipient: str,
        kind: str,
        secret_key: str | None = None,
        organization_epoch: int | None = None,
    ) -> bytearray:
        values = self.api.call(
            "e2eeGetEnvelopes",
            scope_id=scope,
            epoch=epoch,
            recipient_id=recipient,
            recipient_kind=kind,
        )["envelopes"]
        if len(values) > 1024:
            raise E2eeError("limit_exceeded")
        for envelope in values:
            organization_key = bytearray()
            if kind == "organization":
                bound_epoch = envelope.get("organization_epoch")
                if bound_epoch is None:
                    return self._read_legacy_organization_envelope(
                        scope,
                        epoch,
                        envelope,
                        organization=recipient,
                        current_epoch=organization_epoch,
                    )
                if type(bound_epoch) is not int or not 1 <= bound_epoch <= 2**63 - 1:
                    raise E2eeError("invalid_envelope")
                try:
                    organization_key = self.scope_key(recipient, bound_epoch)
                except E2eeError as error:
                    if error.code == "key_redistribution_required":
                        continue
                    raise
                secret_key = encode(organization_key)
            try:
                return self._open_key_envelope(
                    scope,
                    epoch,
                    envelope,
                    recipient=recipient,
                    kind=kind,
                    secret_key=secret_key,
                )
            finally:
                wipe(organization_key)
        raise E2eeError("key_redistribution_required")

    def _open_key_envelope(
        self,
        scope: str,
        epoch: int,
        envelope: dict[str, Any],
        *,
        recipient: str,
        kind: str,
        secret_key: str | None,
    ) -> bytearray:
        fields = {
            "scope_id": scope,
            "key_epoch": epoch,
            "recipient_id": recipient,
            "recipient_kind": kind,
        }
        if any(envelope.get(field) != value for field, value in fields.items()):
            raise E2eeError("invalid_envelope")
        organization_epoch = envelope.get("organization_epoch")
        if organization_epoch is not None:
            if (
                kind != "organization"
                or type(organization_epoch) is not int
                or not 1 <= organization_epoch <= 2**63 - 1
            ):
                raise E2eeError("invalid_envelope")
            fields["organization_epoch"] = organization_epoch
        sender = self.device(scope, envelope["sender_device_id"])
        context = self.crypto.canonical(
            {
                "v": 1,
                "domain": "arteligo.scope-key",
                **fields,
                "sender_device_id": sender["device_id"],
            }
        )
        try:
            opened = self.crypto.execute(
                {
                    "op": "hpke_auth_open",
                    "recipient_secret_key": secret_key,
                    "sender_public_key": sender["encryption_public_key"],
                    "info": encode(context),
                    "aad": encode(context),
                    "envelope": {
                        "v": 1,
                        "suite": "HPKE-Auth-X25519-HKDF-SHA256-AES256GCM",
                        "enc": envelope["encapsulated_key"],
                        "ciphertext": envelope["ciphertext"],
                    },
                }
            )
            key = decode(opened["plaintext"])
            if len(key) != 32:
                wipe(key)
                raise E2eeError("invalid_envelope")
            return key
        finally:
            wipe(context)

    def _read_legacy_organization_envelope(
        self,
        scope: str,
        epoch: int,
        envelope: dict[str, Any],
        *,
        organization: str,
        current_epoch: int | None,
    ) -> bytearray:
        if type(current_epoch) is not int or not 1 <= current_epoch <= 2**63 - 1:
            raise E2eeError("invalid_envelope")

        def open_project_key(key: bytearray) -> bytearray:
            return self._open_key_envelope(
                scope,
                epoch,
                envelope,
                recipient=organization,
                kind="organization",
                secret_key=encode(key),
            )

        current_key = bytearray()
        try:
            current_key = self.scope_key(organization, current_epoch)
            return open_project_key(current_key)
        except E2eeError as error:
            if error.code not in {
                "authentication_failed",
                "key_redistribution_required",
            }:
                raise
        finally:
            wipe(current_key)

        recipients = [(self.device_id, "device", self._device["encryption_secret_key"])]
        if self._restoring_recovery is not None:
            recipients.append(
                (
                    self._restoring_recovery[0],
                    "recovery",
                    encode(self._restoring_recovery[1]),
                )
            )
        for recipient, kind, secret_key in recipients:
            history = self.api.call(
                "e2eeGetEnvelopes",
                scope_id=organization,
                recipient_id=recipient,
                recipient_kind=kind,
            )["envelopes"]
            if len(history) > 1024:
                raise E2eeError("limit_exceeded")
            if any(
                type(item.get("key_epoch")) is not int
                or not 1 <= item["key_epoch"] <= 2**63 - 1
                for item in history
            ):
                raise E2eeError("invalid_envelope")
            for item in sorted(
                history, key=lambda value: value["key_epoch"], reverse=True
            ):
                if item["key_epoch"] >= current_epoch:
                    continue
                key = self._open_key_envelope(
                    organization,
                    item["key_epoch"],
                    item,
                    recipient=recipient,
                    kind=kind,
                    secret_key=secret_key,
                )
                try:
                    return open_project_key(key)
                except E2eeError as error:
                    if error.code != "authentication_failed":
                        raise
                finally:
                    wipe(key)
        raise E2eeError("key_redistribution_required")

    def scope_key(self, scope: str, epoch: int) -> bytearray:
        self.require_approved()
        cached = self._scope_keys.get((scope, epoch))
        if cached is not None:
            return bytearray(cached)
        try:
            key = self._read_key(
                scope,
                epoch,
                recipient=self.device_id,
                kind="device",
                secret_key=self._device["encryption_secret_key"],
            )
        except E2eeError as error:
            if error.code != "key_redistribution_required":
                raise
            metadata = next(
                (item for item in self.scopes() if item["project_id"] == scope), None
            )
            if metadata is None or epoch > metadata["key_epoch"]:
                raise E2eeError("key_redistribution_required") from None
            current = metadata["key_epoch"]
            if epoch < current:
                if metadata.get("owner_org") == scope:
                    raise E2eeError("key_redistribution_required") from None
                key = self._previous_key(scope, epoch, current)
            elif metadata.get(
                "participation_policy"
            ) == "organization" and metadata.get("owner_org"):
                org_id = metadata["owner_org"]
                organization = next(
                    (
                        item
                        for item in self.api.call("e2eeListOrganizations")["projects"]
                        if item["project_id"] == org_id
                    ),
                    None,
                )
                if organization is None:
                    raise E2eeError("organization_approval_required") from None
                key = self._read_key(
                    scope,
                    epoch,
                    recipient=org_id,
                    kind="organization",
                    organization_epoch=organization["key_epoch"],
                )
            else:
                raise
        self._remember(scope, epoch, key)
        return key

    def _previous_key(self, scope: str, target: int, current: int) -> bytearray:
        if current - target > 4096:
            raise E2eeError("epoch_limit_exceeded")
        links: dict[int, dict[str, Any]] = {}
        after = target
        for _ in range(16):
            page = self.api.call(
                "e2eeGetEpochs", scope_id=scope, after_epoch=after, limit=256
            )["epochs"]
            for link in page:
                value = link["key_epoch"]
                if value <= after or value in links:
                    raise E2eeError("invalid_epoch_chain")
                links[value] = link
            if not page or max(links) >= current:
                break
            after = max(links)
        key = self.scope_key(scope, current)
        try:
            for epoch in range(current, target, -1):
                link = links.get(epoch)
                if link is None:
                    raise E2eeError("incomplete_epoch_chain")
                signed = link["signed_command"]
                device = self.device(scope, signed["device_id"])
                body = self.crypto.verify(
                    device["signing_public_key"], "rotate_scope", signed
                )
                if (
                    body.get("scope_id") != scope
                    or body.get("expected_epoch") != epoch - 1
                    or body.get("previous_key_ciphertext")
                    != link["previous_key_ciphertext"]
                ):
                    raise E2eeError("invalid_epoch_chain")
                aad = self.crypto.canonical(
                    {
                        "v": 1,
                        "domain": "arteligo.previous-project-key",
                        "scope_id": scope,
                        "key_epoch": epoch,
                        "previous_epoch": epoch - 1,
                    }
                )
                try:
                    previous = self.crypto.open(
                        key, json.loads(decode(link["previous_key_ciphertext"])), aad
                    )
                    if len(previous) != 32:
                        wipe(previous)
                        raise E2eeError("invalid_epoch_chain")
                    wipe(key)
                    key = previous
                    self._remember(scope, epoch - 1, key)
                finally:
                    wipe(aad)
            return bytearray(key)
        finally:
            wipe(key)

    def _remember(self, scope: str, epoch: int, key: bytearray) -> None:
        previous = self._scope_keys.pop((scope, epoch), None)
        if previous is not None:
            wipe(previous)
        self._scope_keys[(scope, epoch)] = bytearray(key)
        while len(self._scope_keys) > 128:
            wipe(self._scope_keys.pop(next(iter(self._scope_keys))))

    def _clear_keys(self) -> None:
        for key in self._scope_keys.values():
            wipe(key)
        self._scope_keys.clear()

    def lock(self) -> None:
        self._clear_keys()
        if self._device is not None:
            self._device.clear()
        self._device = None
        self._devices.clear()
        self.state = "locked"
