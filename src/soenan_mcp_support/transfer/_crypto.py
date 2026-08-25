from __future__ import annotations

import os
import struct
from base64 import b64decode, b64encode
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, BinaryIO

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MANIFEST_VERSION = 1
MANIFEST_TYPE = "audaligo.managed-encrypted-object-manifest"
SUITE_ID = "aes-256-gcm-audaligo-v1"
ENCRYPTION_MODE = "managed-project-key"
CONTENT_KEY_ALGORITHM = "A256GCM"
WRAP_ALGORITHM = "a256gcm-project-epoch-v1"
SHARE_ID = "project_file_managed_v1"
CHUNK_SIZE = 8 * 1024 * 1024
MAXIMUM_CHUNKS = 4096
_TAG_SIZE = 16


class EncryptionContractError(ValueError):
    """Managed encryption input or ciphertext violates the Audaligo contract."""


@dataclass(frozen=True)
class ChunkMetadata:
    index: int
    ciphertext_offset: int
    ciphertext_sha256: bytes
    ciphertext_size: int
    final: bool
    plaintext_offset: int
    plaintext_size: int

    def wire_value(self) -> dict[str, object]:
        return {
            "chunkIndex": self.index,
            "ciphertextOffset": str(self.ciphertext_offset),
            "ciphertextSha256": b64encode(self.ciphertext_sha256).decode("ascii"),
            "ciphertextSize": str(self.ciphertext_size),
            "finalChunk": self.final,
            "plaintextOffset": str(self.plaintext_offset),
            "plaintextSize": str(self.plaintext_size),
        }


@dataclass(frozen=True)
class EncryptionPlan:
    project_id: str
    file_id: str
    object_id: str
    epoch: int
    plaintext_size: int
    chunk_count: int
    nonce_base: bytes
    data_key: bytes
    wrapped_nonce: bytes
    wrapped_data_key: bytes
    chunks: tuple[ChunkMetadata, ...]

    def manifest(self) -> dict[str, object]:
        return {
            "version": MANIFEST_VERSION,
            "type": MANIFEST_TYPE,
            "suiteId": SUITE_ID,
            "encryptionMode": ENCRYPTION_MODE,
            "contentKeyAlgorithm": CONTENT_KEY_ALGORITHM,
            "wrapAlgorithm": WRAP_ALGORITHM,
            "wrappedDataKey": {
                "nonce": b64encode(self.wrapped_nonce).decode("ascii"),
                "ciphertext": b64encode(self.wrapped_data_key).decode("ascii"),
            },
            "chunkCount": self.chunk_count,
            "chunkSize": CHUNK_SIZE,
            "chunks": [chunk.wire_value() for chunk in self.chunks],
            "ciphertextSize": str(sum(chunk.ciphertext_size for chunk in self.chunks)),
            "epoch": str(self.epoch),
            "fileId": self.file_id,
            "nonceBase": b64encode(self.nonce_base).decode("ascii"),
            "objectId": self.object_id,
            "plaintextSize": str(self.plaintext_size),
            "projectId": self.project_id,
            "shareId": SHARE_ID,
        }

    def seal_chunk(self, cleartext: bytes, index: int) -> bytes:
        chunk = self.chunks[index]
        if len(cleartext) != chunk.plaintext_size:
            raise EncryptionContractError(
                "plaintext chunk size does not match manifest"
            )
        return AESGCM(self.data_key).encrypt(
            chunk_nonce(self.nonce_base, index),
            cleartext,
            chunk_aad(
                project_id=self.project_id,
                file_id=self.file_id,
                object_id=self.object_id,
                epoch=self.epoch,
                total_plaintext_size=self.plaintext_size,
                chunk_count=self.chunk_count,
                chunk_index=index,
                plaintext_offset=chunk.plaintext_offset,
                plaintext_length=chunk.plaintext_size,
                final=chunk.final,
            ),
        )


