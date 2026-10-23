from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Iterable

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_commands import OwnerCommands
from ._owner_protocol import OwnerAuthorityHead, OwnerCapsuleCrypto, OwnerDomain, OwnerOperation, SignedEvidence, authority_head, object_value
from ._owner_state import OwnerKey, OwnerStateStore
from ._owner_verifier import OwnerEvidenceVerifier

if TYPE_CHECKING:
    from ._session import DeviceSession


class OwnerKeyring:
    def __init__(self, session: DeviceSession, store: OwnerStateStore,
                 commands: OwnerCommands, verifier: OwnerEvidenceVerifier, capsules: OwnerCapsuleCrypto):
        self.session, self.store, self.commands = session, store, commands
        self.verifier, self.capsules, self.crypto = verifier, capsules, session.crypto

    def active(self, organization: str, head: OwnerAuthorityHead) -> OwnerKey:
        for key in self.store.get(organization).keys:
            if key.key_id == head.key_id:
                if (key.key_epoch != head.key_epoch or key.public_key != head.public_key
                        or key.binding_digest != head.binding_digest):
                    raise E2eeError("owner_key_changed")
                return key
        raise E2eeError("owner_candidate_secret_missing")

    def verify_history(self, organization: str, values: list[Any], manifest: list[dict[str, Any]],
                       source: OwnerAuthorityHead) -> list[OwnerKey]:
        keys = [OwnerKey.parse(value, organization, self.capsules) for value in values]
        if (len({key.key_id for key in keys}) != len(keys) or len({key.key_epoch for key in keys}) != len(keys)
                or [key.public_binding() for key in keys] != manifest):
            raise E2eeError("owner_keyring_mismatch")
        active = {name: source.to_dict()[name] for name in ("key_id", "key_epoch", "public_key", "binding_digest")}
        if sum(key.public_binding() == active for key in keys) != 1 or manifest.count(active) != 1:
            raise E2eeError("owner_source_key_missing")
        for key in keys:
            selected = self.verifier.account.selected(organization, key.binding_digest)
            if key.public_binding() != {name: selected.head.to_dict()[name] for name in key.public_binding()}:
                raise E2eeError("owner_keyring_mismatch")
            proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=key.binding_digest)
            self.verifier.binding(organization, proof, selected.head)
        return keys

    def merge(self, organization: str, keys: Iterable[OwnerKey]) -> None:
        state = self.store.get(organization)
        merged = {key.key_id: key for key in state.keys}
        for key in keys:
            if key.key_id in merged and merged[key.key_id] != key:
                raise E2eeError("owner_key_changed")
            merged[key.key_id] = key
        state.keys = sorted(merged.values(), key=lambda key: (key.key_epoch, key.key_id))
        self.store.save(organization)

    def backup(self, organization: str, head: OwnerAuthorityHead) -> None:
        state, active = self.store.get(organization), self.active(organization, head)
        if "keyring" in state.journal:
            self.commands.submit(organization, "keyring", OwnerOperation.KEYRING)
            self.store.finish(organization, "keyring")
        plaintext = self.crypto.canonical(self.session.owner_access.recovery.history(organization))
        aad = self.crypto.canonical({"v": 1, "domain": OwnerDomain.KEYRING,
                                     "organization_id": organization, "owner_authority": head.to_dict()})
        secret = decode(active.secret_key)
        try:
            encrypted = self.crypto.canonical(self.crypto.seal(secret, plaintext, aad))
            try:
                self.commands.submit(organization, "keyring", OwnerOperation.KEYRING, {
                    "organization_id": organization, "owner_authority": head.to_dict(), "ciphertext": encode(encrypted),
                })
                self.store.finish(organization, "keyring")
            finally:
                wipe(encrypted)
        finally:
            for value in (plaintext, aad, secret):
                wipe(value)

    def restore(self, organization: str) -> None:
        saved = self.session.call("e2eeGetOwnerKeyring", organization_id=organization)
        signed = SignedEvidence.parse(saved.get("signed_command"))
        head = authority_head(signed.body.get("owner_authority"), organization)
        active = self.active(organization, head)
        proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)
        source = self.verifier.binding(organization, proof, head)
        signer = self.session._device_material(organization, signed.device_id)
        proof_scope = None if signer["account_subject"] == self.session.subject else organization
        historical_roots = tuple(root for root in source.positive_roots
                                 if root.subject == signer["account_subject"]
                                 and root.origin == self.session.trust.origin)
        self.verifier.signer(organization, signed, signer, source.binding.body.recovery_root.to_dict(),
                             proof_scope=proof_scope, historical_roots=historical_roots)
        signed.verify(self.crypto, signer["signing_public_key"], OwnerOperation.KEYRING)
        body = signed.body
        if (signer["account_subject"] != head.owner_subject or body.get("organization_id") != organization
                or body.get("owner_authority") != head.to_dict()):
            raise E2eeError("owner_keyring_mismatch")
        raw, secret = decode(body["ciphertext"]), decode(active.secret_key)
        aad = self.crypto.canonical({"v": 1, "domain": OwnerDomain.KEYRING,
                                     "organization_id": organization, "owner_authority": head.to_dict()})
        plaintext = bytearray()
        try:
            plaintext = self.crypto.open(secret, json.loads(raw), aad)
            payload = object_value(json.loads(plaintext))
            if payload.get("v") != 1 or payload.get("organization_id") != organization or not isinstance(payload.get("keys"), list):
                raise E2eeError("owner_keyring_mismatch")
            self.session.owner_access.recovery.import_history(organization, payload)
        except (ValueError, KeyError, TypeError):
            raise E2eeError("owner_keyring_mismatch") from None
        finally:
            for value in (raw, secret, aad, plaintext):
                wipe(value)
