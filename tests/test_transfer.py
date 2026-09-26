from __future__ import annotations

import io
import json
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from base64 import urlsafe_b64decode, urlsafe_b64encode
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing_extensions import Self

from soenan_arteligo_support.transfer import _claim, _cli, _workflow
from soenan_arteligo_support.transfer._api import ArteligoTransferAPI
from soenan_arteligo_support.transfer._claim import FileKeyClaim
from soenan_arteligo_support.transfer._crypto import (
    CHUNK_SIZE,
    ChunkMetadata,
    chunk_aad,
    chunk_nonce,
    parse_preview_decryption_plan,
    preview_chunk_aad,
)
from soenan_arteligo_support.transfer._handoff import parse_handoff
from soenan_arteligo_support.transfer._http import (
    DEFAULT_TIMEOUTS,
    TransferError,
    TransferHTTPError,
    TransferTimeoutError,
    TransferTimeouts,
)


def test_handoff_rejects_missing_extra_and_operation_mismatched_fields() -> None:
    valid = _upload_handoff()
    for mutated in (
        {key: value for key, value in valid.items() if key != "continuation"},
        {**valid, "unexpected": True},
        {**valid, "operation": "file_download"},
    ):
        with pytest.raises(TransferError):
            parse_handoff(mutated)

def test_preview_upload_handoff_requires_complete_source_binding() -> None:
    handoff = _upload_handoff()
    handoff["upload"]["previewProfile"] = "opus-webm-v1"
    handoff["previewId"] = "preview_1"
    handoff["processingId"] = "processing_1"
    handoff["jobId"] = "job_1"
    parsed = parse_handoff(handoff, now_unix_milliseconds=1)
    assert parsed.upload is not None
    assert parsed.upload.preview_profile == "opus-webm-v1"
    assert parsed.upload.preview_id == "preview_1"
    for missing in ("previewId", "processingId", "jobId"):
        incomplete = {key: value for key, value in handoff.items() if key != missing}
        with pytest.raises(TransferError):
            parse_handoff(incomplete, now_unix_milliseconds=1)
    for unsupported_profile in ("opus-128k-webm-v1", "aac-legacy"):
        handoff["upload"]["previewProfile"] = unsupported_profile
        with pytest.raises(TransferError):
            parse_handoff(handoff, now_unix_milliseconds=1)

@pytest.mark.parametrize("profile", [
    "aac-lc-128k-m4a-v1",
    "h264-aac-fmp4-v1",
])
def test_legacy_preview_upload_handoff_keeps_source_bindings(profile: str) -> None:
    handoff = _upload_handoff()
    handoff["upload"]["previewProfile"] = profile
    handoff.update(previewId="preview_1", processingId="processing_1", jobId="job_1")
    parsed = parse_handoff(handoff, now_unix_milliseconds=1)
    assert parsed.upload is not None
    assert (
        parsed.upload.preview_profile,
        parsed.upload.preview_id,
        parsed.upload.processing_id,
        parsed.upload.job_id,
    ) == (profile, "preview_1", "processing_1", "job_1")


