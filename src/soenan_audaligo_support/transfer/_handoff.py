from __future__ import annotations

import base64
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import urlsplit, urlunsplit

from ._api import _validate_control_origin, _validate_transfer_continuation
from ._claim import FileKeyClaimDescriptor, KEY_CLAIM_PROTOCOL
from ._crypto import CHUNK_SIZE, MAXIMUM_CHUNKS, MAXIMUM_WIRE_INTEGER
from ._http import TransferError
from ._wire import is_base64url

TRANSFER_PROTOCOL = "audaligo.encrypted-transfer.v1"
Operation = Literal["upload", "file_download", "preview_download"]


@dataclass(frozen=True)
class UploadMetadata:
    filename: str
    plaintext_size: int
    operation_id: str
    mix_version_id: str | None


@dataclass(frozen=True)
class FileMetadata:
    project_id: str
    file_id: str
    object_id: str
    filename: str
    plaintext_size: int
    media_type: str
    mix_version_id: str | None
    created_at_unix_milliseconds: int
    updated_at_unix_milliseconds: int


@dataclass(frozen=True)
class PreviewMetadata:
    mix_version_id: str
    preview_id: str
    state: str


@dataclass(frozen=True)
class TransferHandoff:
    operation: Operation
    project_id: str
    object_id: str
    epoch: int
    key_claim: FileKeyClaimDescriptor
    continuation: str
    control_origin: str
    upload: UploadMetadata | None = None
    file: FileMetadata | None = None
    preview: PreviewMetadata | None = None
    manifest: Mapping[str, Any] | None = None


def parse_handoff(
    structured_content: Mapping[str, Any],
    *,
    now_unix_milliseconds: int | None = None,
) -> TransferHandoff:
    if not isinstance(structured_content, Mapping):
        raise TransferError("structuredContent must be an object")
    operation = structured_content.get("operation")
    if operation not in {"upload", "file_download", "preview_download"}:
        raise TransferError("structuredContent operation is unsupported")

    operation_field = {
        "upload": "upload",
        "file_download": "file",
        "preview_download": "preview",
    }[operation]
    required = {
        "operation",
        "projectId",
        "objectId",
        "epoch",
        "keyClaim",
        "continuation",
        "controlOrigin",
        "protocolVersion",
        operation_field,
    }
    if operation != "upload":
        required.add("manifest")
    _exact_fields(structured_content, required, "structuredContent")
    if structured_content.get("protocolVersion") != TRANSFER_PROTOCOL:
        raise TransferError("structuredContent protocol is unsupported")

    project_id = _identifier(structured_content, "projectId")
    object_id = _identifier(structured_content, "objectId")
    epoch = _wire_integer(structured_content, "epoch")
    continuation = _validate_transfer_continuation(
        structured_content.get("continuation")
    )
    control_origin = _validate_control_origin(structured_content.get("controlOrigin"))
    claim = _claim_descriptor(
        structured_content.get("keyClaim"),
        expected_origin=control_origin,
        now_unix_milliseconds=(
            int(time.time() * 1000)
            if now_unix_milliseconds is None
            else now_unix_milliseconds
        ),
    )

    if operation == "upload":
        upload = _upload_metadata(structured_content.get("upload"))
        return TransferHandoff(
            operation=operation,
            project_id=project_id,
            object_id=object_id,
            epoch=epoch,
            key_claim=claim,
            continuation=continuation,
            control_origin=control_origin,
            upload=upload,
        )

    if operation == "file_download":
        file = _file_metadata(structured_content.get("file"))
        manifest = _file_manifest(structured_content.get("manifest"))
        if (
            file.project_id != project_id
            or file.object_id != object_id
            or file.plaintext_size != manifest["plaintextSize"]
            or file.file_id != manifest["fileId"]
        ):
            raise TransferError("file handoff bindings do not match")
        return TransferHandoff(
            operation=operation,
            project_id=project_id,
            object_id=object_id,
            epoch=epoch,
            key_claim=claim,
            continuation=continuation,
            control_origin=control_origin,
            file=file,
            manifest=manifest,
        )

    preview = _preview_metadata(structured_content.get("preview"))
    manifest = _preview_manifest(structured_content.get("manifest"))
    if preview.preview_id != object_id:
        raise TransferError("preview handoff bindings do not match")
    return TransferHandoff(
        operation=operation,
        project_id=project_id,
        object_id=object_id,
        epoch=epoch,
        key_claim=claim,
        continuation=continuation,
        control_origin=control_origin,
        preview=preview,
        manifest=manifest,
    )


