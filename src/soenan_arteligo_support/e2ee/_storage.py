from __future__ import annotations

from typing import Protocol

from ._crypto import E2eeError


class SecureStore(Protocol):
    def read(self, name: str) -> str | None: ...
    def write(self, name: str, value: str) -> None: ...
    def delete(self, name: str) -> None: ...


class SystemSecureStore:
    """Only system-backed keyrings; plaintext fallback backends are not accepted."""

    def __init__(self, profile: str):
        try:
            import keyring

            backend = keyring.get_keyring()
            approved = {
                ("keyring.backends.macOS", "Keyring"),
                ("keyring.backends.Windows", "WinVaultKeyring"),
                ("keyring.backends.SecretService", "Keyring"),
            }
            if (type(backend).__module__, type(backend).__name__) not in approved:
                raise E2eeError("secure_store_unavailable")
            self._backend = backend
        except (ImportError, RuntimeError):
            raise E2eeError("secure_store_unavailable") from None
        self._service = f"app.soenan.arteligo.local.v1:{profile}"

    def read(self, name: str) -> str | None:
        try:
            return self._backend.get_password(self._service, name)
        except Exception:
            raise E2eeError("secure_store_unavailable") from None

    def write(self, name: str, value: str) -> None:
        try:
            self._backend.set_password(self._service, name, value)
        except Exception:
            raise E2eeError("secure_store_unavailable") from None

    def delete(self, name: str) -> None:
        if self.read(name) is None:
            return
        try:
            self._backend.delete_password(self._service, name)
        except Exception:
            raise E2eeError("secure_store_unavailable") from None
