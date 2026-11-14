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
        data = bytearray(
            base64.b64decode(
                value + "=" * (-len(value) % 4), altchars=b"-_", validate=True
            )
        )
    except ValueError:
        raise E2eeError("invalid_encoding") from None
    if encode(data) != value:
        wipe(data)
        raise E2eeError("invalid_encoding")
    return data


def wipe(value: bytearray) -> None:
    value[:] = b"\0" * len(value)