def _claim_descriptor(
    value: Any, *, expected_origin: str, now_unix_milliseconds: int
) -> FileKeyClaimDescriptor:
    value = _object(value, "keyClaim")
    _exact_fields(
        value,
        {"url", "expiresAtUnixMilliseconds", "protocol"},
        "keyClaim",
    )
    if value.get("protocol") != KEY_CLAIM_PROTOCOL:
        raise TransferError("file key claim protocol is unsupported")
    expires_at = _wire_integer(value, "expiresAtUnixMilliseconds")
    if expires_at <= now_unix_milliseconds:
        raise TransferError(
            "file key claim has expired",
            code="claim_expired",
            recoverable=True,
        )
    raw_url = value.get("url")
    if not isinstance(raw_url, str) or not raw_url or len(raw_url) > 8192:
        raise TransferError("file key claim URL is invalid")
    try:
        parsed = urlsplit(raw_url)
        claim_origin = _validate_control_origin(
            urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
        )
    except (TransferError, ValueError):
        raise TransferError("file key claim URL is invalid") from None
    if (
        claim_origin != expected_origin
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or not parsed.path
        or len(parsed.fragment) != 43
        or not is_base64url(parsed.fragment)
    ):
        raise TransferError("file key claim URL is invalid")
    return FileKeyClaimDescriptor(
        redemption_url=urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "")),
        secret=parsed.fragment,
        expires_at_unix_milliseconds=expires_at,
    )


def _upload_metadata(value: Any) -> UploadMetadata:
    value = _object(value, "upload")
    required = {"filename", "plaintextSize", "operationId"}
    allowed = required | {"mixVersionId"}
    _fields(value, required, allowed, "upload")
    mix_version = value.get("mixVersionId")
    if mix_version is not None:
        mix_version = _identifier(value, "mixVersionId")
    return UploadMetadata(
        filename=_bounded_string(value, "filename", 1024),
        plaintext_size=_positive_wire_integer(value, "plaintextSize"),
        operation_id=_identifier(value, "operationId"),
        mix_version_id=mix_version,
    )


def _file_metadata(value: Any) -> FileMetadata:
    value = _object(value, "file")
    required = {
        "projectId",
        "fileId",
        "objectId",
        "filename",
        "plaintextSize",
        "mediaType",
        "createdAtUnixMilliseconds",
        "updatedAtUnixMilliseconds",
    }
    allowed = required | {"mixVersionId"}
    _fields(value, required, allowed, "file")
    mix_version = value.get("mixVersionId")
    if mix_version is not None:
        mix_version = _identifier(value, "mixVersionId")
    return FileMetadata(
        project_id=_identifier(value, "projectId"),
        file_id=_identifier(value, "fileId"),
        object_id=_identifier(value, "objectId"),
        filename=_bounded_string(value, "filename", 1024),
        plaintext_size=_positive_wire_integer(value, "plaintextSize"),
        media_type=_bounded_string(value, "mediaType", 255),
        mix_version_id=mix_version,
        created_at_unix_milliseconds=_wire_integer(value, "createdAtUnixMilliseconds"),
        updated_at_unix_milliseconds=_wire_integer(value, "updatedAtUnixMilliseconds"),
    )


def _preview_metadata(value: Any) -> PreviewMetadata:
    value = _object(value, "preview")
    _fields(
        value,
        {"mixVersionId", "previewId", "state"},
        {"mixVersionId", "previewId", "state", "failureReason"},
        "preview",
    )
    if value.get("state") != "ready" or "failureReason" in value:
        raise TransferError("preview is not ready for download")
    return PreviewMetadata(
        mix_version_id=_identifier(value, "mixVersionId"),
        preview_id=_identifier(value, "previewId"),
        state="ready",
    )


