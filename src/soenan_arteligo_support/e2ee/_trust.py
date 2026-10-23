from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
import json
from typing import TYPE_CHECKING, Any, Protocol

from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe
from ._storage import ProfileSecureStore

if TYPE_CHECKING:
    from ._owner_projection import CertificateSignatureProjection
    from ._owner_protocol import SignedEvidence

_DEVICE_FIELDS = (
    "device_id",
    "account_subject",
    "encryption_public_key",
    "signing_public_key",
)
_DEVICE_ROOT_DOMAIN = b"arteligo-e2ee-device-root-v1\n"


def public_device(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or any(
        not isinstance(value.get(field), str) or not value[field]
        for field in _DEVICE_FIELDS
    ):
        raise E2eeError("invalid_device")
    return {**{field: value[field] for field in _DEVICE_FIELDS}, "state": "approved"}


@dataclass(frozen=True)
class _RootIdentity:
    origin: str
    subject: str
    identifier: str
    generation: int
    encryption_key: str
    signing_key: str

    @classmethod
    def parse(
        cls, origin: str, subject: str, value: Mapping[str, Any]
    ) -> _RootIdentity:
        if value.get("account_subject", subject) != subject:
            raise E2eeError("recovery_subject_mismatch")
        fields = ("recovery_id", "encryption_public_key", "signing_public_key")
        if not subject or any(
            not isinstance(value.get(field), str) or not value[field]
            for field in fields
        ):
            raise E2eeError("invalid_recovery")
        generation = value.get("generation")
        if type(generation) is not int or generation <= 0:
            raise E2eeError("invalid_recovery")
        for field in fields[1:]:
            key = decode(value[field])
            try:
                if len(key) != 32:
                    raise E2eeError("invalid_recovery")
            finally:
                wipe(key)
        if value.get("origin", origin) != origin:
            raise E2eeError("recovery_origin_mismatch")
        return cls(
            origin, subject, value["recovery_id"], generation,
            value["encryption_public_key"], value["signing_public_key"],
        )

    def document(self) -> dict[str, Any]:
        return {
            "origin": self.origin,
            "account_subject": self.subject,
            "recovery_id": self.identifier,
            "generation": self.generation,
            "encryption_public_key": self.encryption_key,
            "signing_public_key": self.signing_key,
        }


@dataclass(frozen=True)
class _CurrentRootHead:
    identity: _RootIdentity
    scope: str | None = None


@dataclass(frozen=True)
class _CurrentDeviceQualification:
    head: _RootIdentity
    device: Mapping[str, Any]


@dataclass(frozen=True)
class _CurrentRecipientSet:
    scope: str
    devices: tuple[dict[str, Any], ...]
    roots: tuple[_CurrentRootHead, ...]


@dataclass(frozen=True)
class _CurrentRootClaim:
    root: _RootIdentity
    anchor: _RootIdentity


class _ProofAuthority(Enum):
    LOCAL_PINS = "local_pins"
    SCOPE_OWNER = "scope_owner"


class _ScopedEvidence:
    value = "scoped_evidence"

    def __init__(self, scope: str | None):
        self.scope = scope
        self.devices: dict[str, dict[str, Any]] = {}
        self.roots: dict[str, dict[str, Any]] = {}

    def require_scope(self, scope: str | None) -> None:
        if scope != self.scope:
            raise E2eeError("participant_scope_mismatch")

    def pin_device(self, device: dict[str, Any]) -> dict[str, Any]:
        identifier = device["device_id"]
        previous = self.devices.get(identifier)
        if previous is not None and previous != device:
            raise E2eeError("device_key_changed")
        self.devices[identifier] = device
        return device

    def pin_root(self, root: _RootIdentity) -> None:
        document = root.document()
        previous = self.roots.get(root.identifier)
        if previous is not None and previous != document:
            raise E2eeError("recovery_key_changed")
        self.roots[root.identifier] = document


class _IdentityBoundEvidence(_ScopedEvidence):
    value = "identity_bound_evidence"


class _CurrentCustodyEvidence(_IdentityBoundEvidence):
    value = "current_ordered_custody"

    def __init__(self, scope: str | None, root: _RootIdentity,
                 authorize: Callable[[str, SignedEvidence | CertificateSignatureProjection, Mapping[str, Any]], None],
                 admitted: Callable[[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any] | None], None],
                 genesis: _RootIdentity | None = None):
        super().__init__(scope)
        self.root, self.authorize, self.admitted, self.genesis = root, authorize, admitted, genesis
        self.pin_root(root)

    def accepts_root(self, recovery_id: Any) -> bool:
        return recovery_id == self.root.identifier



