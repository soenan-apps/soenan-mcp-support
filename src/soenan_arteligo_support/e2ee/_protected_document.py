from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field, replace
import hashlib
import json
import os
import re
import secrets
import sys
from typing import Iterator, Protocol

from ._credential_lock import private_directory, private_subdirectory, validate_private_handle
from ._crypto import E2eeCrypto, E2eeError, decode, encode, wipe


_PREFIX = "soenan:protected-document:1:"
_DESCRIPTOR = re.compile(
    re.escape(_PREFIX) + r"([0-9a-f]{32}):([A-Za-z0-9_-]{43}):(-|[0-9a-f]{64})"
)
_BLOB_NAME = re.compile(r"[0-9a-f]{64}\.sealed")
_BOUND = "bound"


class _NativeItem(Protocol):
    def read(self) -> str | None: ...
    def replace(self, value: str) -> None: ...


class _DocumentFiles(Protocol):
    def names(self) -> list[str]: ...
    def read(self, name: str) -> bytes: ...
    def publish(self, name: str, value: bytes | bytearray) -> None: ...
    def remove(self, name: str) -> None: ...


@dataclass(frozen=True)
class _Descriptor:
    incarnation: str
    key: bytearray = field(repr=False)
    digest: str | None

    @classmethod
    def parse(cls, value: str) -> _Descriptor:
        match = _DESCRIPTOR.fullmatch(value)
        if match is None:
            raise E2eeError("secure_store_corrupt")
        key = decode(match[2])
        if len(key) != 32:
            wipe(key)
            raise E2eeError("secure_store_corrupt")
        return cls(match[1], key, None if match[3] == "-" else match[3])

    def serialize(self) -> str:
        return f"{_PREFIX}{self.incarnation}:{encode(self.key)}:{self.digest or '-'}"


class _PosixDocumentFiles:
    def __init__(self, directory: int):
        self._directory = directory

    @contextmanager
    def _file(self, name: str, *, create: bool = False) -> Iterator[int]:
        flags = os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
        flags |= os.O_WRONLY | os.O_CREAT | os.O_EXCL if create else os.O_RDONLY
        descriptor = os.open(name, flags, 0o600, dir_fd=self._directory)
        try:
            validate_private_handle(descriptor)
            yield descriptor
        finally:
            os.close(descriptor)

    def names(self) -> list[str]:
        return os.listdir(self._directory)

    def read(self, name: str) -> bytes:
        with self._file(name) as descriptor:
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                return stream.read()

    def publish(self, name: str, value: bytes | bytearray) -> None:
        with self._file(name, create=True) as descriptor:
            with os.fdopen(descriptor, "wb", closefd=False) as stream:
                stream.write(value)
                stream.flush()
                os.fsync(descriptor)
                os.fsync(self._directory)
                if sys.platform == "darwin":
                    import fcntl

                    fcntl.fcntl(descriptor, fcntl.F_FULLFSYNC)

    def remove(self, name: str) -> None:
        with self._file(name):
            os.unlink(name, dir_fd=self._directory)
            os.fsync(self._directory)


@contextmanager
def _document_files(namespace: str) -> Iterator[_DocumentFiles]:
    if sys.platform == "win32":
        from ._windows_document_files import document_files

        with document_files(namespace) as files:
            yield files
    else:
        with private_directory(".soenan-protected-documents") as root:
            with private_subdirectory(root, namespace) as directory:
                yield _PosixDocumentFiles(directory)