def _file_manifest(value: Any) -> Mapping[str, Any]:
    value = _object(value, "manifest")
    fields = {
        "version",
        "type",
        "suiteId",
        "encryptionMode",
        "contentKeyAlgorithm",
        "wrapAlgorithm",
        "shareId",
        "fileId",
        "nonceBase64url",
        "plaintextSize",
        "ciphertextSize",
        "chunkSize",
        "chunks",
    }
    _exact_fields(value, fields, "manifest")
    if (
        _numeric_wire_integer(value, "version") != 1
        or value.get("type") != "audaligo.managed-encrypted-object-manifest"
        or value.get("suiteId") != "aes-256-gcm-audaligo-v1"
        or value.get("encryptionMode") != "managed-project-key"
        or value.get("contentKeyAlgorithm") != "A256GCM"
        or value.get("wrapAlgorithm") != "a256gcm-project-epoch-v1"
        or value.get("shareId") != "project_file_managed_v1"
    ):
        raise TransferError("file manifest contract is unsupported")
    _identifier(value, "fileId")
    _base64url_string(value, "nonceBase64url", expected_bytes=8)
    normalized = dict(value)
    normalized["version"] = _numeric_wire_integer(value, "version")
    for key in ("plaintextSize", "ciphertextSize"):
        normalized[key] = _positive_wire_integer(value, key)
    normalized["chunkSize"] = _positive_numeric_wire_integer(value, "chunkSize")
    normalized["chunks"] = list(_chunks(value.get("chunks")))
    _validate_manifest_layout(normalized, preview=False)
    return normalized


def _preview_manifest(value: Any) -> Mapping[str, Any]:
    value = _object(value, "manifest")
    fields = {
        "contract",
        "sourceObjectId",
        "processingId",
        "jobId",
        "mediaType",
        "codec",
        "bitrateBps",
        "nonceBase64url",
        "plaintextSize",
        "ciphertextSize",
        "chunkSize",
        "chunks",
    }
    _exact_fields(value, fields, "manifest")
    if (
        value.get("contract") != "audaligo.managed-preview-read-descriptor"
        or value.get("mediaType") != "audio/mp4"
        or value.get("codec") != "mp4a.40.2"
        or _numeric_wire_integer(value, "bitrateBps") != 128_000
    ):
        raise TransferError("preview manifest contract is unsupported")
    for key in ("sourceObjectId", "processingId", "jobId"):
        _identifier(value, key)
    _base64url_string(value, "nonceBase64url", expected_bytes=8)
    normalized = dict(value)
    normalized["bitrateBps"] = _numeric_wire_integer(value, "bitrateBps")
    for key in ("plaintextSize", "ciphertextSize"):
        normalized[key] = _positive_wire_integer(value, key)
    normalized["chunkSize"] = _positive_numeric_wire_integer(value, "chunkSize")
    normalized["chunks"] = list(_chunks(value.get("chunks")))
    _validate_manifest_layout(normalized, preview=True)
    return normalized


