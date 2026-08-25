from __future__ import annotations

import asyncio
import io
import json
import ssl
import threading
import time
from base64 import urlsafe_b64encode
from collections.abc import Mapping
from contextlib import nullcontext
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import httpx
import pytest
from audaligo_public_api_client.models.bucket_capability import BucketCapability
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from soenan_audaligo_support.transfer import (
    AudaligoTransferAPI,
    TransferError,
    TransferTimeoutError,
    TransferTimeouts,
    TransferTransport,
    _api,
    _claim,
    _cli,
    _http,
    download_file,
    upload_file,
)
from soenan_audaligo_support.transfer._crypto import (
    CHUNK_SIZE,
    MAXIMUM_CHUNKS,
    MAXIMUM_WIRE_INTEGER,
    EncryptionContractError,
    build_encryption_plan,
    chunk_aad,
    chunk_nonce,
    parse_decryption_plan,
)
from soenan_audaligo_support.transfer._http import put_ciphertext


@pytest.fixture
def bucket() -> tuple[str, dict[str, bytes], dict[str, dict[str, object]]]:
    objects: dict[str, bytes] = {}
    claims: dict[str, dict[str, object]] = {}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_PUT(self) -> None:
            length = int(self.headers["Content-Length"])
            objects[self.path] = self.rfile.read(length)
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self) -> None:
            value = objects[self.path]
            self.send_response(200)
            self.send_header("Content-Length", str(len(value)))
            self.end_headers()
            self.wfile.write(value)

        def do_POST(self) -> None:
            assert self.headers["audaligo-key-claim"] == "a" * 43
            value = claims.pop(self.path)
            encoded = json.dumps(value, separators=(",", ":")).encode("ascii")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", objects, claims
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_managed_chunk_encryption_matches_audaligo_vector() -> None:
    key = bytes.fromhex(
        "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
    )
    nonce_base = bytes.fromhex("0102030405060708")
    plaintext = bytes.fromhex("68656c6c6f20776f726c64")
    aad = chunk_aad(
        project_id="project_123",
        file_id="file_123",
        object_id="object_123",
        epoch=7,
        total_plaintext_size=11,
        chunk_count=1,
        chunk_index=0,
        plaintext_offset=0,
        plaintext_length=11,
        final=True,
    )

    assert chunk_nonce(nonce_base, 0).hex() == "010203040506070800000000"
    assert aad.hex() == (
        "001e617564616c69676f3a6d616e616765643a6368756e6b2d616561643a7631"
        "01000100176165732d3235362d67636d2d617564616c69676f2d7631000b7072"
        "6f6a6563745f313233001770726f6a6563745f66696c655f6d616e616765645f"
        "7631000866696c655f3132330000000000000007000a6f626a6563745f313233"
        "000000000000000b00800000000000010000000000000000000000000000000b01"
    )
    ciphertext = AESGCM(key).encrypt(chunk_nonce(nonce_base, 0), plaintext, aad)
    assert ciphertext.hex() == "3e7bf028024103387e74441035931da74f49d51a62099ab7ade31c"
    assert sha256(ciphertext).hexdigest() == (
        "e91438ee31fa9cd996cff6e6d3a3507d4488f73cb378bb5a34cf8c28913c6c08"
    )


def test_generated_client_parses_rfc3339_utc_z() -> None:
    capability = BucketCapability.from_dict(
        {
            "contract": "audaligo.railway-bucket-capability",
            "v": 1,
            "operation": "PUT",
            "objectId": "upload_123",
            "chunkIndex": 0,
            "expiresAt": "2026-07-30T00:00:00Z",
            "contentLength": 17,
            "url": "https://bucket.example/upload",
            "headers": {},
        }
    )

    assert capability.expires_at.isoformat() == "2026-07-30T00:00:00+00:00"


def test_encryption_plan_is_stable_for_operation_replay() -> None:
    plaintext = b"replayed upload"
    arguments = {
        "project_id": "project_123",
        "file_id": "operation_123",
        "object_id": "upload_123",
        "epoch": 7,
        "data_key": bytes(range(1, 33)),
        "wrapped_nonce": bytes(range(1, 13)),
        "wrapped_data_key": bytes(range(33, 81)),
        "plaintext_size": len(plaintext),
    }
    first = build_encryption_plan(io.BytesIO(plaintext), **arguments)
    replay = build_encryption_plan(io.BytesIO(plaintext), **arguments)

    assert first.manifest() == replay.manifest()
    assert first.seal_chunk(plaintext, 0) == replay.seal_chunk(plaintext, 0)


