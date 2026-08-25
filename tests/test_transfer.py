from __future__ import annotations

import io
import json
import threading
from base64 import urlsafe_b64encode
from collections.abc import Mapping
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from soenan_audaligo_support.transfer import download_file, upload_file
from soenan_audaligo_support.transfer._crypto import CHUNK_SIZE, chunk_aad, chunk_nonce


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