@pytest.mark.parametrize("profile,filename,source", [
    (
        "aac-lc-128k-m4a-v1", "recording.wav",
        struct.pack("<4sI4s", b"RIFF", 38, b"WAVE")
        + struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 8000, 16000, 2, 16)
        + struct.pack("<4sI", b"data", 2) + b"\x00\x00",
    ),
    ("h264-aac-fmp4-v1", "scene.mp4", b"\x00\x00\x00\x10ftypisom"),
])
def test_legacy_preview_upload_commits_source_without_local_sidecar(
    monkeypatch: pytest.MonkeyPatch, profile: str, filename: str, source: bytes,
) -> None:
    handoff = _upload_handoff()
    handoff["upload"].update(
        filename=filename, plaintextSize=str(len(source)), previewProfile=profile,
    )
    handoff.update(previewId="preview_1", processingId="processing_1", jobId="job_1")
    uploaded: list[bytes] = []
    manifest: dict[str, Any] = {}
    completed = False

    class API:
        def __init__(self, **kwargs: object) -> None:
            pass

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def put_manifest(self, **kwargs: Any) -> dict[str, str]:
            manifest.update(kwargs["manifest"])
            return {"state": "uploading"}

        def upload_capability(self, **kwargs: object) -> dict[str, object]:
            return {
                "operation": "PUT", "objectId": "upload_1", "chunkIndex": 0,
                "contentLength": len(source) + 16,
                "url": "https://bucket.example/source", "headers": {},
            }

        def complete_upload(self, **kwargs: object) -> dict[str, str]:
            nonlocal completed
            completed = True
            return {"state": "ready"}

        def commit_file(self, **kwargs: object) -> dict[str, object]:
            assert completed and len(uploaded) == 1
            assert kwargs["filename"] == filename
            return {"fileId": kwargs["file_id"]}

        def begin_preview_upload(self, **kwargs: object) -> None:
            pytest.fail("legacy previews must be processed by server jobs")

    monkeypatch.setattr(_workflow, "ArteligoTransferAPI", API)
    monkeypatch.setattr(_workflow, "redeem_file_key_claim", lambda *args, **kwargs: FileKeyClaim(
        direction="upload", project_id="project_1", object_id="upload_1",
        epoch=7, data_key=b"k" * 32, wrapped_nonce=b"n" * 12,
        wrapped_data_key=b"w" * 48,
    ))
    monkeypatch.setattr(_workflow, "put_ciphertext", lambda url, headers, ciphertext, **kwargs: uploaded.append(ciphertext))
    monkeypatch.setattr(
        _workflow, "preflight_wav_preview",
        lambda *args, **kwargs: pytest.fail("legacy previews must not use Opus WAV preflight"),
    )
    monkeypatch.setattr(
        _workflow, "_upload_preview",
        lambda *args, **kwargs: pytest.fail("legacy previews must not create a local sidecar"),
    )
    result = _workflow.upload_file(handoff, source=io.BytesIO(source))
    assert result == {"fileId": handoff["upload"]["operationId"]}
    assert completed and len(uploaded) == 1
    object_manifest = manifest["object"]
    assert object_manifest["plaintext_size"] == len(source)
    assert object_manifest["chunks"][0]["ciphertext_sha256_b64u"] == _b64u(
        sha256(uploaded[0]).digest()
    )
    nonce_base = urlsafe_b64decode(object_manifest["nonce_base_b64u"] + "==")
    assert AESGCM(b"k" * 32).decrypt(
        chunk_nonce(nonce_base, 0),
        uploaded[0],
        chunk_aad(
            project_id="project_1",
            file_id=handoff["upload"]["operationId"],
            object_id="upload_1",
            epoch=7,
            total_plaintext_size=len(source),
            chunk_count=1,
            chunk_index=0,
            plaintext_offset=0,
            plaintext_length=len(source),
            final=True,
        ),
    ) == source


def test_handoff_uses_canonical_file_identity() -> None:
    preview = _preview_handoff()
    parsed = parse_handoff(preview, now_unix_milliseconds=1)
    assert parsed.preview is not None
    assert parsed.preview.file_id == "file_1"




def test_handoff_rejects_wrong_protocol_origin_binding_and_expired_claim() -> None:
    valid = _upload_handoff()
    variants = (
        {**valid, "protocolVersion": "arteligo.encrypted-transfer.v2"},
        {**valid, "protocolVersion": "audaligo.encrypted-transfer.v1"},
        {
            **valid,
            "keyClaim": {
                **valid["keyClaim"],
                "protocol": "audaligo.file-key-claim.v1",
            },
        },
        {
            **valid,
            "keyClaim": {
                **valid["keyClaim"],
                "url": f"https://other.example/claims/key#{'a' * 43}",
            },
        },
        {
            **valid,
            "keyClaim": {
                **valid["keyClaim"],
                "expiresAtUnixMilliseconds": "1000",
            },
        },
    )
    for value in variants:
        with pytest.raises(TransferError):
            parse_handoff(value, now_unix_milliseconds=2000)