def _chunks(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TransferError("manifest chunks must be an array")
    if not 1 <= len(value) <= 4096:
        raise TransferError("manifest chunk count is invalid")
    fields = {
        "chunkIndex",
        "plaintextOffset",
        "plaintextSize",
        "ciphertextOffset",
        "ciphertextSize",
        "ciphertextSha256Base64url",
        "finalChunk",
    }
    result: list[Mapping[str, Any]] = []
    for raw in value:
        chunk = _object(raw, "manifest chunk")
        _exact_fields(chunk, fields, "manifest chunk")
        normalized = dict(chunk)
        normalized["chunkIndex"] = _numeric_wire_integer(chunk, "chunkIndex")
        normalized["plaintextOffset"] = _wire_integer(chunk, "plaintextOffset")
        normalized["plaintextSize"] = _positive_wire_integer(chunk, "plaintextSize")
        normalized["ciphertextOffset"] = _wire_integer(chunk, "ciphertextOffset")
        normalized["ciphertextSize"] = _positive_wire_integer(chunk, "ciphertextSize")
        _base64url_string(chunk, "ciphertextSha256Base64url", expected_bytes=32)
        if not isinstance(chunk.get("finalChunk"), bool):
            raise TransferError("manifest chunk final flag is invalid")
        result.append(normalized)
    return tuple(result)


def _validate_manifest_layout(manifest: Mapping[str, Any], *, preview: bool) -> None:
    plaintext_size = manifest["plaintextSize"]
    ciphertext_size = manifest["ciphertextSize"]
    chunk_size = manifest["chunkSize"]
    chunks = manifest["chunks"]
    if (
        not isinstance(plaintext_size, int)
        or not isinstance(ciphertext_size, int)
        or not isinstance(chunk_size, int)
        or not isinstance(chunks, Sequence)
        or not 1 <= chunk_size <= CHUNK_SIZE
        or (preview and chunk_size != CHUNK_SIZE)
        or not 1 <= len(chunks) <= MAXIMUM_CHUNKS
        or (plaintext_size - 1) // chunk_size + 1 != len(chunks)
    ):
        raise TransferError("manifest chunk layout is invalid")
    plaintext_offset = 0
    ciphertext_offset = 0
    for index, raw in enumerate(chunks):
        if not isinstance(raw, Mapping):
            raise TransferError("manifest chunk layout is invalid")
        expected_plaintext = min(chunk_size, plaintext_size - plaintext_offset)
        if (
            raw["chunkIndex"] != index
            or raw["plaintextOffset"] != plaintext_offset
            or raw["plaintextSize"] != expected_plaintext
            or raw["ciphertextOffset"] != ciphertext_offset
            or raw["ciphertextSize"] != expected_plaintext + 16
            or raw["finalChunk"] != (index + 1 == len(chunks))
        ):
            raise TransferError("manifest chunk layout is invalid")
        plaintext_offset += raw["plaintextSize"]
        ciphertext_offset += raw["ciphertextSize"]
    if plaintext_offset != plaintext_size or ciphertext_offset != ciphertext_size:
        raise TransferError("manifest chunk totals are invalid")


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TransferError(f"{label} must be an object")
    return value


def _exact_fields(value: Mapping[str, Any], fields: set[str], label: str) -> None:
    _fields(value, fields, fields, label)


def _fields(
    value: Mapping[str, Any], required: set[str], allowed: set[str], label: str
) -> None:
    actual = set(value)
    missing = required - actual
    unexpected = actual - allowed
    if missing or unexpected:
        details = []
        if missing:
            details.append("missing=" + ",".join(sorted(missing)))
        if unexpected:
            details.append("unexpected=" + ",".join(sorted(unexpected)))
        raise TransferError(
            f"{label} fields do not match the transfer contract ({'; '.join(details)})"
        )


def _bounded_string(value: Mapping[str, Any], key: str, maximum: int) -> str:
    result = value.get(key)
    if (
        not isinstance(result, str)
        or not 1 <= len(result.encode("utf-8")) <= maximum
        or any(ord(character) < 0x20 for character in result)
    ):
        raise TransferError(f"{key} is invalid")
    return result


def _identifier(value: Mapping[str, Any], key: str) -> str:
    result = _bounded_string(value, key, 256)
    if any(character.isspace() for character in result):
        raise TransferError(f"{key} is invalid")
    return result


def _wire_integer(value: Mapping[str, Any], key: str) -> int:
    raw = value.get(key)
    if isinstance(raw, str):
        if (
            not raw.isascii()
            or not raw.isdecimal()
            or (len(raw) > 1 and raw.startswith("0"))
        ):
            raise TransferError(f"{key} is not a canonical wire integer")
        result = int(raw)
    else:
        result = raw
    if (
        isinstance(result, bool)
        or not isinstance(result, int)
        or not 0 <= result <= MAXIMUM_WIRE_INTEGER
    ):
        raise TransferError(f"{key} is not a canonical wire integer")
    return result


def _numeric_wire_integer(value: Mapping[str, Any], key: str) -> int:
    result = value.get(key)
    if (
        isinstance(result, bool)
        or not isinstance(result, int)
        or not 0 <= result <= MAXIMUM_WIRE_INTEGER
    ):
        raise TransferError(f"{key} is not a canonical wire integer")
    return result


def _positive_wire_integer(value: Mapping[str, Any], key: str) -> int:
    result = _wire_integer(value, key)
    if result == 0:
        raise TransferError(f"{key} must be positive")
    return result


def _positive_numeric_wire_integer(value: Mapping[str, Any], key: str) -> int:
    result = _numeric_wire_integer(value, key)
    if result == 0:
        raise TransferError(f"{key} must be positive")
    return result


def _base64url_string(
    value: Mapping[str, Any], key: str, *, expected_bytes: int | None = None
) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not is_base64url(result):
        raise TransferError(f"{key} is not canonical base64url")
    if expected_bytes is not None:
        try:
            decoded = base64.urlsafe_b64decode(result + "=" * (-len(result) % 4))
        except (ValueError, base64.binascii.Error):
            raise TransferError(f"{key} is not canonical base64url") from None
        if len(decoded) != expected_bytes or _encode_base64url(decoded) != result:
            raise TransferError(f"{key} has an invalid encoded length")
    return result


def _encode_base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


