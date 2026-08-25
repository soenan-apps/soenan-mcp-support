from __future__ import annotations

import io
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any, BinaryIO, TypeAlias

from ._api import AudaligoTransferAPI
from ._claim import redeem_file_key_claim
from ._crypto import (
    ChunkMetadata,
    EncryptionContractError,
    build_encryption_plan,
    parse_decryption_plan,
)
from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferError,
    TransferSizeMismatch,
    TransferTimeouts,
    TransferTransport,
    get_ciphertext,
    put_ciphertext,
)

PathSource: TypeAlias = str | os.PathLike[str]
UploadSource: TypeAlias = PathSource | BinaryIO
DownloadDestination: TypeAlias = PathSource | BinaryIO


def upload_file(
    api: AudaligoTransferAPI,
    *,
    project_id: str,
    filename: str,
    source: UploadSource,
    operation_id: str,
    mix_version_id: str | None = None,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
    claim_transport: TransferTransport = DEFAULT_TRANSPORT,
) -> Mapping[str, Any]:
    """Encrypt locally and upload ciphertext directly to Railway Bucket capabilities."""
    stream, close_stream, plaintext_size = _open_upload_source(source)
    try:
        begin = api.begin_upload(
            project_id=project_id,
            filename=filename,
            plaintext_size=plaintext_size,
            operation_id=operation_id,
            mix_version_id=mix_version_id,
        )
        upload_id = _string(begin, "uploadId")
        epoch = _integer_or_zero(begin, "keyEpoch")
        key_claim = redeem_file_key_claim(
            _mapping(begin, "keyClaim"),
            expected_direction="upload",
            expected_project_id=project_id,
            expected_object_id=upload_id,
            expected_epoch=epoch,
            timeouts=timeouts,
            transport=claim_transport,
        )
        plan = build_encryption_plan(
            stream,
            project_id=project_id,
            file_id=operation_id,
            object_id=upload_id,
            epoch=epoch,
            data_key=key_claim.data_key,
            wrapped_nonce=key_claim.wrapped_nonce,
            wrapped_data_key=key_claim.wrapped_data_key,
            plaintext_size=plaintext_size,
        )
        api.put_manifest(
            project_id=project_id,
            upload_id=upload_id,
            manifest=plan.manifest(),
        )

        for chunk in plan.chunks:
            cleartext = _read_exact(stream, chunk.plaintext_size)
            ciphertext = plan.seal_chunk(cleartext, chunk.index)
            capability = api.upload_capability(
                project_id=project_id,
                upload_id=upload_id,
                chunk_index=chunk.index,
            )
            url, headers = _validate_capability(
                capability, operation="PUT", object_id=upload_id, chunk=chunk
            )
            put_ciphertext(
                url, headers, ciphertext, timeouts=timeouts, transport=transport
            )
        if stream.read(1):
            raise TransferSizeMismatch()

        api.complete_upload(project_id=project_id, upload_id=upload_id)
        return api.commit_file(
            project_id=project_id,
            file_id=operation_id,
            upload_id=upload_id,
            filename=filename,
            plaintext_size=plaintext_size,
            mix_version_id=mix_version_id,
        )
    except EncryptionContractError as error:
        raise TransferError(str(error)) from None
    finally:
        if close_stream:
            stream.close()


def download_file(
    api: AudaligoTransferAPI,
    *,
    project_id: str,
    file_id: str,
    destination: DownloadDestination,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
    claim_transport: TransferTransport = DEFAULT_TRANSPORT,
) -> int:
    """Download ciphertext directly from Railway Bucket and decrypt locally."""
    begin = api.read_descriptor(project_id=project_id, file_id=file_id)
    file_value = _mapping(begin, "file")
    manifest = _mapping(begin, "manifest")
    manifest_object = _mapping(manifest, "object")
    object_id = _string(manifest_object, "object_id")
    epoch = _integer(manifest_object, "epoch")
    if (
        _string(file_value, "projectId") != project_id
        or _string(file_value, "fileId") != file_id
        or _string(file_value, "encryptedObjectId") != object_id
    ):
        raise TransferError("download metadata does not match the requested file")
    key_claim = redeem_file_key_claim(
        _mapping(begin, "keyClaim"),
        expected_direction="download",
        expected_project_id=project_id,
        expected_object_id=object_id,
        expected_epoch=epoch,
        timeouts=timeouts,
        transport=claim_transport,
    )
    try:
        plan = parse_decryption_plan(
            manifest,
            data_key=key_claim.data_key,
            wrapped_nonce=key_claim.wrapped_nonce,
            wrapped_data_key=key_claim.wrapped_data_key,
        )
    except EncryptionContractError as error:
        raise TransferError(str(error)) from None
    if plan.project_id != project_id or plan.file_id != file_id:
        raise TransferError("download manifest does not match the requested file")

    if isinstance(destination, (str, os.PathLike)):
        return _download_to_path(
            api, project_id, file_id, Path(destination), plan, timeouts, transport
        )
    _require_writer(destination)
    rollback = _append_rollback_position(destination)
    try:
        return _download_to_stream(
            api, project_id, file_id, destination, plan, timeouts, transport
        )
    except BaseException:
        _rollback_stream(destination, rollback)
        raise


def _download_to_path(
    api: AudaligoTransferAPI,
    project_id: str,
    file_id: str,
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
                api, project_id, file_id, stream, plan, timeouts, transport
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
    file_id: str,
    destination: BinaryIO,
    plan: Any,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> int:
    written = 0
    for chunk in plan.chunks:
        capability = api.read_capability(
            project_id=project_id,
            object_id=plan.object_id,
            chunk_index=chunk.index,
        )
        url, headers = _validate_capability(
            capability, operation="GET", object_id=plan.object_id, chunk=chunk
        )
        ciphertext = get_ciphertext(
            url,
            headers,
            chunk.ciphertext_size,
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


def _mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise TransferError(f"{key} must be an object")
    return result


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
    elif isinstance(raw, str) and raw.isdecimal():
        result = int(raw)
    else:
        raise TransferError(f"{key} must be an integer")
    if result < 0:
        raise TransferError(f"{key} must be nonnegative")
    return result


def _integer_or_zero(value: Mapping[str, Any], key: str) -> int:
    return 0 if key not in value else _integer(value, key)
