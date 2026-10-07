from __future__ import annotations

import base64
import ctypes
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class E2eeError(Exception):
    """A stable failure that never includes keys, content, or HTTP bodies."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def encode(value: bytes | bytearray) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def decode(value: object) -> bytearray:
    if not isinstance(value, str):
        raise E2eeError("invalid_encoding")
    try:
        data = bytearray(
            base64.b64decode(
                value + "=" * (-len(value) % 4), altchars=b"-_", validate=True
            )
        )
    except (ValueError, base64.binascii.Error):
        raise E2eeError("invalid_encoding") from None
    if encode(data) != value:
        wipe(data)
        raise E2eeError("invalid_encoding")
    return data


def wipe(value: bytearray) -> None:
    value[:] = b"\0" * len(value)


class E2eeCrypto:
    def __init__(self, library: str | Path | None = None):
        try:
            if library is None:
                from arteligo_e2ee_native import library_path

                library = library_path()
            self._library = ctypes.CDLL(str(library))
            pointer = ctypes.POINTER(ctypes.c_uint8)
            self._execute = self._library.arteligo_e2ee_execute
            self._execute.argtypes = [
                pointer,
                ctypes.c_size_t,
                ctypes.POINTER(pointer),
                ctypes.POINTER(ctypes.c_size_t),
            ]
            self._execute.restype = ctypes.c_int32
            self._free = self._library.arteligo_e2ee_free
            self._free.argtypes = [pointer, ctypes.c_size_t]
            self._free.restype = None
        except (ImportError, OSError, AttributeError, RuntimeError):
            raise E2eeError("crypto_unavailable") from None

    def execute(self, request: Mapping[str, Any]) -> dict[str, Any]:
        try:
            raw = bytearray(
                json.dumps(
                    {**request, "v": 1},
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                ).encode()
            )
        except (TypeError, ValueError):
            raise E2eeError("invalid_input") from None
        if len(raw) > 24 * 1024 * 1024:
            wipe(raw)
            raise E2eeError("limit_exceeded")
        input_buffer = (ctypes.c_uint8 * len(raw)).from_buffer(raw)
        pointer = ctypes.POINTER(ctypes.c_uint8)()
        length = ctypes.c_size_t()
        response_bytes = bytearray()
        try:
            status = self._execute(
                input_buffer, len(raw), ctypes.byref(pointer), ctypes.byref(length)
            )
            if status or not pointer:
                raise E2eeError("crypto_unavailable")
            response_bytes.extend(ctypes.string_at(pointer, length.value))
            response = json.loads(response_bytes)
            if response.get("v") != 1:
                raise E2eeError("unsupported_version")
            if response.get("ok") is not True:
                code = response.get("error")
                if code not in {
                    "invalid_input",
                    "authentication_failed",
                    "unsupported_version",
                    "limit_exceeded",
                    "internal_error",
                }:
                    code = "internal_error"
                raise E2eeError(code)
            return response["result"]
        finally:
            if pointer:
                self._free(pointer, length.value)
            wipe(raw)
            wipe(response_bytes)

    def keypair(self) -> dict[str, str]:
        return self.execute({"op": "generate_keypair"})

    def key(self) -> bytearray:
        return decode(self.execute({"op": "generate_key"})["key"])

    def canonical(self, document: Any) -> bytearray:
        return decode(
            self.execute({"op": "canonicalize", "document": document})["bytes"]
        )

    def sign(
        self,
        secret_key: str,
        operation: str,
        document: Mapping[str, Any],
        device_id: str,
    ) -> dict[str, str]:
        if not operation or any(
            c not in "abcdefghijklmnopqrstuvwxyz_" for c in operation
        ):
            raise E2eeError("invalid_operation")
        body = self.canonical(document)
        signed = bytearray(f"arteligo-e2ee-v1\n{operation}\n".encode()) + body
        try:
            if len(body) > 1024 * 1024:
                raise E2eeError("command_too_large")
            signature = self.execute(
                {"op": "sign_bytes", "secret_key": secret_key, "bytes": encode(signed)}
            )["signature"]
            return {
                "device_id": device_id,
                "body_bytes": encode(body),
                "signature": signature,
            }
        finally:
            wipe(body)
            wipe(signed)

    def verify(
        self, public_key: str, operation: str, signed: Mapping[str, Any]
    ) -> dict[str, Any]:
        body = decode(signed.get("body_bytes"))
        message = bytearray(f"arteligo-e2ee-v1\n{operation}\n".encode()) + body
        try:
            if len(body) > 1024 * 1024:
                raise E2eeError("command_too_large")
            self.execute(
                {
                    "op": "verify_bytes",
                    "public_key": public_key,
                    "bytes": encode(message),
                    "signature": signed.get("signature"),
                }
            )
            value = json.loads(body)
            if not isinstance(value, dict):
                raise E2eeError("invalid_command")
            return value
        except (ValueError, TypeError):
            raise E2eeError("invalid_command") from None
        finally:
            wipe(body)
            wipe(message)

    def seal(
        self,
        key: bytes | bytearray,
        plaintext: bytes | bytearray,
        aad: bytes | bytearray,
    ) -> dict[str, Any]:
        return self.execute(
            {
                "op": "aead_seal",
                "key": encode(key),
                "plaintext": encode(plaintext),
                "aad": encode(aad),
            }
        )

    def seal_record(
        self,
        key: bytes | bytearray,
        document: Mapping[str, Any],
        key_aad: bytes | bytearray,
        aad: bytes | bytearray,
        kind: str,
    ) -> str:
        return self.execute(
            {
                "op": "record_seal", "key": encode(key), "document": document,
                "key_aad": encode(key_aad), "aad": encode(aad), "kind": kind,
            }
        )["ciphertext"]

    def open_record(
        self,
        key: bytes | bytearray,
        ciphertext: str,
        key_aad: bytes | bytearray,
        aad: bytes | bytearray,
        kind: str,
    ) -> dict[str, Any]:
        return self.execute(
            {
                "op": "record_open", "key": encode(key), "ciphertext": ciphertext,
                "key_aad": encode(key_aad), "aad": encode(aad), "kind": kind,
            }
        )["document"]

    def open(
        self,
        key: bytes | bytearray,
        envelope: Mapping[str, Any],
        aad: bytes | bytearray,
    ) -> bytearray:
        return decode(
            self.execute(
                {
                    "op": "aead_open",
                    "key": encode(key),
                    "envelope": {"v": 1, "suite": "AES-256-GCM", **envelope},
                    "aad": encode(aad),
                }
            )["plaintext"]
        )