class ScopeParticipantVerifier(Protocol):
    def verify_device(
        self,
        scope: str,
        device: Mapping[str, Any],
        visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        *,
        key_epoch: int | None = None,
        envelope: Mapping[str, Any] | None = None,
    ) -> bool: ...

    def verify_recovery(
        self,
        scope: str,
        recovery: Mapping[str, Any],
        visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> bool: ...

    def current_anchor(
        self,
        scope: str,
        subject: str,
        visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> _RootIdentity | None: ...

    def clear(self) -> None: ...
    def forget_scope(self, scope: str) -> None: ...



class _TrustPathUnavailable(Exception):
    pass


class KeyTrust:
    """Historical signature trust and confirmed current heads have separate storage."""

    def __init__(
        self,
        crypto: E2eeCrypto,
        store: ProfileSecureStore,
        subject: str,
        *,
        origin: str,
        owner_subject: str | None = None,
    ):
        self.crypto = crypto
        self.store = store
        self.name = f"trust:{subject}"
        self.origin = origin
        self._state: dict[str, dict[str, dict[str, Any]]] = {
            "devices": {}, "recovery": {}, "heads": {}, "peer_heads": {},
            "revoked": {}, "scope_revoked": {}, "account_revoked": {}, "root_factors": {},
        }
        self.owner_subject = owner_subject or subject
        self._endorsements: list[dict[str, Any]] = []
        self._recovery_proofs: dict[tuple[str | None, str], dict[str, Any]] = {}
        self._scope_devices: dict[tuple[str, str], dict[str, Any]] = {}
        self._scope_roots: dict[tuple[str, str], dict[str, Any]] = {}
        self.participants: ScopeParticipantVerifier | None = None
        self.certificate_projection: Callable[[Mapping[str, Any]], CertificateSignatureProjection] | None = None
        self.projected_device: Callable[[Mapping[str, Any], CertificateSignatureProjection,
                                         str | None, tuple[_RootIdentity, ...]], dict[str, Any]] | None = None
        self.current_device: Callable[[Mapping[str, Any], str | None, _RootIdentity],
                                      _CurrentDeviceQualification] | None = None
        self.current_recovery: Callable[[Mapping[str, Any], str | None, _RootIdentity],
                                        _CurrentRootHead] | None = None
        self.recipient_set: Callable[[str, tuple[_CurrentRootClaim, ...],
                                      tuple[Mapping[str, Any], ...]], _CurrentRecipientSet] | None = None

    def set_endorsements(self, statements: list[dict[str, Any]]) -> None:
        self._endorsements = statements

    def forget_scope(self, scope: str) -> None:
        for identity in list(self._scope_devices):
            if identity[0] == scope:
                self._scope_devices.pop(identity)
        for identity in list(self._scope_roots):
            if identity[0] == scope:
                self._scope_roots.pop(identity)
        for identity in list(self._recovery_proofs):
            if identity[0] == scope:
                self._recovery_proofs.pop(identity)
        if self.participants is not None:
            self.participants.forget_scope(scope)

    def clear_scope_trust(self) -> None:
        self._scope_devices.clear()
        self._scope_roots.clear()
        self._recovery_proofs.clear()
        if self.participants is not None:
            self.participants.clear()

    def _body(self, command: Mapping[str, Any]) -> dict[str, Any]:
        decoded = decode(command.get("body_bytes"))
        try:
            body = json.loads(decoded)
            if not isinstance(body, dict):
                raise E2eeError("invalid_certificate")
            return body
        except (ValueError, TypeError):
            raise E2eeError("invalid_certificate") from None
        finally:
            wipe(decoded)

    def _lookup_device(
        self, identifier: str, lookup: Callable[[str], Mapping[str, Any]]
    ) -> Mapping[str, Any]:
        if not isinstance(identifier, str) or not identifier:
            raise E2eeError("invalid_certificate")
        try:
            device = lookup(identifier)
        except KeyError:
            raise _TrustPathUnavailable() from None
        except E2eeError as error:
            if error.code == "untrusted_device":
                raise _TrustPathUnavailable() from None
            raise
        if device.get("device_id") != identifier:
            raise E2eeError("device_key_changed")
        return device

    def _endorsed(
        self,
        lookup: Callable[[str], Mapping[str, Any]],
        visiting: frozenset[str],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        scope: str | None,
        *,
        device_id: str | None = None,
        recovery_id: str | None = None,
    ):
        for command in self._endorsements:
            body = self._body(command)
            if body.get("scope_id") is not None:
                continue
            peer = body.get("trusted_device", {})
            root = body.get("recovery_root", {})
            if device_id is not None and peer.get("device_id") != device_id:
                continue
            if recovery_id is not None and root.get("recovery_id") != recovery_id:
                continue
            identifier = command.get("device_id")
            if not isinstance(identifier, str):
                raise E2eeError("invalid_certificate")
            try:
                issuer = self._lookup_device(identifier, lookup)
                if issuer.get("account_subject") != self.owner_subject:
                    raise E2eeError("recovery_subject_mismatch")
                checked = self._verify_device(
                    issuer, lookup, visiting, recovery_lookup, scope
                )
            except _TrustPathUnavailable:
                continue
            yield self.crypto.verify(
                checked["signing_public_key"], "peer_trust", command
            )

    def _load(self, kind: str, identifier: str) -> dict[str, Any] | None:
        with self.store.credential(f"{self.name}:{kind}:{identifier}") as item:
            saved = item.read()
            value = json.loads(saved) if saved is not None else None
            previous = self._state[kind].get(identifier)
            if previous is not None and previous != value:
                raise E2eeError(
                    "device_key_changed" if kind == "devices"
                    else "recovery_key_changed" if kind == "recovery"
                    else "trust_state_changed"
                )
            if value is not None:
                self._state[kind][identifier] = value
            return value

    def _save(self, kind: str, identifier: str, value: dict[str, Any]) -> None:
        with self.store.credential(f"{self.name}:{kind}:{identifier}") as item:
            saved = item.read()
            previous = json.loads(saved) if saved is not None else None
            for known in (previous, self._state[kind].get(identifier)):
                if known is not None and known != value:
                    raise E2eeError(
                        "device_key_changed" if kind == "devices"
                        else "recovery_key_changed" if kind == "recovery"
                        else "trust_state_changed"
                    )
            if previous is None:
                item.replace(json.dumps(value, separators=(",", ":")))
            self._state[kind][identifier] = value

    def observe_devices(
        self, devices: list[dict[str, Any]], scope: str | None = None
    ) -> None:
        for device in devices:
            if device.get("state") != "revoked":
                continue
            public = public_device(device)
            if scope is not None and public["account_subject"] == self.owner_subject:
                continue
            if scope is None and public["account_subject"] != self.owner_subject:
                raise E2eeError("recovery_subject_mismatch")
            self.remember_revoked(public["device_id"], scope)

    def remember_revoked(self, device_id: str, scope: str | None = None) -> None:
        kind = "revoked" if scope is None else "scope_revoked"
        identifier = device_id if scope is None else json.dumps(
            [scope, device_id], separators=(",", ":")
        )
        self._save(kind, identifier, {"device_id": device_id, "scope_id": scope})

    def observe_account_revocations(self, subject: str, device_ids: list[str]) -> None:
        for identifier in device_ids:
            if subject == self.owner_subject:
                self.remember_revoked(identifier)
            else:
                key = json.dumps([subject, identifier], separators=(",", ":"))
                self._save("account_revoked", key, {
                    "account_subject": subject, "device_id": identifier,
                })

    def known_revoked(self, device: Mapping[str, Any], scope: str | None = None) -> bool:
        identifier, subject = device["device_id"], device["account_subject"]
        return (
            subject == self.owner_subject and self._load("revoked", identifier) is not None
        ) or self._load(
            "account_revoked", json.dumps([subject, identifier], separators=(",", ":"))
        ) is not None or (
            subject != self.owner_subject and scope is not None and self._load(
                "scope_revoked", json.dumps([scope, identifier], separators=(",", ":"))
            ) is not None
        )


    def require_current_issuer(
        self, device: Mapping[str, Any], scope: str | None = None
    ) -> None:
        if device.get("state") != "approved" or self.known_revoked(device, scope):
            raise _TrustPathUnavailable()

    def pin_device(self, device: Mapping[str, Any]) -> dict[str, Any]:
        value = public_device(device)
        self._save("devices", value["device_id"], value)
        return value

    def _root_identity(
        self, subject: str, recovery: Mapping[str, Any], scope: str | None = None
    ) -> _RootIdentity:
        identity = _RootIdentity.parse(self.origin, subject, recovery)
        for previous in (
            self._load("recovery", identity.identifier),
            self._scope_roots.get((scope, identity.identifier)),
        ):
            if previous is not None and (
                _RootIdentity.parse(self.origin, subject, previous) != identity
            ):
                raise E2eeError("recovery_key_changed")
        head = self._confirmed_head(subject, scope)
        if head is not None:
            if (
                identity.identifier == head.identifier
                or identity.generation == head.generation
            ) and identity != head:
                raise E2eeError("recovery_head_changed")
        return identity

    def pin_recovery(self, subject: str, recovery: Mapping[str, Any]) -> None:
        identity = self._root_identity(subject, recovery)
        self._save("recovery", identity.identifier, identity.document())

    def _historical_recovery(
        self, scope: str | None, identifier: str,
        authority: _ProofAuthority | _ScopedEvidence = _ProofAuthority.LOCAL_PINS,
    ) -> dict[str, Any] | None:
        if isinstance(authority, _ScopedEvidence):
            authority.require_scope(scope)
            return authority.roots.get(identifier)
        global_root = (
            self._load("recovery", identifier)
            if authority is _ProofAuthority.LOCAL_PINS else None
        )
        return global_root or self._scope_roots.get((scope, identifier))

    def pin_scope_recovery(
        self, scope: str, subject: str, recovery: Mapping[str, Any]
    ) -> None:
        identity = self._root_identity(subject, recovery, scope)
        self._scope_roots[(scope, identity.identifier)] = identity.document()

    def _checked_device(
        self, scope: str | None, device: Mapping[str, Any]
    ) -> dict[str, Any]:
        public = public_device(device)
        for previous in (
            self._load("devices", public["device_id"]),
            self._scope_devices.get((scope, public["device_id"])),
        ):
            if previous is not None and previous != public:
                raise E2eeError("device_key_changed")
        return public

    def pin_scope_device(
        self, scope: str, device: Mapping[str, Any]
    ) -> dict[str, Any]:
        public = self._checked_device(scope, device)
        self._scope_devices[(scope, public["device_id"])] = public
        return public

    def _pin_verified_recovery(
        self, scope: str | None, subject: str, recovery: Mapping[str, Any],
        authority: _ProofAuthority | _ScopedEvidence = _ProofAuthority.LOCAL_PINS,
    ) -> None:
        if isinstance(authority, _ScopedEvidence):
            authority.require_scope(scope)
            authority.pin_root(self._root_identity(subject, recovery, scope))
            return
        if scope is None:
            self.pin_recovery(subject, recovery)
        else:
            self.pin_scope_recovery(scope, subject, recovery)

    def _pin_verified_device(
        self, scope: str | None, device: Mapping[str, Any],
        authority: _ProofAuthority | _ScopedEvidence = _ProofAuthority.LOCAL_PINS,
    ) -> dict[str, Any]:
        if isinstance(authority, _ScopedEvidence):
            authority.require_scope(scope)
            return authority.pin_device(self._checked_device(scope, device))
        public = self.pin_device(device) if scope is None else self.pin_scope_device(scope, device)
        return public

    def _assert_head(
        self, identity: _RootIdentity, previous: Mapping[str, Any] | None
    ) -> None:
        if previous is None:
            return
        head = _RootIdentity.parse(self.origin, identity.subject, previous)
        if identity.identifier == head.identifier and identity != head:
            raise E2eeError("recovery_head_changed")
        if identity.generation < head.generation:
            raise E2eeError("recovery_generation_rollback")
        if identity.generation == head.generation and identity != head:
            raise E2eeError("recovery_head_changed")

    def _head_slot(
        self, subject: str, scope: str | None
    ) -> tuple[str, str] | None:
        if subject == self.owner_subject:
            return "heads", subject
        if scope is None:
            return None
        return "peer_heads", json.dumps([scope, subject], separators=(",", ":"))

    def _head_identity(
        self, subject: str, scope: str | None, document: Mapping[str, Any]
    ) -> _RootIdentity:
        expected_scope = None if subject == self.owner_subject else scope
        if document.get("scope_id") != expected_scope:
            raise E2eeError("recovery_scope_mismatch")
        return _RootIdentity.parse(self.origin, subject, document)

    def has_confirmed_head(self, subject: str) -> bool:
        return self._confirmed_head(subject) is not None

    def _head_document(
        self, subject: str, scope: str | None = None
    ) -> dict[str, Any] | None:
        slot = self._head_slot(subject, scope)
        if slot is None:
            return None
        kind, identifier = slot
        with self.store.credential(f"{self.name}:{kind}:{identifier}") as item:
            saved = item.read()
            document = json.loads(saved) if saved is not None else None
            previous = self._state[kind].get(identifier)
            if document is not None:
                identity = self._head_identity(subject, scope, document)
                self._assert_head(identity, previous)
                self._state[kind][identifier] = document
            elif previous is not None:
                raise E2eeError("recovery_head_changed")
            return document

    def _confirmed_head(
        self, subject: str, scope: str | None = None
    ) -> _RootIdentity | None:
        document = self._head_document(subject, scope)
        return self._head_identity(subject, scope, document) if document else None

    def _check_head(
        self, identity: _RootIdentity, scope: str | None = None
    ) -> None:
        head = self._confirmed_head(identity.subject, scope)
        self._assert_head(identity, head.document() if head else None)

    def _require_current_head(self, identity: _RootIdentity, scope: str | None = None) -> None:
        head = self._confirmed_head(identity.subject, scope)
        self._assert_head(identity, head.document() if head else None)
        if head != identity:
            raise E2eeError("recovery_head_changed")

    def confirm_recovery(
        self, subject: str, recovery: Mapping[str, Any], scope: str | None = None,
        *, current_device: Mapping[str, Any] | None = None,
    ) -> _CurrentRootHead:
        identity = _RootIdentity.parse(self.origin, subject, recovery)
        if self._head_slot(subject, scope) is None:
            raise E2eeError("recovery_scope_required")
        self._check_head(identity, scope)
        self._pin_verified_recovery(scope, subject, recovery)
        return self._confirm_head(identity, scope, current_device=current_device)

    def confirm_private_recovery(self, recovery: Mapping[str, Any], keys: Mapping[str, str]) -> None:
        identity = _RootIdentity.parse(self.origin, self.owner_subject, recovery)
        derived = self.crypto.execute({"op": "public_keys",
            "encryption_secret_key": keys["encryption_secret_key"],
            "signing_secret_key": keys["signing_secret_key"]})
        if (derived["encryption_public_key"] != identity.encryption_key
                or derived["signing_public_key"] != identity.signing_key):
            raise E2eeError("recovery_key_changed")
        self._save("root_factors", identity.identifier, identity.document())

    def has_private_recovery(self, identity: _RootIdentity) -> bool:
        if identity.subject != self.owner_subject:
            return False
        known = self._load("root_factors", identity.identifier)
        return known == identity.document()

    def _confirm_head(
        self, identity: _RootIdentity, scope: str | None = None,
        *, current_device: Mapping[str, Any] | None = None,
    ) -> _CurrentRootHead:
        slot = self._head_slot(identity.subject, scope)
        if slot is None:
            raise E2eeError("recovery_scope_required")
        kind, identifier = slot
        if current_device is not None:
            self.require_current_issuer(current_device, scope)
            public = self._checked_device(scope, current_device)
            if public["account_subject"] != identity.subject:
                raise E2eeError("recovery_subject_mismatch")
        name = f"{self.name}:{kind}:{identifier}"
        with self.store.credential(name) as item:
            self._assert_head(identity, self._state[kind].get(identifier))
            saved = item.read()
            previous = json.loads(saved) if saved else None
            if previous is not None:
                self._head_identity(identity.subject, scope, previous)
            self._assert_head(identity, previous)
            document = identity.document()
            if kind == "peer_heads":
                document["scope_id"] = scope
            if previous != document:
                item.replace(json.dumps(document, separators=(",", ":")))
            self._state[kind][identifier] = document
        return _CurrentRootHead(
            identity, scope if identity.subject != self.owner_subject else None
        )

    def check_recovery_recipient(
        self, scope: str, identifier: str, public_key: str
    ) -> None:
        root = self._historical_recovery(scope, identifier)
        if root is None:
            return
        identity = _RootIdentity.parse(self.origin, root["account_subject"], root)
        self._check_head(identity, scope)
        current = self._confirmed_head(identity.subject, scope)
        if current is None:
            raise E2eeError("untrusted_recovery")
        if identity != current or identity.encryption_key != public_key:
            raise E2eeError("recovery_generation_rollback")

    def current_recipients(
        self,
        scope: str,
        audience: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None],
    ) -> _CurrentRecipientSet:
        if audience.get("purpose") != "distribution":
            raise E2eeError("invalid_recipient_purpose")
        if not scope:
            raise E2eeError("invalid_record_scope")
        claims = []
        qualified_subjects: set[str] = set()
        for recovery in audience["recoveries"]:
            identity = _RootIdentity.parse(self.origin, recovery["account_subject"], recovery)
            if identity.subject in qualified_subjects:
                raise E2eeError("invalid_recipient_set")
            qualified_subjects.add(identity.subject)
            self._check_head(identity, scope)
            try:
                anchor = self._current_recovery_anchor(identity, lookup, recovery_lookup, scope, True)
            except _TrustPathUnavailable:
                raise E2eeError("untrusted_recovery") from None
            claims.append(_CurrentRootClaim(identity, anchor))
        devices = []
        for device in audience["devices"]:
            if device.get("state") != "approved":
                raise E2eeError("device_approval_required")
            if device.get("account_subject") != self.owner_subject and device.get("account_subject") not in qualified_subjects:
                raise E2eeError("untrusted_recovery")
            material = self._lookup_device(device["device_id"], lookup)
            if public_device(material) != public_device(device):
                raise E2eeError("device_key_changed")
            devices.append(material)
        if self.owner_subject not in qualified_subjects and any(
            device["account_subject"] == self.owner_subject for device in devices
        ):
            head = self._confirmed_head(self.owner_subject, scope)
            if head is None:
                raise E2eeError("untrusted_recovery")
            claims.append(_CurrentRootClaim(head, head))
        if self.recipient_set is None:
            raise E2eeError("untrusted_recovery")
        verified = self.recipient_set(scope, tuple(claims), tuple(devices))
        try:
            for device in verified.devices:
                self.require_current_issuer(device, scope)
        except _TrustPathUnavailable:
            raise E2eeError("untrusted_device") from None
        for root in verified.roots:
            self._pin_verified_recovery(scope, root.identity.subject, root.identity.document())
            self._confirm_head(root.identity, scope)
        try:
            for device in verified.devices:
                self._pin_verified_device(scope, device)
                self.require_current_issuer(device, scope)
            for root in verified.roots:
                self._require_current_head(root.identity, scope)
        except _TrustPathUnavailable:
            raise E2eeError("untrusted_device") from None
        return _CurrentRecipientSet(scope, verified.devices,
            tuple(root for root in verified.roots if root.identity.subject in qualified_subjects))

    def remember_recoveries(
        self, recoveries: list[dict[str, Any]], scope: str | None = None
    ) -> None:
        for recovery in recoveries:
            subject = recovery.get("account_subject")
            if not isinstance(subject, str):
                raise E2eeError("invalid_recovery")
            self._remember_recovery(subject, recovery, scope)
            for certificate in recovery.get("certificates", []):
                if certificate.get("operation") != "recovery_public":
                    continue
                body = self._body(certificate.get("signed_command", {}))
                self._remember_recovery(subject, {
                    **body, "certificates": [certificate],
                }, scope)

    def _remember_recovery(
        self, subject: str, recovery: Mapping[str, Any], scope: str | None
    ) -> None:
        identity = self._root_identity(subject, recovery, scope)
        key = (scope, identity.identifier)
        previous = self._recovery_proofs.get(key)
        if previous is not None and (
            _RootIdentity.parse(self.origin, subject, previous) != identity
        ):
            raise E2eeError("recovery_key_changed")
        certificates = list((previous or {}).get("certificates", []))
        for certificate in recovery.get("certificates", []):
            if certificate not in certificates:
                certificates.append(certificate)
        self._recovery_proofs[key] = {
            **identity.document(), "certificates": certificates,
        }

    def _recovery(
        self,
        subject: str,
        identifier: str,
        lookup: Callable[[str], Mapping[str, Any]],
        visiting: frozenset[str],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        scope: str | None,
        offered: Mapping[str, Any] | None = None,
        authority: _ProofAuthority | _ScopedEvidence = _ProofAuthority.LOCAL_PINS,
    ) -> dict[str, Any]:
        if not isinstance(identifier, str) or not identifier:
            raise E2eeError("invalid_certificate")
        if offered is not None:
            self._root_identity(subject, offered, scope)
        previous = self._historical_recovery(scope, identifier, authority)
        if offered is not None:
            self._remember_recovery(subject, offered, scope)
        if previous is not None:
            identity = _RootIdentity.parse(self.origin, subject, previous)
            if offered is not None and (
                _RootIdentity.parse(self.origin, subject, offered) != identity
            ):
                raise E2eeError("recovery_key_changed")
            return previous
        proof = self._recovery_proofs.get((scope, identifier))
        if (proof is None or not proof.get("certificates")) and recovery_lookup:
            fetched = recovery_lookup(identifier)
            if fetched is not None:
                self._remember_recovery(subject, fetched, scope)
            proof = self._recovery_proofs.get((scope, identifier))
        if proof is None and authority is _ProofAuthority.LOCAL_PINS:
            for command in self._endorsements:
                body = self._body(command)
                if body.get("scope_id") is not None:
                    continue
                root = body.get("recovery_root", {})
                if root.get("recovery_id") == identifier:
                    peer = public_device(body.get("trusted_device", {}))
                    if peer["account_subject"] != subject:
                        raise E2eeError("recovery_subject_mismatch")
                    self._remember_recovery(subject, root, scope)
            proof = self._recovery_proofs.get((scope, identifier))
        if proof is None:
            raise _TrustPathUnavailable()
        return self._verify_recovery(
            subject, proof, lookup, visiting, recovery_lookup, scope, authority
        )

    def verify_recovery(
        self,
        subject: str,
        recovery: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
        *,
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None = None,
        scope: str | None = None,
    ) -> dict[str, Any]:
        try:
            return self._verify_recovery(
                subject, recovery, lookup, frozenset(), recovery_lookup, scope
            )
        except _TrustPathUnavailable:
            raise E2eeError("untrusted_recovery") from None

    def _current_recovery_anchor(
        self, identity: _RootIdentity, lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        scope: str | None, current_participant: bool,
    ) -> _RootIdentity:
        subject = identity.subject
        previous = self._confirmed_head(subject, scope)
        self._assert_head(identity, previous.document() if previous else None)
        initial = None
        if subject != self.owner_subject:
            if scope is None or self.participants is None:
                raise _TrustPathUnavailable()
            initial = previous if current_participant and previous is not None else (
                self.participants.current_anchor(scope, subject, frozenset(), lookup, recovery_lookup)
            )
            if initial is None:
                raise _TrustPathUnavailable()
            if initial.subject != subject or initial.origin != self.origin:
                raise E2eeError("recovery_subject_mismatch")
            self._root_identity(subject, initial.document(), scope)
            self._assert_head(identity, initial.document())
        anchor = previous or initial
        if anchor is None:
            raise _TrustPathUnavailable()
        return anchor

    def verify_current_recovery(
        self,
        subject: str,
        recovery: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
        *,
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None = None,
        scope: str | None = None,
        current_participant: bool = False,
    ) -> dict[str, Any]:
        identity = _RootIdentity.parse(self.origin, subject, recovery)
        try:
            anchor = self._current_recovery_anchor(identity, lookup, recovery_lookup, scope, current_participant)
            if self.current_recovery is None:
                raise _TrustPathUnavailable()
            verified = self.current_recovery(recovery, scope, anchor)
            if verified.identity != identity:
                raise E2eeError("recovery_key_changed")
        except _TrustPathUnavailable:
            raise E2eeError("untrusted_recovery") from None
        self._pin_verified_recovery(scope, subject, recovery)
        self._confirm_head(identity, scope)
        return dict(recovery)

    def _verify_recovery(
        self,
        subject: str,
        recovery: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
        visiting: frozenset[str],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        scope: str | None,
        authority: _ProofAuthority | _ScopedEvidence = _ProofAuthority.LOCAL_PINS,
    ) -> dict[str, Any]:
        identity = self._root_identity(subject, recovery, scope)
        previous = self._historical_recovery(scope, identity.identifier, authority)
        if previous is not None:
            if _RootIdentity.parse(self.origin, subject, previous) != identity:
                raise E2eeError("recovery_key_changed")
            return dict(recovery)
        visit = f"recovery:{authority.value}:{identity.identifier}"
        if visit in visiting:
            raise _TrustPathUnavailable()
        visiting = visiting | {visit}
        endorsements = self._endorsed(
            lookup, visiting, recovery_lookup, scope, recovery_id=identity.identifier
        ) if authority is _ProofAuthority.LOCAL_PINS else ()
        for body in endorsements:
            peer = public_device(body.get("trusted_device", {}))
            root = body.get("recovery_root", {})
            if peer["account_subject"] != subject or (
                _RootIdentity.parse(self.origin, subject, root) != identity
            ):
                raise E2eeError("recovery_key_changed")
            self._pin_verified_recovery(scope, subject, recovery, authority)
            return dict(recovery)
        for certificate in recovery.get("certificates", []):
            operation = certificate.get("operation")
            if operation != "recovery_public":
                continue
            command = certificate.get("signed_command", {})
            body = self._body(command)
            if body.get("recovery_id") != identity.identifier:
                continue
            if _RootIdentity.parse(self.origin, subject, body) != identity:
                raise E2eeError("recovery_key_changed")
            try:
                issuer = self._lookup_device(command.get("device_id"), lookup)
                if issuer.get("account_subject") != subject:
                    raise E2eeError("recovery_subject_mismatch")
                checked = self._verify_device(
                    issuer, lookup, visiting, recovery_lookup, scope, authority,
                )
            except _TrustPathUnavailable:
                continue
            self.crypto.verify(checked["signing_public_key"], operation, command)
            self._pin_verified_recovery(scope, subject, recovery, authority)
            return dict(recovery)
        if scope is not None and authority is _ProofAuthority.LOCAL_PINS and self.participants:
            try:
                if self.participants.verify_recovery(
                    scope, recovery, visiting, lookup, recovery_lookup
                ):
                    return dict(recovery)
            except _TrustPathUnavailable:
                pass
        raise _TrustPathUnavailable()

    def verify_device(
        self,
        device: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
        visiting: frozenset[str] = frozenset(),
        *,
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None = None,
        scope: str | None = None,
        key_epoch: int | None = None,
        envelope: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            return self._verify_device(device, lookup, visiting, recovery_lookup, scope)
        except _TrustPathUnavailable:
            if scope is not None and self.participants is not None:
                try:
                    if self.participants.verify_device(
                        scope, device, visiting, lookup, recovery_lookup,
                        key_epoch=key_epoch, envelope=envelope,
                    ):
                        return public_device(device)
                except _TrustPathUnavailable:
                    pass
            raise E2eeError("untrusted_device") from None

    def verify_current_device(
        self,
        device: Mapping[str, Any],
        *,
        scope: str | None = None,
    ) -> dict[str, Any]:
        if device.get("state") != "approved":
            raise E2eeError("device_approval_required")
        public = public_device(device)
        head = self._confirmed_head(public["account_subject"], scope)
        if head is None:
            raise E2eeError("untrusted_recovery")
        try:
            self.require_current_issuer(device, scope)
            if self.current_device is None:
                raise _TrustPathUnavailable()
            qualified = self.current_device(device, scope, head)
            if qualified.head != head or public_device(qualified.device) != public:
                raise E2eeError("device_key_changed")
            verified = self._pin_verified_device(scope, qualified.device)
            self.require_current_issuer(device, scope)
            self._require_current_head(head, scope)
            return verified
        except _TrustPathUnavailable:
            raise E2eeError("untrusted_device") from None


    def _bootstrap_identity_consent(
        self, device: Mapping[str, Any], root: Mapping[str, Any],
        scope: str | None,
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> bool:
        subject = device["account_subject"]
        identity = _RootIdentity.parse(self.origin, subject, root)
        proof = (
            recovery_lookup(identity.identifier) if recovery_lookup is not None
            else self._recovery_proofs.get((scope, identity.identifier))
        )
        for certificate in (proof or {}).get("certificates", []):
            if certificate.get("operation") != "recovery_public":
                continue
            command = certificate.get("signed_command", {})
            if command.get("device_id") != device["device_id"]:
                continue
            body = self._body(command)
            if body.get("account_subject") != subject:
                continue
            if _RootIdentity.parse(self.origin, subject, body) != identity:
                continue
            self.crypto.verify(device["signing_public_key"], "recovery_public", command)
            return True
        return False

    def _enrollment_identity_consent(
        self, device: Mapping[str, Any], approval: Mapping[str, Any],
    ) -> Mapping[str, Any] | None:
        public = public_device(device)
        required = {*_DEVICE_FIELDS, "challenge", "envelopes"}
        for certificate in device.get("certificates", []):
            if certificate.get("operation") != "device_enroll":
                continue
            command = certificate.get("signed_command", {})
            if command.get("device_id") != public["device_id"]:
                continue
            body = self._body(command)
            if (set(body) not in (required, required | {"state"})
                    or body.get("state", "approved") != "approved"
                    or not isinstance(body.get("challenge"), str)
                    or not body["challenge"]):
                continue
            if (public_device(body) != public or body.get("envelopes") != []
                    or body.get("challenge") != approval.get("challenge")):
                continue
            self.crypto.verify(public["signing_public_key"], "device_enroll", command)
            return certificate
        return None

    def _verify_device(
        self,
        device: Mapping[str, Any],
        lookup: Callable[[str], Mapping[str, Any]],
        visiting: frozenset[str],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        scope: str | None,
        authority: _ProofAuthority | _ScopedEvidence = _ProofAuthority.LOCAL_PINS,
    ) -> dict[str, Any]:
        public = self._checked_device(scope, device)
        identifier, subject = public["device_id"], public["account_subject"]
        if isinstance(authority, _ScopedEvidence):
            authority.require_scope(scope)
        if isinstance(authority, _ScopedEvidence):
            previous = authority.devices.get(identifier)
        else:
            previous = self._scope_devices.get((scope, identifier))
            if authority is _ProofAuthority.LOCAL_PINS:
                previous = self._state["devices"].get(identifier) or previous
        if previous is not None:
            if previous != public:
                raise E2eeError("device_key_changed")
            return previous
        visit = f"device:{authority.value}:{identifier}"
        if visit in visiting:
            raise _TrustPathUnavailable()
        visiting = visiting | {visit}
        endorsements = self._endorsed(
            lookup, visiting, recovery_lookup, scope, device_id=identifier
        ) if authority is _ProofAuthority.LOCAL_PINS else ()
        for body in endorsements:
            if public_device(body.get("trusted_device", {})) != public:
                raise E2eeError("device_key_changed")
            if body.get("recovery_root") is not None:
                self._pin_verified_recovery(scope, subject, body["recovery_root"], authority)
            return self._pin_verified_device(scope, device, authority=authority)
        for certificate in device.get("certificates", []):
            operation = certificate.get("operation")
            projection = None
            if operation == "account_signature_projection":
                if self.certificate_projection is None:
                    raise E2eeError("owner_certificate_projection_missing")
                projection = self.certificate_projection(certificate)
                operation = projection.operation
                if not isinstance(authority, _CurrentCustodyEvidence):
                    if self.projected_device is None:
                        raise E2eeError("owner_certificate_projection_missing")
                    if isinstance(authority, _ScopedEvidence):
                        roots = tuple(_RootIdentity.parse(self.origin, subject, value)
                                      for value in authority.roots.values() if value["account_subject"] == subject)
                    else:
                        roots = tuple(_RootIdentity.parse(self.origin, subject, value) for value in (
                            *self._state["recovery"].values(),
                            *(value for (selected, _), value in self._scope_roots.items() if selected == scope),
                        ) if value["account_subject"] == subject)
                    if not roots:
                        raise _TrustPathUnavailable()
                    verified = self.projected_device(device, projection, scope, roots)
                    return self._pin_verified_device(scope, verified, authority=authority)
            if operation == "bootstrap":
                if public_device(certificate.get("public_device", {})) != public:
                    raise E2eeError("invalid_certificate")
                recovery = certificate.get("recovery_root", {})
                if isinstance(authority, _CurrentCustodyEvidence) and (
                    authority.genesis is None
                    or _RootIdentity.parse(self.origin, subject, recovery) != authority.genesis
                ):
                    continue
                try:
                    root = self._recovery(
                        subject, recovery.get("recovery_id"), lookup,
                        visiting, recovery_lookup, scope, recovery, authority,
                    )
                except _TrustPathUnavailable:
                    continue
                if isinstance(authority, _IdentityBoundEvidence) and not self._bootstrap_identity_consent(
                    device, root, scope, recovery_lookup,
                ):
                    continue
                canonical = self.crypto.canonical(public)
                message = bytearray(_DEVICE_ROOT_DOMAIN) + canonical
                try:
                    self.crypto.execute({
                        "op": "verify_bytes",
                        "public_key": root["signing_public_key"],
                        "bytes": encode(message),
                        "signature": certificate.get("root_signature"),
                    })
                finally:
                    wipe(canonical)
                    wipe(message)
                if isinstance(authority, _CurrentCustodyEvidence):
                    authority.admitted(device, certificate, None)
                return self._pin_verified_device(scope, device, authority=authority)
            if operation == "envelopes_save" and isinstance(authority, _CurrentCustodyEvidence):
                from ._organization_admission import OrganizationAdmission

                from ._owner_protocol import SignedEvidence

                command = projection or SignedEvidence.parse(certificate.get("signed_command", {}))
                issuer = self._lookup_device(command.device_id, lookup)
                approval = OrganizationAdmission.parse(self.crypto, self.origin, command, issuer)
                if approval.device != public or approval.root != authority.root:
                    continue
                try:
                    authority.authorize(operation, command, approval.target())
                except _TrustPathUnavailable:
                    continue
                authority.admitted(device, certificate, None)
                return self._pin_verified_device(scope, device, authority=authority)
            if operation not in {"device_approve", "device_add_by_key"}:
                continue
            from ._owner_protocol import SignedEvidence

            command = projection or SignedEvidence.parse(certificate.get("signed_command", {}))
            body = command.body
            if operation == "device_approve":
                if any(body.get(field) != public[field] for field in _DEVICE_FIELDS if field != "account_subject"):
                    raise E2eeError("invalid_certificate")
                declared_subject = body.get("account_subject",
                    projection.reference.witness_subject if projection is not None
                    else subject if isinstance(authority, _CurrentCustodyEvidence) else None)
                if declared_subject != subject:
                    raise E2eeError("recovery_subject_mismatch")
                consent = self._enrollment_identity_consent(device, body) if isinstance(authority, _IdentityBoundEvidence) else None
                if isinstance(authority, _IdentityBoundEvidence) and consent is None:
                    continue
                if (isinstance(authority, _CurrentCustodyEvidence) and body.get("recovery_root") is not None
                        and not authority.accepts_root(body["recovery_root"].get("recovery_id"))):
                    continue
                if isinstance(authority, _CurrentCustodyEvidence):
                    try:
                        authority.authorize(operation, command, {field: body.get(field) for field in (
                            "device_id", "encryption_public_key", "signing_public_key", "challenge",
                        )})
                    except _TrustPathUnavailable:
                        continue
                try:
                    issuer = self._lookup_device(command.device_id, lookup)
                    if issuer.get("account_subject") != subject:
                        raise E2eeError("recovery_subject_mismatch")
                    checked = self._verify_device(
                        issuer, lookup, visiting, recovery_lookup, scope, authority,
                    )
                except _TrustPathUnavailable:
                    continue
                command.verify(self.crypto, checked["signing_public_key"], operation)
                if body.get("recovery_root") is not None:
                    self._pin_verified_recovery(scope, subject, body["recovery_root"], authority)
                if isinstance(authority, _CurrentCustodyEvidence):
                    authority.admitted(device, certificate, consent)
                return self._pin_verified_device(scope, device, authority=authority)
            if command.device_id != identifier or (
                public_device(body.get("device", {})) != public
            ):
                raise E2eeError("invalid_certificate")
            if type(body.get("generation")) is not int or body["generation"] <= 0:
                raise E2eeError("invalid_certificate")
            if isinstance(authority, _CurrentCustodyEvidence) and not authority.accepts_root(body.get("recovery_id")):
                continue
            admission = {
                field: body.get(field)
                for field in ("recovery_id", "generation", "device", "challenge")
            }
            challenge = decode(admission["challenge"])
            try:
                if len(challenge) != 32:
                    raise E2eeError("invalid_certificate")
            finally:
                wipe(challenge)
            canonical = self.crypto.canonical(admission)
            message = bytearray(b"arteligo-e2ee-device-admission-v1\n") + canonical
            try:
                self.crypto.execute({
                    "op": "verify_bytes",
                    "public_key": public["signing_public_key"],
                    "bytes": encode(message),
                    "signature": body.get("device_signature"),
                })
            finally:
                wipe(canonical)
                wipe(message)
            try:
                root = self._recovery(
                    subject, body.get("recovery_id"), lookup,
                    visiting, recovery_lookup, scope, authority=authority,
                )
            except _TrustPathUnavailable:
                continue
            if body.get("generation") != root["generation"]:
                raise E2eeError("invalid_certificate")
            command.verify(self.crypto, root["signing_public_key"], operation)
            if isinstance(authority, _CurrentCustodyEvidence):
                authority.admitted(device, certificate, None)
            return self._pin_verified_device(scope, device, authority=authority)
        raise _TrustPathUnavailable()
