from __future__ import annotations

import uuid
from contextlib import nullcontext
from pathlib import Path
from typing import BinaryIO, cast

from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ..e2ee._crypto import E2eeError
from ..e2ee._records import EncryptedRecords
from ..e2ee._session import DeviceSession
from ..e2ee._signed_commands import AcceptedCommand
from ._crypto import EncryptionPlan, authenticate_source, build_encryption_plan
from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferTimeouts,
    TransferTransport,
)
from ._opus import OpusPreview, prepare_opus_preview
from ._workflow import _file_operation, _put_chunk


def upload_wav_preview(
    session: DeviceSession,
    *,
    project_id: str,
    file_id: str,
    source: str | Path,
    source_stream: BinaryIO | None = None,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> dict[str, str] | AcceptedCommand:
    session.require_approved()
    records = EncryptedRecords(session)
    saved = session.pending_command(project_id)
    if saved is not None:
        body = crypto.MutationBody.FromString(saved.body)
        binding = app.RecordMutationBinding.FromString(body.application_binding)
        effects = [
            effect
            for effect in binding.object_effects
            if effect.artifact_kind == "preview" and effect.file_id == file_id
        ]
        if len(effects) != 1:
            raise E2eeError("record_publication_pending")
        try:
            resumed = records.resume_write_for(
                project_id, {"pvu_" + effects[0].object_id}
            )
        except E2eeError as error:
            if (
                error.code != "revision_conflict"
                or effects[0].action != "preview_publish"
            ):
                raise
            resumed = None
        if isinstance(resumed, AcceptedCommand):
            return resumed
        if resumed is not None and effects[0].action == "preview_publish":
            return {
                "file_id": file_id,
                "preview_id": effects[0].object_id,
                "state": "ready",
            }
    record = records.read(project_id, [file_id]).get(file_id)
    if (
        record is None
        or record["payload_type"] != "content"
        or record["kind"] != "file_metadata"
    ):
        raise E2eeError("not_found")
    metadata = cast(domain.FileMetadata, record["value"])
    pending = None
    cursor = None
    snapshot_epoch = 0
    while True:
        page = records.current(
            project_id,
            kind="file_preview_upload",
            after_record_id=cursor,
            snapshot_epoch=snapshot_epoch,
        )
        snapshot_epoch = page["snapshot_epoch"]
        for item in page["records"]:
            if item["payload_type"] != "content":
                continue
            candidate = item["value"]
            if candidate.file_id == file_id:
                if pending is not None:
                    raise E2eeError("preview_publication_pending")
                pending = item
        if not page["has_more"]:
            break
        following = page["next_record_id"]
        if not following or following == cursor:
            raise E2eeError("invalid_cursor")
        cursor = following
    if pending is not None:
        draft = pending["value"]
        if (
            draft.source_object_id != metadata.original.descriptor.object_id
            or draft.expected_file_revision != record["revision"]
        ):
            raise E2eeError("source_changed")
        identifier = draft.metadata.preview.preview_id
        status = _file_operation(session, project_id, identifier, "status")
        if status.state == "ready":
            return _publish_preview(records, project_id, pending, draft)
    elif (
        metadata.HasField("preview")
        and metadata.preview.state == domain.PREVIEW_STATE_READY
        and metadata.preview.source_object_id == metadata.original.descriptor.object_id
    ):
        return {
            "file_id": file_id,
            "preview_id": metadata.preview.preview_id,
            "state": "ready",
        }
    original = EncryptionPlan(metadata.original, session.core)
    with (
        nullcontext(source_stream)
        if source_stream is not None
        else Path(source).open("rb")
    ) as stream:
        digest = authenticate_source(stream, original)
        with prepare_opus_preview(
            stream,
            source_size=metadata.description.plaintext_size,
            timeout=timeouts.total,
        ) as encoded:
            if encoded.source_sha256 != digest:
                raise E2eeError("source_changed")
            with encoded.path.open("rb") as preview_stream:
                if pending is None:
                    identifier = str(uuid.uuid4())
                    binding = app.FileRevisionBinding(
                        file_id=file_id,
                        original_object_id=metadata.original.descriptor.object_id,
                        preview_object_id=identifier,
                        metadata_revision=record["revision"] + 1,
                        metadata_incarnation=record["incarnation"],
                    ).SerializeToString()
                    plan = build_encryption_plan(
                        preview_stream,
                        core=session.core,
                        object_id=identifier,
                        binding=binding,
                        plaintext_size=encoded.size,
                    )
                    next_metadata = domain.FileMetadata()
                    next_metadata.CopyFrom(metadata)
                    next_metadata.preview.CopyFrom(
                        domain.PreviewMetadata(
                            preview_id=identifier,
                            source_object_id=metadata.original.descriptor.object_id,
                            profile="opus",
                            codec="opus",
                            filename=metadata.description.name + ".webm",
                            media_type="audio/webm",
                            duration_seconds=encoded.duration_seconds,
                            sample_rate=48000,
                            channels=encoded.channels,
                            object=plan.locator,
                            state=domain.PREVIEW_STATE_READY,
                            processing_id=identifier,
                            job_id=identifier,
                            loudness=_playback_loudness(encoded),
                        )
                    )
                    previous = (
                        metadata.preview.preview_id
                        if metadata.HasField("preview")
                        else ""
                    )
                    pending_id = "pvu_" + identifier
                    draft = domain.PreviewUploadDraft(
                        file_id=file_id,
                        metadata=next_metadata,
                        expected_file_revision=record["revision"],
                        expected_file_incarnation=record["incarnation"],
                        expected_preview_id=previous,
                        source_object_id=metadata.original.descriptor.object_id,
                    )
                    committed = records.write(
                        project_id,
                        records=[
                            {
                                "record_id": pending_id,
                                "kind": "file_preview_upload",
                                "expected_revision": 0,
                                "value": draft,
                            }
                        ],
                        preconditions=[
                            app.RecordPrecondition(
                                id=file_id,
                                expected_revision=record["revision"],
                                require_live=True,
                                incarnation=record["incarnation"],
                            )
                        ],
                        object_effects=[
                            app.ObjectEffect(
                                action="begin",
                                object_id=identifier,
                                file_id=file_id,
                                artifact_kind="preview",
                                locator=plan.locator.descriptor,
                                draft_id=pending_id,
                                expected_draft_revision=1,
                                draft_incarnation=records.operation_id,
                                expected_file_incarnation=record["incarnation"],
                                expected_file_revision=record["revision"],
                                expected_preview_id=previous,
                                source_object_id=metadata.original.descriptor.object_id,
                                processing_id=identifier,
                                job_id=identifier,
                                exact_source_binding=metadata.original.descriptor.exact_source_binding,
                            )
                        ],
                    )
                    if isinstance(committed, AcceptedCommand):
                        return committed
                    pending = next(
                        item for item in committed if item["record_id"] == pending_id
                    )
                    status = _file_operation(session, project_id, identifier, "status")
                else:
                    draft = pending["value"]
                    plan = EncryptionPlan(draft.metadata.preview.object, session.core)
                    if plan.plaintext_size != encoded.size:
                        raise E2eeError("preview_encoding_changed")
                if status.state not in {"uploading", "ready"}:
                    raise E2eeError("object_not_ready")
                if status.state != "ready":
                    missing = set(status.missing_indices)
                    for chunk in plan.chunks:
                        if chunk.index not in missing:
                            preview_stream.seek(chunk.frame.plaintext_length, 1)
                            continue
                        try:
                            ciphertext = plan.seal_chunk(
                                preview_stream.read(chunk.frame.plaintext_length),
                                chunk.index,
                            )
                        except E2eeError as error:
                            if error.code != "source_changed":
                                raise
                            raise E2eeError("preview_encoding_changed") from None
                        _put_chunk(
                            session,
                            project_id,
                            identifier,
                            chunk.index,
                            ciphertext,
                            timeouts=timeouts,
                            transport=transport,
                        )
    return _publish_preview(records, project_id, pending, draft)


def _publish_preview(records, project_id, pending, draft):
    preview = draft.metadata.preview
    pending_id = pending["record_id"]
    resumed = records.resume_write_for(project_id, {draft.file_id, pending_id})
    if isinstance(resumed, AcceptedCommand):
        return resumed
    if resumed is not None:
        return {
            "file_id": draft.file_id,
            "preview_id": preview.preview_id,
            "state": "ready",
        }
    committed = records.write(
        project_id,
        records=[
            {
                "record_id": draft.file_id,
                "kind": "file_metadata",
                "expected_revision": draft.expected_file_revision,
                "incarnation": draft.expected_file_incarnation,
                "value": draft.metadata,
            },
        ],
        deletions=[
            {
                "record_id": pending_id,
                "kind": "file_preview_upload",
                "expected_revision": pending["revision"],
                "incarnation": pending["incarnation"],
            }
        ],
        deleted_objects=[draft.expected_preview_id]
        if draft.expected_preview_id
        else [],
        files=[
            app.FileRevisionBinding(
                file_id=draft.file_id,
                revision=draft.expected_file_revision + 1,
                metadata_value_id=draft.file_id,
                metadata_revision=draft.expected_file_revision + 1,
                metadata_incarnation=draft.expected_file_incarnation,
                original_object_id=draft.source_object_id,
                preview_object_id=preview.preview_id,
            )
        ],
        object_effects=[
            app.ObjectEffect(
                action="preview_publish",
                object_id=preview.preview_id,
                file_id=draft.file_id,
                artifact_kind="preview",
                locator=preview.object.descriptor,
                draft_id=pending_id,
                expected_draft_revision=pending["revision"],
                draft_incarnation=pending["incarnation"],
                expected_file_incarnation=draft.expected_file_incarnation,
                expected_file_revision=draft.expected_file_revision,
                expected_preview_id=draft.expected_preview_id,
                source_object_id=draft.source_object_id,
                processing_id=preview.processing_id,
                job_id=preview.job_id,
                exact_source_binding=draft.metadata.original.descriptor.exact_source_binding,
            )
        ],
    )
    if isinstance(committed, AcceptedCommand):
        return committed
    return {
        "file_id": draft.file_id,
        "preview_id": preview.preview_id,
        "state": "ready",
    }


def _playback_loudness(measurement: OpusPreview) -> domain.LoudnessMetadata:
    loudness = domain.LoudnessMetadata(
        state=domain.LOUDNESS_STATE_UNMEASURABLE,
        policy_version="ebu-r128-playback-v1",
        target_integrated_loudness_lufs=-16.0,
        maximum_true_peak_dbtp=-1.5,
        maximum_boost_db=6.0,
    )
    if measurement.loudness is None:
        return loudness
    integrated = measurement.loudness.integrated_lufs_x100 / 100
    peak = measurement.loudness.true_peak_dbtp_x100 / 100
    loudness.state = domain.LOUDNESS_STATE_MEASURED
    loudness.integrated_loudness_lufs = integrated
    loudness.true_peak_dbtp = peak
    loudness.loudness_range_lu = measurement.loudness.loudness_range_lu_x100 / 100
    loudness.recommended_gain_db = round(
        max(-120.0, min(-16 - integrated, -1.5 - peak, 6.0)), 2
    )
    return loudness
