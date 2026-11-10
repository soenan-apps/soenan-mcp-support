from __future__ import annotations

import sys
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, ExitStack, contextmanager
from typing import TYPE_CHECKING, Protocol

from ._credential_lock import credential_lock
from ._crypto import E2eeError, LocalDocumentCrypto

if TYPE_CHECKING:
    from keyring.backends.SecretService import Keyring as SecretServiceKeyring
    from keyring.backends.Windows import DecodingCredential, WinVaultKeyring
    from secretstorage import Item


class SecureStore(Protocol):
    def read(self, name: str) -> str | None: ...
    def write(self, name: str, value: str) -> None: ...
    def delete(self, name: str) -> None: ...


class CredentialItem(Protocol):
    def read(self) -> str | None: ...
    def replace(self, value: str) -> None: ...


class ProfileSecureStore(SecureStore, Protocol):
    def credential(self, name: str) -> AbstractContextManager[CredentialItem]: ...


class _CredentialItem:
    def __init__(self, read: Callable[[], str | None], replace: Callable[[str], None]):
        self._read, self._replace = read, replace
        self.active = True

    def read(self) -> str | None:
        if not self.active:
            raise E2eeError("secure_store_context_closed")
        return self._read()

    def replace(self, value: str) -> None:
        if not self.active:
            raise E2eeError("secure_store_context_closed")
        self._replace(value)


