from __future__ import annotations

import secrets
from collections.abc import Callable, Iterable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar, cast, overload

from google.protobuf.message import Message
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._crypto import E2eeError
from ._ordered_index import OrderedIndex
from ._records import EncryptedRecords, ReadRecord
from ._signed_commands import AcceptedCommand

MAX_INTEGER = 9_007_199_254_740_991

P = ParamSpec("P")
R = TypeVar("R")
C = TypeVar("C", bound="ConversationContext")
M = TypeVar("M", bound=Message)


def chat_header_id(scope):
    return f"conversation_chat_header_{scope}"


def conflict_retry(
    method: Callable[Concatenate[C, P], R],
) -> Callable[Concatenate[C, P], R]:
    @wraps(method)
    def invoke(self: C, /, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._retry(lambda: method(self, *args, **kwargs))

    return invoke


def number(value, minimum=0):
    if type(value) is not int or not minimum <= value <= MAX_INTEGER:
        raise E2eeError("invalid_conversation")
    return value


def text(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 256:
        raise E2eeError("invalid_conversation")
    return value


def reference(value):
    return value if value is not None and value.IsInitialized() else None


def ascending(value):
    return str(number(value)).zfill(16)


def descending(value):
    return ascending(MAX_INTEGER - number(value))


def verify_actor(record, field):
    actor = getattr(record["value"], field)
    if (
        actor.membership_id != record["author_subject"]
        or actor.user_id != record["author_subject"]
    ):
        raise E2eeError("invalid_conversation_author")


def write(identifier, kind, value, revision=0, immutable=False, incarnation=""):
    return {
        "record_id": identifier,
        "kind": kind,
        "expected_revision": revision,
        "incarnation": incarnation,
        "value": value,
        **({"immutable": True} if immutable else {}),
    }


def initial_records(scope):
    return [write(chat_header_id(scope), "chat", domain.ChatHeader(sequence=0))]


class ConversationContext:
    def __init__(
        self,
        records: EncryptedRecords,
        scope: str,
        *,
        checkpoint: Callable[[], None] | None = None,
        mint_id: Callable[[], str] | None = None,
    ) -> None:
        self.records, self.scope = records, scope
        self.checkpoint: Callable[[], None] = checkpoint or (lambda: None)
        self.mint_id: Callable[[], str] = mint_id or (
            lambda: "cnd_" + secrets.token_hex(16)
        )

    @property
    def subject(self):
        return self.records.session.subject

    def _read(self, ids: Iterable[str]):
        wanted = list(dict.fromkeys(ids))
        result = {}
        for start in range(0, len(wanted), 256):
            self.checkpoint()
            selected = wanted[start : start + 256]
            values = self.records.read(self.scope, selected)
            if set(values) - set(selected) or any(
                key != value["record_id"] for key, value in values.items()
            ):
                raise E2eeError("invalid_conversation")
            result.update(values)
        self.checkpoint()
        return result

    def _write(
        self,
        writes,
        preconditions: list[app.RecordPrecondition] | None = None,
        *,
        comments=(),
    ) -> AcceptedCommand | None:
        self.checkpoint()
        if not writes:
            raise E2eeError("conversation_write_limit")
        outcome = self.records.write(
            self.scope,
            records=writes,
            preconditions=preconditions or [],
            comments=comments,
        )
        if isinstance(outcome, AcceptedCommand):
            return outcome
        self.checkpoint()

    def _retry(self, operation: Callable[[], R]) -> R:
        attempt = 0
        while True:
            self.checkpoint()
            try:
                return operation()
            except E2eeError as error:
                if error.code != "revision_conflict" or attempt == 2:
                    raise
                attempt += 1

    @overload
    def _record(
        self, record, kind: str, record_type: type[M], immutable: bool = False
    ) -> ReadRecord[M]: ...

    @overload
    def _record(
        self, record, kind: str, record_type: None = None, immutable: bool = False
    ) -> ReadRecord[Message]: ...

    def _record(
        self,
        record,
        kind: str,
        record_type: type[M] | None = None,
        immutable: bool = False,
    ) -> ReadRecord[M] | ReadRecord[Message]:
        if (
            record is None
            or record["payload_type"] != "content"
            or record["kind"] != kind
            or (
                immutable
                and (record["revision"] != 1 or not record.get("immutable", False))
            )
            or (
                record_type is not None and not isinstance(record["value"], record_type)
            )
        ):
            raise E2eeError("invalid_conversation")
        return cast("ReadRecord[M] | ReadRecord[Message]", record)

    def _header(self, record, kind: str, record_type: type[M]) -> ReadRecord[M]:
        if record is None:
            raise E2eeError("content_format_update_required")
        return self._record(record, kind, record_type)

    def _load_header(
        self, identifier: str, kind: str, record_type: type[M]
    ) -> ReadRecord[M]:
        return self._header(self._read([identifier]).get(identifier), kind, record_type)

    def _index(self, kind, prefetched=None):
        cached = prefetched or {}

        def read(ids):
            values = {
                **cached,
                **self._read(
                    identifier for identifier in ids if identifier not in cached
                ),
            }
            for value in values.values():
                self._record(value, kind)
            return {
                identifier: values[identifier]
                for identifier in ids
                if identifier in values
            }

        return OrderedIndex(read, self.mint_id, kind, self.records.operation_id)

    def _same_records(self, before):
        current = self._read(record["record_id"] for record in before)
        if any(
            record["record_id"] not in current
            or current[record["record_id"]]["revision"] != record["revision"]
            or current[record["record_id"]]["incarnation"] != record["incarnation"]
            or current[record["record_id"]]["value"] != record["value"]
            for record in before
        ):
            raise E2eeError("revision_conflict")

    def initialize(self) -> AcceptedCommand | None:
        chat_header = chat_header_id(self.scope)
        existing = self._read([chat_header])
        if not existing:
            return self._write(initial_records(self.scope))
        self._header(existing.get(chat_header), "chat", domain.ChatHeader)