def test_handoff_accepts_canonical_proto_uint64_strings() -> None:
    handoff = parse_handoff(_file_handoff(), now_unix_milliseconds=1)
    assert handoff.epoch == 7
    assert handoff.file is not None
    assert handoff.file.plaintext_size == 5
    assert handoff.manifest is not None
    assert handoff.manifest["plaintextSize"] == 5
    assert handoff.manifest["chunks"][0]["plaintextOffset"] == 0


def test_handoff_rejects_noncanonical_proto_uint64_strings() -> None:
    value = _file_handoff()
    value["epoch"] = "007"
    with pytest.raises(TransferError, match="canonical wire integer"):
        parse_handoff(value)


def test_download_handoff_rejects_wrapped_or_clear_key_material() -> None:
    for forbidden in ("wrappedDataKey", "dataKey"):
        value = _file_handoff()
        value["manifest"][forbidden] = "forbidden"
        with pytest.raises(TransferError, match="fields do not match"):
            parse_handoff(value)


def test_continuation_control_client_never_sends_authorization_header() -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "capability": {
                    "contract": "arteligo.railway-bucket-capability",
                    "v": 1,
                    "operation": "GET",
                    "objectId": "object_1",
                    "chunkIndex": 0,
                    "expiresAt": "2030-01-01T00:00:00Z",
                    "contentLength": 21,
                    "url": "https://bucket.example/chunk",
                    "headers": {},
                }
            },
        )

    with ArteligoTransferAPI(
        control_origin="https://arteligo.example",
        continuation="c" * 43,
        timeouts=DEFAULT_TIMEOUTS,
        control_transport=httpx.MockTransport(handle),
    ) as api:
        api.read_capability(project_id="project_1", object_id="object_1", chunk_index=0)

    assert len(requests) == 1
    assert "authorization" not in requests[0].headers
    assert requests[0].headers["Arteligo-Transfer-Continuation"] == "c" * 43


def test_preview_control_uses_generated_source_bound_routes_and_continuation() -> None:
    requests: list[httpx.Request] = []
    session = {
        "previewId": "preview_1", "sourceObjectId": "source_1",
        "processingId": "processing_1", "jobId": "job_1",
        "epoch": "7", "nonceBaseB64u": _b64u(b"12345678"),
        "state": "reserved",
        "keyClaim": _key_claim(),
    }

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/preview-upload/reset"):
            return httpx.Response(
                200,
                json={
                    **session,
                    "previewId": "preview_2",
                    "processingId": "processing_2",
                    "jobId": "job_2",
                    "nonceBaseB64u": _b64u(b"87654321"),
                },
            )
        if request.url.path.endswith("/preview-upload"):
            return httpx.Response(200, json=session)
        return httpx.Response(
            201 if request.method == "PUT" else 200,
            json={"ok": True, "objectId": "preview_2", "state": "ready"},
        )

    manifest = {
        "sourceObjectId": "source_1", "previewId": "preview_2",
        "processingId": "processing_2", "jobId": "job_2",
        "epoch": 7, "nonceBaseB64u": _b64u(b"87654321"),
        "plaintextSize": 5, "ciphertextSize": 21, "chunkSize": CHUNK_SIZE,
        "chunks": [{
            "chunkIndex": 0, "plaintextOffset": 0, "plaintextSize": 5,
            "ciphertextOffset": 0, "ciphertextSize": 21,
            "ciphertextSha256B64u": _b64u(sha256(b"ciphertext").digest()),
            "finalChunk": True,
        }],
        "media": {
            "durationSeconds": 1.0, "mimeType": "audio/webm", "codecs": "opus",
            "sampleRate": 48000, "channels": 2, "bitrate": 128000,
            "playbackLoudness": {"kind": "unmeasurable"},
        },
    }
    with ArteligoTransferAPI(
        control_origin="https://arteligo.example",
        continuation="c" * 43,
        timeouts=DEFAULT_TIMEOUTS,
        control_transport=httpx.MockTransport(handle),
    ) as api:
        assert api.begin_preview_upload(project_id="project_1", file_id="file_1") == session
        fresh = api.reset_preview_upload(
            project_id="project_1", file_id="file_1", expected_preview_id="preview_1",
        )
        assert fresh["previewId"] == "preview_2"
        api.put_preview_manifest(
            project_id="project_1", file_id="file_1", manifest=manifest,
        )
        api.complete_preview_upload(project_id="project_1", file_id="file_1")
    assert [request.url.path for request in requests] == [
        "/api/projects/project_1/files/file_1/preview-upload",
        "/api/projects/project_1/files/file_1/preview-upload/reset",
        "/api/projects/project_1/files/file_1/preview-upload/manifest",
        "/api/projects/project_1/files/file_1/preview-upload/completion",
    ]
    assert all(
        request.headers["Arteligo-Transfer-Continuation"] == "c" * 43
        and "authorization" not in request.headers
        for request in requests
    )
    assert json.loads(requests[1].content) == {"expectedPreviewId": "preview_1"}
    assert json.loads(requests[2].content) == manifest