@dataclass(frozen=True)
class DecryptionPlan:
    project_id: str
    file_id: str
    object_id: str
    epoch: int
    plaintext_size: int
    chunk_count: int
    nonce_base: bytes
    data_key: bytes
    chunks: tuple[ChunkMetadata, ...]

    def open_chunk(self, ciphertext: bytes, index: int) -> bytes:
        chunk = self.chunks[index]
        if len(ciphertext) != chunk.ciphertext_size:
            raise EncryptionContractError(
                "ciphertext chunk size does not match manifest"
            )
        if sha256(ciphertext).digest() != chunk.ciphertext_sha256:
            raise EncryptionContractError(
                "ciphertext chunk digest does not match manifest"
            )
        try:
            cleartext = AESGCM(self.data_key).decrypt(
                chunk_nonce(self.nonce_base, index),
                ciphertext,
                chunk_aad(
                    project_id=self.project_id,
                    file_id=self.file_id,
                    object_id=self.object_id,
                    epoch=self.epoch,
                    total_plaintext_size=self.plaintext_size,
                    chunk_count=self.chunk_count,
                    chunk_index=index,
                    plaintext_offset=chunk.plaintext_offset,
                    plaintext_length=chunk.plaintext_size,
                    final=chunk.final,
                ),
            )
        except InvalidTag:
            raise EncryptionContractError("ciphertext authentication failed") from None
        if len(cleartext) != chunk.plaintext_size:
            raise EncryptionContractError(
                "plaintext chunk size does not match manifest"
            )
        return cleartext


