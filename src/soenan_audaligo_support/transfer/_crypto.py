from __future__ import annotations

import hmac
import struct
from base64 import urlsafe_b64decode, urlsafe_b64encode
from binascii import Error as BinasciiError
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
MAXIMUM_WIRE_INTEGER = 9_007_199_254_740_991
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
            "chunk_index": self.index,
            "ciphertext_offset": self.ciphertext_offset,
            "ciphertext_sha256_b64u": _base64url(self.ciphertext_sha256),
            "ciphertext_size": self.ciphertext_size,
            "final_chunk": self.final,
            "plaintext_offset": self.plaintext_offset,
            "plaintext_size": self.plaintext_size,
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
            "v": MANIFEST_VERSION,
            "type": MANIFEST_TYPE,
            "suite_id": SUITE_ID,
            "encryption": {
                "mode": ENCRYPTION_MODE,
                "content_key_alg": CONTENT_KEY_ALGORITHM,
                "wrap_alg": WRAP_ALGORITHM,
                "wrapped_data_key": {
                    "nonceB64u": _base64url(self.wrapped_nonce),
                    "ciphertextB64u": _base64url(self.wrapped_data_key),
                },
            },
            "object": {
                "chunk_count": self.chunk_count,
                "chunk_size": CHUNK_SIZE,
                "chunks": [chunk.wire_value() for chunk in self.chunks],
                "ciphertext_size": sum(chunk.ciphertext_size for chunk in self.chunks),
                "epoch": self.epoch,
                "file_id": self.file_id,
                "nonce_base_b64u": _base64url(self.nonce_base),
                "object_id": self.object_id,
                "plaintext_size": self.plaintext_size,
                "project_id": self.project_id,
                "share_id": SHARE_ID,
            },
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
    chunk_size: int
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
                    chunk_size=self.chunk_size,
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
    if isinstance(epoch, bool) or not 0 <= epoch <= MAXIMUM_WIRE_INTEGER:
        raise EncryptionContractError("epoch must be a canonical wire integer")
    if len(data_key) != 32 or not any(data_key):
        raise EncryptionContractError("data key must be a nonzero 256-bit key")
    if len(wrapped_nonce) != 12 or len(wrapped_data_key) != 48:
        raise EncryptionContractError("wrapped data key is invalid")
    if plaintext_size <= 0:
        raise EncryptionContractError("plaintext size must be positive")
    chunk_count = (plaintext_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    if not 1 <= chunk_count <= MAXIMUM_CHUNKS:
        raise EncryptionContractError("plaintext exceeds the managed transfer limit")

    nonce_base = _replay_stable_nonce_base(
        data_key,
        project_id=project_id,
        file_id=file_id,
        object_id=object_id,
        epoch=epoch,
    )

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
    _require_fields(
        manifest,
        required={"v", "type", "suite_id", "encryption", "object"},
        allowed={"v", "type", "suite_id", "encryption", "object"},
        label="manifest",
    )
    if (
        _integer(manifest, "v") != MANIFEST_VERSION
        or _string(manifest, "type") != MANIFEST_TYPE
        or _string(manifest, "suite_id") != SUITE_ID
    ):
        raise EncryptionContractError("unsupported managed manifest")

    encryption = manifest.get("encryption")
    if not isinstance(encryption, Mapping):
        raise EncryptionContractError("manifest encryption must be an object")
    encryption_fields = {
        "mode",
        "content_key_alg",
        "wrap_alg",
        "wrapped_data_key",
    }
    _require_fields(
        encryption,
        required=encryption_fields,
        allowed=encryption_fields,
        label="manifest encryption",
    )
    if (
        _string(encryption, "mode") != ENCRYPTION_MODE
        or _string(encryption, "content_key_alg") != CONTENT_KEY_ALGORITHM
        or _string(encryption, "wrap_alg") != WRAP_ALGORITHM
    ):
        raise EncryptionContractError("unsupported managed manifest encryption")

    object_value = manifest.get("object")
    if not isinstance(object_value, Mapping):
        raise EncryptionContractError("manifest object must be an object")
    object_fields = {
        "chunk_count",
        "chunk_size",
        "chunks",
        "ciphertext_size",
        "epoch",
        "file_id",
        "nonce_base_b64u",
        "object_id",
        "plaintext_size",
        "project_id",
        "share_id",
    }
    _require_fields(
        object_value,
        required=object_fields,
        allowed=object_fields,
        label="manifest object",
    )
    chunk_size = _integer(object_value, "chunk_size")
    if (
        not 1 <= chunk_size <= CHUNK_SIZE
        or _string(object_value, "share_id") != SHARE_ID
    ):
        raise EncryptionContractError("unsupported managed manifest object")

    project_id = _string(object_value, "project_id")
    file_id = _string(object_value, "file_id")
    object_id = _string(object_value, "object_id")
    for value in (project_id, file_id, object_id):
        _validate_identity(value)
    epoch = _integer(object_value, "epoch")
    plaintext_size = _positive_integer(object_value, "plaintext_size")
    chunk_count = _positive_integer(object_value, "chunk_count")
    if (
        epoch < 0
        or chunk_count > MAXIMUM_CHUNKS
        or (plaintext_size - 1) // chunk_size + 1 != chunk_count
    ):
        raise EncryptionContractError("invalid managed manifest chunk count")
    nonce_base = _base64url_bytes(object_value, "nonce_base_b64u", 8)

    raw_chunks = object_value.get("chunks")
    if not isinstance(raw_chunks, Sequence) or isinstance(raw_chunks, (str, bytes)):
        raise EncryptionContractError("manifest chunks must be an array")
    if len(raw_chunks) != chunk_count:
        raise EncryptionContractError("manifest chunk count does not match chunks")
    chunks: list[ChunkMetadata] = []
    plaintext_offset = 0
    ciphertext_offset = 0
    chunk_fields = {
        "chunk_index",
        "ciphertext_offset",
        "ciphertext_sha256_b64u",
        "ciphertext_size",
        "final_chunk",
        "plaintext_offset",
        "plaintext_size",
    }
    for index, raw in enumerate(raw_chunks):
        if not isinstance(raw, Mapping):
            raise EncryptionContractError("manifest chunk must be an object")
        _require_fields(
            raw,
            required=chunk_fields,
            allowed=chunk_fields,
            label="manifest chunk",
        )
        plaintext_length = _positive_integer(raw, "plaintext_size")
        ciphertext_length = _positive_integer(raw, "ciphertext_size")
        final = raw.get("final_chunk")
        if (
            _integer(raw, "chunk_index") != index
            or _integer(raw, "plaintext_offset") != plaintext_offset
            or _integer(raw, "ciphertext_offset") != ciphertext_offset
            or plaintext_length != min(chunk_size, plaintext_size - plaintext_offset)
            or ciphertext_length != plaintext_length + _TAG_SIZE
            or not isinstance(final, bool)
            or final != (index + 1 == chunk_count)
        ):
            raise EncryptionContractError("invalid managed manifest chunk layout")
        chunks.append(
            ChunkMetadata(
                index=index,
                ciphertext_offset=ciphertext_offset,
                ciphertext_sha256=_base64url_bytes(raw, "ciphertext_sha256_b64u", 32),
                ciphertext_size=ciphertext_length,
                final=final,
                plaintext_offset=plaintext_offset,
                plaintext_size=plaintext_length,
            )
        )
        plaintext_offset += plaintext_length
        ciphertext_offset += ciphertext_length
    if plaintext_offset != plaintext_size or ciphertext_offset != _positive_integer(
        object_value, "ciphertext_size"
    ):
        raise EncryptionContractError("managed manifest totals do not match chunks")

    if len(data_key) != 32 or not any(data_key):
        raise EncryptionContractError("data key must be a nonzero 256-bit key")
    wrapped = encryption.get("wrapped_data_key")
    if not isinstance(wrapped, Mapping):
        raise EncryptionContractError("wrapped data key must be an object")
    if set(wrapped) != {"nonceB64u", "ciphertextB64u"} or (
        _base64url_bytes(wrapped, "nonceB64u", 12) != wrapped_nonce
        or _base64url_bytes(wrapped, "ciphertextB64u", 48) != wrapped_data_key
    ):
        raise EncryptionContractError("file key claim does not match manifest")
    return DecryptionPlan(
        project_id=project_id,
        file_id=file_id,
        object_id=object_id,
        epoch=epoch,
        plaintext_size=plaintext_size,
        chunk_count=chunk_count,
        chunk_size=chunk_size,
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
    chunk_size: int = CHUNK_SIZE,
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
    output.extend(struct.pack(">I", chunk_size))
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


def _replay_stable_nonce_base(
    data_key: bytes,
    *,
    project_id: str,
    file_id: str,
    object_id: str,
    epoch: int,
) -> bytes:
    context = bytearray(b"audaligo:managed:nonce-base:v1")
    for value in (project_id, file_id, object_id):
        _append_string(context, value)
    context.extend(struct.pack(">Q", epoch))
    nonce_base = hmac.digest(data_key, context, "sha256")[:8]
    return nonce_base if any(nonce_base) else b"\x00\x00\x00\x00\x00\x00\x00\x01"


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
    if (
        isinstance(raw, bool)
        or not isinstance(raw, int)
        or not 0 <= raw <= MAXIMUM_WIRE_INTEGER
    ):
        raise EncryptionContractError(f"{key} must be a canonical wire integer")
    return raw


def _positive_integer(value: Mapping[str, Any], key: str) -> int:
    result = _integer(value, key)
    if result == 0:
        raise EncryptionContractError(f"{key} must be positive")
    return result


def _base64url(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _base64url_bytes(value: Mapping[str, Any], key: str, expected_length: int) -> bytes:
    encoded = _string(value, key)
    if not encoded or "=" in encoded:
        raise EncryptionContractError(f"{key} must be canonical base64url")
    try:
        decoded = urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
    except (BinasciiError, ValueError):
        raise EncryptionContractError(f"{key} must be canonical base64url") from None
    if len(decoded) != expected_length or _base64url(decoded) != encoded:
        raise EncryptionContractError(f"{key} has an invalid encoded length")
    return decoded
