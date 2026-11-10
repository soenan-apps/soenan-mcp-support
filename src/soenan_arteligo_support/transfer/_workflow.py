from __future__ import annotations

import errno
import mimetypes
import os
import secrets
import sys
import tempfile
import uuid
from base64 import b64encode
from collections.abc import Callable
from contextlib import AbstractContextManager, ExitStack
from hashlib import sha256
from pathlib import Path
from typing import BinaryIO, cast
from urllib.parse import unquote, urlsplit

from google.protobuf.timestamp_pb2 import Timestamp
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ..e2ee._crypto import E2eeError
from ..e2ee._directory import EncryptedDirectory
from ..e2ee._records import EncryptedRecords
from ..e2ee._session import DeviceSession
from ..e2ee._signed_commands import AcceptedCommand
from ._crypto import EncryptionPlan, build_encryption_plan
from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferTimeouts,
    TransferTransport,
    get_ciphertext,
    put_ciphertext,
)


def _file_operation(
    session: DeviceSession,
    project_id: str,
    object_id: str,
    action: str,
    *,
    index: int = 0,
    length: int = 0,
    digest: bytes = b"",
) -> app.FileOperationResponse:
    session.initialize_project(project_id)
    request = app.FileOperationRequest(
        project_id=project_id,
        device_id=session.device_id,
        object_id=object_id,
        action=action,
        chunk_index=index,
        content_length=length,
        sha256=digest,
    )
    if action == "upload_capability":
        return session.service.create_crypto_file_upload_capability(request)
    return session.service.read_crypto_file(request)


def _capability(
    value: app.FileOperationResponse,
    *,
    method: str,
    scope: str,
    object_id: str,
    index: int,
    length: int,
    ciphertext: bytes | None = None,
) -> tuple[str, dict[str, str]]:
    url = value.url
    try:
        parsed = urlsplit(url)
    except ValueError:
        raise E2eeError("invalid_capability") from None
    path = unquote(parsed.path)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or url != url.strip()
        or any(c.isspace() or ord(c) < 32 or ord(c) == 127 or c == "\\" for c in url)
        or "%" in path
        or "\\" in path
        or "//" in path
        or any(p in {".", ".."} for p in path.split("/"))
        or not path.endswith(
            f"/projects/{scope}/encrypted-objects/{object_id}/chunks/{index}.bin"
        )
        or value.content_length != length
    ):
        raise E2eeError("invalid_capability")
    headers = {header.name: header.value for header in value.headers}
    if len(headers) != len(value.headers) or any(
        name != name.lower() or not val or any(c in val for c in ("\r", "\n", "\x00"))
        for name, val in headers.items()
    ):
        raise E2eeError("invalid_capability")
    if method == "PUT":
        if (
            not headers.keys() <= {"content-type", "x-amz-checksum-sha256"}
            or headers.get("content-type", "application/octet-stream")
            != "application/octet-stream"
            or ciphertext is None
            or len(ciphertext) != length
            or headers.get("x-amz-checksum-sha256")
            != b64encode(sha256(ciphertext).digest()).decode("ascii")
        ):
            raise E2eeError("invalid_capability")
    elif method != "GET" or headers:
        raise E2eeError("invalid_capability")
    return url, headers


def _put_chunk(
    session: DeviceSession,
    project_id: str,
    object_id: str,
    index: int,
    ciphertext: bytes,
    *,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> None:
    capability = _file_operation(
        session,
        project_id,
        object_id,
        "upload_capability",
        index=index,
        length=len(ciphertext),
        digest=sha256(ciphertext).digest(),
    )
    url, headers = _capability(
        capability,
        method="PUT",
        scope=project_id,
        object_id=object_id,
        index=index,
        length=len(ciphertext),
        ciphertext=ciphertext,
    )
    put_ciphertext(url, headers, ciphertext, timeouts=timeouts, transport=transport)


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
            {
                "record_id": pending_id,
                "kind": "file_upload",
                "expected_revision": pending["revision"],
                "deleted": True,
            },
            *directory_writes,
        ],
        preconditions=preconditions,
        files=[
            app.FileRevisionBinding(
                file_id=file_id,
                revision=1,
                metadata_value_id=file_id,
                metadata_revision=1,
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
                    if item["kind"] == "file_metadata" and not item["deleted"]
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
        if pending is not None and pending["deleted"]:
            pending = None
        if upload_id and pending is None:
            cursor = None
            while True:
                page = records.current(
                    project_id, kind="file_metadata", after_record_id=cursor
                )
                for record in page["records"]:
                    if (
                        not record["deleted"]
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
            stream = None
            if pending is None:
                stream = sources.enter_context(open_source())
                size = os.fstat(stream.fileno()).st_size
                file_id = "fil_" + secrets.token_hex(16)
                now = Timestamp()
                now.GetCurrentTime()
                media_type = (
                    mimetypes.guess_type(source_path.name)[0]
                    or "application/octet-stream"
                )
                binding = app.FileRevisionBinding(
                    file_id=file_id, original_object_id=identifier, metadata_revision=1
                ).SerializeToString()
                plan = build_encryption_plan(
                    stream,
                    core=session.core,
                    object_id=identifier,
                    binding=binding,
                    plaintext_size=size,
                )
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
                            draft_id=pending_id,
                            expected_draft_revision=1,
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
            status = _file_operation(session, project_id, identifier, "status")
            if status.state not in {"uploading", "ready"}:
                raise E2eeError("object_not_ready")
            if status.state != "ready":
                if stream is None:
                    stream = sources.enter_context(open_source())
                if (
                    os.fstat(stream.fileno()).st_size
                    != metadata.description.plaintext_size
                ):
                    raise E2eeError("source_changed")
                missing = set(status.missing_indices)
                for chunk in plan.chunks:
                    if chunk.index not in missing:
                        stream.seek(chunk.frame.plaintext_length, 1)
                        continue
                    ciphertext = plan.seal_chunk(
                        stream.read(chunk.frame.plaintext_length), chunk.index
                    )
                    _put_chunk(
                        session,
                        project_id,
                        identifier,
                        chunk.index,
                        ciphertext,
                        timeouts=timeouts,
                        transport=transport,
                    )
                if stream.read(1):
                    raise E2eeError("source_changed")
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
    if record is None or record["deleted"] or record["kind"] != "file_metadata":
        raise E2eeError("not_found")
    metadata = cast(domain.FileMetadata, record["value"])
    plan = EncryptionPlan(metadata.original, session.core)
    status = _file_operation(
        session, project_id, plan.locator.descriptor.object_id, "status"
    )
    if status.state != "ready":
        raise E2eeError("object_not_ready")
    for chunk in plan.chunks:
        length = chunk.frame.plaintext_length + 16
        capability = _file_operation(
            session,
            project_id,
            plan.locator.descriptor.object_id,
            "read_capability",
            index=chunk.index,
        )
        url, headers = _capability(
            capability,
            method="GET",
            scope=project_id,
            object_id=plan.locator.descriptor.object_id,
            index=chunk.index,
            length=length,
        )
        ciphertext = get_ciphertext(
            url, headers, length, timeouts=timeouts, transport=transport
        )
        output.write(plan.open_chunk(ciphertext, chunk.index))
    return metadata.description.plaintext_size
