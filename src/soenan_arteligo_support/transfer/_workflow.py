from __future__ import annotations

import io
import os
import tempfile
import time
from base64 import urlsafe_b64encode
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from typing import Any, BinaryIO, TypeAlias

import httpx

from ._api import ArteligoTransferAPI
from ._claim import redeem_file_key_claim
from ._crypto import (
    CHUNK_SIZE,
    MAXIMUM_CHUNKS,
    ChunkMetadata,
    EncryptionContractError,
    _base64url_bytes,
    build_encryption_plan,
    build_preview_encryption_plan,
    parse_file_handoff_plan,
    parse_preview_decryption_plan,
)
from ._handoff import TransferHandoff, _claim_descriptor, _identifier, parse_handoff
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
from ._opus import OpusPreview, preflight_wav_preview, prepare_opus_preview

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
        if upload.preview_profile == "opus-webm-v1":
            preflight_wav_preview(stream, plaintext_size)
        return _upload_prepared_file(
            handoff, stream, plaintext_size, timeouts,
            transport, claim_transport, control_transport,
        )
    except EncryptionContractError as error:
        raise TransferError(str(error)) from None
    finally:
        if close_stream:
            stream.close()


def _upload_prepared_file(
    handoff: TransferHandoff,
    stream: BinaryIO,
    plaintext_size: int,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
    claim_transport: TransferTransport,
    control_transport: httpx.BaseTransport | None,
) -> Mapping[str, Any]:
    upload = handoff.upload
    if upload is None:
        raise TransferError("upload metadata is missing")
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
        capture_source_sha256=upload.preview_profile == "opus-webm-v1",
    )
    source_start = stream.tell()
    with ArteligoTransferAPI(
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
                    raise TransferSizeMismatch("source changed after the upload manifest was built")
                capability = api.upload_capability(
                    project_id=handoff.project_id,
                    upload_id=handoff.object_id,
                    chunk_index=chunk.index,
                )
                url, headers = _validate_capability(
                    capability, operation="PUT", object_id=handoff.object_id, chunk=chunk,
                )
                put_ciphertext(
                    url, headers, ciphertext, timeouts=timeouts, transport=transport,
                )
            if stream.read(1):
                raise TransferSizeMismatch("source changed after the upload manifest was built")
            api.complete_upload(
                project_id=handoff.project_id,
                upload_id=handoff.object_id,
            )
        result = api.commit_file(
            project_id=handoff.project_id,
            file_id=upload.operation_id,
            upload_id=handoff.object_id,
            filename=upload.filename,
            plaintext_size=upload.plaintext_size,
        )
        if upload.preview_profile == "opus-webm-v1":
            stream.seek(source_start)
            try:
                _upload_preview(
                    api, handoff, stream, plaintext_size, plan.source_sha256,
                    timeouts, transport, claim_transport,
                )
            except (TransferError, EncryptionContractError) as error:
                raise TransferError(
                    "source committed; preview pending; retry the same MCP begin operation ID",
                    code="preview_pending",
                    recoverable=isinstance(error, TransferError) and error.recoverable,
                ) from None
        return result


def _upload_preview(
    api: ArteligoTransferAPI,
    handoff: TransferHandoff,
    source: BinaryIO,
    source_size: int,
    source_sha256: bytes | None,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
    claim_transport: TransferTransport,
) -> None:
    upload = handoff.upload
    if upload is None or upload.preview_id is None or source_sha256 is None:
        raise TransferError("preview upload binding is missing")
    session = api.begin_preview_upload(
        project_id=handoff.project_id, file_id=upload.operation_id,
    )
    _validate_preview_session(session, handoff)
    if (
        session["previewId"] != upload.preview_id
        or session["processingId"] != upload.processing_id
        or session["jobId"] != upload.job_id
    ):
        raise TransferError(
            "preview upload handoff is stale; repeat the same MCP begin operation ID",
            code="preview_handoff_stale",
            recoverable=True,
        )
    if session["state"] == "ready":
        return
    # An earlier invocation may have encoded different WebM bytes. Fence its
    # DEK and nonce before launching a new encoder, even if its manifest was empty.
    old_preview_id = _identifier(session, "previewId")
    old_nonce = _base64url_bytes(session, "nonceBaseB64u", 8)
    session = api.reset_preview_upload(
        project_id=handoff.project_id,
        file_id=upload.operation_id,
        expected_preview_id=old_preview_id,
    )
    _validate_preview_session(session, handoff)
    if (
        session["state"] != "reserved"
        or _identifier(session, "previewId") == old_preview_id
        or _base64url_bytes(session, "nonceBaseB64u", 8) == old_nonce
    ):
        raise TransferError("preview reset did not issue fresh encryption material")
    with prepare_opus_preview(source, source_size=source_size, timeout=timeouts.total) as preview:
        if preview.source_sha256 != source_sha256:
            raise TransferSizeMismatch("WAV source changed after source upload")
        # Encoding can outlive a key claim. Reissue it under this same fenced
        # preview identity; do not reset or encrypt until the binding is checked.
        refreshed = api.begin_preview_upload(
            project_id=handoff.project_id, file_id=upload.operation_id,
        )
        _validate_preview_session(refreshed, handoff)
        if (
            refreshed["previewId"] != session["previewId"]
            or refreshed["nonceBaseB64u"] != session["nonceBaseB64u"]
            or refreshed["processingId"] != session["processingId"]
            or refreshed["jobId"] != session["jobId"]
        ):
            raise TransferError("preview identity changed during local encoding")
        if refreshed["state"] == "ready":
            return
        _publish_preview(
            api, handoff, refreshed, preview, timeouts, transport, claim_transport,
        )


def _validate_preview_session(
    session: Mapping[str, Any], handoff: TransferHandoff,
) -> None:
    required = {
        "previewId", "sourceObjectId", "processingId", "jobId",
        "epoch", "nonceBaseB64u", "state",
    }
    if not required.issubset(session) or set(session) - required - {"keyClaim"}:
        raise TransferError("delegated preview upload session is invalid")
    if (
        _identifier(session, "sourceObjectId") != handoff.object_id
        or _integer(session, "epoch") != handoff.epoch
        or session["state"] not in {"reserved", "waiting", "ready"}
    ):
        raise TransferError("preview upload session does not match the source")
    for key in ("previewId", "processingId", "jobId"):
        _identifier(session, key)
    _base64url_bytes(session, "nonceBaseB64u", 8)


def _publish_preview(
    api: ArteligoTransferAPI,
    handoff: TransferHandoff,
    session: Mapping[str, Any],
    preview: OpusPreview,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
    claim_transport: TransferTransport,
) -> None:
    upload = handoff.upload
    if upload is None:
        raise TransferError("upload metadata is missing")
    preview_id = _identifier(session, "previewId")
    processing_id = _identifier(session, "processingId")
    job_id = _identifier(session, "jobId")
    nonce_base = _base64url_bytes(session, "nonceBaseB64u", 8)
    if "keyClaim" not in session:
        raise TransferError("preview upload key claim is missing")
    claim = _claim_descriptor(
        session["keyClaim"],
        expected_origin=handoff.control_origin,
        now_unix_milliseconds=int(time.time() * 1000),
    )
    preview_key = redeem_file_key_claim(
        claim,
        expected_direction="upload",
        expected_project_id=handoff.project_id,
        expected_object_id=preview_id,
        expected_epoch=handoff.epoch,
        timeouts=timeouts,
        transport=claim_transport,
    )
    loudness = _preview_loudness(preview)
    with preview.path.open("rb") as encoded:
        plan = build_preview_encryption_plan(
            encoded,
            project_id=handoff.project_id,
            source_object_id=handoff.object_id,
            processing_id=processing_id,
            preview_id=preview_id,
            job_id=job_id,
            epoch=handoff.epoch,
            data_key=preview_key.data_key,
            nonce_base=nonce_base,
            plaintext_size=preview.size,
        )
        manifest = {
            "sourceObjectId": handoff.object_id,
            "previewId": preview_id,
            "processingId": processing_id,
            "jobId": job_id,
            "epoch": handoff.epoch,
            "nonceBaseB64u": urlsafe_b64encode(nonce_base).decode("ascii").rstrip("="),
            "plaintextSize": preview.size,
            "ciphertextSize": sum(chunk.ciphertext_size for chunk in plan.chunks),
            "chunkSize": CHUNK_SIZE,
            "chunks": [
                {
                    "chunkIndex": chunk.index,
                    "plaintextOffset": chunk.plaintext_offset,
                    "plaintextSize": chunk.plaintext_size,
                    "ciphertextOffset": chunk.ciphertext_offset,
                    "ciphertextSize": chunk.ciphertext_size,
                    "ciphertextSha256B64u": urlsafe_b64encode(
                        chunk.ciphertext_sha256
                    ).decode("ascii").rstrip("="),
                    "finalChunk": chunk.final,
                }
                for chunk in plan.chunks
            ],
            "media": {
                "durationSeconds": preview.duration_seconds,
                "mimeType": "audio/webm",
                "codecs": "opus",
                "sampleRate": 48000,
                "channels": preview.channels,
                "bitrate": preview.bitrate,
                "playbackLoudness": loudness,
            },
        }
        state = api.put_preview_manifest(
            project_id=handoff.project_id,
            file_id=upload.operation_id,
            manifest=manifest,
        )
        if state.get("objectId") != preview_id:
            raise TransferError("preview manifest response does not match the source")
        if state.get("state") == "ready":
            return
        for chunk in plan.chunks:
            cleartext = _read_exact(encoded, chunk.plaintext_size)
            ciphertext = plan.seal_chunk(cleartext, chunk.index)
            if sha256(ciphertext).digest() != chunk.ciphertext_sha256:
                raise TransferSizeMismatch("encoded preview changed after manifest creation")
            capability = api.preview_upload_capability(
                project_id=handoff.project_id,
                file_id=upload.operation_id,
                chunk_index=chunk.index,
            )
            url, headers = _validate_capability(
                capability,
                operation="PUT",
                object_id=preview_id,
                chunk=chunk,
            )
            put_ciphertext(
                url, headers, ciphertext, timeouts=timeouts, transport=transport,
            )
        if encoded.read(1):
            raise TransferSizeMismatch("encoded preview changed after manifest creation")
        completed = api.complete_preview_upload(
            project_id=handoff.project_id, file_id=upload.operation_id,
        )
        if completed.get("objectId") != preview_id or completed.get("state") != "ready":
            raise TransferError("preview completion was not confirmed")


def _preview_loudness(preview: OpusPreview) -> dict[str, object]:
    integrated = preview.integrated_lufs_x100
    peak = preview.true_peak_dbtp_x100
    loudness_range = preview.loudness_range_lu_x100
    if integrated is None or peak is None or loudness_range is None:
        return {"kind": "unmeasurable"}
    if not (
        -9900 <= integrated <= 9900
        and -9900 <= peak <= 9900
        and 0 <= loudness_range <= 9900
    ):
        raise TransferError("encoded preview loudness exceeds supported range")
    return {
        "kind": "measured",
        "integratedLufsX100": integrated,
        "truePeakDbtpX100": peak,
        "loudnessRangeLuX100": loudness_range,
    }


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
    with ArteligoTransferAPI(
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
    api: ArteligoTransferAPI,
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
    api: ArteligoTransferAPI,
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
    api: ArteligoTransferAPI,
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