class SystemSecureStore:
    """Only system-backed keyrings; plaintext fallback backends are not accepted."""

    _windows_backend: WinVaultKeyring
    _secret_backend: SecretServiceKeyring

    def __init__(self, profile: str):
        try:
            import keyring

            backend = keyring.get_keyring()
            if sys.platform == "win32":
                from keyring.backends.Windows import WinVaultKeyring

                if type(backend) is not WinVaultKeyring:
                    raise E2eeError("secure_store_unavailable")
                self._windows_backend = backend
            elif sys.platform == "darwin":
                from keyring.backends.macOS import Keyring as MacOSKeyring

                if type(backend) is not MacOSKeyring:
                    raise E2eeError("secure_store_unavailable")
            else:
                from keyring.backends.SecretService import (
                    Keyring as SecretServiceKeyring,
                )

                if type(backend) is not SecretServiceKeyring:
                    raise E2eeError("secure_store_unavailable")
                self._secret_backend = backend
            self._backend = backend
        except (ImportError, RuntimeError):
            raise E2eeError("secure_store_unavailable") from None
        self._service = f"app.soenan.arteligo.local.v1:{profile}"
        self._document_crypto: LocalDocumentCrypto | None = None

    @staticmethod
    def _windows_value(name: str, credential: DecodingCredential) -> str:
        from ._windows_item import PREFIX

        blob = credential["CredentialBlob"]
        if name.startswith("oauth:") and blob.startswith(PREFIX):
            return blob[len(PREFIX) :].decode("utf-8")
        return credential.value

    def _read(self, name: str) -> str | None:
        if sys.platform == "win32":
            primary = self._windows_backend._read_credential(self._service)
            if primary and primary["UserName"] == name:
                if name.startswith(("device:", "trust:")):
                    alias = self._windows_backend._read_credential(
                        self._windows_backend._compound_name(name, self._service)
                    )
                    if alias:
                        raise E2eeError("secure_store_conflict")
                return self._windows_value(name, primary)
            alias = self._windows_backend._read_credential(
                self._windows_backend._compound_name(name, self._service)
            )
            if alias and alias["UserName"] != name:
                raise E2eeError("secure_store_unavailable")
            return self._windows_value(name, alias) if alias else None
        return self._backend.get_password(self._service, name)

    def _windows_document_target(self, name: str) -> str:
        primary = self._windows_backend._read_credential(self._service)
        if primary and primary["UserName"] == name:
            return primary["TargetName"]
        compound = self._windows_backend._compound_name(name, self._service)
        alias = self._windows_backend._read_credential(compound)
        return alias["TargetName"] if alias else compound

    def _windows_replace(self, name: str, value: str) -> None:
        from ._windows_item import replace

        primary = self._windows_backend._read_credential(self._service)
        compound = self._windows_backend._compound_name(name, self._service)
        if primary and primary["UserName"] == name:
            target = self._service
        else:
            target = compound
        if name.startswith(("device:", "trust:")):
            target = self._windows_document_target(name)
        replace(
            target,
            name,
            value,
            self._windows_backend.persist,
            oauth=name.startswith("oauth:"),
            protected=name.startswith(("device:", "trust:")),
        )
        if name.startswith("oauth:") and target == self._service:
            alias = self._windows_backend._read_credential(compound)
            if alias and alias["UserName"] == name:
                self._windows_backend._delete_password(compound)

    @contextmanager
    def credential(self, name: str) -> Iterator[CredentialItem]:
        item = None
        connection = None
        try:
            with credential_lock(self._service, name):
                if sys.platform == "win32":
                    item = _CredentialItem(
                        lambda: self._read(name),
                        lambda value: self._windows_replace(name, value),
                    )
                elif sys.platform == "darwin":
                    from ._keychain_item import replace as replace_keychain_item

                    item = _CredentialItem(
                        lambda: self._read(name),
                        lambda value: replace_keychain_item(
                            self._service,
                            name,
                            value,
                            protected=name.startswith(("device:", "trust:")),
                        ),
                    )
                else:
                    collection = self._secret_backend.get_preferred_collection()
                    connection = collection.connection
                    attributes = self._secret_backend._query(self._service, name)
                    native: Item | None = None

                    def read() -> str | None:
                        nonlocal native
                        matches = list(collection.search_items(attributes))
                        if len(matches) > 1:
                            raise E2eeError("secure_store_unavailable")
                        native = matches[0] if matches else None
                        if native is None:
                            return None
                        self._secret_backend.unlock(native)
                        secret = native.get_secret()
                        collection.session = native.session
                        return secret.decode("utf-8")

                    read()

                    def replace_secret(value: str) -> None:
                        nonlocal native
                        if native is None:
                            native = collection.create_item(
                                "Soenan profile credentials",
                                self._secret_backend._query(
                                    self._service,
                                    name,
                                    application=self._secret_backend.appid,
                                ),
                                value.encode("utf-8"),
                                replace=False,
                            )
                        else:
                            native.set_secret(value.encode("utf-8"))

                    item = _CredentialItem(read, replace_secret)
                with ExitStack() as resources:
                    exposed = item
                    if name.startswith(("device:", "trust:")):
                        from ._protected_document import protected_document

                        if self._document_crypto is None:
                            self._document_crypto = LocalDocumentCrypto()
                        document = resources.enter_context(
                            protected_document(
                                self._service,
                                name,
                                item,
                                self._document_crypto,
                            )
                        )
                        exposed = _CredentialItem(document.read, document.replace)
                    try:
                        yield exposed
                    finally:
                        exposed.active = False
        except E2eeError:
            raise
        except Exception:
            raise E2eeError("secure_store_unavailable") from None
        finally:
            if item is not None:
                item.active = False
            if connection is not None:
                connection.close()

    def read(self, name: str) -> str | None:
        if name.startswith("oauth:"):
            raise E2eeError("credential_context_required")
        if name.startswith(("device:", "trust:")):
            with self.credential(name) as item:
                return item.read()
        try:
            if sys.platform == "win32":
                with credential_lock(self._service, name):
                    return self._read(name)
            return self._read(name)
        except Exception:
            raise E2eeError("secure_store_unavailable") from None

    def write(self, name: str, value: str) -> None:
        if name.startswith(("oauth:", "device:", "trust:")):
            raise E2eeError("credential_context_required")
        try:
            if sys.platform == "win32":
                with credential_lock(self._service, name):
                    self._windows_replace(name, value)
            else:
                self._backend.set_password(self._service, name, value)
        except Exception:
            raise E2eeError("secure_store_unavailable") from None

    def delete(self, name: str) -> None:
        if name.startswith(("oauth:", "device:", "trust:")):
            raise E2eeError("credential_context_required")
        try:
            if sys.platform == "win32":
                with credential_lock(self._service, name):
                    if self._read(name) is not None:
                        self._backend.delete_password(self._service, name)
            elif self._read(name) is not None:
                self._backend.delete_password(self._service, name)
        except Exception:
            raise E2eeError("secure_store_unavailable") from None
