from __future__ import annotations

import io
import os
import tempfile
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from typing import Any, BinaryIO, TypeAlias

import httpx

from ._api import AudaligoTransferAPI
from ._claim import redeem_file_key_claim
from ._crypto import (
    CHUNK_SIZE,
    MAXIMUM_CHUNKS,
    ChunkMetadata,
    EncryptionContractError,
    build_encryption_plan,
    parse_file_handoff_plan,
    parse_preview_decryption_plan,
)
from ._handoff import TransferHandoff, parse_handoff
from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferError,
    TransferHTTPError,
    TransferSizeMismatch,
    TransferTimeouts,
    TransferTransport,
    get_ciphertext,
    put_ciphertext,
)

PathSource: TypeAlias = str | os.PathLike[str]
UploadSource: TypeAlias = PathSource | BinaryIO
DownloadDestination: TypeAlias = PathSource | BinaryIO

_DOWNLOAD_SPOOL_MEMORY_LIMIT = 8 * 1024 * 1024
_DOWNLOAD_COPY_SIZE = 1024 * 1024


def upload_file(
    structured_content: Mapping[str, Any],
    *,
    source: UploadSource,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
    claim_transport: TransferTransport = DEFAULT_TRANSPORT,
    control_transport: httpx.BaseTransport | None = None,
) -> Mapping[str, Any]:
    """Consume an MCP upload handoff and transfer locally encrypted ciphertext."""
    handoff = _parse_handoff(structured_content)
    if handoff.operation != "upload" or handoff.upload is None:
        raise TransferError("structuredContent is not an upload handoff")
    upload = handoff.upload
    stream, close_stream, plaintext_size = _open_upload_source(source)
    try:
        if plaintext_size != upload.plaintext_size:
            raise TransferSizeMismatch("source size does not match the MCP handoff")
        if plaintext_size > CHUNK_SIZE * MAXIMUM_CHUNKS:
            raise TransferError("plaintext exceeds the managed transfer limit")
        key_claim = redeem_file_key_claim(
            handoff.key_claim,
            expected_direction="upload",
            expected_project_id=handoff.project_id,
            expected_object_id=handoff.object_id,
            expected_epoch=handoff.epoch,
            timeouts=timeouts,
            transport=claim_transport,
        )
        plan = build_encryption_plan(
            stream,
            project_id=handoff.project_id,
            file_id=upload.operation_id,
            object_id=handoff.object_id,
            epoch=handoff.epoch,
            data_key=key_claim.data_key,
            wrapped_nonce=key_claim.wrapped_nonce,
            wrapped_data_key=key_claim.wrapped_data_key,
            plaintext_size=plaintext_size,
        )
        with AudaligoTransferAPI(
            control_origin=handoff.control_origin,
            continuation=handoff.continuation,
            timeouts=timeouts,
            control_transport=control_transport,
        ) as api:
            manifest = api.put_manifest(
                project_id=handoff.project_id,
                upload_id=handoff.object_id,
                manifest=plan.manifest(),
            )
            if manifest.get("state") != "ready":
                for chunk in plan.chunks:
                    cleartext = _read_exact(stream, chunk.plaintext_size)
                    ciphertext = plan.seal_chunk(cleartext, chunk.index)
                    if sha256(ciphertext).digest() != chunk.ciphertext_sha256:
                        raise TransferSizeMismatch(
                            "source changed after the upload manifest was built"
                        )
                    capability = api.upload_capability(
                        project_id=handoff.project_id,
                        upload_id=handoff.object_id,
                        chunk_index=chunk.index,
                    )
                    url, headers = _validate_capability(
                        capability,
                        operation="PUT",
                        object_id=handoff.object_id,
                        chunk=chunk,
                    )
                    put_ciphertext(
                        url,
                        headers,
                        ciphertext,
                        timeouts=timeouts,
                        transport=transport,
                    )
                if stream.read(1):
                    raise TransferSizeMismatch(
                        "source changed after the upload manifest was built"
                    )
                api.complete_upload(
                    project_id=handoff.project_id,
                    upload_id=handoff.object_id,
                )
            return api.commit_file(
                project_id=handoff.project_id,
                file_id=upload.operation_id,
                upload_id=handoff.object_id,
                filename=upload.filename,
                plaintext_size=upload.plaintext_size,
                mix_version_id=upload.mix_version_id,
            )
    except EncryptionContractError as error:
        raise TransferError(str(error)) from None
    finally:
        if close_stream:
            stream.close()


def download_file(
    structured_content: Mapping[str, Any],
    *,
    destination: DownloadDestination,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
    claim_transport: TransferTransport = DEFAULT_TRANSPORT,
    control_transport: httpx.BaseTransport | None = None,
) -> int:
    """Consume an MCP file handoff and atomically write locally decrypted bytes."""
    handoff = _parse_handoff(structured_content)
    if handoff.operation != "file_download" or handoff.file is None:
        raise TransferError("structuredContent is not a file download handoff")
    key_claim = _redeem_download_claim(handoff, timeouts, claim_transport)
    try:
        plan = parse_file_handoff_plan(
            _required_manifest(handoff),
            project_id=handoff.project_id,
            object_id=handoff.object_id,
            epoch=handoff.epoch,
            data_key=key_claim.data_key,
            wrapped_nonce=key_claim.wrapped_nonce,
            wrapped_data_key=key_claim.wrapped_data_key,
        )
    except EncryptionContractError as error:
        raise TransferError(str(error)) from None
    if plan.file_id != handoff.file.file_id:
        raise TransferError("file manifest does not match the handoff")
    return _download(
        handoff,
        destination,
        plan,
        timeouts,
        transport,
        control_transport,
    )


