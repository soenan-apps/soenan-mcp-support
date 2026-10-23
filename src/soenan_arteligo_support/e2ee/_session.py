from __future__ import annotations

import hashlib
import json
import secrets
import threading
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from ._admission import AdmissionAttempt, AdmissionResult, ScopeAcquisition, admission_message
from ._api import E2eeAPI
from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe
from ._storage import ProfileSecureStore
from ._trust import KeyTrust, public_device
from ._participants import ScopeParticipants
from ._owner_access import CurrentCreatorQualification, OwnerAccess
from ._owner_protocol import SignedEvidence
from ._owner_envelopes import OWNER_KEY_PROOF
from ._signed_commands import PublicationJournal, SavedCommand, UncertainCommand
from ._root_admission import RootAdmissions, open_recovery_code
from ._root_replacement import RootReplacements
from ._device_approval import DeviceApprovals


class _ScopeResponse(dict[str, Any]):
    def __init__(self, response: dict[str, Any], owners: dict[str, dict[str, Any]]):
        super().__init__(response)
        self.owners = owners


class DeviceSession:
    def __init__(
        self,
        api: E2eeAPI,
        crypto: E2eeCrypto,
        store: ProfileSecureStore,
        *,
        origin: str,
        subject: str,
    ):
        self._api, self.crypto, self.store = api, crypto, store
        self._credentials = api.credentials
        self.subject = subject
        namespace = hashlib.sha256((origin + "\n" + subject).encode()).hexdigest()
        self._storage_key = "device:" + namespace
        self.trust = KeyTrust(
            crypto, store, namespace, origin=origin, owner_subject=subject
        )
        self._device: dict[str, Any] | None = None
        self._device_snapshot: str | None = None
        self._device_observed = False
        self._devices: dict[str, dict[str, Any]] = {}
        self._scope_device_material: dict[tuple[str, str], dict[str, Any]] = {}
        self._scope_keys: dict[tuple[str, int], bytearray] = {}
        self._scope_metadata: dict[str, dict[str, Any]] = {}
        self._key_bundles: dict[str, dict[str, Any]] = {}
        self._scope_state_lock = threading.RLock()

        self._key_admission: AdmissionAttempt | None = None
        self._last_key_acquisition_progress: dict[str, Any] = {
            "available": [], "pending": [], "remaining": {},
        }
        self._device_approval = "unregistered"
        self.recovery: dict[str, Any] | None = None
        self.state = "needs_setup"
        self._participants = ScopeParticipants(self)
        self.trust.participants = self._participants
        self.owner_access = OwnerAccess(self)
        self.trust.certificate_projection = self.owner_access.account.projection
        self.trust.projected_device = self.owner_access.current.projected_device
        self.publications = PublicationJournal(self)
        self.root_admissions = RootAdmissions(self)
        self.root_replacements = RootReplacements(self)
        self.device_approvals = DeviceApprovals(self)

    def _check_current(self) -> None:
        try:
            self._credentials.check_current()
            if self._device_observed:
                with self.store.credential(self._storage_key) as item:
                    if item.read() != self._device_snapshot:
                        raise E2eeError("device_session_superseded")
        except E2eeError as error:
            if error.code in {"authentication_superseded", "device_session_superseded"}:
                self.lock()
            raise

    def call(
        self, operation: str, *, body: dict[str, Any] | None = None, **parameters: Any
    ) -> _ScopeResponse:
        scope = parameters.get("scope_id", parameters.get("project_id"))
        identifiers = (
            [scope] if isinstance(scope, str) else
            [item["scope_id"] for item in (body or {}).get("scopes", [])]
            if operation == "e2eeReadRecords" else []
        )
        with self._scope_state_lock:
            for identifier in identifiers:
                self._scope_metadata.setdefault(identifier, {})
            captured = dict(self._scope_metadata)
        try:
            response = self._api.call(operation, body=body, **parameters)
        except E2eeError as error:
            if error.code == "authentication_superseded":
                self.lock()
            elif error.code == "project_access_denied" and scope in captured:
                self._deny_scope(scope, captured[scope])
            raise
        self._check_current()
        devices = response.get("devices")
        if isinstance(devices, list):
            if isinstance(scope, str):
                self._remember_device_material(scope, devices)
            elif operation == "e2eeListDevices":
                self._remember_device_material(None, devices)
        context = response.get("key_context") or {}
        for item in (
            response.get("scopes", []) + response.get("key_scopes", [])
            + context.get("scopes", []) + context.get("key_scopes", [])
        ):
            identifier = item.get("scope_id")
            if item.get("error") == "project_access_denied" and identifier in captured:
                self._deny_scope(identifier, captured[identifier])
        return _ScopeResponse(response, captured)

    def _deny_scope(self, scope: str, captured: dict[str, Any] | None) -> None:
        with self._scope_state_lock:
            if self._scope_metadata.get(scope) is not captured:
                return
            self._scope_metadata.pop(scope, None)
            self._key_bundles.pop(scope, None)
            self.trust.forget_scope(scope)
            for identity in list(self._scope_device_material):
                if identity[0] == scope:
                    self._scope_device_material.pop(identity)
            for identity in list(self._scope_keys):
                if identity[0] == scope:
                    wipe(self._scope_keys.pop(identity))

    def _scope_owner(self, scope: str) -> dict[str, Any]:
        with self._scope_state_lock:
            return self._scope_metadata.setdefault(scope, {})

    def _check_scope(self, scope: str, owner: dict[str, Any]) -> None:
        self._check_current()
        with self._scope_state_lock:
            if self._scope_metadata.get(scope) is not owner:
                raise E2eeError("scope_read_superseded")

    def _response_scope(self, scope: str, response: _ScopeResponse) -> dict[str, Any]:
        self._check_current()
        with self._scope_state_lock:
            owner = response.owners.get(scope)
            if owner is None:
                if scope in self._scope_metadata:
                    raise E2eeError("scope_read_superseded")
                owner = self._scope_owner(scope)
                response.owners[scope] = owner
            if self._scope_metadata.get(scope) is not owner:
                raise E2eeError("scope_read_superseded")
            return owner

    def _adopt_scope(
        self, scope: str, owner: dict[str, Any], metadata: dict[str, Any]
    ) -> None:
        with self._scope_state_lock:
            if self._scope_metadata.get(scope) is not owner:
                raise E2eeError("scope_read_superseded")
            if owner.get("key_epoch") != metadata["key_epoch"]:
                self._key_bundles.pop(scope, None)
            owner.clear()
            owner.update(metadata)

    @property
    def device_id(self) -> str:
        return self._device["device_id"] if self._device else ""

    @property
    def public(self) -> dict[str, Any]:
        if self._device is None:
            raise E2eeError("device_approval_required")
        return public_device({**self._device, "account_subject": self.subject})

    def _new_device(self) -> dict[str, Any]:
        self._check_current()
        device = {**self.crypto.keypair(), "device_id": secrets.token_urlsafe(24)}
        for name in ("project_creation", "owner_access", "owner_root_provenance", "root_scope_generations",
                     "owner_source_observations", "owner_provisional_root_evidence",
                     "device_approvals", "scope_initializations", "scope_rotations", "record_publications",
                     RootAdmissions.HISTORY_COLLECTION, RootReplacements.HISTORY_COLLECTION):
            pending = (self._device or {}).get(name)
            if pending is not None:
                device[name] = pending
        return device

    @property
    def device_approval(self) -> str:
        return self._device_approval

    @property
    def key_acquisition_progress(self) -> dict[str, Any]:
        progress = (
            self._key_admission.progress() if self._key_admission is not None
            else self._last_key_acquisition_progress
        )
        return {
            "available": list(progress["available"]),
            "pending": list(progress["pending"]),
            "remaining": dict(progress["remaining"]),
        }

    def _persist(self) -> None:
        self._check_current()
        if self._device is None:
            raise E2eeError("device_approval_required")
        self._device.pop("completed_commands", None)
        if self._key_admission is None:
            self._device.pop("key_admission", None)
        else:
            self._device["key_admission"] = self._key_admission.document()
        value = json.dumps(self._device, separators=(",", ":"))
        try:
            with self.store.credential(self._storage_key) as item:
                if item.read() != self._device_snapshot:
                    raise E2eeError("device_session_superseded")
                if value != self._device_snapshot:
                    item.replace(value)
                self._device_snapshot = value
                self._device_observed = True
        except E2eeError as error:
            if error.code == "device_session_superseded":
                self.lock()
            raise

    def refresh(self) -> str:
        self._check_current()
        self.state = "pending_approval"
        self._device_approval = "unregistered"
        with self.store.credential(self._storage_key) as item:
            saved = item.read()
        device = None
        attempt = None
        if saved is not None:
            device = json.loads(saved)
            if not isinstance(device, dict):
                raise TypeError("Stored device must be an object")
            derived = self.crypto.execute(
                {
                    "op": "public_keys",
                    "encryption_secret_key": device["encryption_secret_key"],
                    "signing_secret_key": device["signing_secret_key"],
                }
            )
            if any(derived[field] != device[field] for field in derived):
                raise E2eeError("device_key_changed")
            if device.get("key_admission") is not None:
                attempt = AdmissionAttempt.load(
                    device["key_admission"], self.crypto, self.subject,
                    public_device({**device, "account_subject": self.subject}),
                )
        self._check_current()
        try:
            with self.store.credential(self._storage_key) as item:
                if item.read() != saved:
                    raise E2eeError("device_session_superseded")
                self._device = device
                self._key_admission = attempt
                self._device_snapshot = saved
                self._device_observed = True
        except E2eeError as error:
            if error.code == "device_session_superseded":
                self.lock()
            raise
        if self._device is not None:
            self.trust.pin_device(self.public)
        try:
            self.recovery = self.call("e2eeGetRecovery")
        except E2eeError as error:
            if error.code != "not_found":
                raise
            self.recovery = None
        if self.recovery is not None:
            if self.recovery.get("account_subject", self.subject) != self.subject:
                raise E2eeError("recovery_subject_mismatch")
            self.trust.set_endorsements(self.call("e2eeGetTrust")["statements"])
        if self._device is None:
            self.state = "needs_setup" if self.recovery is None else "pending_approval"
            return self.state
        values = self.call("e2eeListDevices")["devices"]
        self._devices = {value["device_id"]: value for value in values}
        current = self._devices.get(self.device_id)
        if current is None:
            self.state = "needs_setup" if self.recovery is None else "pending_approval"
        else:
            if public_device(current) != self.public:
                raise E2eeError("device_key_changed")
            self.state = current["state"]
            self._device_approval = current["state"]
        observed_state = self.state
        self.state = (
            "pending_approval" if observed_state == "approved" else observed_state
        )
        if observed_state != "approved":
            self._clear_keys()
            if observed_state == "revoked":
                self._end_key_admission(revoked=True)
                return self.state
        elif self.recovery is not None:
            try:
                self.trust.verify_current_recovery(
                    self.subject,
                    self.recovery,
                    self._current_device_lookup(None, values),
                    recovery_lookup=lambda identifier: self._recovery_material(
                        None, identifier
                    ),
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
            self.root_admissions.complete()
            self.owner_access.recovery.accept_device_backup(current)
        if self._key_admission is not None:
            self.state = "key_acquisition_pending"
        return self.state

    def require_approved(self) -> None:
        self._check_current()
        if (
            self._device is None or self.device_approval != "approved"
            or self.state not in {"approved", "key_acquisition_pending"}
        ):
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
            if device["account_subject"] == self.subject:
                self.trust.confirm_recovery(self.subject, recovery)
            else:
                self.trust.pin_recovery(device["account_subject"], recovery)

    def confirm_project_owner(
        self, project_id: str, invitation: str, *, invitation_id: str | None = None,
    ) -> dict[str, str]:
        """Confirm an owner using an invitation received directly from that owner."""
        from ._invitations import confirm_project_owner

        return confirm_project_owner(self, project_id, invitation, invitation_id=invitation_id)

    def _scope_owner_statement(
        self, scope: str, device: dict[str, Any], recovery: dict[str, Any],
    ) -> dict[str, str]:
        self.require_approved()
        document = {
            field: recovery[field] for field in (
                "recovery_id", "generation", "encryption_public_key", "signing_public_key",
            )
        }
        root = self._participants._root(document, device["account_subject"])
        self.trust._root_identity(root.subject, root.document(), scope)
        return self.sign("peer_trust", {
            "scope_id": scope, "trusted_device": public_device(device), "recovery_root": document,
        })

    def _record_scope_owner(
        self, scope: str, device: dict[str, Any], recovery: dict[str, Any],
        qualification: CurrentCreatorQualification | None = None,
    ) -> None:
        self._save_scope_owner(scope, self._scope_owner_statement(scope, device, recovery), qualification)

    def _save_scope_owner(self, scope: str, statement: dict[str, str],
                          qualification: CurrentCreatorQualification | None = None) -> None:
        self.require_approved()
        if statement.get("device_id") != self.device_id:
            raise E2eeError("invalid_certificate")
        body = self.crypto.verify(self.public["signing_public_key"], "peer_trust", statement)
        if body.get("scope_id") != scope:
            raise E2eeError("participant_scope_mismatch")
        device = body["trusted_device"]
        owner = self._scope_owner(scope)
        root = self._participants._root(body["recovery_root"], device["account_subject"])
        self.owner_access.assert_project_creator(scope, root, device=device, qualification=qualification)
        self.trust._root_identity(root.subject, root.document(), scope)
        self.call("e2eeSaveTrust", body=statement)
        self._check_scope(scope, owner)
        self.trust.pin_scope_device(scope, device)
        self.trust.pin_scope_recovery(scope, root.subject, root.document())
        self.trust.set_endorsements([*self.trust._endorsements, statement])
        if qualification is not None:
            self.trust._confirm_head(root, scope, current_device=qualification.current.device)
        self.owner_access.recovery.remember_confirmation(scope, statement)

    def sign(
        self, operation: str, body: Mapping[str, Any], *, secret_key: str | None = None
    ) -> dict[str, str]:
        self._check_current()
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
        result = self.call(
            api_operation, body=self.sign(operation, body, secret_key=secret_key),
            **parameters,
        )
        if operation == "device_revoke":
            self.trust.remember_revoked(body["device_id"])
            self.owner_access.after_custody_change()
        return result

    def prepare_setup(self) -> dict[str, Any]:
        self._check_current()
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
            self._device = device
            self.root_admissions.prepare({
                "recovery_id": identifier, "generation": 1,
                "encryption_public_key": recovery["encryption_public_key"],
                "signing_public_key": recovery["signing_public_key"],
            }, recovery)
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
        self._check_current()
        pending = (self._device or {}).get("project_creation")
        self._device = dict(draft["device"])
        if pending is not None:
            self._device["project_creation"] = pending
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
        self.trust.confirm_recovery(
            self.subject, self.recovery, current_device=self.public
        )
        self._devices[self.device_id] = self.public
        self._device_approval = "approved"
        self.state = "approved"
        self.root_admissions.complete()

    def reanchor(self) -> dict[str, Any]:
        """Replace this profile's device keys after explicit out-of-band approval."""
        self._check_current()
        if not self.trust.has_confirmed_head(self.subject):
            raise E2eeError("recovery_missing")
        if self._key_admission is not None:
            raise E2eeError("key_acquisition_pending")
        self._device = self._new_device()
        self._device_approval = "unregistered"
        self.state = "pending_approval"
        self._persist()
        return self.enroll()

    def enroll(self) -> dict[str, Any]:
        self._check_current()
        if self.device_approval == "approved":
            raise E2eeError("already_approved")
        if self._key_admission is not None:
            raise E2eeError("key_acquisition_pending")
        if self._device is None or self.state == "revoked":
            self._device = self._new_device()
        self._device.setdefault("challenge", secrets.token_urlsafe(32))
        self._persist()
        pairing = {**self.public, "challenge": self._device["challenge"]}
        self.command("e2eeEnrollDevice", "device_enroll", {**pairing, "envelopes": []})
        self._device_approval = "pending"
        self.state = "pending_approval"
        return pairing

    def scopes(self) -> list[dict[str, Any]]:
        self.require_approved()
        projects = self.call("e2eeListProjects")
        organizations = self.call("e2eeListOrganizations")
        values = organizations["projects"] + projects["projects"]
        for response in (organizations, projects):
            for value in response["projects"]:
                scope = value["project_id"]
                self._adopt_scope(scope, self._response_scope(scope, response), value)
        return values

    def scope_metadata(self, scope: str, *, refresh: bool = False) -> dict[str, Any]:
        self.require_approved()
        owner = self._scope_owner(scope)
        if refresh or not owner:
            response = self.call("e2eeGetScope", scope_id=scope)
            self._check_scope(scope, owner)
            value = response
            if value.get("project_id") != scope:
                raise E2eeError("invalid_record_scope")
            self._adopt_scope(scope, owner, value)
        return owner

    def receive_read_bundle(self, bundle: dict[str, Any], response: _ScopeResponse) -> None:
        self._check_current()
        scope = bundle["scope_id"]
        metadata = bundle["metadata"]
        if metadata.get("project_id") != scope:
            raise E2eeError("invalid_record_scope")
        owner = self._response_scope(scope, response)
        with self._scope_state_lock:
            self._adopt_scope(scope, owner, metadata)
            self._remember_device_material(scope, bundle.get("devices", []))
            self.trust.remember_recoveries(bundle.get("recoveries", []), scope)
            self._key_bundles[scope] = {
                field: bundle.get(field, []) for field in ("envelopes", "epochs")
            }


    def prepare_recovery_replacement(self) -> dict[str, Any]:
        return self.root_replacements.prepare()

    @property
    def recovery_replacement_pending(self) -> bool:
        return (
            self._device is not None
            and self._device.get("recovery_replacement") is not None
        )


    def resume_recovery_replacement(self, code: str) -> None:
        self.root_replacements.resume(code)


    def replace_recovery(self, draft: dict[str, Any]) -> None:
        self.root_replacements.apply(draft)

    def reconcile_keys(self) -> None:
        self._check_current()
        for _ in range(3):
            pending = [
                scope
                for scope in self.scopes()
                if scope["key_state"] == "rekey_required"
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
            scope["key_state"] == "rekey_required"
            and scope.get("role") in {"owner", "editor", "admin"}
            for scope in self.scopes()
        ):
            raise E2eeError("rekey_required")

    def rotate_scope(self, scope: dict[str, Any]) -> None:
        self.require_approved()
        identifier, epoch = scope["project_id"], scope["key_epoch"]
        pending = self.publications.pending("scope_rotations", identifier)
        if pending is not None:
            self._resume_scope_rotation(identifier, pending)
            return
        owner = self._scope_owner(identifier)
        organization_id = scope.get("owner_org")
        authority = (
            self.owner_access.authority(organization_id)
            if organization_id is not None else None
        )
        if authority is not None and identifier == organization_id and authority.owner_subject != self.subject:
            self.owner_access.organizations.qualify_admin(identifier, self.public, authority)
        if (
            scope.get("participation_policy") == "organization"
            and organization_id is not None
            and organization_id != identifier
        ):
            organization = self.scope_metadata(organization_id, refresh=True)
            if organization["key_state"] == "rekey_required":
                if organization.get("role") not in {"owner", "editor", "admin"}:
                    raise E2eeError("rekey_required")
                self.rotate_scope(organization)
                organization = self.scope_metadata(organization_id, refresh=True)
            if organization["key_state"] != "ready":
                raise E2eeError("rekey_required")
            self._check_scope(identifier, owner)
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
            audience = self.call("e2eeGetRecipients", scope_id=identifier)
            recipients = self.trust.current_recipients(
                identifier, audience,
                self._current_device_lookup(identifier, audience["devices"]),
                lambda value: self._recovery_material(identifier, value),
            )
            if authority is not None and identifier == organization_id:
                self.owner_access.organizations.qualify_recipients(identifier, recipients, authority)
            maintenance = (
                self.owner_access.maintenance_issuer(authority)
                if authority is not None and authority.owner_subject == self.subject else None
            )
            wrap_key = maintenance.wrap if maintenance is not None else self.wrap_key
            envelopes = []
            for checked in recipients.devices:
                if authority is not None and checked["account_subject"] == authority.owner_subject:
                    continue
                envelopes.append(
                    wrap_key(
                        identifier,
                        epoch + 1,
                        key,
                        recipient=checked["device_id"],
                        kind="device",
                        public_key=checked["encryption_public_key"],
                    )
                )
            for head in recipients.roots:
                recovery = head.identity
                if authority is not None and recovery.subject == authority.owner_subject:
                    continue
                envelopes.append(
                    wrap_key(
                        identifier,
                        epoch + 1,
                        key,
                        recipient=recovery.identifier,
                        kind="recovery",
                        public_key=recovery.encryption_key,
                    )
                )
            if audience.get("organization_id") is not None:
                organization = audience["organization_id"]
                with self.owner_access.publications.key(organization, audience["organization_epoch"], authority) as organization_key:
                    org_key = organization_key.key
                    public = self.crypto.execute(
                        {
                            "op": "public_keys",
                            "encryption_secret_key": encode(org_key),
                            "signing_secret_key": encode(bytes(32)),
                        }
                    )
                    envelopes.append(
                        wrap_key(
                            identifier,
                            epoch + 1,
                            key,
                            recipient=organization,
                            kind="organization",
                            public_key=public["encryption_public_key"],
                            organization_epoch=audience["organization_epoch"],
                        )
                    )
            body["envelopes"] = envelopes
            if authority is not None:
                body["owner_authority"] = authority.to_dict()
                body["envelopes"].append(wrap_key(identifier, epoch + 1, key,
                    recipient=authority.key_id, kind="owner", public_key=authority.public_key,
                    owner_key_epoch=authority.key_epoch, owner_binding_digest=authority.binding_digest))
            if maintenance is not None:
                body["owner_key_proof"] = OWNER_KEY_PROOF
            operation = "owner_rotate_scope" if maintenance is not None else "rotate_scope"
            pending = SavedCommand(
                operation, UncertainCommand(SignedEvidence.parse(self.sign(operation, body))),
                key=encode(key), epoch=epoch + 1,
            )
            self.publications.save("scope_rotations", identifier, pending)
            self._resume_scope_rotation(identifier, pending)
        finally:
            wipe(key)
            wipe(previous)

    def _resume_scope_rotation(self, scope: str, pending: SavedCommand) -> None:
        if pending.operation not in {"owner_rotate_scope", "rotate_scope"}:
            raise E2eeError("invalid_scope_rotation")
        body = pending.command.body
        if pending.operation == "owner_rotate_scope" and body.get("owner_key_proof") != OWNER_KEY_PROOF:
            raise E2eeError("unsupported_owner_key_proof")
        if (pending.key is None or type(pending.epoch) is not int
                or body.get("scope_id") != scope or body.get("expected_epoch") != pending.epoch - 1):
            raise E2eeError("invalid_scope_rotation")
        api = "e2eeRotateOwnerScope" if pending.operation == "owner_rotate_scope" else "e2eeRotateScope"
        self.publications.submit(
            "scope_rotations", scope, pending,
            lambda command: self.call(api, scope_id=scope, body=command),
        )
        key = decode(pending.key)
        try:
            if len(key) != 32:
                raise E2eeError("invalid_scope_rotation")
            self._remember(scope, pending.epoch, key, owner=self._scope_owner(scope))
        finally:
            wipe(key)
        self.publications.finish("scope_rotations", scope, pending)

    def approve(self, pairing: dict[str, Any]) -> dict[str, Any]:
        return self.device_approvals.approve(pairing)

    def accept_approval(self, receipt: dict[str, Any]) -> None:
        self._check_current()
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
                for device in self.call("e2eeListDevices")["devices"]
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
        self.trust.confirm_recovery(
            self.subject, recovery, current_device=approved
        )
        self._devices[approver["device_id"]] = approver
        self._devices[self.device_id] = approved
        self._device["paired"] = True
        self._persist()
        self.refresh()
        self.endorse(approver, recovery)

    def add_by_key(self, code: str) -> AdmissionResult:
        self._check_current()
        previously_revoked = self.device_approval == "revoked"
        self.refresh()
        if self.device_approval == "revoked" and not previously_revoked:
            raise E2eeError("device_revoked")
        attempt = self._key_admission
        recovery = self.recovery
        if recovery is None:
            raise E2eeError("recovery_missing")
        has_confirmed_head = self.trust._confirmed_head(self.subject) is not None
        if attempt is not None and self.device_approval != "approved" and any(
            recovery.get(name) != value for name, value in attempt.root.items()
        ):
            if not has_confirmed_head:
                raise E2eeError("untrusted_recovery")
            current = self._admission_current_device()
            if current is None or current["state"] != "approved":
                self._end_key_admission()
                raise E2eeError("key_admission_superseded")
        keys: dict[str, str] = {}
        try:
            keys = open_recovery_code(self.crypto, self.subject, recovery, code)
            self.trust.confirm_private_recovery(recovery, keys)
            self.trust.confirm_recovery(self.subject, recovery)
            if attempt is None:
                if self._device is None or self.device_approval == "revoked":
                    self._clear_keys()
                    self._device = self._new_device()
                    self._device_approval = "unregistered"
                proof = self.root_admissions.prepare(recovery, keys)
                attempt = AdmissionAttempt(
                    secrets.token_urlsafe(24), self.subject, proof.root,
                    proof.command.body["challenge"], proof.command.document(),
                )
                self._key_admission = attempt
                self.state = "key_acquisition_pending"
                self._persist()
            if self._device.get("root_admission") is None:
                self._device["root_admission"] = {
                    "root": attempt.root, "signed_command": attempt.signed_command,
                }
                self._persist()
            self.root_admissions.complete()
            self._admission_current_device(require_approved=True)
            self.trust.pin_device(self.public)
            self.state = "key_acquisition_pending"
            self.owner_access.recovery.restore_root(keys["encryption_secret_key"])
            self.owner_access.maintain()
            attempt.synchronize(self.scopes())
            self._persist()
            for scope in list(attempt.scopes):
                self._acquire_admission_scope(scope, attempt, recovery, keys)
            for scope in self.scopes():
                self.root_admissions.publish_history(scope, recovery, keys["encryption_secret_key"])
            attempt.synchronize(self.scopes())
            self._persist()
            for scope, progress in list(attempt.scopes.items()):
                if progress.state == "available":
                    try:
                        self._verify_admission_scope(scope, progress)
                    except E2eeError as error:
                        self._admission_scope_failure(scope, attempt, error)
            attempt.synchronize(self.scopes())
            self._admission_current_device(require_approved=True)
            self._last_key_acquisition_progress = attempt.progress()
            if self._last_key_acquisition_progress["pending"]:
                result = AdmissionResult.KEY_ACQUISITION_PENDING
            else:
                self._key_admission = None
                self.state = "approved"
                result = AdmissionResult.READY
            self._persist()
            return result
        except E2eeError as error:
            if error.code == "device_revoked":
                if self.state != "revoked":
                    self._end_key_admission(revoked=True)
            elif self._device is not None and self.state != "locked":
                try:
                    self._admission_current_device()
                except E2eeError as observation:
                    if observation.code == "device_revoked":
                        raise
            raise
        finally:
            if self._key_admission is not None and self.state not in {"revoked", "locked"}:
                self.state = "key_acquisition_pending"
            if isinstance(keys, dict):
                keys.clear()
            code = ""

    def _end_key_admission(self, *, revoked: bool = False) -> None:
        self._key_admission = None
        self._last_key_acquisition_progress = {
            "available": [], "pending": [], "remaining": {},
        }
        self._clear_keys()
        if revoked:
            self._device_approval = "revoked"
        self.state = "revoked" if revoked else "pending_approval"
        if self._device is not None:
            self._persist()

    def _admission_current_device(
        self, *, require_approved: bool = False
    ) -> dict[str, Any] | None:
        values = self.call("e2eeListDevices")["devices"]
        self._devices.update({device["device_id"]: device for device in values})
        current = next((device for device in values if device["device_id"] == self.device_id), None)
        if current is not None and current["state"] == "revoked":
            self._end_key_admission(revoked=True)
            raise E2eeError("device_revoked")
        if current is not None and public_device(current) != self.public:
            raise E2eeError("device_key_changed")
        self._device_approval = current["state"] if current is not None else "unregistered"
        if require_approved and self.device_approval != "approved":
            self._clear_keys()
            raise E2eeError("device_admission_unconfirmed")
        return current

    def _admission_device_key(self, scope: str, epoch: int) -> bytearray:
        organization = self.scope_metadata(scope).get("owner_org")
        if organization and self.owner_access.authority(organization, active=False).owner_subject == self.subject:
            return self.owner_access.read_key(scope, epoch)
        envelopes = self.call(
            "e2eeGetEnvelopes", scope_id=scope, epoch=epoch,
            recipient_id=self.device_id, recipient_kind="device",
        )["envelopes"]
        if not envelopes:
            raise E2eeError("key_redistribution_required")
        return self._open_key_envelope(
            scope, epoch, envelopes[0], recipient=self.device_id, kind="device",
            secret_key=self._device["encryption_secret_key"],
        )

    def _verify_admission_scope(self, scope: str, progress: ScopeAcquisition) -> None:
        metadata = self.scope_metadata(scope, refresh=True)
        if metadata["key_epoch"] != progress.epoch:
            raise E2eeError("revision_conflict")
        owner = self._scope_owner(scope)
        key = self._admission_device_key(scope, progress.epoch)
        try:
            if self.scope_metadata(scope, refresh=True)["key_epoch"] != progress.epoch:
                raise E2eeError("revision_conflict")
            self._remember(scope, progress.epoch, key, owner=owner)
        finally:
            wipe(key)
        progress.state = "available"
        progress.signed_command = None

    def _admission_scope_failure(
        self, scope: str, attempt: AdmissionAttempt, error: E2eeError
    ) -> None:
        if error.code not in {
            "key_redistribution_required", "rekey_required", "revision_conflict",
            "scope_read_superseded", "not_found", "project_access_denied",
            "access_denied", "service_unavailable", "rate_limited",
            "untrusted_device",
        }:
            raise error
        progress = attempt.scopes[scope]
        progress.state = "pending"
        progress.reason = (
            "trust_verification_required" if error.code == "untrusted_device" else error.code
        )
        self._persist()

    def _acquire_admission_scope(
        self, scope: str, attempt: AdmissionAttempt,
        recovery: dict[str, Any], keys: dict[str, str],
    ) -> None:
        for _ in range(3):
            key = bytearray()
            try:
                current = self._admission_current_device(require_approved=True)
                metadata = dict(self.scope_metadata(scope, refresh=True))
                epoch = metadata["key_epoch"]
                progress = attempt.scopes[scope]
                if progress.epoch != epoch:
                    progress = attempt.scopes[scope] = ScopeAcquisition(epoch)
                if epoch == 0 and metadata["key_state"] == "uninitialized":
                    progress.state, progress.signed_command = "uninitialized", None
                    self._persist()
                    return
                try:
                    self._verify_admission_scope(scope, progress)
                    self._persist()
                    return
                except E2eeError as error:
                    if error.code != "key_redistribution_required":
                        raise
                progress.state = "pending"
                if progress.signed_command is None:
                    publication = self.owner_access.publications.key(scope, epoch, recovery_secret=keys["encryption_secret_key"])
                    key = publication.key
                    recipients = self.trust.current_recipients(
                        scope, {
                            "purpose": "distribution",
                            "devices": [current], "recoveries": [],
                        },
                        self._current_device_lookup(scope, [current]),
                        lambda identifier: self._recovery_material(scope, identifier),
                    )
                    target = recipients.devices[0]
                    if target != self.public:
                        raise E2eeError("device_key_changed")
                    envelope = self.wrap_key(
                        scope, epoch, key, recipient=self.device_id, kind="device",
                        public_key=target["encryption_public_key"],
                    )
                    body = {"scope_id": scope, "key_epoch": epoch, "envelopes": [envelope]}
                    if publication.generation is not None:
                        body["owner_authority"] = publication.generation.authority.to_dict()
                    progress.signed_command = self.sign("envelopes_save", body)
                    self._persist()
                body = self.crypto.verify(
                    self.public["signing_public_key"], "envelopes_save",
                    progress.signed_command,
                )
                envelopes = body.get("envelopes")
                if (
                    body.get("scope_id") != scope or body.get("key_epoch") != epoch
                    or not isinstance(envelopes, list) or len(envelopes) != 1
                    or not isinstance(envelopes[0], dict)
                    or envelopes[0].get("recipient_id") != self.device_id
                    or envelopes[0].get("recipient_kind") != "device"
                    or progress.signed_command["device_id"] != self.device_id
                ):
                    raise E2eeError("invalid_key_admission")
                self._admission_current_device(require_approved=True)
                if self.scope_metadata(scope, refresh=True)["key_epoch"] != epoch:
                    raise E2eeError("revision_conflict")
                self.call(
                    "e2eeSaveEnvelopes", body=progress.signed_command, scope_id=scope,
                )
                self._verify_admission_scope(scope, progress)
                self._persist()
                return
            except E2eeError as error:
                self._admission_scope_failure(scope, attempt, error)
                if error.code not in {"revision_conflict", "scope_read_superseded"}:
                    return
            finally:
                wipe(key)


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
        owner_key_epoch: int | None = None,
        owner_binding_digest: str | None = None,
    ) -> dict[str, Any]:
        self.require_approved()
        if kind == "recovery":
            self.trust.check_recovery_recipient(scope, recipient, public_key)
        fields = {
            "scope_id": scope,
            "key_epoch": epoch,
            "sender_device_id": self.device_id,
            "recipient_id": recipient,
            "recipient_kind": kind,
        }
        if kind == "owner":
            if (type(owner_key_epoch) is not int or owner_key_epoch < 1
                    or not isinstance(owner_binding_digest, str)):
                raise E2eeError("invalid_envelope")
            digest = decode(owner_binding_digest)
            try:
                if len(digest) != 32:
                    raise E2eeError("invalid_envelope")
            finally:
                wipe(digest)
            fields["owner_key_epoch"] = owner_key_epoch
            fields["owner_binding_digest"] = owner_binding_digest
        elif owner_key_epoch is not None or owner_binding_digest is not None:
            raise E2eeError("invalid_envelope")
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

    def approved_self_devices(self) -> list[dict[str, Any]]:
        self.require_approved()
        devices = self.call("e2eeListDevices")["devices"]
        self._check_current()
        owned = [
            device
            for device in devices
            if device.get("account_subject") == self.subject
        ]
        self._devices.update({device["device_id"]: device for device in owned})
        lookup = self._current_device_lookup(None, owned)
        approved = []
        for device in owned:
            if device.get("state") != "approved":
                continue
            expected = public_device(device)
            checked = self.trust.verify_current_device(
                lookup(expected["device_id"]),
                lookup,
                recovery_lookup=lambda value: self._recovery_material(None, value),
            )
            if public_device(checked) != expected:
                raise E2eeError("device_key_changed")
            approved.append(checked)
            self.require_approved()
        self.require_approved()
        return approved

    def _remember_device_material(
        self, scope: str | None, devices: list[dict[str, Any]]
    ) -> None:
        self.trust.observe_devices(devices, scope)
        if scope is None:
            for device in devices:
                if device.get("account_subject") != self.subject:
                    raise E2eeError("recovery_subject_mismatch")
                self._devices[device["device_id"]] = device
        else:
            self._scope_device_material.update(
                {(scope, device["device_id"]): device for device in devices}
            )

    def _current_device_lookup(
        self, scope: str | None, fresh: Iterable[dict[str, Any]] = ()
    ) -> Callable[[str], dict[str, Any]]:
        material = {
            device["device_id"]: device for device in fresh
            if scope is None or device.get("account_subject") != self.subject
        }

        def lookup(identifier: str) -> dict[str, Any]:
            if identifier not in material:
                cached = (
                    self._devices.get(identifier) if scope is None
                    else self._scope_device_material.get((scope, identifier))
                )
                selected_scope = (
                    None if cached and cached.get("account_subject") == self.subject
                    else scope
                )
                device = self._device_material(selected_scope, identifier, refresh=True)
                if selected_scope is not None and device.get("account_subject") == self.subject:
                    device = self._device_material(None, identifier, refresh=True)
                material[identifier] = device
            return material[identifier]

        return lookup

    def _device_material(
        self, scope: str | None, identifier: str, *, refresh: bool = False
    ) -> dict[str, Any]:
        cached = (
            self._devices.get(identifier) if scope is None
            else self._scope_device_material.get((scope, identifier))
        )
        if refresh or cached is None or not cached.get("certificates"):
            values = (
                self.call("e2eeListDevices", device_id=identifier)
                if scope is None
                else self.call(
                    "e2eeGetMemberDevices", scope_id=scope, device_id=identifier
                )
            )["devices"]
            found = next(
                (item for item in values if item["device_id"] == identifier), None
            )
            if found is None:
                raise E2eeError("untrusted_device")
            return found
        return cached

    def _recovery_material(
        self, scope: str | None, identifier: str
    ) -> dict[str, Any] | None:
        if scope is None:
            recovery = self.call("e2eeGetRecovery")
            if recovery.get("account_subject", self.subject) != self.subject:
                raise E2eeError("recovery_subject_mismatch")
            roots = [{**recovery, "account_subject": self.subject}]
        else:
            roots = self.call(
                "e2eeGetScopeRecoveryRoots", scope_id=scope, recovery_id=identifier
            )["recoveries"]
        self.trust.remember_recoveries(roots, scope)
        return self.trust._recovery_proofs.get((scope, identifier))

    def device(
        self, scope: str | None, identifier: str, *,
        key_epoch: int | None = None, envelope: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        attempted: set[str] = set()

        def lookup(value: str) -> dict[str, Any]:
            attempted.add(value)
            return self._device_material(scope, value)

        def verify() -> dict[str, Any]:
            return self.trust.verify_device(
                lookup(identifier),
                lookup,
                recovery_lookup=lambda value: self._recovery_material(scope, value),
                scope=scope, key_epoch=key_epoch, envelope=envelope,
            )

        try:
            return verify()
        except E2eeError as error:
            if error.code != "untrusted_device":
                raise
            for value in attempted:
                self._device_material(scope, value, refresh=True)
            return verify()

    def _read_key(
        self,
        scope: str,
        epoch: int,
        *,
        recipient: str,
        kind: str,
        secret_key: str | None = None,
    ) -> bytearray:
        bundle = self._key_bundles.get(scope)
        values = (
            [
                value
                for value in bundle.get("envelopes", [])
                if value["key_epoch"] == epoch
                and value["recipient_id"] == recipient
                and value["recipient_kind"] == kind
            ]
            if bundle is not None
            else []
        )
        if not values:
            metadata = self._scope_metadata.get(scope, {})
            if (
                kind == "device"
                and metadata.get("participation_policy") == "organization"
                and any(
                    value.get("key_epoch") == epoch
                    and value.get("recipient_kind") == "organization"
                    and value.get("recipient_id") == metadata.get("owner_org")
                    for value in (bundle or {}).get("envelopes", [])
                )
            ):
                raise E2eeError("key_redistribution_required")
            values = self.call("e2eeGetEnvelopes",
            scope_id=scope,
            epoch=epoch,
            recipient_id=recipient,
            recipient_kind=kind,)["envelopes"]
        for envelope in values:
            organization_key = bytearray()
            if kind == "organization":
                bound_epoch = envelope.get("organization_epoch")
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
        if kind == "owner":
            owner_epoch = envelope.get("owner_key_epoch")
            owner_digest = envelope.get("owner_binding_digest")
            if type(owner_epoch) is not int or owner_epoch < 1 or not isinstance(owner_digest, str):
                raise E2eeError("invalid_envelope")
            organization = self.scope_metadata(scope).get("owner_org")
            self.owner_access.envelope_binding(organization, recipient, owner_epoch, owner_digest)
            fields["owner_key_epoch"] = owner_epoch
            fields["owner_binding_digest"] = owner_digest
        elif "owner_key_epoch" in envelope or "owner_binding_digest" in envelope:
            raise E2eeError("invalid_envelope")
        organization_epoch = envelope.get("organization_epoch")
        if kind == "organization":
            if (
                type(organization_epoch) is not int
                or not 1 <= organization_epoch <= 2**63 - 1
            ):
                raise E2eeError("invalid_envelope")
            fields["organization_epoch"] = organization_epoch
        elif organization_epoch is not None:
            raise E2eeError("invalid_envelope")
        source_body = SignedEvidence.parse(envelope.get("signed_command")).body
        owner_source = (envelope.get("operation") in {"owner_envelopes_save", "owner_rotate_scope"}
                        or source_body.get("owner_key_proof") == OWNER_KEY_PROOF)
        if owner_source:
            if not isinstance(secret_key, str):
                raise E2eeError("invalid_envelope")
            return self.owner_access.envelopes.open(scope, epoch, envelope, secret_key)
        sender = (
            self.owner_access.envelopes.sender(scope, epoch, envelope)
            if kind == "owner"
            else self._participants.organization_envelope_sender(scope, recipient, envelope)
            if kind == "organization" else self.device(
                scope, envelope["sender_device_id"], key_epoch=epoch, envelope=envelope,
            )
        )
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


    def scope_key(self, scope: str, epoch: int) -> bytearray:
        self.require_approved()
        owner = self._scope_owner(scope)
        with self._scope_state_lock:
            if self._scope_metadata.get(scope) is not owner:
                raise E2eeError("scope_read_superseded")
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
            metadata = self.scope_metadata(scope)
            if epoch > metadata["key_epoch"]:
                raise E2eeError("key_redistribution_required") from None
            current = metadata["key_epoch"]
            if epoch < current:
                if metadata.get("owner_org") == scope:
                    key = self.owner_access.read_key(scope, epoch)
                else:
                    try:
                        key = self._previous_key(scope, epoch, current)
                    except E2eeError as historical_error:
                        if historical_error.code != "key_redistribution_required":
                            raise
                        key = self.owner_access.read_key(scope, epoch)
            elif metadata.get("participation_policy") == "organization" and metadata.get("owner_org"):
                try:
                    key = self._read_key(
                        scope, epoch, recipient=metadata["owner_org"], kind="organization",
                    )
                except E2eeError as organization_error:
                    if organization_error.code != "key_redistribution_required":
                        raise
                    key = self.owner_access.read_key(scope, epoch)
            elif metadata.get("owner_key_maintenance") is True:
                key = self.owner_access.read_key(scope, epoch)
            else:
                raise
        try:
            self._remember(scope, epoch, key, owner=owner)
        except BaseException:
            wipe(key)
            raise
        return key

    def _previous_key(self, scope: str, target: int, current: int) -> bytearray:
        owner = self._scope_owner(scope)
        links = {
            link["key_epoch"]: link
            for link in self._key_bundles.get(scope, {}).get("epochs", [])
        }
        if not all(epoch in links for epoch in range(target + 1, current + 1)):
            links = {}
            after = target
            while after < current:
                page = self.call("e2eeGetEpochs", scope_id=scope, after_epoch=after, limit=16)["epochs"]
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
                if link.get("operation") == "owner_rotate_scope":
                    self.owner_access.envelopes.verify(scope, epoch, signed, "owner_rotate_scope")
                    body = self.trust._body(signed)
                else:
                    device = self.device(scope, signed["device_id"], key_epoch=epoch)
                    body = self.crypto.verify(device["signing_public_key"], "rotate_scope", signed)
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
                    self._remember(scope, epoch - 1, key, owner=owner)
                finally:
                    wipe(aad)
            return bytearray(key)
        finally:
            wipe(key)

    def _remember(
        self, scope: str, epoch: int, key: bytearray, *, owner: dict[str, Any]
    ) -> None:
        self._check_scope(scope, owner)
        with self._scope_state_lock:
            if self._scope_metadata.get(scope) is not owner:
                raise E2eeError("scope_read_superseded")
            previous = self._scope_keys.pop((scope, epoch), None)
            if previous is not None:
                wipe(previous)
            self._scope_keys[(scope, epoch)] = bytearray(key)
            while len(self._scope_keys) > 128:
                wipe(self._scope_keys.pop(next(iter(self._scope_keys))))

    def _clear_keys(self) -> None:
        with self._scope_state_lock:
            for key in self._scope_keys.values():
                wipe(key)
            self._scope_keys.clear()

    def lock(self) -> None:
        with self._scope_state_lock:
            self._clear_keys()
            self._scope_metadata.clear()
            self._key_bundles.clear()
            self._scope_device_material.clear()
            self.trust.clear_scope_trust()
        self.owner_access.clear()
        if self._device is not None:
            self._device.clear()
        self._device = None
        self._device_snapshot = None
        self._device_observed = False
        self._devices.clear()
        self._key_admission = None
        self._last_key_acquisition_progress = {
            "available": [], "pending": [], "remaining": {},
        }
        self._device_approval = "unregistered"

        self.state = "locked"
