from __future__ import annotations

import json
import secrets
from collections.abc import Callable, Iterable
from functools import wraps

from ._crypto import E2eeError
from ._ordered_index import OrderedIndex

FORMAT = 3
CHAT_HEADER = "conversation_chat_header"
COMMENT_HEADER = "conversation_comment_header"
MAX_INTEGER = 9_007_199_254_740_991


def conflict_retry(method):
    @wraps(method)
    def invoke(self, *args, **kwargs):
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
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"id", "revision"}:
        raise E2eeError("invalid_conversation")
    return {"id": text(value["id"]), "revision": number(value["revision"], 1)}


def ascending(value):
    return str(number(value)).zfill(16)


def descending(value):
    return ascending(MAX_INTEGER - number(value))


def anchor_key(value):
    if not isinstance(value, dict):
        raise E2eeError("invalid_conversation")

    def canonical(item):
        if isinstance(item, dict):
            return {
                key: canonical(item[key])
                for key in sorted(item, key=lambda key: key.encode("utf-16-be"))
            }
        if isinstance(item, list):
            return [canonical(child) for child in item]
        return item

    return json.dumps(
        canonical(value), ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )


def verify_actor(record, field):
    actor = record["value"].get(field)
    member = actor.get("member") if isinstance(actor, dict) else None
    if (
        not isinstance(member, dict)
        or actor.get("kind") != "member"
        or member.get("membershipId") != record["author_subject"]
        or member.get("userId") != record["author_subject"]
    ):
        raise E2eeError("invalid_conversation_author")


def write(identifier, kind, value, revision=0, immutable=False):
    return {
        "record_id": identifier,
        "kind": kind,
        "expected_revision": revision,
        "value": value,
        **({"immutable": True} if immutable else {}),
    }


def initial_records():
    return [
        write(
            CHAT_HEADER,
            "chat",
            {
                "format": FORMAT,
                "recordType": "chat_header",
                "sequence": 0,
                "events": None,
                "messages": None,
            },
        ),
        write(
            COMMENT_HEADER,
            "comment",
            {
                "format": FORMAT,
                "recordType": "comment_header",
                "sequence": 0,
                "threads": None,
            },
        ),
    ]


class ConversationContext:
    def __init__(
        self,
        records,
        scope: str,
        *,
        checkpoint: Callable[[], None] | None = None,
        mint_id: Callable[[], str] | None = None,
    ):
        self.records, self.scope = records, scope
        self.checkpoint = checkpoint or (lambda: None)
        self.mint_id = mint_id or (lambda: "cnd_" + secrets.token_hex(16))

    @property
    def subject(self):
        return self.records.session.subject

    def _read(self, ids: Iterable[str]):
        wanted = list(dict.fromkeys(ids))
        if len(wanted) > 512:
            raise E2eeError("conversation_read_limit")
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

    def _write(self, writes, preconditions=None):
        self.checkpoint()
        if not writes or len(writes) > 256:
            raise E2eeError("conversation_write_limit")
        epoch = self.records.session.scope_metadata(self.scope)["key_epoch"]
        self.records.write(
            self.scope,
            key_epoch=epoch,
            records=writes,
            preconditions=preconditions or [],
        )
        self.checkpoint()

    def _retry(self, operation):
        for attempt in range(3):
            self.checkpoint()
            try:
                return operation()
            except E2eeError as error:
                if error.code != "revision_conflict" or attempt == 2:
                    raise

    def _record(self, record, kind, record_type=None, immutable=False):
        if (
            record is None
            or record["deleted"]
            or record["kind"] != kind
            or (
                immutable
                and (record["revision"] != 1 or not record.get("immutable", False))
            )
            or (
                record_type is not None
                and record["value"].get("recordType") != record_type
            )
        ):
            raise E2eeError("invalid_conversation")
        return record

    def _header(self, record, kind, record_type):
        if record is None:
            raise E2eeError("content_format_update_required")
        self._record(record, kind, record_type)
        if record["value"].get("format") != FORMAT:
            raise E2eeError("content_format_update_required")
        return record

    def _load_header(self, identifier, kind, record_type):
        return self._header(self._read([identifier]).get(identifier), kind, record_type)

    def _index(self, kind, prefetched=None):
        prefetched = prefetched or {}

        def read(ids):
            values = {
                **prefetched,
                **self._read(
                    identifier for identifier in ids if identifier not in prefetched
                ),
            }
            for value in values.values():
                self._record(value, kind)
            return {
                identifier: values[identifier]
                for identifier in ids
                if identifier in values
            }

        return OrderedIndex(read, self.mint_id, kind)

    def _page_size(self, values):
        if (
            len(json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode())
            > 8 * 1024 * 1024
        ):
            raise E2eeError("conversation_page_byte_limit")

    def _same_records(self, before):
        current = self._read(record["record_id"] for record in before)
        if any(
            record["record_id"] not in current
            or current[record["record_id"]]["revision"] != record["revision"]
            or current[record["record_id"]]["value"] != record["value"]
            for record in before
        ):
            raise E2eeError("revision_conflict")

    def initialize(self):
        existing = self._read([CHAT_HEADER, COMMENT_HEADER])
        if not existing:
            self._write(initial_records())
        else:
            self._header(existing.get(CHAT_HEADER), "chat", "chat_header")
            self._header(existing.get(COMMENT_HEADER), "comment", "comment_header")
