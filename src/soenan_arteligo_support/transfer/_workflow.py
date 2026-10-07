from __future__ import annotations

import mimetypes
import os
import secrets
import struct
import tempfile
import time
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from ..e2ee._crypto import E2eeError, decode, encode, wipe
from ..e2ee._directory import EncryptedDirectory
from ..e2ee._records import EncryptedRecords
from ..e2ee._session import DeviceSession
from ._crypto import EncryptionPlan, build_encryption_plan, parse_decryption_plan
from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferTimeouts,
    TransferTransport,
    get_ciphertext,
    put_ciphertext,
)


def key_aad(project: str, epoch: int, object_id: str, purpose: int = 1) -> bytes:
    result = bytearray(b"audaligo-project-key-v1\0") + bytes([purpose])
    for field in (project, str(epoch), object_id):
        try:
            value = field.encode("ascii")
        except UnicodeEncodeError:
            raise E2eeError("invalid_object_context") from None
        if not 1 <= len(value) <= 256:
            raise E2eeError("invalid_object_context")
        result.extend(struct.pack(">I", len(value)))
        result.extend(value)
    return bytes(result)


def _epoch(session: DeviceSession, scope: str) -> int:
    return session.scope_metadata(scope, refresh=True)["key_epoch"]


def _file_metadata_for_write(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.pop("directoryEntry", None)
    return result


def _completed_file_metadata(pending: dict[str, Any], file: dict[str, Any]) -> dict[str, Any]:
    value = _file_metadata_for_write(pending)
    for key in ("uploadId", "keyEpoch", "sourceState", "entryIntent", "filename", "mimeType",
                "originalFilename", "originalPlaintextSize", "fileKind"):
        value.pop(key, None)
    return {**value, "file": file}


def _completed_upload(
    records: EncryptedRecords, scope: str, pending: dict[str, Any], upload_id: str
) -> dict[str, Any]:
    identifier = pending["value"].get("file_id")
    if not isinstance(identifier, str):
        raise E2eeError("upload_not_found")
    record = records.read(scope, [identifier]).get(identifier)
    if (record is None or record["deleted"] or
            record["value"].get("file", {}).get("encryptedObjectId") != upload_id):
        raise E2eeError("upload_not_found")
    return record


def _object(
    session: DeviceSession,
    scope: str,
    identifier: str,
    action: str,
    index: int | None = None,
) -> dict[str, Any]:
    operations = {
        "put": ("e2eePutObjectCapability", "object_put"),
        "finalize": ("e2eeFinalizeObject", "object_finalize"),
        "delete": ("e2eeDeleteObject", "object_delete"),
    }
    body: dict[str, Any] = {"scope_id": scope, "object_id": identifier}
    if index is not None:
        body["index"] = index
    api_operation, operation = operations[action]
    return session.command(
        api_operation, operation, body, scope_id=scope, object_id=identifier
    )


def _capability(
    value: dict[str, Any], method: str, length: int
) -> tuple[str, dict[str, str]]:
    if (
        value.get("method") != method
        or not isinstance(value.get("expires_at"), int)
        or value["expires_at"] <= time.time()
        or value.get("content_length", length) not in {None, length}
        or not isinstance(value.get("url"), str)
        or not isinstance(value.get("headers"), dict)
    ):
        raise E2eeError("invalid_capability")
    return value["url"], value["headers"]


def upload_file(
    session: DeviceSession,
    *,
    project_id: str,
    source: str | Path,
    parent_folder_id: str | None = None,
    upload_id: str | None = None,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> dict[str, Any]:
    session.require_approved()
    source = Path(source)
    records = EncryptedRecords(session)
    epoch = _epoch(session, project_id)
    identifier = upload_id or str(uuid.uuid4())
    pending_id = "upl_" + identifier
    current = records.read(project_id, [pending_id])
    pending = current.get(pending_id)
    completed = None
    if pending is not None and pending["deleted"]:
        completed = _completed_upload(records, project_id, pending, identifier)
    data_key = bytearray()
    project_key = session.scope_key(project_id, epoch)
    try:
        with source.open("rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            if not 0 < size <= 8 * 1024**3 - 1024 * 16:
                raise E2eeError("file_size_limit")
            if pending is None:
                if upload_id is not None:
                    raise E2eeError("upload_not_found")
                file_id = "fil_" + secrets.token_hex(16)
                data_key = session.crypto.key()
                wrapped = session.crypto.seal(
                    project_key, data_key, key_aad(project_id, epoch, identifier)
                )
                plan = build_encryption_plan(
                    stream,
                    project_id=project_id,
                    file_id=file_id,
                    object_id=identifier,
                    epoch=epoch,
                    data_key=data_key,
                    wrapped_nonce=bytes(decode(wrapped["nonce"])),
                    wrapped_data_key=bytes(decode(wrapped["ciphertext"])),
                    plaintext_size=size,
                )
                private = {
                    "uploadId": identifier,
                    "keyEpoch": epoch,
                    "source": plan.manifest(),
                    "sourceState": "uploading",
                    "entryIntent": {
                        "parentFolderId": parent_folder_id,
                        "name": source.name,
                    },
                    "filename": source.name,
                    "mimeType": mimetypes.guess_type(source.name)[0]
                    or "application/octet-stream",
                }
                pending = records.write(
                    project_id,
                    key_epoch=epoch,
                    records=[
                        {
                            "record_id": pending_id,
                            "kind": "file",
                            "expected_revision": 0,
                            "value": private,
                        }
                    ],
                )[0]
            else:
                private = (completed or pending)["value"]
                if private.get("uploadId", private.get("file", {}).get("encryptedObjectId")) != identifier:
                    raise E2eeError("upload_not_found")
                manifest = private["source"]
                object_value = manifest["object"]
                if (
                    object_value["project_id"] != project_id
                    or object_value["object_id"] != identifier
                    or object_value["plaintext_size"] != size
                ):
                    raise E2eeError("source_changed")
                epoch = object_value["epoch"]
                wipe(project_key)
                project_key = session.scope_key(project_id, epoch)
                wrapped = manifest["encryption"]["wrapped_data_key"]
                data_key = session.crypto.open(
                    project_key,
                    {
                        "nonce": wrapped["nonceB64u"],
                        "ciphertext": wrapped["ciphertextB64u"],
                    },
                    key_aad(project_id, epoch, identifier),
                )
                parsed = parse_decryption_plan(
                    manifest,
                    data_key=data_key,
                    wrapped_nonce=bytes(decode(wrapped["nonceB64u"])),
                    wrapped_data_key=bytes(decode(wrapped["ciphertextB64u"])),
                )
                plan = EncryptionPlan(
                    parsed.project_id,
                    parsed.file_id,
                    parsed.object_id,
                    parsed.epoch,
                    parsed.plaintext_size,
                    parsed.chunk_count,
                    parsed.nonce_base,
                    data_key,
                    bytes(decode(wrapped["nonceB64u"])),
                    bytes(decode(wrapped["ciphertextB64u"])),
                    parsed.chunks,
                )
                file_id = plan.file_id
                if completed is not None and completed["record_id"] != file_id:
                    raise E2eeError("invalid_object_context")
            if completed is not None:
                descriptor = session.api.call(
                    "e2eeGetObject", scope_id=project_id, object_id=identifier
                )
            else:
                descriptor = session.command(
                    "e2eeBeginObject",
                    "object_begin",
                    {
                        "scope_id": project_id,
                        "object_id": identifier,
                        "key_epoch": epoch,
                        "ciphertext_size": sum(
                            chunk.ciphertext_size for chunk in plan.chunks
                        ),
                        "chunks": [
                            {
                                "index": chunk.index,
                                "ciphertext_size": chunk.ciphertext_size,
                                "checksum_sha256": encode(chunk.ciphertext_sha256),
                            }
                            for chunk in plan.chunks
                        ],
                    },
                    scope_id=project_id,
                )
            state = descriptor.get("state")
            if state not in {"uploading", "ready"} or (
                completed is not None and state != "ready"
            ):
                raise E2eeError("object_not_ready")
            for chunk in plan.chunks:
                clear = bytearray(stream.read(chunk.plaintext_size))
                try:
                    ciphertext = plan.seal_chunk(clear, chunk.index)
                    if sha256(ciphertext).digest() != chunk.ciphertext_sha256:
                        raise E2eeError("source_changed")
                    if state == "uploading":
                        capability = _object(
                            session, project_id, identifier, "put", chunk.index
                        )
                        url, headers = _capability(capability, "PUT", len(ciphertext))
                        put_ciphertext(
                            url,
                            headers,
                            ciphertext,
                            timeouts=timeouts,
                            transport=transport,
                        )
                finally:
                    wipe(clear)
            if stream.read(1):
                raise E2eeError("source_changed")
        result = {"project_id": project_id, "file_id": file_id, "object_id": identifier}
        if completed is not None:
            return result
        if state == "uploading":
            _object(session, project_id, identifier, "finalize")
        current = records.read(project_id, [pending_id, file_id])
        pending = current[pending_id]
        if pending["deleted"]:
            committed = current.get(file_id)
            if (
                committed is not None
                and not committed["deleted"]
                and committed["value"].get("file", {}).get("encryptedObjectId") == identifier
            ):
                return result
            raise E2eeError("upload_not_found")
        epoch = _epoch(session, project_id)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entry_id = "ent_" + file_id
        file = {
            "projectId": project_id,
            "fileId": file_id,
            "entryId": entry_id,
            "encryptedObjectId": identifier,
            "createdBy": session.subject,
            "fileKind": "project_file",
            "originalFilename": private["filename"],
            "originalPlaintextSize": size,
            "mimeType": private["mimeType"],
            "createdAt": now,
            "updatedAt": now,
        }
        entry = {
            **private["entryIntent"],
            "kind": "file",
            "id": entry_id,
            "fileId": file_id,
            "projectId": project_id,
            "revision": 1,
            "createdAt": now,
            "updatedAt": now,
            "deletedAt": None,
            "file": {
                "id": file_id,
                "originalFilename": file["originalFilename"],
                "sizeBytes": size,
                "createdAt": now,
                "sourceState": "available",
                "media": {"kind": file["mimeType"].split("/")[0]},
            },
            "breadcrumbs": [],
        }
        writes = [
            {"record_id": "floc_" + file_id, "kind": "directory", "expected_revision": 0,
             "value": {"format": 2, "type": "file_locator", "fileId": file_id,
                       "entryId": entry_id, "name": entry["name"],
                       "parentFolderId": entry["parentFolderId"], "entryRevision": 1}},
            {
                "record_id": file_id,
                "kind": "file",
                "expected_revision": 0,
                "value": _completed_file_metadata(private, file),
            },
            {
                "record_id": pending_id,
                "kind": "file",
                "expected_revision": pending["revision"],
                "value": {"file_id": file_id},
                "deleted": True,
            },
        ]
        EncryptedDirectory(records, project_id).insert(
            entry, key_epoch=epoch, additional_records=writes
        )
        return result
    except (OSError, KeyError, ValueError):
        raise E2eeError("transfer_failed") from None
    finally:
        wipe(data_key)
        wipe(project_key)


def download_file(
    session: DeviceSession,
    *,
    project_id: str,
    file_id: str,
    destination: str | Path,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> int:
    session.require_approved()
    record = EncryptedRecords(session).read(project_id, [file_id]).get(file_id)
    if (
        record is None
        or record["deleted"]
        or record["kind"] != "file"
        or "file" not in record["value"]
    ):
        raise E2eeError("not_found")
    manifest = record["value"]["source"]
    value = manifest["object"]
    if value["project_id"] != project_id or value["file_id"] != file_id:
        raise E2eeError("invalid_object_context")
    wrapped = manifest["encryption"]["wrapped_data_key"]
    project_key = session.scope_key(project_id, value["epoch"])
    data_key = bytearray()
    temporary: str | None = None
    destination = Path(destination)
    if destination.exists():
        wipe(project_key)
        raise E2eeError("destination_exists")
    try:
        data_key = session.crypto.open(
            project_key,
            {"nonce": wrapped["nonceB64u"], "ciphertext": wrapped["ciphertextB64u"]},
            key_aad(project_id, value["epoch"], value["object_id"]),
        )
        plan = parse_decryption_plan(
            manifest,
            data_key=data_key,
            wrapped_nonce=bytes(decode(wrapped["nonceB64u"])),
            wrapped_data_key=bytes(decode(wrapped["ciphertextB64u"])),
        )
        descriptor = session.api.call(
            "e2eeGetObject", scope_id=project_id, object_id=plan.object_id
        )
        if descriptor.get("state") != "ready":
            raise E2eeError("object_not_ready")
        handle, temporary = tempfile.mkstemp(
            prefix=".arteligo-", dir=destination.parent
        )
        with os.fdopen(handle, "wb") as output:
            for chunk in plan.chunks:
                capability = session.api.call(
                    "e2eeGetObjectCapability",
                    scope_id=project_id,
                    object_id=plan.object_id,
                    index=chunk.index,
                )
                url, headers = _capability(capability, "GET", chunk.ciphertext_size)
                encrypted = get_ciphertext(
                    url,
                    headers,
                    chunk.ciphertext_size,
                    timeouts=timeouts,
                    transport=transport,
                )
                clear = bytearray(plan.open_chunk(encrypted, chunk.index))
                try:
                    output.write(clear)
                finally:
                    wipe(clear)
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, destination)
        return plan.plaintext_size
    except FileExistsError:
        raise E2eeError("destination_exists") from None
    except (OSError, KeyError, ValueError):
        raise E2eeError("transfer_failed") from None
    finally:
        wipe(data_key)
        wipe(project_key)
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