def test_capability_plaintext_requires_loopback() -> None:
    with pytest.raises(TransferError, match="must use HTTPS"):
        put_ciphertext(
            "http://bucket.example/upload?signature=secret",
            {},
            b"ciphertext",
            timeouts=TransferTimeouts(connect=1, read=1, total=1),
            transport=TransferTransport(),
        )


def test_api_allows_plaintext_only_for_exact_loopback_hosts() -> None:
    for endpoint in (
        "http://localhost.attacker.example",
        "http://127.0.0.1.attacker.example",
        "http://user@localhost",
    ):
        with pytest.raises(ValueError):
            AudaligoTransferAPI(
                base_url=endpoint,
                access_token="a" * 43,
                timeouts=TransferTimeouts(connect=1, read=1, total=1),
            )
    for endpoint in ("https://", "https://audaligo.example:invalid"):
        with pytest.raises(ValueError):
            AudaligoTransferAPI(
                base_url=endpoint,
                access_token="a" * 43,
                timeouts=TransferTimeouts(connect=1, read=1, total=1),
            )


def test_api_translates_generated_transport_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unavailable(*args: object, **arguments: object) -> object:
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(
        _api.create_encrypted_object_upload,
        "asyncio_detailed",
        unavailable,
    )
    with (
        AudaligoTransferAPI(
            base_url="https://audaligo.example",
            access_token="a" * 43,
            timeouts=TransferTimeouts(connect=1, read=1, total=1),
        ) as api,
        pytest.raises(TransferError, match="Audaligo API request failed"),
    ):
        api.begin_upload(
            project_id="project_123",
            operation_id="operation_123",
            mix_version_id=None,
            filename="mix.wav",
            plaintext_size=4096,
        )


def test_timed_out_control_mutation_is_cancelled_before_return_and_worker_joins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cancelled = threading.Event()
    mutated = threading.Event()

    async def slow_mutation(*args: object, **arguments: object) -> object:
        try:
            await asyncio.sleep(0.2)
            mutated.set()
            return object()
        finally:
            cancelled.set()

    monkeypatch.setattr(
        _api.create_encrypted_object_upload,
        "asyncio_detailed",
        slow_mutation,
    )
    api = AudaligoTransferAPI(
        base_url="https://audaligo.example",
        access_token="a" * 43,
        timeouts=TransferTimeouts(connect=1, read=1, total=0.02),
    )
    worker = api._thread
    started = time.monotonic()
    with api:
        with pytest.raises(TransferTimeoutError):
            api.begin_upload(
                project_id="project_123",
                operation_id="operation_123",
                mix_version_id=None,
                filename="mix.wav",
                plaintext_size=4096,
            )
        assert cancelled.is_set()
        assert not mutated.is_set()
        time.sleep(0.05)
        assert not mutated.is_set()
    assert time.monotonic() - started < 0.15
    assert not worker.is_alive()


def test_api_translates_generated_response_parsing_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def malformed(*args: object, **arguments: object) -> object:
        raise AttributeError("timestamp was not a string")

    monkeypatch.setattr(
        _api.create_encrypted_object_upload,
        "asyncio_detailed",
        malformed,
    )
    with (
        AudaligoTransferAPI(
            base_url="https://audaligo.example",
            access_token="a" * 43,
            timeouts=TransferTimeouts(connect=1, read=1, total=1),
        ) as api,
        pytest.raises(TransferError, match="Audaligo API request failed"),
    ):
        api.begin_upload(
            project_id="project_123",
            operation_id="operation_123",
            mix_version_id=None,
            filename="mix.wav",
            plaintext_size=4096,
        )


def test_api_context_closes_the_async_control_transport() -> None:
    class RecordingTransport(httpx.MockTransport):
        closed = False

        async def aclose(self) -> None:
            self.closed = True
            await super().aclose()

    transport = RecordingTransport(lambda request: httpx.Response(204))
    with AudaligoTransferAPI(
        base_url="https://audaligo.example",
        access_token="a" * 43,
        timeouts=TransferTimeouts(connect=1, read=1, total=1),
        control_transport=transport,
    ):
        pass
    assert transport.closed