def test_control_request_total_deadline_includes_dribbling_response_parse() -> None:
    payload = json.dumps(
        {
            "capability": {
                "contract": "arteligo.railway-bucket-capability",
                "v": 1,
                "operation": "GET",
                "objectId": "object_1",
                "chunkIndex": 0,
                "expiresAt": "2030-01-01T00:00:00Z",
                "contentLength": 21,
                "url": "https://bucket.example/chunk",
                "headers": {},
            }
        }
    ).encode()

    class DribblingStream(httpx.SyncByteStream):
        def __iter__(self) -> Any:
            for offset in range(0, len(payload), 8):
                time.sleep(0.01)
                yield payload[offset : offset + 8]

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, stream=DribblingStream())

    started = time.monotonic()
    with (
        pytest.raises(TransferTimeoutError) as captured,
        ArteligoTransferAPI(
            control_origin="https://arteligo.example",
            continuation="c" * 43,
            timeouts=TransferTimeouts(connect=0.05, read=0.05, total=0.05),
            control_transport=httpx.MockTransport(handle),
        ) as api,
    ):
        api.read_capability(
            project_id="project_1",
            object_id="object_1",
            chunk_index=0,
        )
    assert time.monotonic() - started < 0.25
    assert captured.value.wire_value() == {
        "error": {
            "code": "timeout",
            "message": "direct transfer deadline elapsed",
            "recoverable": True,
        }
    }


def test_later_chunk_failure_writes_nothing_to_nonseekable_destination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class API:
        def __init__(self, **kwargs: object) -> None:
            pass

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            pass

    class NonseekableDestination:
        def __init__(self) -> None:
            self.value = bytearray()

        def write(self, value: bytes) -> int:
            self.value.extend(value)
            return len(value)

    chunks = [SimpleNamespace(index=0), SimpleNamespace(index=1)]
    plan = SimpleNamespace(
        chunks=chunks,
        object_id="object_1",
        plaintext_size=2,
        open_chunk=lambda ciphertext, index: ciphertext,
    )
    calls = 0

    def download_chunk(*args: object, **kwargs: object) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise TransferError("later chunk failed")
        return b"a"

    monkeypatch.setattr(_workflow, "ArteligoTransferAPI", API)
    monkeypatch.setattr(_workflow, "_download_ciphertext_chunk", download_chunk)
    destination = NonseekableDestination()

    with pytest.raises(TransferError, match="later chunk failed"):
        _workflow._download(
            SimpleNamespace(
                control_origin="https://arteligo.example",
                continuation="c" * 43,
                project_id="project_1",
            ),
            destination,
            plan,
            DEFAULT_TIMEOUTS,
            _workflow.DEFAULT_TRANSPORT,
            None,
        )

    assert calls == 2
    assert destination.value == b""


def test_claim_expiry_prevents_any_transfer_engine_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = _upload_handoff()
    value["keyClaim"]["expiresAtUnixMilliseconds"] = "1"
    started = False

    def unexpected(*args: object, **kwargs: object) -> object:
        nonlocal started
        started = True
        raise AssertionError("claim redemption must not start")

    monkeypatch.setattr(_workflow, "redeem_file_key_claim", unexpected)
    with pytest.raises(TransferError) as captured:
        _workflow.upload_file(value, source=io.BytesIO(b"hello"))
    assert captured.value.code == "claim_expired"
    assert captured.value.recoverable
    assert not started


