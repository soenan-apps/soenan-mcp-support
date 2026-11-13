from __future__ import annotations

import ctypes as c
import os
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from ctypes import wintypes as w
from hashlib import sha256
from pathlib import Path, PureWindowsPath
from uuid import uuid4

from ._windows_document_files import _FileInformation, _WindowsFileHandles


class WindowsProfileFiles(_WindowsFileHandles):
    def __init__(self, resources: ExitStack, path: Path, profile: str, *, create: bool):
        super().__init__(resources)
        if len(profile) != 64 or any(ch not in "0123456789abcdef" for ch in profile):
            raise ValueError("profile must be a SHA-256 hexadecimal digest")
        original = PureWindowsPath(path)
        if ".." in original.parts:
            raise PermissionError
        root = PureWindowsPath(os.path.abspath(path))
        if (
            not root.is_absolute()
            or len(root.drive) != 2
            or root.drive[1] != ":"
            or not root.drive[0].isascii()
            or not root.drive[0].isalpha()
            or any(
                part.endswith((".", " "))
                or any(ch in part for ch in ':<>"|?*')
                or any(ord(ch) < 32 for ch in part)
                for part in root.parts[1:]
            )
        ):
            raise PermissionError
        self._validate_volume(root)
        kernel = self._kernel
        current = PureWindowsPath(root.anchor)
        for part in (None, *root.parts[1:]):
            if part is not None:
                current /= part
                if create and not kernel.CreateDirectoryW(
                    str(current), c.byref(self._attributes)
                ):
                    if c.get_last_error() != 183:
                        raise c.WinError(c.get_last_error())
            handle = self._open(str(current), directory=True)
            resources.callback(kernel.CloseHandle, handle)
            self._validate(handle, directory=True, private=current == root)
        info = _FileInformation()
        if not kernel.GetFileInformationByHandle(handle, c.byref(info)):
            raise c.WinError(c.get_last_error())
        identity = (
            f"{self._user}:{info.volume}:{info.index_high}:{info.index_low}:{profile}"
        )
        kernel.CreateMutexW.argtypes = [
            c.POINTER(type(self._attributes)),
            w.BOOL,
            w.LPCWSTR,
        ]
        kernel.CreateMutexW.restype = w.HANDLE
        kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        kernel.WaitForSingleObject.restype = w.DWORD
        kernel.ReleaseMutex.argtypes = [w.HANDLE]
        kernel.ReleaseMutex.restype = w.BOOL
        kernel.MoveFileExW.argtypes = [w.LPCWSTR, w.LPCWSTR, w.DWORD]
        kernel.MoveFileExW.restype = w.BOOL
        self._mutex = kernel.CreateMutexW(
            c.byref(self._attributes),
            False,
            "Global\\SoenanProfile-" + sha256(identity.encode()).hexdigest(),
        )
        if not self._mutex:
            raise c.WinError(c.get_last_error())
        resources.callback(kernel.CloseHandle, self._mutex)
        self._validate_security(self._mutex, object_type=6)
        # Keep creation and the caller's first envelope publication under one lock.
        resources.enter_context(self.locked())
        directory = root / profile
        self.fresh = False
        if create:
            self.fresh = bool(
                kernel.CreateDirectoryW(str(directory), c.byref(self._attributes))
            )
            if not self.fresh and c.get_last_error() != 183:
                raise c.WinError(c.get_last_error())
        handle = self._open(str(directory), directory=True)
        resources.callback(kernel.CloseHandle, handle)
        self._validate(handle, directory=True)
        self._path = str(directory)

    @contextmanager
    def locked(self) -> Iterator[None]:
        result = self._kernel.WaitForSingleObject(self._mutex, 0xFFFFFFFF)
        if result not in (0, 0x80):
            raise c.WinError(c.get_last_error())
        try:
            yield
        finally:
            if not self._kernel.ReleaseMutex(self._mutex):
                raise c.WinError(c.get_last_error())

    def read(self) -> bytes:
        with self._file("state.json") as handle:
            with self._stream(handle) as stream:
                return stream.read()

    def replace(self, value: bytes) -> None:
        try:
            with self._file("state.json"):
                pass
        except FileNotFoundError:
            pass
        name = ".state-" + uuid4().hex + ".tmp"
        temporary = os.path.join(self._path, name)
        published = False
        created = False
        try:
            with self._file(name, create=True) as handle:
                created = True
                with self._stream(handle, write=True) as stream:
                    stream.write(value)
                    stream.flush()
                    if not self._kernel.FlushFileBuffers(handle):
                        raise c.WinError(c.get_last_error())
            if not self._kernel.MoveFileExW(
                temporary, os.path.join(self._path, "state.json"), 0x9
            ):
                raise c.WinError(c.get_last_error())
            published = True
        finally:
            if created and not published:
                try:
                    os.unlink(temporary)
                except FileNotFoundError:
                    pass


@contextmanager
def profile_files(
    path: Path, profile: str, *, create: bool
) -> Iterator[WindowsProfileFiles]:
    with ExitStack() as resources:
        yield WindowsProfileFiles(resources, path, profile, create=create)
