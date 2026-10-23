from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError, encode, decode, wipe
from ._owner_protocol import OwnerAuthorityHead, SignedEvidence
from ._owner_state import OwnerKey

if TYPE_CHECKING:
    from ._session import DeviceSession


OWNER_KEY_PROOF = "hpke_auth_v1"


@dataclass(frozen=True)
class VerifiedGeneration:
    scope: str
    epoch: int
    operation: str
    command: SignedEvidence
    authority: OwnerAuthorityHead

    def document(self) -> dict[str, Any]:
        return {"key_epoch": self.epoch, "owner_authority": self.authority.to_dict(),
                "signed_command": self.command.document(), "operation": self.operation}


@dataclass(frozen=True)
class VerifiedPublicationKey:
    scope: str
    epoch: int
    key: bytearray = field(repr=False)
    generation: VerifiedGeneration | None
    source: SignedEvidence | None

    def validate_checkpoint(self, saved: Any) -> None:
        if saved != (self.generation.document() if self.generation is not None else None):
            raise E2eeError("owner_upload_restart_required")

    def __enter__(self) -> VerifiedPublicationKey:
        return self

    def __exit__(self, *_: Any) -> None:
        wipe(self.key)


@dataclass(frozen=True)
class OwnerEnvelopeContext:
    fields: Mapping[str, Any]
    authority: OwnerAuthorityHead

    def document(self) -> dict[str, Any]:
        return {
            "v": 1, "domain": "arteligo.owner-scope-key", **self.fields,
            "sender_owner": {"organization_id": self.authority.organization_id,
                             "key_id": self.authority.key_id, "key_epoch": self.authority.key_epoch,
                             "binding_digest": self.authority.binding_digest},
        }


class OwnerEnvelopeIssuer:
    def __init__(self, session: DeviceSession, head: OwnerAuthorityHead, key: OwnerKey):
        if (key.key_id != head.key_id or key.key_epoch != head.key_epoch
                or key.public_key != head.public_key or key.binding_digest != head.binding_digest):
            raise E2eeError("owner_key_changed")
        self.session, self.head, self.key = session, head, key

    def wrap(self, scope: str, epoch: int, key: bytearray, *, recipient: str,
             kind: str, public_key: str, organization_epoch: int | None = None,
             owner_key_epoch: int | None = None, owner_binding_digest: str | None = None) -> dict[str, Any]:
        self.session.require_approved()
        if kind == "recovery":
            self.session.trust.check_recovery_recipient(scope, recipient, public_key)
        fields: dict[str, Any] = {"scope_id": scope, "key_epoch": epoch,
            "sender_device_id": self.session.device_id, "recipient_id": recipient, "recipient_kind": kind}
        if kind == "owner":
            if recipient != self.head.key_id or owner_key_epoch != self.head.key_epoch or owner_binding_digest != self.head.binding_digest:
                raise E2eeError("invalid_owner_key_command")
            fields.update(owner_key_epoch=owner_key_epoch, owner_binding_digest=owner_binding_digest)
        elif kind == "organization":
            if type(organization_epoch) is not int or organization_epoch < 1:
                raise E2eeError("invalid_envelope")
            fields["organization_epoch"] = organization_epoch
        elif kind not in {"device", "recovery"}:
            raise E2eeError("invalid_envelope")
        context = self.session.crypto.canonical(OwnerEnvelopeContext(fields, self.head).document())
        try:
            sealed = self.session.crypto.execute({
                "op": "hpke_auth_seal", "sender_secret_key": self.key.secret_key,
                "recipient_public_key": public_key, "plaintext": encode(key),
                "info": encode(context), "aad": encode(context),
            })
            return {**fields, "encapsulated_key": sealed["enc"], "ciphertext": sealed["ciphertext"]}
        finally:
            wipe(context)


def open_owner_envelope(session: DeviceSession, fields: Mapping[str, Any],
                        envelope: Mapping[str, Any], authority: OwnerAuthorityHead,
                        recipient_secret: str) -> bytearray:
    context = session.crypto.canonical(OwnerEnvelopeContext(fields, authority).document())
    try:
        opened = session.crypto.execute({
            "op": "hpke_auth_open", "recipient_secret_key": recipient_secret,
            "sender_public_key": authority.public_key, "info": encode(context), "aad": encode(context),
            "envelope": {"v": 1, "suite": "HPKE-Auth-X25519-HKDF-SHA256-AES256GCM",
                         "enc": envelope["encapsulated_key"], "ciphertext": envelope["ciphertext"]},
        })
        key = decode(opened["plaintext"])
        if len(key) != 32:
            wipe(key)
            raise E2eeError("invalid_envelope")
        return key
    finally:
        wipe(context)
