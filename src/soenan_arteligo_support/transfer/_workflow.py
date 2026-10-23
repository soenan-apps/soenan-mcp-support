from __future__ import annotations

import errno
import mimetypes
import os
import secrets
import struct
import sys
import tempfile
import time
import uuid
from base64 import b64encode
from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager, ExitStack
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import unquote, urlsplit

from ..e2ee._crypto import E2eeError, decode, encode, wipe
from ..e2ee._directory import EncryptedDirectory
from ..e2ee._records import EncryptedRecords
from ..e2ee._session import DeviceSession
from ._crypto import (
    MANIFEST_FIELDS, MAXIMUM_WIRE_INTEGER, EncryptionContractError, EncryptionPlan,
    build_encryption_plan, parse_decryption_plan,
)
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


def _file_source(
    session: DeviceSession, project_id: str, metadata: Mapping[str, Any],
) -> tuple[Mapping[str, Any], Any]:
    manifest = metadata.get("source")
    if not isinstance(manifest, Mapping):
        raise EncryptionContractError("manifest must be an object")
    if set(manifest) - {"owner_generation"} != MANIFEST_FIELDS:
        raise EncryptionContractError("manifest fields do not match managed contract")
    checkpoint = metadata.get("owner_generation")
    if "owner_generation" not in manifest:
        return manifest, checkpoint
    embedded = manifest["owner_generation"]
    if ("owner_generation" in metadata and checkpoint != embedded
            or not isinstance(embedded, Mapping) or type(embedded.get("key_epoch")) is not int):
        raise E2eeError("owner_key_generation_stale")
    object_value = manifest["object"]
    if not isinstance(object_value, Mapping):
        raise EncryptionContractError("manifest object must be an object")
    epoch = object_value.get("epoch")
    if (object_value.get("project_id") != project_id or type(epoch) is not int
            or not 1 <= epoch <= MAXIMUM_WIRE_INTEGER):
        raise E2eeError("invalid_object_context")
    generation = session.owner_access.publications.generation(project_id, epoch)
    if embedded != generation.document():
        raise E2eeError("owner_key_generation_stale")
    return {name: manifest[name] for name in MANIFEST_FIELDS}, embedded


def _completed_file_metadata(
    pending: dict[str, Any], file: dict[str, Any]
) -> dict[str, Any]:
    value = _file_metadata_for_write(pending)
    for key in (
        "uploadId",
        "keyEpoch",
        "sourceState",
        "entryIntent",
        "filename",
        "mimeType",
        "originalFilename",
        "originalPlaintextSize",
        "fileKind",
    ):
        value.pop(key, None)
    return {**value, "file": file}


