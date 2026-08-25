from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferError,
    TransferTimeouts,
    TransferTransport,
    post_control_json,
)

_PROTOCOL = "audaligo.file-key-claim.v1"


@dataclass(frozen=True)
class FileKeyClaim:
    direction: str
    project_id: str
    object_id: str
    epoch: int
    data_key: bytes
    wrapped_nonce: bytes
    wrapped_data_key: bytes


def redeem_file_key_claim(
    descriptor: Mapping[str, Any],
    *,
    expected_direction: str,
    expected_project_id: str,
    expected_object_id: str,
    expected_epoch: int,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> FileKeyClaim:
    if set(descriptor) != {"url", "expiresAtUnixMilliseconds", "protocol"}:
        raise TransferError("file key claim descriptor is invalid")
    if descriptor.get("protocol") != _PROTOCOL:
        raise TransferError("file key claim protocol is unsupported")
    expires_at_raw = descriptor.get("expiresAtUnixMilliseconds")
    if isinstance(expires_at_raw, str) and expires_at_raw.isdecimal():
        expires_at = int(expires_at_raw)
    else:
        expires_at = expires_at_raw
    if (
        isinstance(expires_at, bool)
        or not isinstance(expires_at, int)
        or expires_at <= 0
    ):
        raise TransferError("file key claim expiry is invalid")
    raw_url = descriptor.get("url")
    if not isinstance(raw_url, str) or not raw_url or len(raw_url) > 8192:
        raise TransferError("file key claim URL is invalid")
    parsed = urlsplit(raw_url)
    secret = parsed.fragment
    if (
        parsed.scheme not in ("http", "https")
        or (
            parsed.scheme == "http"
            and parsed.hostname not in ("localhost", "127.0.0.1")
        )
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or len(secret) != 43
        or not _is_base64url(secret)
    ):
        raise TransferError("file key claim URL is invalid")
    redemption_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
    encoded = post_control_json(
        redemption_url,
        {"audaligo-key-claim": secret},
        maximum_response_bytes=4096,
        timeouts=timeouts,
        transport=transport,
    )
    try:
        value = json.loads(encoded, object_pairs_hook=_strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise TransferError("file key claim response is invalid") from None
    if not isinstance(value, Mapping) or set(value) != {
        "version",
        "protocol",
        "direction",
        "projectId",
        "objectId",
        "epoch",
        "dataKey",
        "wrappedDataKey",
    }:
        raise TransferError("file key claim response is invalid")
    wrapped = value.get("wrappedDataKey")
    if not isinstance(wrapped, Mapping) or set(wrapped) != {"nonce", "ciphertext"}:
        raise TransferError("file key claim wrapped key is invalid")
    epoch = value.get("epoch")
    if (
        value.get("version") != 1
        or value.get("protocol") != _PROTOCOL
        or value.get("direction") != expected_direction
        or value.get("projectId") != expected_project_id
        or value.get("objectId") != expected_object_id
        or isinstance(epoch, bool)
        or not isinstance(epoch, int)
        or epoch != expected_epoch
    ):
        raise TransferError("file key claim does not match the transfer")
    return FileKeyClaim(
        direction=expected_direction,
        project_id=expected_project_id,
        object_id=expected_object_id,
        epoch=expected_epoch,
        data_key=_decode_key(value.get("dataKey"), 32),
        wrapped_nonce=_decode_key(wrapped.get("nonce"), 12),
        wrapped_data_key=_decode_key(wrapped.get("ciphertext"), 48),
    )


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _decode_key(value: object, expected_bytes: int) -> bytes:
    if not isinstance(value, str) or not _is_base64url(value):
        raise TransferError("file key claim key encoding is invalid")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, base64.binascii.Error):
        raise TransferError("file key claim key encoding is invalid") from None
    if len(decoded) != expected_bytes or not any(decoded):
        raise TransferError("file key claim key material is invalid")
    return decoded


def _is_base64url(value: str) -> bool:
    return bool(value) and all(
        character.isascii() and (character.isalnum() or character in "-_")
        for character in value
    )