def test_managed_processing_read_descriptor_is_locally_decryptable() -> None:
    manifest = _api._manifest_from_descriptor(
        {
            "object": {
                "securityScope": "managed_processing",
                "chunks": [],
            },
            "wrappedDataKey": {},
        }
    )

    assert manifest["object"]["chunks"] == []


def test_key_claim_accepts_ipv6_loopback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    encoded = json.dumps(
        _key_claim(
            "upload",
            bytes(range(1, 33)),
            bytes(range(1, 13)),
            bytes(range(33, 81)),
        )
    ).encode("ascii")
    monkeypatch.setattr(_claim, "post_control_json", lambda *args, **kwargs: encoded)

    claim = _claim.redeem_file_key_claim(
        {
            "url": f"http://[::1]/claims/upload#{'a' * 43}",
            "expiresAtUnixMilliseconds": 4_102_444_800_000,
            "protocol": "audaligo.file-key-claim.v1",
        },
        expected_direction="upload",
        expected_project_id="project_123",
        expected_object_id="upload_123",
        expected_epoch=0,
    )
    assert claim.data_key == bytes(range(1, 33))


def test_key_claim_accepts_an_all_zero_wrapped_nonce(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    encoded = json.dumps(
        _key_claim(
            "upload",
            bytes(range(1, 33)),
            bytes(12),
            bytes(48),
        )
    ).encode("ascii")
    monkeypatch.setattr(_claim, "post_control_json", lambda *args, **kwargs: encoded)

    claim = _claim.redeem_file_key_claim(
        _key_claim_descriptor("http://127.0.0.1", "upload"),
        expected_direction="upload",
        expected_project_id="project_123",
        expected_object_id="upload_123",
        expected_epoch=0,
    )

    assert claim.wrapped_nonce == bytes(12)
    assert claim.wrapped_data_key == bytes(48)


def test_key_claim_requires_the_data_key_itself_to_be_nonzero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    encoded = json.dumps(
        _key_claim(
            "upload",
            bytes(32),
            bytes(12),
            bytes(48),
        )
    ).encode("ascii")
    monkeypatch.setattr(_claim, "post_control_json", lambda *args, **kwargs: encoded)

    with pytest.raises(TransferError, match="key material is invalid"):
        _claim.redeem_file_key_claim(
            _key_claim_descriptor("http://127.0.0.1", "upload"),
            expected_direction="upload",
            expected_project_id="project_123",
            expected_object_id="upload_123",
            expected_epoch=0,
        )


def test_key_claim_rejects_wrapped_ciphertext_with_the_wrong_length(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    encoded = json.dumps(
        _key_claim(
            "upload",
            bytes(range(1, 33)),
            bytes(12),
            bytes(47),
        )
    ).encode("ascii")
    monkeypatch.setattr(_claim, "post_control_json", lambda *args, **kwargs: encoded)

    with pytest.raises(TransferError, match="key material is invalid"):
        _claim.redeem_file_key_claim(
            _key_claim_descriptor("http://127.0.0.1", "upload"),
            expected_direction="upload",
            expected_project_id="project_123",
            expected_object_id="upload_123",
            expected_epoch=0,
        )


def test_claim_response_read_enforces_the_total_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Socket:
        def settimeout(self, timeout: float) -> None:
            pass

    class Response:
        status = 200

        def read1(self, size: int) -> bytes:
            time.sleep(0.02)
            return b"x"

        def close(self) -> None:
            pass

    class Connection:
        sock = Socket()

        def connect(self) -> None:
            pass

        def putrequest(self, *args: object, **arguments: object) -> None:
            pass

        def putheader(self, *args: object) -> None:
            pass

        def endheaders(self) -> None:
            pass

        def send(self, body: bytes) -> None:
            pass

        def getresponse(self) -> Response:
            return Response()

        def close(self) -> None:
            pass

    monkeypatch.setattr(_http, "_connection", lambda *args: Connection())
    with pytest.raises(TransferTimeoutError):
        _http.post_control_json(
            "http://127.0.0.1/claim",
            {"audaligo-key-claim": "a" * 43},
            maximum_response_bytes=1_024,
            timeouts=TransferTimeouts(connect=1, read=1, total=0.03),
            transport=TransferTransport(),
        )


def test_tls_construction_failures_are_sanitized_as_transfer_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_tls_setup(*args: object, **kwargs: object) -> object:
        raise ssl.SSLError("private TLS setup detail")

    monkeypatch.setattr(_http, "_connection", fail_tls_setup)
    timeouts = TransferTimeouts(connect=1, read=1, total=1)
    transport = TransferTransport()
    operations = (
        (
            lambda: _http.put_ciphertext(
                "https://bucket.example/object",
                {},
                b"x",
                timeouts=timeouts,
                transport=transport,
            ),
            "direct Bucket upload failed",
        ),
        (
            lambda: _http.get_ciphertext(
                "https://bucket.example/object",
                {},
                1,
                timeouts=timeouts,
                transport=transport,
            ),
            "direct Bucket download failed",
        ),
        (
            lambda: _http.post_control_json(
                "https://audaligo.example/claim",
                {"audaligo-key-claim": "a" * 43},
                maximum_response_bytes=1024,
                timeouts=timeouts,
                transport=transport,
            ),
            "key claim redemption failed",
        ),
    )

    for operation, message in operations:
        with pytest.raises(TransferError, match=message) as caught:
            operation()
        assert "private TLS setup detail" not in str(caught.value)


def test_ipv6_authority_is_bracketed_and_malformed_urls_are_sanitized() -> None:
    parsed = _http._parse_url("http://[::1]:8081/claim", TransferTransport())
    assert _http._authority(parsed) == "[::1]:8081"
    with pytest.raises(TransferError, match="URL is invalid"):
        _http._parse_url("http://[::1", TransferTransport())
    with pytest.raises(TransferError, match="claim URL is invalid"):
        _claim.redeem_file_key_claim(
            {
                "url": f"http://[::1/claim#{'a' * 43}",
                "expiresAtUnixMilliseconds": 4_102_444_800_000,
                "protocol": "audaligo.file-key-claim.v1",
            },
            expected_direction="upload",
            expected_project_id="project_123",
            expected_object_id="upload_123",
            expected_epoch=0,
        )


def test_epoch_rejects_values_outside_the_wire_integer_contract() -> None:
    with pytest.raises(EncryptionContractError, match="canonical wire integer"):
        build_encryption_plan(
            io.BytesIO(b"x"),
            project_id="project_123",
            file_id="file_123",
            object_id="upload_123",
            epoch=MAXIMUM_WIRE_INTEGER + 1,
            data_key=bytes(range(1, 33)),
            wrapped_nonce=bytes(range(1, 13)),
            wrapped_data_key=bytes(range(33, 81)),
            plaintext_size=1,
        )


def test_decryption_uses_the_validated_manifest_chunk_size_for_layout_and_aad() -> None:
    plaintext = b"variable chunk manifest"
    chunk_size = 4
    chunk_count = (len(plaintext) + chunk_size - 1) // chunk_size
    data_key = bytes(range(1, 33))
    nonce_base = bytes(range(1, 9))
    chunks: list[dict[str, object]] = []
    ciphertext_chunks: list[bytes] = []
    plaintext_offset = 0
    ciphertext_offset = 0
    for index in range(chunk_count):
        cleartext = plaintext[plaintext_offset : plaintext_offset + chunk_size]
        final = index + 1 == chunk_count
        ciphertext = AESGCM(data_key).encrypt(
            chunk_nonce(nonce_base, index),
            cleartext,
            chunk_aad(
                project_id="project_123",
                file_id="file_123",
                object_id="object_123",
                epoch=7,
                total_plaintext_size=len(plaintext),
                chunk_count=chunk_count,
                chunk_size=chunk_size,
                chunk_index=index,
                plaintext_offset=plaintext_offset,
                plaintext_length=len(cleartext),
                final=final,
            ),
        )
        chunks.append(
            {
                "chunk_index": index,
                "ciphertext_offset": ciphertext_offset,
                "ciphertext_sha256_b64u": _b64url(sha256(ciphertext).digest()),
                "ciphertext_size": len(ciphertext),
                "final_chunk": final,
                "plaintext_offset": plaintext_offset,
                "plaintext_size": len(cleartext),
            }
        )
        ciphertext_chunks.append(ciphertext)
        plaintext_offset += len(cleartext)
        ciphertext_offset += len(ciphertext)
    wrapped_nonce = bytes(12)
    wrapped_data_key = bytes(48)
    manifest = {
        "v": 1,
        "type": "audaligo.managed-encrypted-object-manifest",
        "suite_id": "aes-256-gcm-audaligo-v1",
        "encryption": {
            "mode": "managed-project-key",
            "content_key_alg": "A256GCM",
            "wrap_alg": "a256gcm-project-epoch-v1",
            "wrapped_data_key": {
                "nonceB64u": _b64url(wrapped_nonce),
                "ciphertextB64u": _b64url(wrapped_data_key),
            },
        },
        "object": {
            "chunk_count": chunk_count,
            "chunk_size": chunk_size,
            "chunks": chunks,
            "ciphertext_size": ciphertext_offset,
            "epoch": 7,
            "file_id": "file_123",
            "nonce_base_b64u": _b64url(nonce_base),
            "object_id": "object_123",
            "plaintext_size": len(plaintext),
            "project_id": "project_123",
            "share_id": "project_file_managed_v1",
        },
    }

    plan = parse_decryption_plan(
        manifest,
        data_key=data_key,
        wrapped_nonce=wrapped_nonce,
        wrapped_data_key=wrapped_data_key,
    )

    assert plan.chunk_size == chunk_size
    assert (
        b"".join(
            plan.open_chunk(ciphertext, index)
            for index, ciphertext in enumerate(ciphertext_chunks)
        )
        == plaintext
    )


def test_upload_size_is_rejected_before_beginning_remote_state() -> None:
    class OversizedSource:
        position = 0

        def tell(self) -> int:
            return self.position

        def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
            self.position = (
                CHUNK_SIZE * MAXIMUM_CHUNKS + 1 if whence == io.SEEK_END else offset
            )
            return self.position

        def read(self, size: int = -1) -> bytes:
            raise AssertionError("rejected source must not be read")

    class NoRemoteStateAPI:
        def begin_upload(self, **arguments: object) -> Mapping[str, Any]:
            raise AssertionError("invalid source must not create remote upload state")

    for source, message in (
        (io.BytesIO(b""), "plaintext size must be positive"),
        (OversizedSource(), "plaintext exceeds the managed transfer limit"),
    ):
        with pytest.raises(TransferError, match=message):
            upload_file(
                NoRemoteStateAPI(),
                project_id="project_123",
                filename="mix.wav",
                source=source,
                operation_id="file_123",
            )


def test_upload_rejects_oversized_epoch_before_consuming_claim(
    bucket: tuple[str, dict[str, bytes], dict[str, dict[str, object]]],
) -> None:
    endpoint, _, claims = bucket
    claims["/claims/upload"] = _key_claim(
        "upload",
        bytes(range(1, 33)),
        bytes(range(1, 13)),
        bytes(range(33, 81)),
    )

    class OversizedEpochAPI:
        def begin_upload(self, **arguments: object) -> Mapping[str, Any]:
            return {
                "uploadId": "upload_123",
                "keyEpoch": MAXIMUM_WIRE_INTEGER + 1,
                "keyClaim": _key_claim_descriptor(endpoint, "upload"),
            }

    with pytest.raises(TransferError, match="must be between"):
        upload_file(
            OversizedEpochAPI(),
            project_id="project_123",
            filename="mix.wav",
            source=io.BytesIO(b"x"),
            operation_id="file_123",
        )
    assert "/claims/upload" in claims


def test_upload_replay_commits_an_already_ready_object(
    bucket: tuple[str, dict[str, bytes], dict[str, dict[str, object]]],
) -> None:
    endpoint, _, claims = bucket
    calls: list[str] = []

    class ReadyAPI:
        def begin_upload(self, **arguments: object) -> Mapping[str, Any]:
            claims["/claims/upload"] = _key_claim(
                "upload",
                bytes(range(1, 33)),
                bytes(range(1, 13)),
                bytes(range(33, 81)),
            )
            return {
                "uploadId": "upload_123",
                "keyEpoch": 0,
                "keyClaim": _key_claim_descriptor(endpoint, "upload"),
            }

        def put_manifest(self, **arguments: object) -> Mapping[str, Any]:
            calls.append("put_manifest")
            return {"objectId": "upload_123", "state": "ready"}

        def upload_capability(self, **arguments: object) -> Mapping[str, Any]:
            raise AssertionError("ready uploads must not request PUT capabilities")

        def complete_upload(self, **arguments: object) -> Mapping[str, Any]:
            raise AssertionError("ready uploads must not be completed again")

        def commit_file(self, **arguments: object) -> Mapping[str, Any]:
            calls.append("commit_file")
            return {"file": {"fileId": "file_123"}, "idempotent": True}

    result = upload_file(
        ReadyAPI(),
        project_id="project_123",
        filename="mix.wav",
        source=io.BytesIO(b"ready"),
        operation_id="file_123",
    )
    assert result["file"]["fileId"] == "file_123"
    assert calls == ["put_manifest", "commit_file"]


def test_preview_upload_uses_generated_contract_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def begin(*args: object, **arguments: Any) -> object:
        captured.update(arguments["body"].to_dict())
        return object()

    monkeypatch.setattr(_api.create_encrypted_object_upload, "asyncio_detailed", begin)
    monkeypatch.setattr(
        AudaligoTransferAPI,
        "_body",
        staticmethod(lambda response, *expected: {}),
    )
    with AudaligoTransferAPI(
        base_url="https://audaligo.example",
        access_token="a" * 43,
        timeouts=TransferTimeouts(connect=1, read=1, total=1),
    ) as api:
        api.begin_upload(
            project_id="project_123",
            operation_id="operation_123",
            mix_version_id="mix_123",
            filename="mix.wav",
            plaintext_size=4096,
        )

    assert captured["previewIntent"] == {
        "v": 1,
        "profile": "aac-lc-128k-m4a-v1",
        "filename": "mix.wav",
        "mediaType": "audio/wav",
        "plaintextSize": 4096,
        "mixVersionId": "mix_123",
    }


def test_cli_reads_committed_file_id_from_response_envelope(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "mix.wav"
    source.write_bytes(b"audio")
    monkeypatch.setenv("AUDALIGO_ACCESS_TOKEN", "a" * 43)
    monkeypatch.setattr(
        _cli,
        "AudaligoTransferAPI",
        lambda **arguments: nullcontext(object()),
    )
    monkeypatch.setattr(
        _cli,
        "upload_file",
        lambda *args, **arguments: {"file": {"fileId": "file_123"}},
    )

    assert (
        _cli.main(
            [
                "--api-url",
                "https://audaligo.example",
                "upload",
                "--project-id",
                "project_123",
                "--source",
                str(source),
                "--operation-id",
                "operation_123",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out) == {"fileId": "file_123"}


def test_sdk_encrypts_locally_and_transfers_ciphertext_directly(
    bucket: tuple[str, dict[str, bytes], dict[str, dict[str, object]]],
    tmp_path: Path,
) -> None:
    endpoint, objects, claims = bucket
    data_key = bytes(range(33, 65))
    wrapped_nonce = bytes(range(1, 13))
    wrapped_data_key = bytes(range(65, 113))
    plaintext = bytes((index * 37) % 251 for index in range(CHUNK_SIZE + 17))
    state: dict[str, Any] = {"manifest": None}
    calls: list[str] = []

    class FakeAudaligoAPI:
        def begin_upload(self, **arguments: object) -> Mapping[str, Any]:
            calls.append("begin_upload")
            assert arguments["plaintext_size"] == len(plaintext)
            claims["/claims/upload"] = _key_claim(
                "upload", data_key, wrapped_nonce, wrapped_data_key
            )
            return {
                "uploadId": "upload_123",
                "keyEpoch": 0,
                "keyClaim": _key_claim_descriptor(endpoint, "upload"),
            }

        def put_manifest(
            self, *, project_id: str, upload_id: str, manifest: Mapping[str, Any]
        ) -> Mapping[str, Any]:
            calls.append("put_manifest")
            assert set(manifest) == {"v", "type", "suite_id", "encryption", "object"}
            assert manifest["v"] == 1
            assert manifest["suite_id"] == "aes-256-gcm-audaligo-v1"
            state["manifest"] = dict(manifest)
            return {"objectId": upload_id, "state": "manifest_stored"}

        def upload_capability(
            self, *, project_id: str, upload_id: str, chunk_index: int
        ) -> Mapping[str, Any]:
            calls.append("upload_capability")
            manifest = state["manifest"]
            assert isinstance(manifest, Mapping)
            length = int(manifest["object"]["chunks"][chunk_index]["ciphertext_size"])
            return _capability(endpoint, "PUT", chunk_index, length)

        def complete_upload(
            self, *, project_id: str, upload_id: str
        ) -> Mapping[str, Any]:
            calls.append("complete_upload")
            return {"objectId": upload_id, "state": "chunks_complete"}

        def commit_file(self, **arguments: object) -> Mapping[str, Any]:
            calls.append("commit_file")
            return {
                "file": {
                    "projectId": "project_123",
                    "fileId": "file_123",
                    "encryptedObjectId": "upload_123",
                    "originalFilename": "mix.wav",
                    "originalPlaintextSize": str(len(plaintext)),
                },
                "idempotent": False,
            }

        def read_descriptor(
            self, *, project_id: str, file_id: str
        ) -> Mapping[str, Any]:
            calls.append("read_descriptor")
            manifest = state["manifest"]
            assert isinstance(manifest, Mapping)
            claims["/claims/download"] = _key_claim(
                "download", data_key, wrapped_nonce, wrapped_data_key
            )
            return {
                "file": {
                    "projectId": project_id,
                    "fileId": file_id,
                    "encryptedObjectId": "upload_123",
                },
                "manifest": manifest,
                "keyClaim": _key_claim_descriptor(endpoint, "download"),
            }

        def read_capability(
            self, *, project_id: str, object_id: str, chunk_index: int
        ) -> Mapping[str, Any]:
            calls.append("read_capability")
            manifest = state["manifest"]
            assert isinstance(manifest, Mapping)
            length = int(manifest["object"]["chunks"][chunk_index]["ciphertext_size"])
            return _capability(endpoint, "GET", chunk_index, length)

    api = FakeAudaligoAPI()

    upload_result = upload_file(
        api,
        project_id="project_123",
        filename="mix.wav",
        source=io.BytesIO(plaintext),
        operation_id="file_123",
    )
    assert upload_result["file"]["fileId"] == "file_123"
    assert len(objects) == 2
    assert objects["/upload_123/0?signature=test"] != plaintext[:CHUNK_SIZE]
    assert objects["/upload_123/1?signature=test"] != plaintext[CHUNK_SIZE:]

    destination = tmp_path / "download.wav"
    assert download_file(
        api,
        project_id="project_123",
        file_id="file_123",
        destination=destination,
    ) == len(plaintext)
    assert destination.read_bytes() == plaintext
    assert calls.count("upload_capability") == 2
    assert calls.count("read_capability") == 2
    assert claims == {}


def _key_claim_descriptor(endpoint: str, direction: str) -> dict[str, object]:
    return {
        "url": f"{endpoint}/claims/{direction}#{'a' * 43}",
        "expiresAtUnixMilliseconds": 4_102_444_800_000,
        "protocol": "audaligo.file-key-claim.v1",
    }


def _key_claim(
    direction: str,
    data_key: bytes,
    wrapped_nonce: bytes,
    wrapped_data_key: bytes,
) -> dict[str, object]:
    return {
        "version": 1,
        "protocol": "audaligo.file-key-claim.v1",
        "direction": direction,
        "projectId": "project_123",
        "objectId": "upload_123",
        "epoch": 0,
        "dataKey": _b64url(data_key),
        "wrappedDataKey": {
            "nonce": _b64url(wrapped_nonce),
            "ciphertext": _b64url(wrapped_data_key),
        },
    }


def _b64url(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _capability(
    endpoint: str, operation: str, index: int, content_length: int
) -> dict[str, object]:
    return {
        "operation": operation,
        "objectId": "upload_123",
        "chunkIndex": index,
        "contentLength": content_length,
        "url": f"{endpoint}/upload_123/{index}?signature=test",
        "headers": {},
    }
