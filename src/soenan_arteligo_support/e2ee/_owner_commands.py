from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._crypto import E2eeError
from ._owner_envelopes import OWNER_KEY_PROOF
from ._owner_protocol import OwnerManifest, OwnerOperation
from ._owner_state import OwnerStateStore
from ._signed_commands import RejectedCommand, SavedCommand

if TYPE_CHECKING:
    from ._session import DeviceSession


class OwnerCommands:
    def __init__(self, session: DeviceSession, store: OwnerStateStore):
        self.session, self.store = session, store

    def _send(self, organization: str, saved: SavedCommand, command: dict[str, str]) -> dict[str, Any]:
        operation = OwnerOperation(saved.operation)
        scope = saved.command.body.get("scope_id")
        match operation:
            case OwnerOperation.INVALIDATE:
                return self.session.call("e2eeInvalidateOwnerCustody", organization_id=organization, body=command)
            case OwnerOperation.KEYRING:
                return self.session.call("e2eeSaveOwnerKeyring", organization_id=organization, body=command)
            case OwnerOperation.MANIFEST:
                if saved.source_documents is None:
                    raise E2eeError("owner_source_document_missing")
                manifest = OwnerManifest.parse(self.session.crypto, command, saved.source_documents)
                return self.session.call("e2eeSaveOwnerManifest", organization_id=organization, body=manifest.submission())
            case OwnerOperation.GATE:
                return self.session.call("e2eeCreateOwnerGate", organization_id=organization, body=command)
            case OwnerOperation.PREPARE:
                return self.session.call("e2eeSaveOwnerPreparation", organization_id=organization, body=command)
            case OwnerOperation.ENVELOPES:
                return self.session.call("e2eeSaveOwnerEnvelopes", scope_id=scope, body=command)
            case OwnerOperation.ORDINARY_ENVELOPES:
                return self.session.call("e2eeSaveEnvelopes", scope_id=scope, body=command)
            case OwnerOperation.ROTATE:
                return self.session.call("e2eeRotateOwnerScope", scope_id=scope, body=command)
            case OwnerOperation.REGISTER_KEY:
                return self.session.call("e2eeRegisterOwnerKey", organization_id=organization, body=command)
            case OwnerOperation.OFFER:
                return self.session.call("e2eeRegisterOwnerCandidate", organization_id=organization, body=command)
        raise E2eeError("invalid_owner_command")

    def submit(self, organization: str, slot: str, operation: OwnerOperation,
               body: dict[str, Any] | None = None) -> dict[str, Any]:
        saved = self.store.command(organization, slot, operation, body)
        if operation in {OwnerOperation.ENVELOPES, OwnerOperation.ROTATE} and saved.command.body.get("owner_key_proof") != OWNER_KEY_PROOF:
            raise E2eeError("unsupported_owner_key_proof")
        try:
            return saved.submit(lambda command: self._send(organization, saved, command),
                                lambda: self.store.save(organization))
        except E2eeError:
            if isinstance(saved.outcome, RejectedCommand):
                self.store.finish(organization, slot)
            raise

    def resume(self, organization: str) -> None:
        for slot, saved in tuple(self.store.get(organization).journal.items()):
            self.submit(organization, slot, OwnerOperation(saved.operation))
            if saved.operation in {OwnerOperation.ENVELOPES, OwnerOperation.ORDINARY_ENVELOPES, OwnerOperation.KEYRING}:
                self.store.finish(organization, slot)