def download_preview(
    structured_content: Mapping[str, Any],
    *,
    destination: DownloadDestination,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
    claim_transport: TransferTransport = DEFAULT_TRANSPORT,
    control_transport: httpx.BaseTransport | None = None,
) -> int:
    """Consume an MCP preview handoff and atomically write decrypted preview bytes."""
    handoff = _parse_handoff(structured_content)
    if handoff.operation != "preview_download" or handoff.preview is None:
        raise TransferError("structuredContent is not a preview download handoff")
    key_claim = _redeem_download_claim(handoff, timeouts, claim_transport)
    try:
        plan = parse_preview_decryption_plan(
            _required_manifest(handoff),
            project_id=handoff.project_id,
            preview_id=handoff.object_id,
            epoch=handoff.epoch,
            data_key=key_claim.data_key,
        )
    except EncryptionContractError as error:
        raise TransferError(str(error)) from None
    return _download(
        handoff,
        destination,
        plan,
        timeouts,
        transport,
        control_transport,
    )


def _redeem_download_claim(
    handoff: TransferHandoff,
    timeouts: TransferTimeouts,
    claim_transport: TransferTransport,
) -> Any:
    return redeem_file_key_claim(
        handoff.key_claim,
        expected_direction="download",
        expected_project_id=handoff.project_id,
        expected_object_id=handoff.object_id,
        expected_epoch=handoff.epoch,
        timeouts=timeouts,
        transport=claim_transport,
    )


def _parse_handoff(structured_content: Mapping[str, Any]) -> TransferHandoff:
    try:
        return parse_handoff(structured_content)
    except TransferError as error:
        if error.code != "transfer_failed":
            raise
        raise TransferError(
            str(error),
            code="handoff_invalid",
            recoverable=False,
        ) from None


def _required_manifest(handoff: TransferHandoff) -> Mapping[str, Any]:
    if handoff.manifest is None:
        raise TransferError("structuredContent omitted the download manifest")
    return handoff.manifest


def _download(
    handoff: TransferHandoff,
    destination: DownloadDestination,
    plan: Any,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
    control_transport: httpx.BaseTransport | None,
) -> int:
    with AudaligoTransferAPI(
        control_origin=handoff.control_origin,
        continuation=handoff.continuation,
        timeouts=timeouts,
        control_transport=control_transport,
    ) as api:
        if isinstance(destination, (str, os.PathLike)):
            return _download_to_path(
                api,
                handoff.project_id,
                Path(destination),
                plan,
                timeouts,
                transport,
            )
        _require_writer(destination)
        with tempfile.SpooledTemporaryFile(
            max_size=_DOWNLOAD_SPOOL_MEMORY_LIMIT,
            mode="w+b",
        ) as staged:
            count = _download_to_stream(
                api,
                handoff.project_id,
                staged,
                plan,
                timeouts,
                transport,
            )
            staged.seek(0)
            _commit_staged_stream(destination, staged, count)
            return count