def _completed_upload(
    records: EncryptedRecords, scope: str, pending: dict[str, Any], upload_id: str
) -> dict[str, Any]:
    if pending["payload_type"] == "historical_encrypted_deletion":
        identifier = pending["value"].get("file_id")
        if not isinstance(identifier, str):
            raise E2eeError("upload_not_found")
        candidates = [identifier]
    else:
        writes = records.committed_record_writes(scope, pending)
        candidates = [
            value["record_id"]
            for value in writes
            if value["kind"] == "file"
            and value.get("deleted") is False
            and "ciphertext" in value
        ]
    if not candidates or len(candidates) != len(set(candidates)):
        raise E2eeError("upload_not_found")
    matches = [
        record
        for record in records.read(scope, candidates).values()
        if record["payload_type"] == "content"
        and record["value"].get("file", {}).get("encryptedObjectId") == upload_id
    ]
    if len(matches) != 1:
        raise E2eeError("upload_not_found")
    completed = matches[0]
    object_value = completed["value"]["source"]["object"]
    file = completed["value"]["file"]
    if (
        completed["kind"] != "file"
        or object_value["project_id"] != scope
        or object_value["file_id"] != completed["record_id"]
        or object_value["object_id"] != upload_id
        or file["projectId"] != scope
        or file["fileId"] != completed["record_id"]
    ):
        raise E2eeError("invalid_object_context")
    return completed


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
    value: dict[str, Any],
    *,
    method: str,
    scope: str,
    object_id: str,
    index: int,
    length: int,
    ciphertext: bytes | None = None,
) -> tuple[str, dict[str, str]]:
    if not isinstance(value, dict) or method not in {"GET", "PUT"}:
        raise E2eeError("invalid_capability")
    for identifier in (scope, object_id):
        if (
            not isinstance(identifier, str)
            or not 1 <= len(identifier) <= 128
            or not all(
                character.isascii() and (character.isalnum() or character in "-_")
                for character in identifier
            )
        ):
            raise E2eeError("invalid_capability")
    if (
        isinstance(index, bool)
        or not isinstance(index, int)
        or not 0 <= index <= 4_294_967_294
        or isinstance(length, bool)
        or not isinstance(length, int)
        or length <= 0
    ):
        raise E2eeError("invalid_capability")
    expires_at = value.get("expires_at")
    if (
        isinstance(expires_at, bool)
        or not isinstance(expires_at, int)
        or expires_at <= time.time()
        or value.get("method") != method
    ):
        raise E2eeError("invalid_capability")
    url = value.get("url")
    if (
        not isinstance(url, str)
        or url != url.strip()
        or any(
            character.isspace()
            or ord(character) < 0x20
            or ord(character) == 0x7F
            or character == "\\"
            for character in url
        )
    ):
        raise E2eeError("invalid_capability")
    try:
        parsed = urlsplit(url)
    except ValueError:
        raise E2eeError("invalid_capability") from None
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        raise E2eeError("invalid_capability")
    path = unquote(parsed.path)
    if (
        "%" in path
        or "\\" in path
        or "//" in path
        or any(segment in {".", ".."} for segment in path.split("/"))
        or any(ord(character) < 0x20 or ord(character) == 0x7F for character in path)
        or not path.endswith(
            f"/projects/{scope}/encrypted-objects/{object_id}/chunks/{index}.bin"
        )
    ):
        raise E2eeError("invalid_capability")
    headers = value.get("headers")
    if not isinstance(headers, Mapping) or any(
        not isinstance(name, str)
        or not isinstance(header, str)
        or name != name.lower()
        or not header
        or any(character in header for character in ("\r", "\n", "\x00"))
        for name, header in headers.items()
    ):
        raise E2eeError("invalid_capability")
    content_length = value.get("content_length")
    if method == "PUT":
        if (
            not headers.keys() <= {"content-type", "x-amz-checksum-sha256"}
            or headers.get("content-type", "application/octet-stream")
            != "application/octet-stream"
            or isinstance(content_length, bool)
            or not isinstance(content_length, int)
            or content_length != length
            or not isinstance(ciphertext, (bytes, bytearray))
            or len(ciphertext) != length
            or headers.get("x-amz-checksum-sha256")
            != b64encode(sha256(ciphertext).digest()).decode("ascii")
        ):
            raise E2eeError("invalid_capability")
    elif (
        headers
        or ciphertext is not None
        or (
            "content_length" in value
            and (
                isinstance(content_length, bool)
                or not isinstance(content_length, int)
                or content_length != length
            )
        )
    ):
        raise E2eeError("invalid_capability")
    return url, dict(headers)


