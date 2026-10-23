from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError
from ._owner_envelopes import OWNER_KEY_PROOF, VerifiedGeneration, open_owner_envelope
from ._owner_protocol import OwnerAuthorityHead, OwnerOperation, SignedEvidence, authority_head

if TYPE_CHECKING:
    from ._owner_access import OwnerAccess


@dataclass(frozen=True)
class VerifiedOwnerEnvelopeCommand:
    operation: str
    scope: str
    epoch: int
    command: SignedEvidence
    sender: Mapping[str, Any]
    envelopes: tuple[Mapping[str, Any], ...]
    authority: OwnerAuthorityHead


class OwnerEnvelopeCommands:
    def __init__(self, owner: OwnerAccess):
        self.owner, self.session, self.crypto = owner, owner.session, owner.crypto

    def _invitation_authority(self, scope: str, signed: SignedEvidence) -> None:
        request = SignedEvidence.parse(signed.body.get("request_command"))
        participants = self.session._participants
        for proof in participants._load(scope, request.body.get("account_subject")):
            if proof.get("kind") != "invitation" or proof.get("approval_command") != signed.document():
                continue
            evidence = participants._evidence(scope, proof)
            if participants._authority(evidence, frozenset(), self.session._current_device_lookup(scope),
                    lambda identifier: self.session._recovery_material(scope, identifier)):
                return
        raise E2eeError("participant_approval_mismatch")

    def source(self, scope: str, epoch: int, command: Mapping[str, Any], operation: str) -> VerifiedOwnerEnvelopeCommand:
        signed = SignedEvidence.parse(dict(command))
        body = signed.body
        if body.get("owner_key_proof") != OWNER_KEY_PROOF:
            raise E2eeError("unsupported_owner_key_proof")
        organization = self.session.scope_metadata(scope).get("owner_org")
        head = authority_head(body.get("owner_authority"), organization)
        if operation == "project_create":
            if epoch != 1 or body.get("project_id") != scope or body.get("owner_org") != organization:
                raise E2eeError("invalid_owner_creation")
            creation = self.owner._project_source(organization, scope)
            if creation.command != signed:
                raise E2eeError("owner_project_source_mismatch")
            sender = creation.creator
        elif operation == "organization_create":
            if scope != organization or epoch != 1 or body.get("scope_id") != scope or body.get("key_epoch") != 1:
                raise E2eeError("invalid_owner_creation")
            sender = self.session._device_material(scope, signed.device_id)
        elif operation in {OwnerOperation.ROTATE, OwnerOperation.ENVELOPES, OwnerOperation.ORDINARY_ENVELOPES, "invitation_approve"}:
            previous = body.get("expected_epoch")
            expected = previous + 1 if operation == OwnerOperation.ROTATE and type(previous) is int else body.get("key_epoch")
            target = SignedEvidence.parse(body.get("request_command")).body.get("project_id") if operation == "invitation_approve" else body.get("scope_id")
            if target != scope or expected != epoch:
                raise E2eeError("invalid_owner_key_command")
            sender = self.session._device_material(scope, signed.device_id)
        else:
            raise E2eeError("invalid_owner_key_command")
        if sender["account_subject"] != head.owner_subject:
            raise E2eeError("owner_signer_mismatch")
        proof = self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=head.binding_digest)
        binding = self.owner.verifier.binding(organization, proof, head)
        self.owner.verifier.signer(organization, signed, sender, binding.binding.body.recovery_root.to_dict())
        signed.verify(self.crypto, sender["signing_public_key"], operation)
        envelopes = body.get("envelopes")
        if not isinstance(envelopes, list) or not envelopes or any(not isinstance(value, dict)
                or value.get("scope_id") != scope or value.get("key_epoch") != epoch
                or value.get("sender_device_id") != signed.device_id for value in envelopes):
            raise E2eeError("invalid_owner_key_command")
        if operation == OwnerOperation.ENVELOPES and any(value.get("recipient_kind") != "owner" for value in envelopes):
            raise E2eeError("invalid_owner_key_command")
        if organization != scope:
            self.owner._project_source(organization, scope)
            if operation == "invitation_approve":
                self._invitation_authority(scope, signed)
            elif operation == OwnerOperation.ORDINARY_ENVELOPES:
                self.owner.publications.qualify_scope_writer(scope, sender, head, current=False)
        return VerifiedOwnerEnvelopeCommand(operation, scope, epoch, signed, sender, tuple(envelopes), head)

    def verify(self, scope: str, epoch: int, command: Mapping[str, Any], operation: str,
               *, generation: VerifiedGeneration | None = None) -> VerifiedOwnerEnvelopeCommand:
        verified = self.source(scope, epoch, command, operation)
        if generation is not None:
            if generation.scope != scope or generation.epoch != epoch or verified.authority != generation.authority:
                raise E2eeError("owner_key_generation_stale")
            proof = self.session.call("e2eeGetOwnerBinding", organization_id=verified.authority.organization_id,
                binding_digest=verified.authority.binding_digest)
            binding = self.owner.verifier.binding(verified.authority.organization_id, proof, verified.authority)
            self.owner.current.qualify(verified.authority.organization_id, verified.sender, binding.root,
                generation.authority, expected_root=binding.root)
        else:
            try:
                original = self.owner.publications.generation(scope, epoch)
            except E2eeError as error:
                if error.code != "owner_generation_proof_missing":
                    raise
            else:
                issuer, created = verified.authority, original.authority
                if (issuer.key_epoch < created.key_epoch or issuer.ownership_revision < created.ownership_revision
                        or (issuer.key_epoch == created.key_epoch and issuer.binding_digest != created.binding_digest)):
                    raise E2eeError("owner_key_generation_stale")
        return verified

    def open(self, scope: str, epoch: int, envelope: Mapping[str, Any], secret: str,
             *, generation: VerifiedGeneration | None = None) -> bytearray:
        signed = SignedEvidence.parse(envelope.get("signed_command"))
        verified = self.verify(scope, epoch, signed.document(), envelope.get("operation"), generation=generation)
        selected = {name: value for name, value in envelope.items() if name not in {"signed_command", "operation"}}
        if sum(value == selected for value in verified.envelopes) != 1:
            raise E2eeError("participant_envelope_mismatch")
        fields = {name: value for name, value in selected.items() if name not in {"encapsulated_key", "ciphertext"}}
        required = {"scope_id", "key_epoch", "sender_device_id", "recipient_id", "recipient_kind"}
        kind = fields.get("recipient_kind")
        if kind == "owner":
            required |= {"owner_key_epoch", "owner_binding_digest"}
            self.owner.envelope_binding(verified.authority.organization_id, fields.get("recipient_id"),
                fields.get("owner_key_epoch"), fields.get("owner_binding_digest"))
        elif kind == "organization":
            required.add("organization_epoch")
        elif kind not in {"device", "recovery"}:
            raise E2eeError("invalid_envelope")
        if set(fields) != required:
            raise E2eeError("invalid_envelope")
        return open_owner_envelope(self.session, fields, selected, verified.authority, secret)

    def sender(self, scope: str, epoch: int, envelope: Mapping[str, Any]) -> dict[str, Any]:
        signed = SignedEvidence.parse(envelope.get("signed_command"))
        body, operation = signed.body, envelope.get("operation")
        if body.get("owner_key_proof") == OWNER_KEY_PROOF or operation in {OwnerOperation.ENVELOPES, OwnerOperation.ROTATE}:
            return dict(self.verify(scope, epoch, signed.document(), operation).sender)
        if operation not in {"project_create", "organization_create", "rotate_scope", "envelopes_save", "invitation_approve"}:
            raise E2eeError("invalid_owner_key_command")
        sender = self.session.device(scope, signed.device_id, key_epoch=epoch)
        signed.verify(self.crypto, sender["signing_public_key"], operation)
        previous = body.get("expected_epoch")
        expected = 1 if operation in {"project_create", "organization_create"} else previous + 1 if operation == "rotate_scope" and type(previous) is int else body.get("key_epoch")
        target = SignedEvidence.parse(body.get("request_command")).body.get("project_id") if operation == "invitation_approve" else body.get("scope_id", body.get("project_id"))
        selected = {name: value for name, value in envelope.items() if name not in {"signed_command", "operation"}}
        if (target != scope or expected != epoch or signed.device_id != selected.get("sender_device_id")
                or sum(value == selected for value in body.get("envelopes", [])) != 1):
            raise E2eeError("participant_envelope_mismatch")
        return sender
