from __future__ import annotations

import json
import uuid
from contextlib import nullcontext
from pathlib import Path
from typing import BinaryIO

from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from ..e2ee._crypto import E2eeError
from ..e2ee._records import EncryptedRecords
from ..e2ee._session import DeviceSession
from ..e2ee._signed_commands import AcceptedCommand
from ._crypto import EncryptionPlan, authenticate_source, build_encryption_plan
from ._http import DEFAULT_TIMEOUTS, DEFAULT_TRANSPORT, TransferTimeouts, TransferTransport
from ._opus import prepare_opus_preview
from ._workflow import _file_operation, _file_source, _public_locator, _put_chunk


def upload_wav_preview(
    session: DeviceSession, *, project_id: str, file_id: str, source: str | Path,
    source_stream: BinaryIO | None = None, timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
    transport: TransferTransport = DEFAULT_TRANSPORT,
) -> dict[str, str] | AcceptedCommand:
    session.require_approved()
    records = EncryptedRecords(session)
    saved = session.pending_command(project_id)
    if saved is not None:
        body = crypto.MutationBody.FromString(saved.body)
        binding = app.RecordMutationBinding.FromString(body.application_binding)
        effects = [effect for effect in binding.object_effects
                   if effect.artifact_kind == "preview" and effect.file_id == file_id]
        if len(effects) != 1:
            raise E2eeError("record_publication_pending")
        try:
            resumed = records.resume_write_for(project_id, {"pvu_" + effects[0].object_id})
        except E2eeError as error:
            if error.code != "revision_conflict" or effects[0].action != "publish":
                raise
            resumed = None
        if isinstance(resumed, AcceptedCommand):
            return resumed
        if resumed is not None and effects[0].action == "publish":
            return {"file_id": file_id, "preview_id": effects[0].object_id, "state": "ready"}
    record = records.read(project_id, [file_id]).get(file_id)
    if record is None or record["deleted"] or record["kind"] != "file_metadata":
        raise E2eeError("not_found")
    metadata = _file_source(record["value"])
    pending = None
    cursor = None
    while True:
        page = records.current(project_id, kind="file_preview_upload", after_record_id=cursor)
        for item in page["records"]:
            if item["deleted"]:
                continue
            candidate = app.PreviewUploadDraft.FromString(item["value"])
            if candidate.metadata.file_id == file_id:
                if pending is not None:
                    raise E2eeError("preview_publication_pending")
                pending, draft = item, candidate
        if not page["has_more"]:
            break
        following = page["next_record_id"]
        if not following or following == cursor:
            raise E2eeError("invalid_cursor")
        cursor = following
    if pending is not None:
        if draft.source_object_id != metadata.original.object_id or draft.expected_file_revision != record["revision"]:
            raise E2eeError("source_changed")
        identifier = draft.metadata.preview.preview_id
        status = _file_operation(session, project_id, identifier, "status")
        if status.state == "ready":
            return _publish_preview(records, project_id, pending, draft)
    elif metadata.HasField("preview") and metadata.preview.state == "ready" and metadata.preview.source_object_id == metadata.original.object_id:
        return {"file_id": file_id, "preview_id": metadata.preview.preview_id, "state": "ready"}
    original = EncryptionPlan(metadata.original, session.core)
    with (nullcontext(source_stream) if source_stream is not None else Path(source).open("rb")) as stream:
        digest = authenticate_source(stream, original)
        with prepare_opus_preview(stream, source_size=metadata.plaintext_size, timeout=timeouts.total) as encoded:
            if encoded.source_sha256 != digest:
                raise E2eeError("source_changed")
            with encoded.path.open("rb") as preview_stream:
                if pending is None:
                    identifier = str(uuid.uuid4())
                    binding = app.FileRevisionBinding(file_id=file_id,
                        original_object_id=metadata.original.object_id, preview_object_id=identifier,
                        metadata_revision=record["revision"] + 1).SerializeToString()
                    plan = build_encryption_plan(preview_stream, core=session.core, object_id=identifier,
                        binding=binding, plaintext_size=encoded.size)
                    next_metadata = app.FileMetadata()
                    next_metadata.CopyFrom(metadata)
                    loudness = ({"kind": "unmeasurable"} if encoded.integrated_lufs_x100 is None else {
                        "kind": "measured", "integratedLufsX100": encoded.integrated_lufs_x100,
                        "truePeakDbtpX100": encoded.true_peak_dbtp_x100, "loudnessRangeLuX100": encoded.loudness_range_lu_x100})
                    next_metadata.preview.CopyFrom(app.PreviewMetadata(preview_id=identifier,
                        source_object_id=metadata.original.object_id, profile="opus", codec="opus",
                        filename=metadata.name + ".webm", media_type="audio/webm", duration_seconds=encoded.duration_seconds,
                        sample_rate=48000, channels=encoded.channels, object=plan.locator, state="ready",
                        processing_id=identifier, job_id=identifier,
                        loudness=json.dumps(_playback_loudness(loudness), separators=(",", ":")).encode()))
                    previous = metadata.preview.preview_id if metadata.HasField("preview") else ""
                    draft = app.PreviewUploadDraft(draft_id="pvu_" + identifier, metadata=next_metadata,
                        expected_file_revision=record["revision"], expected_preview_id=previous,
                        source_object_id=metadata.original.object_id, revision=1)
                    committed = records.write(project_id, records=[{"record_id": draft.draft_id,
                        "kind": "file_preview_upload", "expected_revision": 0, "immutable": True,
                        "value": draft.SerializeToString()}],
                        preconditions=[{"record_id": file_id, "expected_revision": record["revision"], "require_live": True}],
                        object_effects=[app.ObjectEffect(action="begin", object_id=identifier, file_id=file_id,
                            artifact_kind="preview", locator=_public_locator(plan.locator), draft_id=draft.draft_id,
                            expected_file_revision=record["revision"], expected_preview_id=previous,
                            source_object_id=metadata.original.object_id, processing_id=identifier, job_id=identifier,
                            exact_source_binding=metadata.original.exact_source_binding)])
                    if isinstance(committed, AcceptedCommand):
                        return committed
                    pending = next(item for item in committed if item["record_id"] == draft.draft_id)
                    status = _file_operation(session, project_id, identifier, "status")
                else:
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
                            ciphertext = plan.seal_chunk(preview_stream.read(chunk.frame.plaintext_length), chunk.index)
                        except E2eeError as error:
                            if error.code != "source_changed":
                                raise
                            raise E2eeError("preview_encoding_changed") from None
                        _put_chunk(session, project_id, identifier, chunk.index, ciphertext, timeouts=timeouts, transport=transport)
    return _publish_preview(records, project_id, pending, draft)


