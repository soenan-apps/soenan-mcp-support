from __future__ import annotations

import base64
import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, field

from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferError,
    TransferHTTPError,
    TransferTimeouts,
    TransferTransport,
    post_control_json,
)
from ._wire import is_base64url, strict_object

KEY_CLAIM_PROTOCOL = "audaligo.file-key-claim.v1"


@dataclass(frozen=True)
class FileKeyClaimDescriptor:
    redemption_url: str
    secret: str = field(repr=False)
    expires_at_unix_milliseconds: int


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
    descriptor: FileKeyClaimDescriptor,
    *,
    expected_direction: str,
    expected_project_id: str,
    expected_object_id: str,
    expected_epoch: int,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> FileKeyClaim:
    if descriptor.expires_at_unix_milliseconds <= int(time.time() * 1000):
        raise TransferError(
            "file key claim has expired",
            code="claim_expired",
            recoverable=True,
        )
    try:
        encoded = post_control_json(
            descriptor.redemption_url,
            {"audaligo-key-claim": descriptor.secret},
            maximum_response_bytes=4096,
            timeouts=timeouts,
            transport=transport,
        )
    except TransferHTTPError as error:
        if error.status in {404, 409, 410}:
            raise TransferError(
                "file key claim is unavailable",
                code="claim_unavailable",
                recoverable=True,
            ) from None
        raise
    try:
        value = json.loads(encoded, object_pairs_hook=strict_object)
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
        or value.get("protocol") != KEY_CLAIM_PROTOCOL
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
        data_key=_decode_key(value.get("dataKey"), 32, require_nonzero=True),
        wrapped_nonce=_decode_key(wrapped.get("nonce"), 12),
        wrapped_data_key=_decode_key(wrapped.get("ciphertext"), 48),
    )




def _decode_key(
    value: object, expected_bytes: int, *, require_nonzero: bool = False
) -> bytes:
    if not isinstance(value, str) or not is_base64url(value):
        raise TransferError("file key claim key encoding is invalid")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, base64.binascii.Error):
        raise TransferError("file key claim key encoding is invalid") from None
    if len(decoded) != expected_bytes or (require_nonzero and not any(decoded)):
        raise TransferError("file key claim key material is invalid")
    return decoded