def _download_to_path(
    api: AudaligoTransferAPI,
    project_id: str,
    destination: Path,
    plan: Any,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> int:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".part", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            count = _download_to_stream(
                api,
                project_id,
                stream,
                plan,
                timeouts,
                transport,
            )
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        return count
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def _download_to_stream(
    api: AudaligoTransferAPI,
    project_id: str,
    destination: BinaryIO,
    plan: Any,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> int:
    written = 0
    for chunk in plan.chunks:
        ciphertext = _download_ciphertext_chunk(
            api,
            project_id=project_id,
            object_id=plan.object_id,
            chunk=chunk,
            timeouts=timeouts,
            transport=transport,
        )
        try:
            cleartext = plan.open_chunk(ciphertext, chunk.index)
        except EncryptionContractError as error:
            raise TransferError(str(error)) from None
        _write_all(destination, cleartext)
        written += len(cleartext)
    if written != plan.plaintext_size:
        raise TransferSizeMismatch()
    return written


def _download_ciphertext_chunk(
    api: AudaligoTransferAPI,
    *,
    project_id: str,
    object_id: str,
    chunk: ChunkMetadata,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> bytes:
    for attempt in range(2):
        capability = api.read_capability(
            project_id=project_id,
            object_id=object_id,
            chunk_index=chunk.index,
        )
        url, headers = _validate_capability(
            capability, operation="GET", object_id=object_id, chunk=chunk
        )
        try:
            return get_ciphertext(
                url,
                headers,
                chunk.ciphertext_size,
                timeouts=timeouts,
                transport=transport,
            )
        except TransferHTTPError as error:
            # A GET has no caller-visible effect and is buffered before decryption. Only
            # rejected, expiring capabilities may be reacquired, and only once.
            if attempt == 0 and error.status in {401, 403}:
                continue
            raise
    raise TransferError("download capability reacquisition failed")


def _validate_capability(
    capability: Mapping[str, Any],
    *,
    operation: str,
    object_id: str,
    chunk: ChunkMetadata,
) -> tuple[str, dict[str, str]]:
    if (
        _string(capability, "operation") != operation
        or _string(capability, "objectId") != object_id
        or _integer_or_zero(capability, "chunkIndex") != chunk.index
        or _integer(capability, "contentLength") != chunk.ciphertext_size
    ):
        raise TransferError("Bucket capability does not match the requested chunk")
    url = _string(capability, "url")
    raw_headers = capability.get("headers", {})
    if not isinstance(raw_headers, Mapping):
        raise TransferError("Bucket capability headers are invalid")
    headers: dict[str, str] = {}
    for name, value in raw_headers.items():
        if not isinstance(name, str) or not isinstance(value, str):
            raise TransferError("Bucket capability headers are invalid")
        lowered = name.lower()
        if not lowered or lowered in headers:
            raise TransferError("Bucket capability headers are invalid")
        headers[lowered] = value
    return url, headers


def _open_upload_source(source: UploadSource) -> tuple[BinaryIO, bool, int]:
    if isinstance(source, (str, os.PathLike)):
        path = Path(source)
        size = path.stat().st_size
        stream = path.open("rb")
        return stream, True, size
    _require_reader(source)
    size = _remaining_stream_size(source)
    if size is None:
        raise TypeError("source binary stream must be seekable")
    return source, False, size


def _remaining_stream_size(stream: BinaryIO) -> int | None:
    try:
        start = stream.tell()
        end = stream.seek(0, io.SEEK_END)
        stream.seek(start)
    except (AttributeError, OSError, io.UnsupportedOperation):
        return None
    if (
        not isinstance(start, int)
        or not isinstance(end, int)
        or start < 0
        or end < start
    ):
        return None
    return end - start


def _require_reader(stream: BinaryIO) -> None:
    if not callable(getattr(stream, "read", None)):
        raise TypeError("source must be a path or readable binary stream")


def _require_writer(stream: BinaryIO) -> None:
    if not callable(getattr(stream, "write", None)):
        raise TypeError("destination must be a path or writable binary stream")


def _read_exact(stream: BinaryIO, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length
    while remaining:
        value = stream.read(remaining)
        if not isinstance(value, bytes) or not value:
            raise TransferSizeMismatch()
        if len(value) > remaining:
            raise TransferSizeMismatch()
        chunks.append(value)
        remaining -= len(value)
    return b"".join(chunks)


def _write_all(destination: BinaryIO, data: bytes) -> None:
    view = memoryview(data)
    written = 0
    while written < len(view):
        count = destination.write(view[written:])
        if not isinstance(count, int) or count <= 0:
            raise TransferError("destination rejected plaintext")
        written += count


def _commit_staged_stream(
    destination: BinaryIO,
    staged: BinaryIO,
    expected_size: int,
) -> None:
    rollback = _append_rollback_position(destination)
    copied = 0
    try:
        while copied < expected_size:
            data = staged.read(min(_DOWNLOAD_COPY_SIZE, expected_size - copied))
            if not isinstance(data, bytes) or not data:
                raise TransferSizeMismatch(
                    "staged plaintext size does not match manifest"
                )
            _write_all(destination, data)
            copied += len(data)
        if staged.read(1):
            raise TransferSizeMismatch("staged plaintext size does not match manifest")
    except BaseException:
        _rollback_stream(destination, rollback)
        raise


def _append_rollback_position(destination: BinaryIO) -> int | None:
    try:
        position = destination.tell()
        if not isinstance(position, int) or position < 0:
            return None
        return position
    except (AttributeError, OSError, io.UnsupportedOperation):
        return None


def _rollback_stream(destination: BinaryIO, position: int | None) -> None:
    if position is None:
        return
    try:
        destination.seek(position)
        destination.truncate(position)
    except (AttributeError, OSError, io.UnsupportedOperation):
        pass


def _string(value: Mapping[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise TransferError(f"{key} must be a nonempty string")
    return result


def _integer(value: Mapping[str, Any], key: str) -> int:
    raw = value.get(key)
    if isinstance(raw, bool):
        raise TransferError(f"{key} must be an integer")
    if isinstance(raw, int):
        result = raw
    elif (
        isinstance(raw, str)
        and raw.isdecimal()
        and (len(raw) == 1 or not raw.startswith("0"))
    ):
        result = int(raw)
    else:
        raise TransferError(f"{key} must be an integer")
    if not 0 <= result <= 9_007_199_254_740_991:
        raise TransferError("capability integer exceeds the wire limit")
    return result


def _integer_or_zero(value: Mapping[str, Any], key: str) -> int:
    return 0 if key not in value else _integer(value, key)