def upload_file(
    session: DeviceSession,
    *,
    project_id: str,
    source: str | Path,
    parent_folder_id: str | None = None,
    upload_id: str | None = None,
    source_opener: Callable[[], AbstractContextManager[BinaryIO]] | None = None,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> dict[str, Any]:
    session.require_approved()
    source = Path(source)
    if source_opener is None:
        source_opener = lambda: source.open("rb")
    records = EncryptedRecords(session)
    identifier = upload_id or str(uuid.uuid4())
    pending_id = "upl_" + identifier
    if upload_id is not None:
        records.resume_write_for(project_id, {pending_id})
    current = records.read(project_id, [pending_id])
    pending = current.get(pending_id)
    data_key = bytearray()
    project_key = bytearray()
    try:
        if pending is not None and pending["deleted"]:
            completed = _completed_upload(records, project_id, pending, identifier)
            return {
                "project_id": project_id,
                "file_id": completed["record_id"],
                "object_id": identifier,
            }
        with ExitStack() as sources:
            stream = None
            descriptor = None
            if pending is None:
                if upload_id is not None:
                    raise E2eeError("upload_not_found")
                epoch = _epoch(session, project_id)
                publication = session.owner_access.publications.key(project_id, epoch)
                project_key = publication.key
                stream = sources.enter_context(source_opener())
                size = os.fstat(stream.fileno()).st_size
                if size <= 0:
                    raise E2eeError("file_size_invalid")
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
                manifest = plan.manifest()
                checkpoint = publication.generation.document() if publication.generation is not None else None
                private = {
                    "uploadId": identifier,
                    "keyEpoch": epoch,
                    "owner_generation": checkpoint,
                    "source": manifest,
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
                    publication=publication,
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
                private = pending["value"]
                if private.get("uploadId") != identifier:
                    raise E2eeError("upload_not_found")
                manifest, checkpoint = _file_source(session, project_id, private)
                object_value = manifest["object"]
                if (
                    object_value["project_id"] != project_id
                    or object_value["object_id"] != identifier
                ):
                    raise E2eeError("invalid_object_context")
                epoch = object_value["epoch"]
                publication = session.owner_access.publications.key(project_id, epoch)
                project_key = publication.key
                publication.validate_checkpoint(checkpoint)
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
                size = plan.plaintext_size
                try:
                    descriptor = session.call(
                        "e2eeGetObject", scope_id=project_id, object_id=identifier
                    )
                except E2eeError as error:
                    if error.code != "not_found":
                        raise
            object_manifest = {
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
            }
            if descriptor is None:
                descriptor = session.command(
                    "e2eeBeginObject",
                    "object_begin",
                    object_manifest,
                    scope_id=project_id,
                )
            if descriptor.get("manifest") != object_manifest:
                raise E2eeError("invalid_object_context")
            state = descriptor.get("state")
            if state not in {"uploading", "ready"}:
                raise E2eeError("object_not_ready")
            if state == "uploading":
                if stream is None:
                    stream = sources.enter_context(source_opener())
                if os.fstat(stream.fileno()).st_size != size:
                    raise E2eeError("source_changed")
                for chunk in plan.chunks:
                    clear = bytearray(stream.read(chunk.plaintext_size))
                    try:
                        if len(clear) != chunk.plaintext_size:
                            raise E2eeError("source_changed")
                        ciphertext = plan.seal_chunk(clear, chunk.index)
                        if sha256(ciphertext).digest() != chunk.ciphertext_sha256:
                            raise E2eeError("source_changed")
                        capability = _object(
                            session, project_id, identifier, "put", chunk.index
                        )
                        url, headers = _capability(
                            capability,
                            method="PUT",
                            scope=project_id,
                            object_id=identifier,
                            index=chunk.index,
                            length=chunk.ciphertext_size,
                            ciphertext=ciphertext,
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
                if stream.read(1):
                    raise E2eeError("source_changed")
        result = {"project_id": project_id, "file_id": file_id, "object_id": identifier}
        if state == "uploading":
            _object(session, project_id, identifier, "finalize")
        current = records.read(project_id, [pending_id])
        latest_pending = current[pending_id]
        if latest_pending["deleted"]:
            completed = _completed_upload(
                records, project_id, latest_pending, identifier
            )
            if (
                completed["record_id"] != file_id
                or _file_source(session, project_id, completed["value"]) != (manifest, checkpoint)
            ):
                raise E2eeError("invalid_object_context")
            return result
        if latest_pending["revision"] != pending["revision"]:
            raise E2eeError("revision_conflict")
        if records.resume_write_for(project_id, {file_id, pending_id}) is not None:
            return result
        epoch = _epoch(session, project_id)
        if epoch != private["source"]["object"]["epoch"]:
            raise E2eeError("upload_owner_epoch_changed")
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
            {
                "record_id": "floc_" + file_id,
                "kind": "directory",
                "expected_revision": 0,
                "value": {
                    "format": 2,
                    "type": "file_locator",
                    "fileId": file_id,
                    "entryId": entry_id,
                    "name": entry["name"],
                    "parentFolderId": entry["parentFolderId"],
                    "entryRevision": 1,
                },
            },
            {
                "record_id": file_id,
                "kind": "file",
                "expected_revision": 0,
                "value": _completed_file_metadata({
                    **private, "source": manifest, "owner_generation": checkpoint,
                }, file),
            },
            {
                "record_id": pending_id,
                "kind": "file",
                "expected_revision": pending["revision"],
                "deleted": True,
            },
        ]
        with session.owner_access.publications.key(project_id, epoch) as publication:
            publication.validate_checkpoint(checkpoint)
            EncryptedDirectory(records, project_id).insert(
                entry, key_epoch=epoch, additional_records=writes, publication=publication
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
    destination = Path(destination)
    if destination.exists():
        raise E2eeError("destination_exists")
    temporary: str | None = None
    try:
        output_file = None
        if sys.platform == "linux":
            try:
                handle = os.open(destination.parent, os.O_TMPFILE | os.O_RDWR, 0o600)
            except OSError as error:
                if error.errno not in {
                    errno.EOPNOTSUPP,
                    errno.EINVAL,
                    errno.EISDIR,
                    errno.ENOSYS,
                }:
                    raise
            else:
                output_file = os.fdopen(handle, "w+b")
        if output_file is None:
            handle, temporary = tempfile.mkstemp(
                prefix=".arteligo-", dir=destination.parent
            )
            output_file = os.fdopen(handle, "wb")
        with output_file as output:
            written = _download_to_stream(
                session,
                project_id=project_id,
                file_id=file_id,
                output=output,
                timeouts=timeouts,
                transport=transport,
            )
            output.flush()
            os.fsync(output.fileno())
            if temporary is None:
                os.link(
                    f"/proc/self/fd/{output.fileno()}",
                    destination,
                    src_dir_fd=0,
                    follow_symlinks=True,
                )
            else:
                os.link(temporary, destination)
        return written
    except FileExistsError:
        raise E2eeError("destination_exists") from None
    except (OSError, KeyError, ValueError):
        raise E2eeError("transfer_failed") from None
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def _download_to_stream(
    session: DeviceSession,
    *,
    project_id: str,
    file_id: str,
    output: BinaryIO,
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
    manifest, _ = _file_source(session, project_id, record["value"])
    value = manifest["object"]
    if value["project_id"] != project_id or value["file_id"] != file_id:
        raise E2eeError("invalid_object_context")
    wrapped = manifest["encryption"]["wrapped_data_key"]
    project_key = session.scope_key(project_id, value["epoch"])
    data_key = bytearray()
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
        descriptor = session.call(
            "e2eeGetObject", scope_id=project_id, object_id=plan.object_id
        )
        if descriptor.get("state") != "ready":
            raise E2eeError("object_not_ready")
        for chunk in plan.chunks:
            capability = session.call(
                "e2eeGetObjectCapability",
                scope_id=project_id,
                object_id=plan.object_id,
                index=chunk.index,
            )
            url, headers = _capability(
                capability,
                method="GET",
                scope=project_id,
                object_id=plan.object_id,
                index=chunk.index,
                length=chunk.ciphertext_size,
            )
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
        return plan.plaintext_size
    except (OSError, KeyError, ValueError):
        raise E2eeError("transfer_failed") from None
    finally:
        wipe(data_key)
        wipe(project_key)
