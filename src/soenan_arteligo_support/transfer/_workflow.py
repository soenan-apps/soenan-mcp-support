from __future__ import annotations

import errno
import mimetypes
import os
import secrets
import sys
import tempfile
import uuid
from base64 import b64encode
from collections.abc import Callable, Generator, Iterator, Sequence
from contextlib import AbstractContextManager, ExitStack, contextmanager
from pathlib import Path
from typing import BinaryIO, cast
from urllib.parse import parse_qsl, unquote, urlsplit

from google.protobuf.timestamp_pb2 import Timestamp
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ..e2ee._crypto import E2eeError
from ..e2ee._directory import EncryptedDirectory
from ..e2ee._records import EncryptedRecords
from ..e2ee._session import DeviceSession
from ..e2ee._signed_commands import AcceptedCommand
from ._crypto import EncryptionPlan, prepare_upload, restore_missing_parts
from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferHTTPError,
    TransferSizeMismatch,
    TransferTimeouts,
    TransferTransport,
    get_ciphertext,
    put_ciphertext,
)

_SIGNING_QUERY_NAMES = {
    "X-Amz-Algorithm",
    "X-Amz-Credential",
    "X-Amz-Date",
    "X-Amz-Expires",
    "X-Amz-Signature",
    "X-Amz-SignedHeaders",
}


def _file_operation(
    session: DeviceSession,
    project_id: str,
    object_id: str,
    action: str,
    *,
    object_length: int,
    part_number: int = 0,
    length: int = 0,
    digest: bytes = b"",
) -> app.FileOperationResponse:
    session.initialize_project(project_id)
    request = app.FileOperationRequest(
        project_id=project_id,
        device_id=session.device_id,
        object_id=object_id,
        action=action,
        part_number=part_number,
        content_length=length,
        sha256=digest,
    )
    upload = action == "upload_capability"
    operation = (
        session.service.create_crypto_file_upload_capability
        if upload
        else session.service.read_crypto_file
    )
    value = operation(request)
    if (
        value.contract != "arteligo.s3-object-capability"
        or value.version != 1
        or value.operation != ("put" if upload else "get")
        or value.object_id != object_id
        or value.part_number != part_number
        or value.object_length != object_length
    ):
        raise E2eeError("invalid_capability")
    return value


def _capability(
    value: app.FileOperationResponse,
    *,
    method: str,
    scope: str,
    object_id: str,
    length: int,
    digest: bytes = b"",
    multipart: bool = False,
) -> tuple[str, dict[str, str]]:
    url = value.url
    try:
        parsed = urlsplit(url)
        query_pairs = parse_qsl(
            parsed.query, keep_blank_values=True, strict_parsing=True
        )
    except ValueError:
        raise E2eeError("invalid_capability") from None
    path = unquote(parsed.path)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or url != url.strip()
        or any(c.isspace() or ord(c) < 32 or ord(c) == 127 or c == "\\" for c in url)
        or "%" in path
        or "\\" in path
        or "//" in path
        or any(p in {".", ".."} for p in path.split("/"))
        or not path.endswith(f"/projects/{scope}/encrypted-objects/{object_id}.bin")
        or value.content_length != length
        or value.state != ("uploading" if method == "PUT" else "ready")
    ):
        raise E2eeError("invalid_capability")
    query = dict(query_pairs)
    headers = {header.name: header.value for header in value.headers}
    expected_query = _SIGNING_QUERY_NAMES
    expected_headers: dict[str, str] = {}
    signed = {"host"}
    if method == "PUT":
        expected_headers = {
            "content-type": "application/octet-stream",
            "x-amz-checksum-sha256": b64encode(digest).decode("ascii"),
        }
        if multipart:
            expected_query = _SIGNING_QUERY_NAMES | {"partNumber", "uploadId"}
            if query.get("partNumber") != str(value.part_number) or not query.get(
                "uploadId"
            ):
                raise E2eeError("invalid_capability")
        else:
            expected_headers["if-none-match"] = "*"
        signed.update(expected_headers)
        signed.add("content-length")
    if (
        len(query) != len(query_pairs)
        or query.keys() != expected_query
        or not all(query.values())
        or query["X-Amz-Algorithm"] != "AWS4-HMAC-SHA256"
        or query.get("X-Amz-SignedHeaders") != ";".join(sorted(signed))
        or len(headers) != len(value.headers)
        or headers != expected_headers
    ):
        raise E2eeError("invalid_capability")
    return url, headers


