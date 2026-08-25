from __future__ import annotations

import io
import json
import struct
from base64 import urlsafe_b64encode
from hashlib import sha256
from pathlib import Path
from typing import Any

import httpx
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from soenan_audaligo_support.transfer import _cli, _workflow
from soenan_audaligo_support.transfer._api import AudaligoTransferAPI
from soenan_audaligo_support.transfer._crypto import (
    CHUNK_SIZE,
    ChunkMetadata,
    parse_preview_decryption_plan,
    preview_chunk_aad,
)
from soenan_audaligo_support.transfer._handoff import parse_handoff
from soenan_audaligo_support.transfer._http import (
    DEFAULT_TIMEOUTS,
    TransferError,
    TransferHTTPError,
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


def test_handoff_rejects_wrong_protocol_origin_binding_and_expired_claim() -> None:
    valid = _upload_handoff()
    variants = (
        {**valid, "protocolVersion": "audaligo.encrypted-transfer.v2"},
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
                    "contract": "audaligo.railway-bucket-capability",
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

    with AudaligoTransferAPI(
        control_origin="https://audaligo.example",
        continuation="c" * 43,
        timeouts=DEFAULT_TIMEOUTS,
        control_transport=httpx.MockTransport(handle),
    ) as api:
        api.read_capability(project_id="project_1", object_id="object_1", chunk_index=0)

    assert len(requests) == 1
    assert "authorization" not in requests[0].headers
    assert requests[0].headers["Audaligo-Transfer-Continuation"] == "c" * 43


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


def test_cli_passes_stdin_handoff_unchanged_to_public_engine(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    handoff = _upload_handoff()
    raw = json.dumps(handoff).encode()
    captured: dict[str, Any] = {}

    class Input:
        buffer = io.BytesIO(raw)

    def upload(structured_content: dict[str, Any], *, source: Path) -> dict[str, Any]:
        captured["handoff"] = structured_content
        captured["source"] = source
        return {"file": {"fileId": "file_1"}}

    monkeypatch.setattr(_cli.sys, "stdin", Input())
    monkeypatch.setattr(_cli, "upload_file", upload)
    assert _cli.main(["upload", "--source", "/tmp/source.wav"]) == 0
    assert captured == {"handoff": handoff, "source": Path("/tmp/source.wav")}
    assert json.loads(capsys.readouterr().out) == {"file": {"fileId": "file_1"}}


def test_cli_and_api_share_recoverable_error_taxonomy(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    handoff = _file_handoff()
    error = TransferError(
        "file key claim is unavailable",
        code="claim_unavailable",
        recoverable=True,
    )

    class Input:
        buffer = io.BytesIO(json.dumps(handoff).encode())

    def fail(*args: object, **kwargs: object) -> int:
        raise error

    monkeypatch.setattr(_cli.sys, "stdin", Input())
    monkeypatch.setattr(_cli, "download_file", fail)
    assert _cli.main(["download", "--destination", "/tmp/file"]) == 1
    assert json.loads(capsys.readouterr().err) == error.wire_value()


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


def test_preview_aad_matches_audaligo_ordered_encoding() -> None:
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


def test_preview_plan_authenticates_approved_preview_fields() -> None:
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
    manifest = _preview_manifest(ciphertext)
    plan = parse_preview_decryption_plan(
        manifest,
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


def test_upload_never_retries_after_bucket_put_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def put(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        raise TransferHTTPError(403)

    monkeypatch.setattr(_workflow, "put_ciphertext", put)
    assert calls == 0
    with pytest.raises(TransferHTTPError):
        put("https://bucket.example", {}, b"ciphertext")
    assert calls == 1


def test_error_wire_values_do_not_disclose_authority() -> None:
    secret = "s" * 43
    error = TransferError(
        "file key claim is unavailable",
        code="claim_unavailable",
        recoverable=True,
    )
    encoded = json.dumps(error.wire_value())
    assert secret not in encoded
    assert "https://" not in encoded
    assert encoded == (
        '{"error": {"code": "claim_unavailable", '
        '"message": "file key claim is unavailable", "recoverable": true}}'
    )


def _upload_handoff() -> dict[str, Any]:
    return {
        "operation": "upload",
        "projectId": "project_1",
        "objectId": "upload_1",
        "epoch": "7",
        "keyClaim": _key_claim(),
        "continuation": "c" * 43,
        "controlOrigin": "https://audaligo.example",
        "protocolVersion": "audaligo.encrypted-transfer.v1",
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
        "controlOrigin": "https://audaligo.example",
        "protocolVersion": "audaligo.encrypted-transfer.v1",
        "file": {
            "projectId": "project_1",
            "fileId": "file_1",
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


def _preview_manifest(ciphertext: bytes) -> dict[str, Any]:
    return {
        "contract": "audaligo.managed-preview-read-descriptor",
        "sourceObjectId": "source_1",
        "processingId": "processing_1",
        "jobId": "job_1",
        "mediaType": "audio/mp4",
        "codec": "mp4a.40.2",
        "bitrateBps": 128_000,
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
        "url": f"https://audaligo.example/claims/key#{'a' * 43}",
        "expiresAtUnixMilliseconds": "4102444800000",
        "protocol": "audaligo.file-key-claim.v1",
    }


def _b64u(value: bytes) -> str:
    return urlsafe_b64encode(value).decode().rstrip("=")
