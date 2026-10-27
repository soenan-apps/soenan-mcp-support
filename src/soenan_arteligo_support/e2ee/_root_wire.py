from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Iterator
from typing import Any

from ._crypto import E2eeError, decode, encode, wipe


_FRAGMENT_BYTES = 16384


def _root_parts(operation_id: str, body: dict[str, Any], *, prepare: bool) -> Iterator[bytes]:
    def parts() -> Iterator[dict[str, Any]]:
        if prepare:
            yield {"kind": "prepare_header", "issuer_device_id": body["issuer_device_id"],
                   "expected_root": body["expected_root"]}
            manifest = body["dependency_manifest"]
            for name in ("reference", "retained_binding", "protected_source", "pending_command"):
                for value in manifest[name + "s"]:
                    yield {"kind": name, name: value}
        else:
            yield {"kind": "apply_header", "preparation_digest": body["preparation_digest"],
                   "read_set_digest": body["read_set_digest"]}
            yield {"kind": "root_command", "command": body["root_command"]}
            yield {"kind": "companion_admission", "command": body["companion_admission"]}
            for name, collection, field in (
                ("owner_key", "owner_key_commands", "command"),
                ("owner_candidate", "owner_candidate_commands", "command"),
                ("scope_command", "scope_commands", "scope_command"),
                ("source_submission", "source_submissions", "source_submission"),
                ("keyring", "keyring_commands", "command"),
                ("gate", "gate_commands", "command"),
                ("preparation", "preparation_commands", "command"),
            ):
                for value in body[collection]:
                    yield {"kind": name, field: value}

    for sequence, value in enumerate(parts()):
        event = {"operation_id": operation_id, "sequence": sequence, **value}
        yield json.dumps(event, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def root_request_digest(operation_id: str, body: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for raw in _root_parts(operation_id, body, prepare=False):
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
    return encode(digest.digest())


def root_input(operation_id: str, body: dict[str, Any], *, prepare: bool) -> Iterator[bytes]:
    digest, count = hashlib.sha256(), 0
    for count, raw in enumerate(_root_parts(operation_id, body, prepare=prepare), start=1):
        sequence = count - 1
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
        if len(raw) <= _FRAGMENT_BYTES:
            yield raw + b"\n"
        else:
            for index, start in enumerate(range(0, len(raw), _FRAGMENT_BYTES)):
                fragment = {"operation_id": operation_id, "sequence": sequence, "kind": "fragment",
                            "fragment_index": index, "fragment_final": start + _FRAGMENT_BYTES >= len(raw),
                            "fragment_data": encode(raw[start:start + _FRAGMENT_BYTES])}
                yield json.dumps(fragment, separators=(",", ":")).encode() + b"\n"
    yield json.dumps({"operation_id": operation_id, "sequence": count, "kind": "complete",
                      "event_count": count, "payload_digest": encode(digest.digest())},
                     separators=(",", ":")).encode() + b"\n"


def root_events(events: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    fragments = bytearray()
    identity: tuple[str, int, str] | None = None
    index = 0
    try:
        for event in events:
            if event.get("kind") != "fragment":
                if identity is not None:
                    raise E2eeError("incomplete_key_operation_stream")
                yield event
                continue
            key = (event.get("operation_id"), event.get("sequence"), event.get("fragment_kind"))
            if (identity is not None and key != identity or event.get("fragment_index") != index
                    or type(event.get("fragment_final")) is not bool):
                raise E2eeError("invalid_key_operation_stream")
            identity = key
            raw = decode(event.get("fragment_data"))
            try:
                if not 0 < len(raw) <= _FRAGMENT_BYTES:
                    raise E2eeError("invalid_key_operation_stream")
                fragments.extend(raw)
            finally:
                wipe(raw)
            index += 1
            if event["fragment_final"]:
                value = json.loads(fragments)
                if (not isinstance(value, dict)
                        or (value.get("operation_id"), value.get("sequence"), value.get("kind")) != identity):
                    raise E2eeError("invalid_key_operation_stream")
                wipe(fragments)
                fragments.clear()
                identity, index = None, 0
                yield value
        if identity is not None:
            raise E2eeError("incomplete_key_operation_stream")
    finally:
        wipe(fragments)
