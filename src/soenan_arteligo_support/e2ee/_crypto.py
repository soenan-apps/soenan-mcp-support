from __future__ import annotations

import base64


class E2eeError(Exception):
    """Stable error codes; never include plaintext, keys, or HTTP bodies."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def encode(value: bytes | bytearray) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def decode(value: object) -> bytearray:
    if not isinstance(value, str):
        raise E2eeError("invalid_encoding")
    try:
        data = bytearray(base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True))
    except (ValueError, base64.binascii.Error):
        raise E2eeError("invalid_encoding") from None
    if encode(data) != value:
        wipe(data)
        raise E2eeError("invalid_encoding")
    return data


def wipe(value: bytearray) -> None:
    value[:] = b"\0" * len(value)


class LocalDocumentCrypto:
    def __init__(self):
        from ._core import CryptoCore
        self._core = CryptoCore()

    def key(self):
        from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
        response = self._core.execute_utility(crypto.CoreUtilityRequest(random=crypto.RandomInput(length=32)))
        return bytearray(response.random_bytes)

    def seal(self, key, plaintext, aad):
        from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
        response = self._core.execute_utility(crypto.CoreUtilityRequest(seal_local=crypto.LocalSeal(
            key=bytes(key), plaintext=bytes(plaintext), aad=bytes(aad)))).local_sealed
        return {"nonce": encode(response.value.nonce), "ciphertext": encode(response.value.ciphertext)}

    def open(self, key, envelope, aad):
        from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
        response = self._core.execute_utility(crypto.CoreUtilityRequest(open_local=crypto.LocalOpen(
            key=bytes(key), value=crypto.AeadValue(nonce=bytes(decode(envelope["nonce"])),
                ciphertext=bytes(decode(envelope["ciphertext"]))), aad=bytes(aad))))
        return bytearray(response.local_plaintext)
