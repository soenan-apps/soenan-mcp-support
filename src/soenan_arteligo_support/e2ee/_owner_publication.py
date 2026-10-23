from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_envelopes import VerifiedGeneration, VerifiedPublicationKey
from ._owner_envelopes import OWNER_KEY_PROOF
from ._trust import _TrustPathUnavailable
from ._owner_protocol import OwnerAuthorityHead, OwnerOperation, SignedEvidence, authority_head

if TYPE_CHECKING:
    from ._owner_access import OwnerAccess
    from ._session import DeviceSession


class OwnerPublicationKeys:
    """New encryption opens a key against one captured authority and exact generation."""

    def __init__(self, session: DeviceSession, owner: OwnerAccess):
        self.session, self.owner = session, owner

    def qualify_scope_writer(self, scope: str, device: Mapping[str, Any], head: OwnerAuthorityHead, *, current: bool = True) -> None:
        from ._participant_sources import _organization_history

        organization = self.session.scope_metadata(scope).get("owner_org")
        if scope == organization:
            if not current and device["account_subject"] == head.owner_subject:
                return
            self.owner.organizations.qualify_admin(organization, device, head)
            return
        source = self.owner._project_source(organization, scope)
        participants, trust = self.session._participants, self.session.trust
        lookup = self.session._current_device_lookup(scope)
        roots = lambda identifier: self.session._recovery_material(scope, identifier)
        subject = device["account_subject"]
        authorized = subject == source.creator["account_subject"]
        if not authorized and source.command.body.get("participation_policy") == "organization":
            def verify_member(evidence, context: Mapping[str, Any]) -> None:
                if context.get("project_command") != source.command.document():
                    raise E2eeError("participant_source_changed")
                trust._verify_device(device, lookup, frozenset(), roots, scope, evidence)

            authorized = _organization_history(participants, scope, subject, lookup, roots, verify_member)
        if not authorized:
            for proof in participants._load(scope, subject):
                if proof.get("kind") != "invitation":
                    continue
                evidence = participants._evidence(scope, proof)
                invitation = SignedEvidence.parse(proof["invitation_command"])
                if invitation.body.get("role") == "editor" and participants._authority(evidence, frozenset(), lookup, roots):
                    authorized = True
                    break
        if not authorized:
            raise E2eeError("owner_generation_issuer_unqualified")
        if not current:
            return
        selected_scope = None if subject == self.session.subject else scope
        material = self.session._device_material(selected_scope, device["device_id"], refresh=True)
        anchor = source.root if subject == source.creator["account_subject"] else self.owner.current.independent_root(scope, material)
        self.owner.current.qualify(organization, material, anchor, head, proof_scope=scope)

    def generation(self, scope: str, epoch: int, expected: OwnerAuthorityHead | None = None) -> VerifiedGeneration:
        organization = self.session.scope_metadata(scope).get("owner_org")
        try:
            proof = self.session.call("e2eeGetOwnerGeneration", scope_id=scope, epoch=epoch)
        except E2eeError as error:
            if error.code == "rekey_required":
                raise E2eeError("owner_generation_proof_missing") from None
            raise
        signed = SignedEvidence.parse(proof.get("signed_command"))
        operation, body = proof.get("operation"), signed.body
        head = authority_head(proof.get("owner_authority"), organization)
        if operation == OwnerOperation.ROTATE:
            self.owner.envelopes.source(scope, epoch, signed.document(), operation)
        elif operation in {"project_create", "organization_create", "rotate_scope"}:
            owner_created = operation in {"project_create", "organization_create"} and body.get("owner_key_proof") == OWNER_KEY_PROOF
            if owner_created:
                self.owner.envelopes.source(scope, epoch, signed.document(), operation)
            else:
                signer = self.session.device(scope, signed.device_id, key_epoch=epoch)
                signed.verify(self.session.crypto, signer["signing_public_key"], operation)
                if signer["account_subject"] == head.owner_subject:
                    raise E2eeError("owner_key_proof_required")
                if expected is not None:
                    try:
                        self.qualify_scope_writer(scope, signer, head)
                    except _TrustPathUnavailable:
                        raise E2eeError("owner_generation_issuer_unqualified") from None
        else:
            raise E2eeError("owner_generation_proof_missing")
        previous = body.get("expected_epoch")
        generated_epoch = 1 if operation in {"project_create", "organization_create"} else previous + 1 if type(previous) is int else None
        if (proof.get("key_epoch") != epoch or generated_epoch != epoch
                or body.get("scope_id", body.get("project_id")) != scope
                or body.get("owner_authority") != head.to_dict()
                or (expected is not None and head != expected)):
            raise E2eeError("owner_key_generation_stale")
        return VerifiedGeneration(scope, epoch, operation, signed, head)

    def validate_checkpoint(self, scope: str, epoch: int, saved: Any) -> VerifiedGeneration | None:
        current = self.require_generation(scope, epoch)
        expected = current.document() if current is not None else None
        if saved != expected:
            raise E2eeError("owner_upload_restart_required")
        return current

    def require_generation(self, scope: str, epoch: int, expected: OwnerAuthorityHead | None = None) -> VerifiedGeneration | None:
        organization = self.session.scope_metadata(scope).get("owner_org")
        if not organization:
            return None
        if expected is not None and expected.organization_id != organization:
            raise E2eeError("owner_key_generation_stale")
        return self.generation(scope, epoch, expected or self.owner.authority(organization))

    def _recipient_secret(self, generation: VerifiedGeneration, envelope: Mapping[str, Any]) -> str | None:
        kind, recipient = envelope.get("recipient_kind"), envelope.get("recipient_id")
        if kind == "device":
            return self.session._device["encryption_secret_key"] if recipient == self.session.device_id and generation.authority.owner_subject != self.session.subject else None
        if kind == "owner" and generation.authority.owner_subject == self.session.subject:
            key = next((item for item in self.owner.store.get(generation.authority.organization_id).keys
                        if item.key_id == recipient), None)
            return key.secret_key if key is not None else None
        return None

    def _restored_key(self, generation: VerifiedGeneration, envelope: Mapping[str, Any], source: SignedEvidence,
                      operation: str, secret: str) -> bytearray:
        if not self.owner.recovery.root_history.matches_generation(generation, source, operation):
            raise E2eeError("owner_key_generation_stale")
        selected = {name: value for name, value in envelope.items() if name not in {"operation", "signed_command"}}
        if (selected.get("scope_id") != generation.scope or selected.get("key_epoch") != generation.epoch
                or selected.get("sender_device_id") != source.device_id
                or sum(value == selected for value in source.body.get("envelopes", [])) != 1):
            raise E2eeError("participant_envelope_mismatch")
        issuer = self.session._device_material(None, source.device_id)
        if issuer["account_subject"] != self.session.subject:
            raise E2eeError("account_mismatch")
        source.verify(self.session.crypto, issuer["signing_public_key"], operation)
        fields = {name: value for name, value in selected.items() if name not in {"encapsulated_key", "ciphertext"}}
        if set(fields) != {"scope_id", "key_epoch", "sender_device_id", "recipient_id", "recipient_kind"}:
            raise E2eeError("invalid_envelope")
        context = self.session.crypto.canonical({"v": 1, "domain": "arteligo.scope-key", **fields})
        try:
            key = decode(self.session.crypto.execute({"op": "hpke_auth_open", "recipient_secret_key": secret,
                "sender_public_key": issuer["encryption_public_key"], "info": encode(context), "aad": encode(context),
                "envelope": {"v": 1, "suite": "HPKE-Auth-X25519-HKDF-SHA256-AES256GCM",
                             "enc": selected["encapsulated_key"], "ciphertext": selected["ciphertext"]}})["plaintext"])
            if len(key) != 32:
                wipe(key)
                raise E2eeError("invalid_envelope")
            return key
        finally:
            wipe(context)

    def _open(self, generation: VerifiedGeneration, envelope: dict[str, Any],
              recovery_secret: str | None = None) -> VerifiedPublicationKey | None:
        scope, epoch = generation.scope, generation.epoch
        secret = self._recipient_secret(generation, envelope)
        if recovery_secret is not None and envelope.get("recipient_kind") == "recovery":
            root = self.session.recovery
            if (root is not None and envelope.get("recipient_id") == root["recovery_id"]
                    and generation.authority.owner_subject != self.session.subject):
                secret = recovery_secret
        with ExitStack() as keys:
            if envelope.get("recipient_kind") == "organization":
                if envelope.get("recipient_id") != generation.authority.organization_id or scope == generation.authority.organization_id:
                    raise E2eeError("invalid_envelope")
                bound_epoch = envelope.get("organization_epoch")
                if type(bound_epoch) is not int or bound_epoch < 1:
                    raise E2eeError("invalid_envelope")
                organization = keys.enter_context(self.key(generation.authority.organization_id, bound_epoch, generation.authority))
                secret = encode(organization.key)
            if secret is None:
                return None
            try:
                source = SignedEvidence.parse(envelope.get("signed_command"))
                operation = envelope.get("operation")
                if operation in {"recovery_rotate", "device_approve"}:
                    key = self._restored_key(generation, envelope, source, operation, secret)
                elif operation in {OwnerOperation.ENVELOPES, OwnerOperation.ROTATE} or source.body.get("owner_key_proof") == OWNER_KEY_PROOF:
                    key = self.owner.envelopes.open(scope, epoch, envelope, secret, generation=generation)
                else:
                    if source.document() != generation.command.document():
                        if operation in {"project_create", "organization_create", "rotate_scope"}:
                            raise E2eeError("owner_key_generation_stale")
                        if source.body.get("owner_authority") != generation.authority.to_dict():
                            raise E2eeError("owner_key_generation_stale")
                        issuer = self.session.device(scope, source.device_id, key_epoch=epoch, envelope=envelope)
                        if issuer["account_subject"] == generation.authority.owner_subject:
                            raise E2eeError("owner_key_proof_required")
                        self.qualify_scope_writer(scope, issuer, generation.authority)
                    key = self.session._open_key_envelope(scope, epoch, envelope,
                        recipient=envelope["recipient_id"], kind=envelope["recipient_kind"], secret_key=secret)
                return VerifiedPublicationKey(scope, epoch, key, generation, source)
            except _TrustPathUnavailable:
                raise E2eeError("owner_key_source_unqualified") from None

    def key(self, scope: str, epoch: int, expected: OwnerAuthorityHead | None = None,
            *, recovery_secret: str | None = None) -> VerifiedPublicationKey:
        generation = self.require_generation(scope, epoch, expected)
        if generation is None:
            key = (self.session._read_key(scope, epoch, recipient=self.session.recovery["recovery_id"],
                    kind="recovery", secret_key=recovery_secret) if recovery_secret is not None and self.session.recovery is not None
                   else self.session.scope_key(scope, epoch))
            return VerifiedPublicationKey(scope, epoch, key, None, None)
        original = generation.command.body.get("envelopes")
        if not isinstance(original, list):
            raise E2eeError("owner_generation_proof_missing")
        for envelope in original:
            if not isinstance(envelope, dict):
                raise E2eeError("invalid_envelope")
            opened = self._open(generation, {**envelope, "signed_command": generation.command.document(), "operation": generation.operation}, recovery_secret)
            if opened is not None:
                return opened
        recipients = [(self.session.device_id, "device")]
        if recovery_secret is not None and self.session.recovery is not None:
            recipients.append((self.session.recovery["recovery_id"], "recovery"))
        if generation.authority.owner_subject == self.session.subject:
            recipients.extend((key.key_id, "owner") for key in self.owner.store.get(generation.authority.organization_id).keys)
        metadata = self.session.scope_metadata(scope)
        if metadata.get("participation_policy") == "organization":
            recipients.append((generation.authority.organization_id, "organization"))
        for recipient, kind in recipients:
            values = self.session.call("e2eeGetEnvelopes", scope_id=scope, epoch=epoch,
                                       recipient_id=recipient, recipient_kind=kind)["envelopes"]
            for envelope in values:
                opened = self._open(generation, envelope, recovery_secret)
                if opened is not None:
                    return opened
        raise E2eeError("key_redistribution_required")
