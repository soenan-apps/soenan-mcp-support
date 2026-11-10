from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto


@dataclass(frozen=True)
class AcceptedCommand:
    command: crypto.SignedBytes
    result: dict[str, Any]
    finalization_error: Exception | None = field(
        default=None, compare=False, repr=False
    )
