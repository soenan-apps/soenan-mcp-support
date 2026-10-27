from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError, wipe
from ._owner_protocol import ROOT_FIELDS, SignedEvidence, canonical_digest
from ._owner_root_history import ScopeGenerationReference
from ._signed_commands import SavedCommand, UncertainCommand
from ._trust import public_device

if TYPE_CHECKING:
    from ._session import DeviceSession


class DeviceApprovals:
    def __init__(self, session: DeviceSession):
        self.session = session

    def _matches(self, command: SignedEvidence, pairing: Mapping[str, Any]) -> bool:
        body = command.body
        return (body.get("challenge") == pairing["challenge"]
                and all(body.get(name) == pairing[name] for name in (
                    "device_id", "account_subject", "encryption_public_key", "signing_public_key")))

    def _receipt(self, command: SignedEvidence, target: Mapping[str, Any]) -> dict[str, Any]:
        issuer = public_device(self.session._device_material(None, command.device_id))
        if issuer["account_subject"] != self.session.subject:
            raise E2eeError("account_mismatch")
        command.verify(self.session.crypto, issuer["signing_public_key"], "device_approve")
        return {"trusted_device": issuer, "recovery_root": command.body["recovery_root"],
                "approved_device": public_device(target), "challenge": command.body["challenge"]}

    def approve(self, pairing: dict[str, Any]) -> dict[str, Any]:
        session = self.session
        session.require_approved()
        target = public_device(pairing)
        if target["account_subject"] != session.subject or not isinstance(pairing.get("challenge"), str):
            raise E2eeError("pairing_mismatch")
        identifier = target["device_id"]
        pending = session.publications.pending("device_approvals", identifier, "device_approve")
        if pending is not None and not self._matches(pending.command, pairing):
            raise E2eeError("device_approval_pending")
        context = session.load_owner_context()
        devices = session.call("e2eeListDevices")["devices"]
        registered = next((item for item in devices if item["device_id"] == identifier), None)
        if registered is not None:
            if public_device(registered) != target:
                raise E2eeError("device_key_changed")
            for certificate in registered.get("certificates", []):
                if certificate.get("operation") != "device_approve":
                    continue
                command = SignedEvidence.parse(certificate["signed_command"])
                if self._matches(command, pairing) and (
                    command == pending.command if pending is not None else command.device_id == session.device_id
                ):
                    receipt = self._receipt(command, registered)
                    if pending is not None:
                        session.publications.finish("device_approvals", identifier, pending)
                    return receipt
            if registered.get("state") == "revoked":
                raise E2eeError("device_revoked")
        if pending is None:
            if session.recovery is None:
                raise E2eeError("recovery_missing")
            qualified = session.owner_access.recovery.root_history.qualified()
            admission = qualified.original_admission if qualified is not None else session.root_admissions.original_current()
            envelopes, references = [], []
            for captured in context.scopes.values():
                scope = captured["scope"]
                if scope["key_epoch"] == 0 and scope["key_state"] == "uninitialized":
                    continue
                organization = scope.get("owner_org")
                if organization and session.owner_access.authority(organization, active=False).owner_subject == session.subject:
                    continue
                epochs = {scope["key_epoch"], *session.root_admissions.recovery_epochs(scope, session.recovery)}
                for epoch in sorted(epochs):
                    publication = (session.owner_access.publications.key(scope["project_id"], epoch)
                                   if epoch == scope["key_epoch"] else None)
                    key = publication.key if publication is not None else session.scope_key(scope["project_id"], epoch)
                    try:
                        envelopes.append(session.wrap_key(scope["project_id"], epoch, key,
                            recipient=identifier, kind="device", public_key=target["encryption_public_key"]))
                        if publication is not None and publication.generation is not None:
                            generation = publication.generation
                            references.append(ScopeGenerationReference(generation.scope, generation.epoch,
                                canonical_digest(session.crypto, {"operation": generation.operation,
                                    "signed_command": generation.command.document()})))
                    finally:
                        wipe(key)
            body = {**target, "challenge": pairing["challenge"],
                    "recovery_root": {name: session.recovery[name] for name in ROOT_FIELDS},
                    "issuer_admission": admission.document(), "envelopes": envelopes}
            body["owner_access_backup"] = session.owner_access.recovery.device_backup(body, admission, references, qualified=qualified)
            pending = SavedCommand("device_approve", UncertainCommand(SignedEvidence.parse(session.sign("device_approve", body))))
            session.publications.save("device_approvals", identifier, pending)
        approved = session.publications.submit("device_approvals", identifier, pending,
            lambda command: session.call("e2eeApproveDevice", body=command, device_id=identifier))
        if public_device(approved) != target or approved.get("state") != "approved":
            raise E2eeError("device_admission_unconfirmed")
        receipt = self._receipt(pending.command, approved)
        session.trust.pin_device(target)
        session.publications.finish("device_approvals", identifier, pending)
        return receipt