def _missing_parts(
    session: DeviceSession,
    project_id: str,
    plan: EncryptionPlan,
    parts: Sequence[domain.UploadPart],
) -> tuple[int, ...]:
    descriptor = plan.locator.descriptor
    status = _file_operation(
        session,
        project_id,
        descriptor.object_id,
        "status",
        object_length=descriptor.ciphertext_size,
    )
    if status.state not in {"ready", "uploading"}:
        raise E2eeError("object_not_ready")
    missing = tuple(sorted(set(status.missing_parts)))
    if (
        status.content_length
        or len(missing) != len(status.missing_parts)
        or (
            missing
            and (status.state == "ready" or missing[0] < 1 or missing[-1] > len(parts))
        )
    ):
        raise E2eeError("invalid_capability")
    return missing


def _put_missing_parts(
    session: DeviceSession,
    project_id: str,
    plan: EncryptionPlan,
    parts: Sequence[domain.UploadPart],
    missing: Sequence[int],
    spool: BinaryIO,
    *,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> None:
    descriptor = plan.locator.descriptor
    needed = set(missing)
    offset = 0
    multipart = len(parts) > 1
    for number, part in enumerate(parts, 1):
        if number in needed:
            capability = _file_operation(
                session,
                project_id,
                descriptor.object_id,
                "upload_capability",
                object_length=descriptor.ciphertext_size,
                part_number=number,
                length=part.ciphertext_size,
                digest=part.sha256,
            )
            url, headers = _capability(
                capability,
                method="PUT",
                scope=project_id,
                object_id=descriptor.object_id,
                length=part.ciphertext_size,
                digest=part.sha256,
                multipart=multipart,
            )
            spool.seek(offset)
            try:
                put_ciphertext(
                    url,
                    headers,
                    spool,
                    part.ciphertext_size,
                    timeouts=timeouts,
                    transport=transport,
                )
            except TransferHTTPError as error:
                if multipart or error.status != 412:
                    raise
                if _missing_parts(session, project_id, plan, parts):
                    raise
        offset += part.ciphertext_size


def _publish_source(records, scope, pending, draft):
    metadata = draft.metadata
    identifier, file_id = metadata.original.descriptor.object_id, draft.file_id
    pending_id = pending["record_id"]
    result = {"project_id": scope, "file_id": file_id, "object_id": identifier}
    resumed = records.resume_write_for(scope, {file_id, pending_id})
    if isinstance(resumed, AcceptedCommand):
        return resumed
    if resumed is not None:
        return result
    records.operation_id = draft.publish_operation_id
    description = metadata.description
    values = domain.ProjectEntryValues(
        name=draft.entry.name,
        created_at=description.created_at,
        updated_at=description.updated_at,
    )
    if draft.entry.HasField("parent_folder_id"):
        values.parent_folder_id = draft.entry.parent_folder_id
    entry = domain.ProjectEntry(
        id="ent_" + file_id,
        revision=1,
        file=domain.ProjectFileEntry(
            values=values, file_id=file_id, description=description
        ),
    )
    directory_writes, preconditions = EncryptedDirectory(records, scope).insertion(
        [entry]
    )
    committed = records.write(
        scope,
        records=[
            {
                "record_id": "floc_" + file_id,
                "kind": "directory",
                "expected_revision": 0,
                "value": domain.DirectoryFileLocator(entry=entry),
            },
            {
                "record_id": file_id,
                "kind": "file_metadata",
                "expected_revision": 0,
                "value": metadata,
            },
            *directory_writes,
        ],
        deletions=[
            {
                "record_id": pending_id,
                "kind": "file_upload",
                "expected_revision": pending["revision"],
                "incarnation": pending["incarnation"],
            }
        ],
        operation_id=draft.publish_operation_id,
        preconditions=preconditions,
        files=[
            app.FileRevisionBinding(
                file_id=file_id,
                revision=1,
                metadata_value_id=file_id,
                metadata_revision=1,
                metadata_incarnation=records.operation_id,
                original_object_id=identifier,
            )
        ],
        object_effects=[
            app.ObjectEffect(
                action="finalize",
                object_id=identifier,
                file_id=file_id,
                artifact_kind="source",
                locator=metadata.original.descriptor,
                draft_id=pending_id,
                expected_draft_revision=pending["revision"],
                draft_incarnation=pending["incarnation"],
            )
        ],
    )
    return committed if isinstance(committed, AcceptedCommand) else result


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
) -> dict[str, str] | AcceptedCommand:
    session.require_approved()
    source_path = Path(source)
    records = EncryptedRecords(session)
    open_source = (
        source_opener if source_opener is not None else lambda: source_path.open("rb")
    )
    saved = session.pending_command(project_id)
    if saved is not None and upload_id is None:
        body = crypto.MutationBody.FromString(saved.body)
        binding = app.RecordMutationBinding.FromString(body.application_binding)
        effects = [
            effect
            for effect in binding.object_effects
            if effect.artifact_kind == "source"
        ]
        if len(effects) != 1:
            raise E2eeError("record_publication_pending")
        upload_id = effects[0].object_id
    identifier = upload_id or str(uuid.uuid4())
    pending_id = "upl_" + identifier
    try:
        try:
            resumed = records.resume_write_for(project_id, {pending_id})
        except E2eeError as error:
            if error.code != "revision_conflict" or saved is None:
                raise
            saved_body = crypto.MutationBody.FromString(saved.body)
            saved_binding = app.RecordMutationBinding.FromString(
                saved_body.application_binding
            )
            if not any(
                effect.action == "finalize" and effect.object_id == identifier
                for effect in saved_binding.object_effects
            ):
                raise
            resumed = None
        if isinstance(resumed, AcceptedCommand):
            return resumed
        if resumed:
            completed = next(
                (
                    item
                    for item in resumed
                    if item["kind"] == "file_metadata"
                    and item["payload_type"] == "content"
                ),
                None,
            )
            if completed:
                return {
                    "project_id": project_id,
                    "file_id": completed["record_id"],
                    "object_id": identifier,
                }
        pending = (
            records.read(project_id, [pending_id]).get(pending_id)
            if upload_id
            else None
        )
        if pending is not None and pending["payload_type"] == "deletion":
            pending = None
        if upload_id and pending is None:
            cursor = None
            snapshot_epoch = 0
            while True:
                page = records.current(
                    project_id,
                    kind="file_metadata",
                    after_record_id=cursor,
                    snapshot_epoch=snapshot_epoch,
                )
                snapshot_epoch = page["snapshot_epoch"]
                for record in page["records"]:
                    if (
                        record["payload_type"] == "content"
                        and record["value"].original.descriptor.object_id == identifier
                    ):
                        return {
                            "project_id": project_id,
                            "file_id": record["record_id"],
                            "object_id": identifier,
                        }
                if not page["has_more"]:
                    raise E2eeError("upload_not_found")
                following = page["next_record_id"]
                if not following or following == cursor:
                    raise E2eeError("invalid_cursor")
                cursor = following
        with ExitStack() as sources:
            spool = None
            if pending is None:
                stream = sources.enter_context(open_source())
                size = os.fstat(stream.fileno()).st_size
                file_id = "fil_" + secrets.token_hex(16)
                publish_operation_id = str(uuid.uuid4())
                now = Timestamp()
                now.GetCurrentTime()
                media_type = (
                    mimetypes.guess_type(source_path.name)[0]
                    or "application/octet-stream"
                )
                binding = app.FileRevisionBinding(
                    file_id=file_id,
                    original_object_id=identifier,
                    metadata_revision=1,
                    metadata_incarnation=publish_operation_id,
                ).SerializeToString()
                spool = sources.enter_context(
                    cast(BinaryIO, tempfile.TemporaryFile(mode="w+b"))
                )
                prepared = prepare_upload(
                    stream,
                    spool,
                    core=session.core,
                    object_id=identifier,
                    binding=binding,
                    plaintext_size=size,
                )
                plan = prepared.plan
                metadata = domain.FileMetadata(
                    description=domain.FileDescription(
                        name=source_path.name,
                        media_type=media_type,
                        plaintext_size=size,
                        created_by_user_id=session.subject,
                        created_at=now,
                        updated_at=now,
                    ),
                    original=plan.locator,
                )
                entry = domain.ProjectEntryIntent(name=source_path.name)
                if parent_folder_id is not None:
                    entry.parent_folder_id = parent_folder_id
                draft = domain.FileUploadDraft(
                    file_id=file_id,
                    metadata=metadata,
                    entry=entry,
                    state=domain.FILE_UPLOAD_STATE_UPLOADING,
                    publish_operation_id=publish_operation_id,
                    upload_parts=prepared.parts,
                    plaintext_sha256=prepared.plaintext_sha256,
                )
                committed = records.write(
                    project_id,
                    records=[
                        {
                            "record_id": pending_id,
                            "kind": "file_upload",
                            "expected_revision": 0,
                            "value": draft,
                        }
                    ],
                    object_effects=[
                        app.ObjectEffect(
                            action="begin",
                            object_id=identifier,
                            file_id=file_id,
                            artifact_kind="source",
                            locator=plan.locator.descriptor,
                            upload_parts=draft.upload_parts,
                            draft_id=pending_id,
                            expected_draft_revision=1,
                            draft_incarnation=records.operation_id,
                        )
                    ],
                )
                if isinstance(committed, AcceptedCommand):
                    return committed
                pending = next(
                    item for item in committed if item["record_id"] == pending_id
                )
            else:
                draft = cast(domain.FileUploadDraft, pending["value"])
                metadata = draft.metadata
                plan = EncryptionPlan(metadata.original, session.core)
                if metadata.original.descriptor.object_id != identifier:
                    raise E2eeError("invalid_object_context")
            parts = draft.upload_parts
            missing = _missing_parts(session, project_id, plan, parts)
            if missing:
                if spool is None:
                    if len(draft.plaintext_sha256) != 32:
                        raise E2eeError("source_changed")
                    stream = sources.enter_context(open_source())
                    spool = sources.enter_context(
                        cast(BinaryIO, tempfile.TemporaryFile(mode="w+b"))
                    )
                    restore_missing_parts(
                        stream, spool, plan, parts, missing, draft.plaintext_sha256
                    )
                _put_missing_parts(
                    session,
                    project_id,
                    plan,
                    parts,
                    missing,
                    spool,
                    timeouts=timeouts,
                    transport=transport,
                )
        return _publish_source(records, project_id, pending, draft)
    except (OSError, KeyError, ValueError):
        raise E2eeError("transfer_failed") from None


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
    temporary = None
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
        or record["payload_type"] != "content"
        or record["kind"] != "file_metadata"
    ):
        raise E2eeError("not_found")
    metadata = cast(domain.FileMetadata, record["value"])
    plan = EncryptionPlan(metadata.original, session.core)
    written = 0
    with _download_frames(
        session, project_id, plan, timeouts=timeouts, transport=transport
    ) as frames:
        for plaintext in frames:
            output.write(plaintext)
            written += len(plaintext)
    if written != metadata.description.plaintext_size:
        raise TransferSizeMismatch("plaintext byte count does not match metadata")
    return written


@contextmanager
def _download_frames(
    session: DeviceSession,
    project_id: str,
    plan: EncryptionPlan,
    *,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> Generator[Iterator[bytes], None, None]:
    descriptor = plan.locator.descriptor
    capability = _file_operation(
        session,
        project_id,
        descriptor.object_id,
        "read_capability",
        object_length=descriptor.ciphertext_size,
    )
    url, headers = _capability(
        capability,
        method="GET",
        scope=project_id,
        object_id=descriptor.object_id,
        length=descriptor.ciphertext_size,
    )
    with get_ciphertext(
        url, headers, descriptor.ciphertext_size, timeouts=timeouts, transport=transport
    ) as read:
        yield plan.open_frames(read)