def build_encryption_plan(
    stream: BinaryIO,
    *,
    project_id: str,
    file_id: str,
    object_id: str,
    epoch: int,
    data_key: bytes,
    wrapped_nonce: bytes,
    wrapped_data_key: bytes,
    plaintext_size: int,
) -> EncryptionPlan:
    _validate_identity(project_id)
    _validate_identity(file_id)
    _validate_identity(object_id)
    if len(data_key) != 32 or not any(data_key):
        raise EncryptionContractError("data key must be a nonzero 256-bit key")
    if len(wrapped_nonce) != 12 or len(wrapped_data_key) != 48:
        raise EncryptionContractError("wrapped data key is invalid")
    if plaintext_size <= 0:
        raise EncryptionContractError("plaintext size must be positive")
    chunk_count = (plaintext_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    if not 1 <= chunk_count <= MAXIMUM_CHUNKS:
        raise EncryptionContractError("plaintext exceeds the managed transfer limit")

    nonce_base = _nonzero_random(8)

    start = stream.tell()
    chunks: list[ChunkMetadata] = []
    plaintext_offset = 0
    ciphertext_offset = 0
    for index in range(chunk_count):
        plaintext_length = min(CHUNK_SIZE, plaintext_size - plaintext_offset)
        cleartext = _read_exact(stream, plaintext_length)
        final = index + 1 == chunk_count
        ciphertext = AESGCM(data_key).encrypt(
            chunk_nonce(nonce_base, index),
            cleartext,
            chunk_aad(
                project_id=project_id,
                file_id=file_id,
                object_id=object_id,
                epoch=epoch,
                total_plaintext_size=plaintext_size,
                chunk_count=chunk_count,
                chunk_index=index,
                plaintext_offset=plaintext_offset,
                plaintext_length=plaintext_length,
                final=final,
            ),
        )
        chunks.append(
            ChunkMetadata(
                index=index,
                ciphertext_offset=ciphertext_offset,
                ciphertext_sha256=sha256(ciphertext).digest(),
                ciphertext_size=len(ciphertext),
                final=final,
                plaintext_offset=plaintext_offset,
                plaintext_size=plaintext_length,
            )
        )
        plaintext_offset += plaintext_length
        ciphertext_offset += len(ciphertext)
    if stream.read(1):
        raise EncryptionContractError("plaintext stream exceeds its declared size")
    stream.seek(start)
    return EncryptionPlan(
        project_id=project_id,
        file_id=file_id,
        object_id=object_id,
        epoch=epoch,
        plaintext_size=plaintext_size,
        chunk_count=chunk_count,
        nonce_base=nonce_base,
        data_key=data_key,
        wrapped_nonce=wrapped_nonce,
        wrapped_data_key=wrapped_data_key,
        chunks=tuple(chunks),
    )


def parse_decryption_plan(
    manifest: Mapping[str, Any],
    *,
    data_key: bytes,
    wrapped_nonce: bytes,
    wrapped_data_key: bytes,
) -> DecryptionPlan:
    manifest_fields = {
        "version",
        "type",
        "suiteId",
        "encryptionMode",
        "contentKeyAlgorithm",
        "wrapAlgorithm",
        "wrappedDataKey",
        "chunkCount",
        "chunkSize",
        "chunks",
        "ciphertextSize",
        "epoch",
        "fileId",
        "nonceBase",
        "objectId",
        "plaintextSize",
        "projectId",
        "shareId",
    }
    _require_fields(
        manifest,
        required=manifest_fields - {"epoch"},
        allowed=manifest_fields,
        label="manifest",
    )
    expected_strings = {
        "type": MANIFEST_TYPE,
        "suiteId": SUITE_ID,
        "contentKeyAlgorithm": CONTENT_KEY_ALGORITHM,
        "wrapAlgorithm": WRAP_ALGORITHM,
        "shareId": SHARE_ID,
    }
    for key, expected in expected_strings.items():
        if _string(manifest, key) != expected:
            raise EncryptionContractError(f"unsupported managed manifest {key}")
    if _string(manifest, "encryptionMode") not in {
        ENCRYPTION_MODE,
        "managed_encryption",
    }:
        raise EncryptionContractError("unsupported managed manifest encryptionMode")
    for key, expected in (("version", MANIFEST_VERSION), ("chunkSize", CHUNK_SIZE)):
        if _integer(manifest, key) != expected:
            raise EncryptionContractError(f"unsupported managed manifest {key}")

    project_id = _string(manifest, "projectId")
    file_id = _string(manifest, "fileId")
    object_id = _string(manifest, "objectId")
    for value in (project_id, file_id, object_id):
        _validate_identity(value)
    epoch = _integer_or_zero(manifest, "epoch")
    plaintext_size = _positive_integer(manifest, "plaintextSize")
    chunk_count = _positive_integer(manifest, "chunkCount")
    if (
        chunk_count > MAXIMUM_CHUNKS
        or (plaintext_size - 1) // CHUNK_SIZE + 1 != chunk_count
    ):
        raise EncryptionContractError("invalid managed manifest chunk count")
    nonce_base = _base64_bytes(manifest, "nonceBase", 8)

    raw_chunks = manifest.get("chunks")
    if not isinstance(raw_chunks, Sequence) or isinstance(raw_chunks, (str, bytes)):
        raise EncryptionContractError("manifest chunks must be an array")
    if len(raw_chunks) != chunk_count:
        raise EncryptionContractError("manifest chunk count does not match chunks")
    chunks: list[ChunkMetadata] = []
    plaintext_offset = 0
    ciphertext_offset = 0
    for index, raw in enumerate(raw_chunks):
        if not isinstance(raw, Mapping):
            raise EncryptionContractError("manifest chunk must be an object")
        chunk_fields = {
            "chunkIndex",
            "ciphertextOffset",
            "ciphertextSha256",
            "ciphertextSize",
            "finalChunk",
            "plaintextOffset",
            "plaintextSize",
        }
        _require_fields(
            raw,
            required=chunk_fields
            - {"chunkIndex", "ciphertextOffset", "finalChunk", "plaintextOffset"},
            allowed=chunk_fields,
            label="manifest chunk",
        )
        plaintext_length = _positive_integer(raw, "plaintextSize")
        ciphertext_length = _positive_integer(raw, "ciphertextSize")
        final = raw.get("finalChunk", False)
        if (
            _integer_or_zero(raw, "chunkIndex") != index
            or _integer_or_zero(raw, "plaintextOffset") != plaintext_offset
            or _integer_or_zero(raw, "ciphertextOffset") != ciphertext_offset
            or plaintext_length > CHUNK_SIZE
            or ciphertext_length != plaintext_length + _TAG_SIZE
            or not isinstance(final, bool)
            or final != (index + 1 == chunk_count)
        ):
            raise EncryptionContractError("invalid managed manifest chunk layout")
        chunks.append(
            ChunkMetadata(
                index=index,
                ciphertext_offset=ciphertext_offset,
                ciphertext_sha256=_base64_bytes(raw, "ciphertextSha256", 32),
                ciphertext_size=ciphertext_length,
                final=final,
                plaintext_offset=plaintext_offset,
                plaintext_size=plaintext_length,
            )
        )
        plaintext_offset += plaintext_length
        ciphertext_offset += ciphertext_length
    if plaintext_offset != plaintext_size or ciphertext_offset != _positive_integer(
        manifest, "ciphertextSize"
    ):
        raise EncryptionContractError("managed manifest totals do not match chunks")

    if len(data_key) != 32 or not any(data_key):
        raise EncryptionContractError("data key must be a nonzero 256-bit key")
    wrapped = manifest.get("wrappedDataKey")
    if not isinstance(wrapped, Mapping):
        raise EncryptionContractError("wrapped data key must be an object")
    if (
        _base64_bytes(wrapped, "nonce", 12) != wrapped_nonce
        or _base64_bytes(wrapped, "ciphertext", 48) != wrapped_data_key
    ):
        raise EncryptionContractError("file key claim does not match manifest")
    return DecryptionPlan(
        project_id=project_id,
        file_id=file_id,
        object_id=object_id,
        epoch=epoch,
        plaintext_size=plaintext_size,
        chunk_count=chunk_count,
        nonce_base=nonce_base,
        data_key=data_key,
        chunks=tuple(chunks),
    )




def chunk_nonce(nonce_base: bytes, index: int) -> bytes:
    if len(nonce_base) != 8 or not 0 <= index <= 0xFFFFFFFF:
        raise EncryptionContractError("invalid managed chunk nonce input")
    return nonce_base + struct.pack(">I", index)


def chunk_aad(
    *,
    project_id: str,
    file_id: str,
    object_id: str,
    epoch: int,
    total_plaintext_size: int,
    chunk_count: int,
    chunk_index: int,
    plaintext_offset: int,
    plaintext_length: int,
    final: bool,
) -> bytes:
    output = bytearray()
    _append_string(output, "audaligo:managed:chunk-aead:v1")
    output.extend(b"\x01")
    output.extend(struct.pack(">H", MANIFEST_VERSION))
    for value in (SUITE_ID, project_id, SHARE_ID, file_id):
        _append_string(output, value)
    output.extend(struct.pack(">Q", epoch))
    _append_string(output, object_id)
    output.extend(struct.pack(">Q", total_plaintext_size))
    output.extend(struct.pack(">I", CHUNK_SIZE))
    output.extend(struct.pack(">I", chunk_count))
    output.extend(struct.pack(">I", chunk_index))
    output.extend(struct.pack(">Q", plaintext_offset))
    output.extend(struct.pack(">I", plaintext_length))
    output.extend(b"\x01" if final else b"\x00")
    return bytes(output)


def _append_string(output: bytearray, value: str) -> None:
    encoded = value.encode("utf-8")
    if len(encoded) > 0xFFFF:
        raise EncryptionContractError("managed encryption context is too long")
    output.extend(struct.pack(">H", len(encoded)))
    output.extend(encoded)


def _context(value: str) -> bytes:
    encoded = value.encode("utf-8")
    if not 1 <= len(encoded) <= 256 or any(
        byte < 0x21 or byte > 0x7E for byte in encoded
    ):
        raise EncryptionContractError("managed key context is invalid")
    return encoded


def _validate_identity(value: str) -> None:
    _context(value)


def _nonzero_random(length: int) -> bytes:
    while True:
        value = os.urandom(length)
        if any(value):
            return value


def _read_exact(stream: BinaryIO, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length
    while remaining:
        value = stream.read(remaining)
        if not isinstance(value, bytes) or not value:
            raise EncryptionContractError(
                "plaintext stream ended before its declared size"
            )
        if len(value) > remaining:
            raise EncryptionContractError(
                "plaintext stream returned an oversized chunk"
            )
        chunks.append(value)
        remaining -= len(value)
    return b"".join(chunks)


def _require_fields(
    value: Mapping[str, Any],
    *,
    required: set[str],
    allowed: set[str],
    label: str,
) -> None:
    fields = set(value)
    if not required.issubset(fields) or not fields.issubset(allowed):
        raise EncryptionContractError(
            f"{label} fields do not match the managed contract"
        )


def _string(value: Mapping[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise EncryptionContractError(f"{key} must be a nonempty string")
    return result


def _integer(value: Mapping[str, Any], key: str) -> int:
    raw = value.get(key)
    if isinstance(raw, bool):
        raise EncryptionContractError(f"{key} must be an integer")
    if isinstance(raw, int):
        result = raw
    elif isinstance(raw, str) and raw.isdecimal():
        result = int(raw)
    else:
        raise EncryptionContractError(f"{key} must be an integer")
    if result < 0:
        raise EncryptionContractError(f"{key} must be nonnegative")
    return result


def _integer_or_zero(value: Mapping[str, Any], key: str) -> int:
    return 0 if key not in value else _integer(value, key)


def _positive_integer(value: Mapping[str, Any], key: str) -> int:
    result = _integer(value, key)
    if result == 0:
        raise EncryptionContractError(f"{key} must be positive")
    return result


def _base64_bytes(value: Mapping[str, Any], key: str, expected_length: int) -> bytes:
    encoded = _string(value, key)
    try:
        decoded = b64decode(encoded, validate=True)
    except ValueError:
        raise EncryptionContractError(f"{key} must be canonical base64") from None
    if len(decoded) != expected_length or b64encode(decoded).decode("ascii") != encoded:
        raise EncryptionContractError(f"{key} has an invalid encoded length")
    return decoded