def test_claim_expiry_is_rechecked_immediately_before_redemption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = _upload_handoff()
    value["keyClaim"]["expiresAtUnixMilliseconds"] = "2000"
    descriptor = parse_handoff(value, now_unix_milliseconds=1000).key_claim
    secret = value["keyClaim"]["url"].rsplit("#", 1)[1]
    assert secret not in repr(descriptor)

    calls = 0

    def unexpected(*args: object, **kwargs: object) -> bytes:
        nonlocal calls
        calls += 1
        raise AssertionError("expired claim must not reach the transport")

    monkeypatch.setattr(_claim.time, "time", lambda: 2.0)
    monkeypatch.setattr(_claim, "post_control_json", unexpected)
    with pytest.raises(TransferError) as captured:
        _claim.redeem_file_key_claim(
            descriptor,
            expected_direction="upload",
            expected_project_id="project_1",
            expected_object_id="upload_1",
            expected_epoch=7,
        )
    assert captured.value.code == "claim_expired"
    assert captured.value.recoverable
    assert secret not in str(captured.value)
    assert calls == 0






def test_cli_rejects_duplicate_handoff_fields_before_engine_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    class Input:
        buffer = io.BytesIO(b'{"operation":"upload","operation":"upload"}')

    def unexpected(*args: object, **kwargs: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("engine must not start")

    monkeypatch.setattr(_cli.sys, "stdin", Input())
    monkeypatch.setattr(_cli, "upload_file", unexpected)
    assert _cli.main(["upload", "--source", "/tmp/source"]) == 1
    assert not called


def test_preview_aad_preserves_persisted_format_encoding() -> None:
    actual = preview_chunk_aad(
        project_id="project_1",
        source_object_id="source_1",
        processing_id="processing_1",
        preview_id="preview_1",
        job_id="job_1",
        total_plaintext_size=5,
        chunk_size=CHUNK_SIZE,
        chunk_count=1,
        chunk_index=0,
        plaintext_offset=0,
        plaintext_length=5,
        final=True,
    )
    expected = bytearray()
    for value in (
        "audaligo:managed:file-preview:chunk-aead:v1",
        "project_1",
        "source_1",
        "processing_1",
        "preview_1",
        "job_1",
    ):
        encoded = value.encode()
        expected.extend(struct.pack(">H", len(encoded)))
        expected.extend(encoded)
        if value.endswith(":v1"):
            expected.extend(b"\x01")
    expected.extend(struct.pack(">Q", 5))
    expected.extend(struct.pack(">I", CHUNK_SIZE))
    expected.extend(struct.pack(">I", 1))
    expected.extend(struct.pack(">I", 0))
    expected.extend(struct.pack(">Q", 0))
    expected.extend(struct.pack(">I", 5))
    expected.extend(b"\x01")
    assert actual == bytes(expected)


@pytest.mark.parametrize(
    ("media_type", "codec"),
    [
        ("audio/webm", "mp4a.40.2"),
        ("video/webm", "opus"),
        ("audio/mp4", "avc1.640028"),
        ("video/mp4", "mp4a.40.2"),
        ("video/mp4", "avc1.invalid"),
    ],
)
def test_preview_handoff_rejects_mismatched_media_tuple(
    media_type: str, codec: str
) -> None:
    handoff = _preview_handoff()
    handoff["manifest"]["mediaType"] = media_type
    handoff["manifest"]["codec"] = codec
    with pytest.raises(TransferError, match="preview manifest contract"):
        parse_handoff(handoff, now_unix_milliseconds=1)


@pytest.mark.parametrize(
    ("media_type", "codec"),
    [
        ("audio/mp4", "mp4a.40.2"),
        ("audio/webm", "opus"),
        ("video/mp4", "avc1.640028, mp4a.40.2"),
    ],
)
def test_preview_plan_authenticates_approved_preview_fields(
    media_type: str, codec: str
) -> None:
    cleartext = b"audio"
    key = bytes(range(1, 33))
    nonce_base = b"12345678"
    aad = preview_chunk_aad(
        project_id="project_1",
        source_object_id="source_1",
        processing_id="processing_1",
        preview_id="preview_1",
        job_id="job_1",
        total_plaintext_size=len(cleartext),
        chunk_size=CHUNK_SIZE,
        chunk_count=1,
        chunk_index=0,
        plaintext_offset=0,
        plaintext_length=len(cleartext),
        final=True,
    )
    ciphertext = AESGCM(key).encrypt(nonce_base + struct.pack(">I", 0), cleartext, aad)
    manifest = _preview_manifest(ciphertext, media_type=media_type, codec=codec)
    wire_handoff = _preview_handoff()
    wire_handoff["manifest"] = manifest
    parsed_handoff = parse_handoff(wire_handoff, now_unix_milliseconds=1)
    assert parsed_handoff.manifest is not None
    plan = parse_preview_decryption_plan(
        parsed_handoff.manifest,
        project_id="project_1",
        preview_id="preview_1",
        epoch=7,
        data_key=key,
    )
    assert plan.open_chunk(ciphertext, 0) == cleartext

    changed = dict(manifest)
    changed["jobId"] = "other_job"
    changed_plan = parse_preview_decryption_plan(
        changed,
        project_id="project_1",
        preview_id="preview_1",
        epoch=7,
        data_key=key,
    )
    with pytest.raises(Exception, match="authentication failed"):
        changed_plan.open_chunk(ciphertext, 0)


def test_download_reacquires_only_rejected_get_capability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chunk = ChunkMetadata(
        index=0,
        ciphertext_offset=0,
        ciphertext_sha256=sha256(b"ciphertext").digest(),
        ciphertext_size=10,
        final=True,
        plaintext_offset=0,
        plaintext_size=1,
    )

    class API:
        calls = 0

        def read_capability(self, **kwargs: object) -> dict[str, object]:
            self.calls += 1
            return {
                "operation": "GET",
                "objectId": "object_1",
                "chunkIndex": 0,
                "contentLength": 10,
                "url": "https://bucket.example/chunk",
                "headers": {},
            }

    attempts = 0

    def get(*args: object, **kwargs: object) -> bytes:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise TransferHTTPError(403)
        return b"ciphertext"

    api = API()
    monkeypatch.setattr(_workflow, "get_ciphertext", get)
    assert (
        _workflow._download_ciphertext_chunk(
            api,  # type: ignore[arg-type]
            project_id="project_1",
            object_id="object_1",
            chunk=chunk,
            timeouts=DEFAULT_TIMEOUTS,
            transport=_workflow.DEFAULT_TRANSPORT,
        )
        == b"ciphertext"
    )
    assert api.calls == attempts == 2


def test_upload_stops_after_first_bucket_put_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    put_count = 0
    completed = False
    committed = False

    class BucketHandler(BaseHTTPRequestHandler):
        def do_PUT(self) -> None:
            nonlocal put_count
            put_count += 1
            length = int(self.headers["Content-Length"])
            self.rfile.read(length)
            self.send_response(403)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), BucketHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    class API:
        def __init__(self, **kwargs: object) -> None:
            pass

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def put_manifest(self, **kwargs: object) -> dict[str, str]:
            return {"state": "uploading"}

        def upload_capability(self, **kwargs: object) -> dict[str, object]:
            return {
                "operation": "PUT",
                "objectId": "upload_1",
                "chunkIndex": 0,
                "contentLength": 21,
                "url": f"http://127.0.0.1:{server.server_port}/bucket/chunk",
                "headers": {},
            }

        def complete_upload(self, **kwargs: object) -> dict[str, object]:
            nonlocal completed
            completed = True
            return {}

        def commit_file(self, **kwargs: object) -> dict[str, object]:
            nonlocal committed
            committed = True
            return {}

    monkeypatch.setattr(_workflow, "ArteligoTransferAPI", API)
    monkeypatch.setattr(
        _workflow,
        "redeem_file_key_claim",
        lambda *args, **kwargs: FileKeyClaim(
            direction="upload",
            project_id="project_1",
            object_id="upload_1",
            epoch=7,
            data_key=bytes(range(1, 33)),
            wrapped_nonce=b"n" * 12,
            wrapped_data_key=b"k" * 48,
        ),
    )
    try:
        with pytest.raises(TransferHTTPError) as captured:
            _workflow.upload_file(_upload_handoff(), source=io.BytesIO(b"hello"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert captured.value.status == 403
    assert put_count == 1
    assert not completed
    assert not committed


def _upload_handoff() -> dict[str, Any]:
    return {
        "operation": "upload",
        "projectId": "project_1",
        "objectId": "upload_1",
        "epoch": "7",
        "keyClaim": _key_claim(),
        "continuation": "c" * 43,
        "controlOrigin": "https://arteligo.example",
        "protocolVersion": "arteligo.encrypted-transfer.v1",
        "upload": {
            "filename": "recording.wav",
            "plaintextSize": "5",
            "operationId": "00000000-0000-4000-8000-000000000001",
        },
    }


def _file_handoff() -> dict[str, Any]:
    digest = _b64u(sha256(b"ciphertext").digest())
    return {
        "operation": "file_download",
        "projectId": "project_1",
        "objectId": "object_1",
        "epoch": "7",
        "keyClaim": _key_claim(),
        "continuation": "c" * 43,
        "controlOrigin": "https://arteligo.example",
        "protocolVersion": "arteligo.encrypted-transfer.v1",
        "file": {
            "projectId": "project_1",
            "fileId": "file_1",
            "entryId": "entry_1",
            "objectId": "object_1",
            "filename": "recording.wav",
            "plaintextSize": "5",
            "mediaType": "audio/wav",
            "createdAtUnixMilliseconds": "1000",
            "updatedAtUnixMilliseconds": "1000",
        },
        "manifest": {
            "version": 1,
            "type": "audaligo.managed-encrypted-object-manifest",
            "suiteId": "aes-256-gcm-audaligo-v1",
            "encryptionMode": "managed-project-key",
            "contentKeyAlgorithm": "A256GCM",
            "wrapAlgorithm": "a256gcm-project-epoch-v1",
            "shareId": "project_file_managed_v1",
            "fileId": "file_1",
            "nonceBase64url": _b64u(b"12345678"),
            "plaintextSize": "5",
            "ciphertextSize": "21",
            "chunkSize": CHUNK_SIZE,
            "chunks": [
                {
                    "chunkIndex": 0,
                    "plaintextOffset": "0",
                    "plaintextSize": "5",
                    "ciphertextOffset": "0",
                    "ciphertextSize": "21",
                    "ciphertextSha256Base64url": digest,
                    "finalChunk": True,
                }
            ],
        },
    }


def _preview_handoff() -> dict[str, Any]:
    value = _file_handoff()
    value["operation"] = "preview_download"
    value["objectId"] = "preview_1"
    del value["file"]
    value["preview"] = {
        "fileId": "file_1",
        "previewId": "preview_1",
        "state": "ready",
    }
    value["manifest"] = _preview_manifest(b"ciphertext-cipher")
    return value


def _preview_manifest(
    ciphertext: bytes,
    *,
    media_type: str = "audio/mp4",
    codec: str = "mp4a.40.2",
) -> dict[str, Any]:
    return {
        "contract": "audaligo.preview.read.v1",
        "sourceObjectId": "source_1",
        "processingId": "processing_1",
        "jobId": "job_1",
        "mediaType": media_type,
        "codec": codec,
        "nonceBase64url": _b64u(b"12345678"),
        "plaintextSize": len(ciphertext) - 16,
        "ciphertextSize": len(ciphertext),
        "chunkSize": CHUNK_SIZE,
        "chunks": [
            {
                "chunkIndex": 0,
                "plaintextOffset": 0,
                "plaintextSize": len(ciphertext) - 16,
                "ciphertextOffset": 0,
                "ciphertextSize": len(ciphertext),
                "ciphertextSha256Base64url": _b64u(sha256(ciphertext).digest()),
                "finalChunk": True,
            }
        ],
    }


def _key_claim() -> dict[str, Any]:
    return {
        "url": f"https://arteligo.example/claims/key#{'a' * 43}",
        "expiresAtUnixMilliseconds": "4102444800000",
        "protocol": "arteligo.file-key-claim.v1",
    }


def _b64u(value: bytes) -> str:
    return urlsafe_b64encode(value).decode().rstrip("=")
