from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import threading
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path

from ._credential_lock import validate_private_handle
from ._crypto import E2eeError


class _FileItem:
    def __init__(
        self,
        values: dict[str, str],
        name: str,
        save: Callable[[dict[str, str]], None],
    ):
        self._values, self._name, self._save = values, name, save
        self.active = True

    def read(self) -> str | None:
        if not self.active:
            raise E2eeError("profile_store_context_closed")
        return self._values.get(self._name)

    def replace(self, value: str) -> None:
        if not self.active:
            raise E2eeError("profile_store_context_closed")
        self._values[self._name] = value
        self._save(self._values)


class FileProfileStore:
    """Owner-only profile files shared by desktop and cloud SDK processes."""

    def __init__(
        self,
        directory: str | os.PathLike[str] | None = None,
        profile: str = "default",
        *,
        create: bool = False,
    ):
        if directory is None:
            from platformdirs import user_state_path

            directory = user_state_path("soenan-arteligo-support", appauthor=False)
        self._path = Path(directory).absolute()
        self._profile = hashlib.sha256(profile.encode()).hexdigest()
        self._thread_lock = threading.RLock()
        self._local = threading.local()
        with self._transaction(create=create):
            pass

    @contextmanager
    def _directory(self, *, create: bool = False) -> Iterator[int]:
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        parent = os.open(self._path.anchor, flags)
        try:
            for part in self._path.parts[1:-1]:
                if create:
                    try:
                        os.mkdir(part, 0o700, dir_fd=parent)
                        os.fsync(parent)
                    except FileExistsError:
                        pass
                child = os.open(part, flags, dir_fd=parent)
                os.close(parent)
                parent = child
            name = self._path.name
            if create:
                try:
                    os.mkdir(name, 0o700, dir_fd=parent)
                    os.fsync(parent)
                except FileExistsError:
                    pass
            root = os.open(name, flags, dir_fd=parent)
            try:
                validate_private_handle(root, directory=True)
                with self._locked(root):
                    if create:
                        try:
                            os.mkdir(self._profile, 0o700, dir_fd=root)
                            os.fsync(root)
                            fresh = True
                        except FileExistsError:
                            fresh = False
                    else:
                        fresh = False
                    profile = os.open(self._profile, flags, dir_fd=root)
                    try:
                        validate_private_handle(profile, directory=True)
                        if fresh:
                            self._save(profile, {})
                        yield profile
                    finally:
                        os.close(profile)
            finally:
                os.close(root)
        finally:
            os.close(parent)

    @contextmanager
    def _locked(self, directory: int) -> Iterator[None]:
        import fcntl

        with self._thread_lock:
            descriptor = os.open(
                self._profile + ".lock",
                os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o600,
                dir_fd=directory,
            )
            try:
                validate_private_handle(descriptor)
                fcntl.flock(descriptor, fcntl.LOCK_EX)
                yield
            finally:
                os.close(descriptor)

    @staticmethod
    def _load(directory: int) -> dict[str, str]:
        descriptor = os.open(
            "state.json",
            os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
            dir_fd=directory,
        )
        try:
            validate_private_handle(descriptor)
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                return FileProfileStore._decode(stream.read())
        finally:
            os.close(descriptor)

    @staticmethod
    def _decode(raw: bytes) -> dict[str, str]:
        envelope = json.loads(raw)
        if (
            not isinstance(envelope, dict)
            or set(envelope) != {"version", "values", "sha256"}
            or type(envelope["version"]) is not int
            or envelope["version"] != 1
            or not isinstance(envelope["values"], dict)
            or any(
                type(k) is not str or type(v) is not str
                for k, v in envelope["values"].items()
            )
        ):
            raise ValueError
        values = envelope["values"]
        encoded = json.dumps(values, sort_keys=True, separators=(",", ":")).encode()
        if envelope["sha256"] != hashlib.sha256(encoded).hexdigest():
            raise ValueError
        return values

    @staticmethod
    def _encode(values: dict[str, str]) -> bytes:
        encoded = json.dumps(values, sort_keys=True, separators=(",", ":")).encode()
        return json.dumps(
            {
                "version": 1,
                "values": values,
                "sha256": hashlib.sha256(encoded).hexdigest(),
            },
            separators=(",", ":"),
        ).encode()

    @staticmethod
    def _save(directory: int, values: dict[str, str]) -> None:
        envelope = FileProfileStore._encode(values)
        temporary = ".write-" + secrets.token_hex(16)
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o600,
            dir_fd=directory,
        )
        try:
            validate_private_handle(descriptor)
            with os.fdopen(descriptor, "wb", closefd=False) as stream:
                stream.write(envelope)
                stream.flush()
                os.fsync(descriptor)
            os.replace(
                temporary, "state.json", src_dir_fd=directory, dst_dir_fd=directory
            )
            os.fsync(directory)
        finally:
            os.close(descriptor)
            try:
                os.unlink(temporary, dir_fd=directory)
            except FileNotFoundError:
                pass

    @contextmanager
    def _transaction(
        self, *, create: bool = False
    ) -> Iterator[tuple[Callable[[dict[str, str]], None], dict[str, str]]]:
        with self._thread_lock:
            active = getattr(self._local, "transaction", None)
            if active is not None:
                yield active
                return
            try:
                with ExitStack() as resources:
                    if sys.platform == "win32":
                        from ._windows_profile_files import profile_files

                        files = resources.enter_context(
                            profile_files(self._path, self._profile, create=create)
                        )
                        if files.fresh:
                            files.replace(self._encode({}))
                        values = self._decode(files.read())

                        def save(current: dict[str, str]) -> None:
                            files.replace(self._encode(current))

                    else:
                        directory = resources.enter_context(
                            self._directory(create=create)
                        )
                        values = self._load(directory)

                        def save(current: dict[str, str]) -> None:
                            self._save(directory, current)

                    transaction = save, values
                    self._local.transaction = transaction
                    try:
                        yield transaction
                    finally:
                        del self._local.transaction
            except (OSError, ValueError, TypeError):
                raise E2eeError("profile_store_unavailable") from None

    @contextmanager
    def credential(self, name: str) -> Iterator[_FileItem]:
        with self._transaction() as (save, values):
            item = _FileItem(values, name, save)
            try:
                yield item
            finally:
                item.active = False

    def read(self, name: str) -> str | None:
        with self.credential(name) as item:
            return item.read()

    def write(self, name: str, value: str) -> None:
        with self.credential(name) as item:
            item.replace(value)

    def delete(self, name: str) -> None:
        with self._transaction() as (save, values):
            values.pop(name, None)
            save(values)