def _publish_preview(records, project_id, pending, draft):
    preview = draft.metadata.preview
    resumed = records.resume_write_for(project_id, {draft.metadata.file_id, draft.draft_id})
    if isinstance(resumed, AcceptedCommand):
        return resumed
    if resumed is not None:
        return {"file_id": draft.metadata.file_id, "preview_id": preview.preview_id, "state": "ready"}
    committed = records.write(project_id, records=[
        {"record_id": draft.metadata.file_id, "kind": "file_metadata", "expected_revision": draft.expected_file_revision,
         "value": draft.metadata.SerializeToString()},
        {"record_id": draft.draft_id, "kind": "file_preview_upload", "expected_revision": pending["revision"], "deleted": True}],
        deleted_objects=[draft.expected_preview_id] if draft.expected_preview_id else [],
        files=[app.FileRevisionBinding(file_id=draft.metadata.file_id, revision=draft.expected_file_revision + 1,
            metadata_value_id=draft.metadata.file_id, metadata_revision=draft.expected_file_revision + 1,
            original_object_id=draft.source_object_id, preview_object_id=preview.preview_id)],
        object_effects=[app.ObjectEffect(action="publish", object_id=preview.preview_id, file_id=draft.metadata.file_id,
            artifact_kind="preview", locator=_public_locator(preview.object), draft_id=draft.draft_id,
            expected_draft_revision=pending["revision"], expected_file_revision=draft.expected_file_revision,
            expected_preview_id=draft.expected_preview_id, source_object_id=draft.source_object_id,
            processing_id=preview.processing_id, job_id=preview.job_id,
            exact_source_binding=draft.metadata.original.exact_source_binding)])
    if isinstance(committed, AcceptedCommand):
        return committed
    return {"file_id": draft.metadata.file_id, "preview_id": preview.preview_id, "state": "ready"}


def _playback_loudness(measurement):
    policy = {"policyVersion": "ebu-r128-playback-v1", "targetIntegratedLoudnessLufs": -16.0,
              "maximumTruePeakDbtp": -1.5, "maximumBoostDb": 6.0}
    if measurement["kind"] != "measured":
        return {**policy, "kind": "unmeasurable", "recommendedGainDb": 0.0}
    integrated = measurement["integratedLufsX100"] / 100
    peak = measurement["truePeakDbtpX100"] / 100
    return {**policy, "kind": "measured", "integratedLoudnessLufs": integrated, "truePeakDbtp": peak,
            "loudnessRangeLu": measurement["loudnessRangeLuX100"] / 100,
            "recommendedGainDb": min(-16 - integrated, -1.5 - peak, 6.0)}
