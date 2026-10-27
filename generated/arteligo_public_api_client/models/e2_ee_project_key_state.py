from enum import Enum


class E2EeProjectKeyState(str, Enum):
    READY = "ready"
    REKEY_REQUIRED = "rekey_required"
    UNINITIALIZED = "uninitialized"

    def __str__(self) -> str:
        return str(self.value)
