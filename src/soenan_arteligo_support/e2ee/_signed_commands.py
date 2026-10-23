from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from ._crypto import E2eeError
from ._owner_protocol import SignedEvidence, object_value

if TYPE_CHECKING:
    from ._session import DeviceSession

_DEFINITIVE_REJECTIONS = frozenset({
    "revision_conflict", "owner_authority_changed", "owner_custody_changed",
    "owner_candidate_invalidated", "owner_candidate_key_consumed",
})


@dataclass(frozen=True)
class UncertainCommand:
    command: SignedEvidence


@dataclass(frozen=True)
class AcceptedCommand:
    command: SignedEvidence
    result: dict[str, Any]


@dataclass(frozen=True)
class RejectedCommand:
    command: SignedEvidence
    code: str


CommandOutcome = UncertainCommand | AcceptedCommand | RejectedCommand


@dataclass
class SavedCommand:
    operation: str
    outcome: CommandOutcome
    intent: str | None = None
    key: str | None = field(default=None, repr=False)
    epoch: int | None = None
    source_documents: tuple[dict[str, str], ...] | None = None

    @property
    def command(self) -> SignedEvidence:
        return self.outcome.command

    @classmethod
    def parse(cls, value: Any, operation: str | None = None) -> SavedCommand:
        value = object_value(value)
        try:
            selected = operation or value["operation"]
            if not isinstance(selected, str) or not selected:
                raise E2eeError("invalid_saved_command")
            command = SignedEvidence.parse(value["command"])
            outcome = value.get("outcome", {"state": "uncertain"})
            if outcome["state"] == "uncertain":
                parsed: CommandOutcome = UncertainCommand(command)
            elif outcome["state"] == "accepted":
                parsed = AcceptedCommand(command, object_value(outcome["result"]))
            elif outcome["state"] == "rejected" and isinstance(outcome["code"], str):
                parsed = RejectedCommand(command, outcome["code"])
            else:
                raise E2eeError("invalid_saved_command")
            if "outcome" not in value and "result" in value:
                parsed = AcceptedCommand(command, object_value(value["result"]))
            documents = value.get("source_documents")
            if documents is not None and (not isinstance(documents, list) or any(
                not isinstance(item, dict) or set(item) != {"document_bytes"}
                or not isinstance(item["document_bytes"], str) for item in documents
            )):
                raise E2eeError("invalid_saved_command")
            return cls(selected, parsed, value.get("intent"), value.get("key"), value.get("epoch"),
                       tuple(documents) if documents is not None else None)
        except (KeyError, TypeError):
            raise E2eeError("invalid_saved_command") from None

    def document(self) -> dict[str, Any]:
        match self.outcome:
            case UncertainCommand():
                outcome = {"state": "uncertain"}
            case AcceptedCommand(result=result):
                outcome = {"state": "accepted", "result": result}
            case RejectedCommand(code=code):
                outcome = {"state": "rejected", "code": code}
        value = {"operation": self.operation, "command": self.command.document(), "outcome": outcome}
        for field in ("intent", "key", "epoch"):
            item = getattr(self, field)
            if item is not None:
                value[field] = item
        if self.source_documents is not None:
            value["source_documents"] = list(self.source_documents)
        return value

    def submit(self, send: Callable[[dict[str, str]], dict[str, Any]],
               persist: Callable[[], None], *, rejections: frozenset[str] = _DEFINITIVE_REJECTIONS) -> dict[str, Any]:
        if isinstance(self.outcome, AcceptedCommand):
            return self.outcome.result
        if isinstance(self.outcome, RejectedCommand):
            raise E2eeError(self.outcome.code)
        try:
            result = send(self.command.document())
        except E2eeError as error:
            if error.code in rejections:
                self.outcome = RejectedCommand(self.command, error.code)
                persist()
            raise
        self.outcome = AcceptedCommand(self.command, result)
        persist()
        return result


class PublicationJournal:
    """Owns publication and rotation outcomes inside the existing protected document."""

    def __init__(self, session: DeviceSession):
        self.session = session

    def _document(self) -> dict[str, Any]:
        self.session.require_approved()
        if self.session._device is None:
            raise E2eeError("device_approval_required")
        return self.session._device

    def pending(self, collection: str, scope: str, operation: str | None = None) -> SavedCommand | None:
        value = self._document().get(collection, {}).get(scope)
        if value is None:
            return None
        if collection == "scope_rotations" and operation is None:
            operation = "owner_rotate_scope" if value.get("api") == "e2eeRotateOwnerScope" else value.get("operation", "rotate_scope")
        saved = SavedCommand.parse(value, operation)
        if isinstance(saved.outcome, RejectedCommand):
            self.finish(collection, scope, saved)
            return None
        return saved

    def _persist(self) -> None:
        try:
            self.session._persist()
        except BaseException:
            self.session.lock()
            raise

    def save(self, collection: str, scope: str, saved: SavedCommand) -> None:
        self._document().setdefault(collection, {})[scope] = saved.document()
        self._persist()

    def finish(self, collection: str, scope: str, saved: SavedCommand) -> None:
        document = self._document()
        document.setdefault(collection, {}).pop(scope, None)
        self._persist()

    def submit(self, collection: str, scope: str, saved: SavedCommand,
               send: Callable[[dict[str, str]], dict[str, Any]]) -> dict[str, Any]:
        try:
            return saved.submit(send, lambda: self.save(collection, scope, saved),
                                rejections=frozenset({"revision_conflict"}))
        except E2eeError:
            if isinstance(saved.outcome, RejectedCommand):
                self.finish(collection, scope, saved)
            raise
