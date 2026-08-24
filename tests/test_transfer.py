from __future__ import annotations

import io
import json
import threading
from base64 import b64encode
from collections.abc import Mapping
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from soenan_mcp_support.transfer import download_file, upload_file
from soenan_mcp_support.transfer._crypto import CHUNK_SIZE, chunk_aad, chunk_nonce


@pytest.fixture
def bucket() -> tuple[str, dict[str, bytes]]:
    objects: dict[str, bytes] = {}

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

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", objects
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
    bucket: tuple[str, dict[str, bytes]], tmp_path: Path
) -> None:
    endpoint, objects = bucket
    project_key = bytes(range(1, 33))
    plaintext = bytes((index * 37) % 251 for index in range(CHUNK_SIZE + 17))
    manifest: dict[str, Any] | None = None
    calls: list[str] = []

    def call_tool(name: str, arguments: Mapping[str, object]) -> Mapping[str, Any]:
        nonlocal manifest
        calls.append(name)
        if name == "audaligo_begin_file_upload":
            assert arguments["plaintextSize"] == len(plaintext)
            return {
                "uploadId": "upload_123",
                "keyring": {
                    "projectId": "project_123",
                    "keys": [{"key": b64encode(project_key).decode("ascii")}],
                },
            }
        if name == "audaligo_put_file_upload_manifest":
            manifest = json.loads(str(arguments["manifestJson"]))
            return {"objectId": "upload_123", "state": "manifest_stored"}
        if name == "audaligo_create_file_upload_chunk_capability":
            index = int(arguments["chunkIndex"])
            return _capability(endpoint, "put", index, int(arguments["contentLength"]))
        if name == "audaligo_complete_file_upload_chunks":
            assert arguments["chunkIndexes"] == [0, 1]
            return {"objectId": "upload_123", "state": "chunks_complete"}
        if name == "audaligo_commit_file_upload":
            return {
                "file": {
                    "projectId": "project_123",
                    "fileId": "file_123",
                    "encryptedObjectId": "upload_123",
                    "originalFilename": "mix.wav",
                    "originalPlaintextSize": str(len(plaintext)),
                    "mimeType": "application/octet-stream",
                    "createdAtUnixMilliseconds": "1",
                    "updatedAtUnixMilliseconds": "1",
                },
                "idempotent": False,
            }
        if name == "audaligo_begin_file_download":
            assert manifest is not None
            return {
                "file": {
                    "projectId": "project_123",
                    "fileId": "file_123",
                    "encryptedObjectId": "upload_123",
                    "originalFilename": "mix.wav",
                    "originalPlaintextSize": str(len(plaintext)),
                    "mimeType": "application/octet-stream",
                    "createdAtUnixMilliseconds": "1",
                    "updatedAtUnixMilliseconds": "1",
                },
                "manifest": _protobuf_json_manifest(manifest),
                "keyring": {
                    "projectId": "project_123",
                    "keys": [{"key": b64encode(project_key).decode("ascii")}],
                },
            }
        if name == "audaligo_create_file_read_chunk_capability":
            assert manifest is not None
            index = int(arguments["chunkIndex"])
            length = int(manifest["chunks"][index]["ciphertextSize"])
            return _capability(endpoint, "get", index, length)
        raise AssertionError(f"unexpected tool: {name}")

    upload_result = upload_file(
        call_tool,
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
        call_tool,
        project_id="project_123",
        file_id="file_123",
        destination=destination,
    ) == len(plaintext)
    assert destination.read_bytes() == plaintext
    assert calls.count("audaligo_create_file_upload_chunk_capability") == 2
    assert calls.count("audaligo_create_file_read_chunk_capability") == 2


def _capability(
    endpoint: str, operation: str, index: int, content_length: int
) -> dict[str, object]:
    capability: dict[str, object] = {
        "operation": operation,
        "objectId": "upload_123",
        "expiresAtUnixMilliseconds": "4102444800000",
        "contentLength": str(content_length),
        "url": f"{endpoint}/upload_123/{index}?signature=test",
    }
    if index:
        capability["chunkIndex"] = index
    return capability


def _protobuf_json_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(manifest))
    result["encryptionMode"] = "managed_encryption"
    if result["epoch"] == "0":
        del result["epoch"]
    for chunk in result["chunks"]:
        for key in ("chunkIndex", "ciphertextOffset", "plaintextOffset"):
            if chunk[key] in (0, "0"):
                del chunk[key]
        if chunk["finalChunk"] is False:
            del chunk["finalChunk"]
    return result
