from __future__ import annotations

import secrets
import uuid
from hashlib import sha256
from pathlib import Path
from typing import Any

from ..e2ee._crypto import E2eeError, decode, encode, wipe
from ..e2ee._records import EncryptedRecords
from ..e2ee._session import DeviceSession
from ._crypto import (
    CHUNK_SIZE,
    EncryptionPlan,
    build_preview_encryption_plan,
    parse_decryption_plan,
)
from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferTimeouts,
    TransferTransport,
    put_ciphertext,
)
from ._opus import prepare_opus_preview
from ._workflow import _capability, _epoch, _object, key_aad


def upload_wav_preview(
    session: DeviceSession,
    *,
    project_id: str,
    file_id: str,
    source: str | Path,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> dict[str, str]:
    """Encode the authenticated source locally and publish an encrypted Opus preview."""
    session.require_approved()
    records = EncryptedRecords(session)
    record = EncryptedRecords(session).read(project_id, [file_id]).get(file_id)
    if record is None or record["deleted"] or record["kind"] != "file":
        raise E2eeError("not_found")
    value = record["value"]
    pending = value.get("preview")
    source_manifest = value["source"]
    source_object = source_manifest["object"]
    wrapped_source = source_manifest["encryption"]["wrapped_data_key"]
    source_key = session.scope_key(project_id, source_object["epoch"])
    source_dek = bytearray()
    project_key = bytearray()
    data_key = bytearray()
    try:
        source_dek = session.crypto.open(
            source_key,
            {
                "nonce": wrapped_source["nonceB64u"],
                "ciphertext": wrapped_source["ciphertextB64u"],
            },
            key_aad(project_id, source_object["epoch"], source_object["object_id"]),
        )
        parsed = parse_decryption_plan(
            source_manifest,
            data_key=source_dek,
            wrapped_nonce=bytes(decode(wrapped_source["nonceB64u"])),
            wrapped_data_key=bytes(decode(wrapped_source["ciphertextB64u"])),
        )
        authenticated = EncryptionPlan(
            parsed.project_id,
            parsed.file_id,
            parsed.object_id,
            parsed.epoch,
            parsed.plaintext_size,
            parsed.chunk_count,
            parsed.nonce_base,
            source_dek,
            bytes(decode(wrapped_source["nonceB64u"])),
            bytes(decode(wrapped_source["ciphertextB64u"])),
            parsed.chunks,
        )
        with Path(source).open("rb") as stream:
            digest = sha256()
            for chunk in authenticated.chunks:
                clear = bytearray(stream.read(chunk.plaintext_size))
                try:
                    digest.update(clear)
                    if (
                        sha256(authenticated.seal_chunk(clear, chunk.index)).digest()
                        != chunk.ciphertext_sha256
                    ):
                        raise E2eeError("source_changed")
                finally:
                    wipe(clear)
            if stream.read(1):
                raise E2eeError("source_changed")
            stream.seek(0)
            if pending is not None:
                if pending.get("sourceObjectId") != source_object["object_id"]:
                    raise E2eeError("source_changed")
                if pending.get("state") == "ready":
                    return {
                        "file_id": file_id,
                        "preview_id": pending["previewId"],
                        "state": "ready",
                    }
                if pending.get("state") not in {"reserved", "waiting"}:
                    raise E2eeError("invalid_preview_state")
                epoch = pending["epoch"]
                identifier = pending["previewId"]
                nonce_base = bytes(decode(pending["nonceBaseB64u"]))
                project_key = session.scope_key(project_id, epoch)
                wrapped = {
                    "nonce": pending["wrappedDataKey"]["nonceB64u"],
                    "ciphertext": pending["wrappedDataKey"]["ciphertextB64u"],
                }
                data_key = session.crypto.open(
                    project_key, wrapped, key_aad(project_id, epoch, identifier, 2)
                )
                if pending["state"] == "waiting":
                    try:
                        descriptor = session.api.call(
                            "e2eeGetObject", scope_id=project_id, object_id=identifier
                        )
                    except E2eeError as error:
                        if error.code != "not_found":
                            raise
                    else:
                        if descriptor.get("state") == "ready":
                            return _publish_preview(
                                session, project_id, file_id, pending
                            )
            else:
                epoch = _epoch(session, project_id)
                project_key = session.scope_key(project_id, epoch)
                data_key = session.crypto.key()
                identifier = str(uuid.uuid4())
                nonce_base = secrets.token_bytes(8)
                wrapped = session.crypto.seal(
                    project_key, data_key, key_aad(project_id, epoch, identifier, 2)
                )
            with prepare_opus_preview(
                stream, source_size=parsed.plaintext_size, timeout=timeouts.total
            ) as encoded:
                if encoded.source_sha256 != digest.digest():
                    raise E2eeError("source_changed")
                with encoded.path.open("rb") as preview_stream:
                    plan = build_preview_encryption_plan(
                        preview_stream,
                        project_id=project_id,
                        source_object_id=source_object["object_id"],
                        processing_id=identifier,
                        preview_id=identifier,
                        job_id=identifier,
                        epoch=epoch,
                        data_key=data_key,
                        nonce_base=nonce_base,
                        plaintext_size=encoded.size,
                    )
                    loudness = (
                        {"kind": "unmeasurable"}
                        if encoded.integrated_lufs_x100 is None
                        else {
                            "kind": "measured",
                            "integratedLufsX100": encoded.integrated_lufs_x100,
                            "truePeakDbtpX100": encoded.true_peak_dbtp_x100,
                            "loudnessRangeLuX100": encoded.loudness_range_lu_x100,
                        }
                    )
                    media = {
                        "durationSeconds": encoded.duration_seconds,
                        "mimeType": "audio/webm",
                        "codecs": "opus",
                        "sampleRate": 48000,
                        "channels": encoded.channels,
                        "bitrate": encoded.bitrate,
                        "playbackLoudness": loudness,
                    }
                    manifest = {
                        "sourceObjectId": source_object["object_id"],
                        "previewId": identifier,
                        "processingId": identifier,
                        "jobId": identifier,
                        "epoch": epoch,
                        "nonceBaseB64u": encode(nonce_base),
                        "plaintextSize": encoded.size,
                        "ciphertextSize": sum(c.ciphertext_size for c in plan.chunks),
                        "chunkSize": CHUNK_SIZE,
                        "media": media,
                        "chunks": [
                            {
                                "chunkIndex": c.index,
                                "plaintextOffset": c.plaintext_offset,
                                "plaintextSize": c.plaintext_size,
                                "ciphertextOffset": c.ciphertext_offset,
                                "ciphertextSize": c.ciphertext_size,
                                "ciphertextSha256B64u": encode(c.ciphertext_sha256),
                                "finalChunk": c.final,
                            }
                            for c in plan.chunks
                        ],
                    }
                    preview = {
                        "previewId": identifier,
                        "sourceObjectId": source_object["object_id"],
                        "processingId": identifier,
                        "jobId": identifier,
                        "epoch": epoch,
                        "nonceBaseB64u": encode(nonce_base),
                        "wrappedDataKey": {
                            "nonceB64u": wrapped["nonce"],
                            "ciphertextB64u": wrapped["ciphertext"],
                        },
                        "manifest": manifest,
                        "media": {
                            **media,
                            "width": None,
                            "height": None,
                            "frameRate": None,
                            "hasAudio": True,
                            "initSegment": None,
                            "playbackLoudness": _playback_loudness(loudness),
                        },
                        "state": "waiting",
                    }
                    if pending is not None and pending["state"] == "waiting":
                        if pending["manifest"] != manifest:
                            raise E2eeError("preview_encoding_changed")
                        preview = pending
                    else:
                        records.write(
                            project_id,
                            key_epoch=_epoch(session, project_id),
                            records=[
                                {
                                    "record_id": file_id,
                                    "kind": "file",
                                    "expected_revision": record["revision"],
                                    "value": {**value, "preview": preview},
                                }
                            ],
                        )
                    descriptor = session.command(
                        "e2eeBeginObject",
                        "object_begin",
                        {
                            "scope_id": project_id,
                            "object_id": identifier,
                            "key_epoch": epoch,
                            "ciphertext_size": manifest["ciphertextSize"],
                            "chunks": [
                                {
                                    "index": c.index,
                                    "ciphertext_size": c.ciphertext_size,
                                    "checksum_sha256": encode(c.ciphertext_sha256),
                                }
                                for c in plan.chunks
                            ],
                        },
                        scope_id=project_id,
                    )
                    state = descriptor.get("state")
                    if state not in {"uploading", "ready"}:
                        raise E2eeError("object_not_ready")
                    for chunk in plan.chunks:
                        clear = bytearray(preview_stream.read(chunk.plaintext_size))
                        try:
                            ciphertext = plan.seal_chunk(clear, chunk.index)
                            if sha256(ciphertext).digest() != chunk.ciphertext_sha256:
                                raise E2eeError("preview_encoding_changed")
                            if state == "ready":
                                continue
                            url, headers = _capability(
                                _object(
                                    session, project_id, identifier, "put", chunk.index
                                ),
                                "PUT",
                                len(ciphertext),
                            )
                            put_ciphertext(
                                url,
                                headers,
                                ciphertext,
                                timeouts=timeouts,
                                transport=transport,
                            )
                        finally:
                            wipe(clear)
                    if state == "uploading":
                        _object(session, project_id, identifier, "finalize")
                return _publish_preview(session, project_id, file_id, preview)
    finally:
        for key in (source_key, source_dek, project_key, data_key):
            wipe(key)


def _publish_preview(
    session: DeviceSession, project_id: str, file_id: str, preview: dict[str, Any]
) -> dict[str, str]:
    current = EncryptedRecords(session).read(project_id, [file_id]).get(file_id)
    if (
        current is None
        or current["deleted"]
        or current["value"]["file"]["encryptedObjectId"] != preview["sourceObjectId"]
    ):
        raise E2eeError("source_changed")
    saved = current["value"].get("preview", {})
    if any(
        saved.get(field) != preview.get(field)
        for field in (
            "previewId",
            "sourceObjectId",
            "epoch",
            "nonceBaseB64u",
            "wrappedDataKey",
            "manifest",
        )
    ):
        raise E2eeError("revision_conflict")
    if saved.get("state") != "ready":
        EncryptedRecords(session).write(
            project_id,
            key_epoch=_epoch(session, project_id),
            records=[
                {
                    "record_id": file_id,
                    "kind": "file",
                    "expected_revision": current["revision"],
                    "value": {
                        **current["value"],
                        "preview": {**saved, "state": "ready"},
                    },
                }
            ],
        )
    return {"file_id": file_id, "preview_id": preview["previewId"], "state": "ready"}


def _playback_loudness(measurement: dict[str, Any]) -> dict[str, Any]:
    policy = {
        "policyVersion": "ebu-r128-playback-v1",
        "targetIntegratedLoudnessLufs": -16.0,
        "maximumTruePeakDbtp": -1.5,
        "maximumBoostDb": 6.0,
    }
    if measurement["kind"] != "measured":
        return {**policy, "kind": "unmeasurable", "recommendedGainDb": 0.0}
    integrated = measurement["integratedLufsX100"] / 100
    peak = measurement["truePeakDbtpX100"] / 100
    return {
        **policy,
        "kind": "measured",
        "integratedLoudnessLufs": integrated,
        "truePeakDbtp": peak,
        "loudnessRangeLu": measurement["loudnessRangeLuX100"] / 100,
        "recommendedGainDb": min(-16 - integrated, -1.5 - peak, 6.0),
    }