class _ProtectedDocument:
    def __init__(self, namespace: bytes, native: _NativeItem,
                 files: _DocumentFiles, crypto: E2eeCrypto):
        self._namespace, self._native, self._files, self._crypto = namespace, native, files, crypto
        self._head: str | None = None
        self._descriptor: _Descriptor | None = None
        self._value: str | None = None
        self._usable = True

    def load(self) -> None:
        self._head = self._native.read()
        if self._head is None:
            if self._files.names():
                raise E2eeError("secure_store_key_lost")
            return
        if self._head.startswith("soenan:protected-document:"):
            descriptor = _Descriptor.parse(self._head)
            self._descriptor = descriptor
            if descriptor.digest is not None:
                self._value = self._open(descriptor, descriptor.digest)
            self._bound()
            self._prune(descriptor.digest)
            return
        # Conversion replaces this same native item only after the exact value is durable.
        self._value = self._head
        descriptor = self._new_descriptor()
        self._descriptor = descriptor
        self._bound()
        self._prune(None)
        self._publish(descriptor, self._head)

    def _new_descriptor(self) -> _Descriptor:
        return _Descriptor(secrets.token_hex(16), self._crypto.key(), None)

    def _aad(self, descriptor: _Descriptor) -> bytes:
        return _PREFIX.encode("ascii") + self._namespace + b"\0" + descriptor.incarnation.encode("ascii")

    def _open(self, descriptor: _Descriptor, digest: str) -> str:
        try:
            blob = self._files.read(digest + ".sealed")
            if len(blob) < 28 or hashlib.sha256(blob).hexdigest() != digest:
                raise E2eeError("secure_store_corrupt")
            plaintext = self._crypto.open(
                descriptor.key, {"nonce": encode(blob[:12]), "ciphertext": encode(blob[12:])},
                self._aad(descriptor),
            )
            try:
                return plaintext.decode("utf-8")
            finally:
                wipe(plaintext)
        except (FileNotFoundError, UnicodeError):
            raise E2eeError("secure_store_corrupt") from None
        except E2eeError as error:
            if error.code in {"authentication_failed", "invalid_encoding", "invalid_input"}:
                raise E2eeError("secure_store_corrupt") from None
            raise

    def _bound(self) -> None:
        try:
            if self._files.read(_BOUND) != b"":
                raise E2eeError("secure_store_corrupt")
        except FileNotFoundError:
            self._files.publish(_BOUND, b"")

    def _check_current(self) -> None:
        if not self._usable:
            raise E2eeError("secure_store_context_closed")
        if self._native.read() != self._head:
            self._usable = False
            raise E2eeError("secure_store_conflict")

    def _prune(self, digest: str | None) -> None:
        self._check_current()
        committed = digest + ".sealed" if digest is not None else None
        names = self._files.names()
        if any(name != _BOUND and _BLOB_NAME.fullmatch(name) is None for name in names):
            raise E2eeError("secure_store_corrupt")
        for name in names:
            if name not in {_BOUND, committed}:
                self._files.remove(name)

    def _commit(self, descriptor: _Descriptor) -> None:
        self._check_current()
        proposed = descriptor.serialize()
        try:
            try:
                self._native.replace(proposed)
            except Exception:
                # Native APIs may report failure after persisting the replacement.
                pass
            observed = self._native.read()
            if observed != proposed:
                if observed == self._head:
                    raise E2eeError("secure_store_write_failed")
                raise E2eeError("secure_store_conflict")
        except BaseException:
            self._usable = False
            raise
        # Only a reread of the native commit pointer may adopt the proposed value.
        self._head = proposed
        self._descriptor = descriptor

    def _publish(self, descriptor: _Descriptor, value: str) -> None:
        plaintext = bytearray(value, "utf-8")
        try:
            envelope = self._crypto.seal(descriptor.key, plaintext, self._aad(descriptor))
        finally:
            wipe(plaintext)
        blob = decode(envelope["nonce"])
        blob.extend(decode(envelope["ciphertext"]))
        digest = hashlib.sha256(blob).hexdigest()
        self._files.publish(digest + ".sealed", blob)
        self._commit(replace(descriptor, digest=digest))
        self._value = value

    def read(self) -> str | None:
        self._check_current()
        return self._value

    def replace(self, value: str) -> None:
        self._check_current()
        if value == self._value:
            return
        descriptor = self._descriptor
        if descriptor is None:
            descriptor = self._new_descriptor()
            self._descriptor = descriptor
            self._commit(descriptor)
        self._bound()
        self._prune(descriptor.digest)
        self._publish(descriptor, value)

    def close(self) -> None:
        self._usable = False
        if self._descriptor is not None:
            wipe(self._descriptor.key)
        self._head = self._value = None


@contextmanager
def protected_document(service: str, name: str, native: _NativeItem,
                       crypto: E2eeCrypto) -> Iterator[_ProtectedDocument]:
    if sys.platform == "win32":
        from ._windows_item import canonical_target

        # The primary/compound slot may disappear, but the logical service cannot change.
        service = canonical_target(service)
    namespace = json.dumps([service, name], ensure_ascii=True, separators=(",", ":")).encode("ascii")
    with _document_files(hashlib.sha256(namespace).hexdigest()) as files:
        document = _ProtectedDocument(namespace, native, files, crypto)
        try:
            document.load()
            yield document
        finally:
            document.close()
