from __future__ import annotations

import ctypes
import errno
import os
import platform
import stat
import sys
from contextlib import ExitStack, contextmanager
from pathlib import PurePosixPath
from typing import BinaryIO, Iterator

from ._crypto import E2eeError


class _OpenHow(ctypes.Structure):
    _fields_ = [("flags", ctypes.c_uint64), ("mode", ctypes.c_uint64), ("resolve", ctypes.c_uint64)]


def _open_beneath(root: int, path: str, flags: int, mode: int = 0) -> int:
    if sys.platform != "linux" or platform.machine().lower() not in {
        "x86_64", "amd64", "aarch64", "arm64", "riscv64", "i386", "i686",
    }:
        raise E2eeError("safe_file_access_unavailable")
    libc = ctypes.CDLL(None, use_errno=True)
    how = _OpenHow(flags | os.O_CLOEXEC | getattr(os, "O_LARGEFILE", 0), mode, 0x02 | 0x04 | 0x08)
    result = libc.syscall(
        ctypes.c_long(437), ctypes.c_int(root), ctypes.c_char_p(os.fsencode(path)),
        ctypes.byref(how), ctypes.sizeof(how),
    )
    if result < 0:
        failure = ctypes.get_errno()
        if failure in {errno.ENOSYS, errno.EINVAL, errno.EOPNOTSUPP}:
            raise E2eeError("safe_file_access_unavailable")
        if failure in {errno.ELOOP, errno.EXDEV, errno.EAGAIN}:
            raise E2eeError("file_path_not_allowed")
        raise OSError(failure, os.strerror(failure))
    return result


def _relative(path: str) -> PurePosixPath:
    if (
        not isinstance(path, str) or not path or "\0" in path or "\\" in path
        or path.startswith("/") or any(part in {"", ".", ".."} for part in path.split("/"))
    ):
        raise E2eeError("file_path_not_allowed")
    return PurePosixPath(path)


class GrantedOutput:
    def __init__(self, root: int, path: PurePosixPath):
        self._parents = ExitStack()
        self._published = False
        try:
            self._parent = _open_beneath(root, str(path.parent), os.O_RDONLY | os.O_DIRECTORY)
            self._parents.callback(os.close, self._parent)
            self._name = path.name
            descriptor = _open_beneath(
                self._parent, ".", os.O_TMPFILE | os.O_RDWR, 0o600
            )
            self.stream = self._parents.enter_context(os.fdopen(descriptor, "w+b"))
        except BaseException:
            self._parents.close()
            raise

    def publish(self) -> None:
        if self._published:
            raise E2eeError("output_already_published")
        self.stream.flush()
        os.fsync(self.stream.fileno())
        try:
            os.link(
                f"/proc/self/fd/{self.stream.fileno()}", self._name,
                src_dir_fd=0, dst_dir_fd=self._parent, follow_symlinks=True,
            )
        except FileExistsError:
            raise E2eeError("destination_exists") from None
        self._published = True

    def close(self) -> None:
        self._parents.close()


class FileBoundary:
    """Opened directory objects are the authority, not their replaceable pathnames."""

    def __init__(self, input_directory: str | None, output_directory: str | None):
        self._roots = ExitStack()
        self._input: int | None = None
        self._output: int | None = None
        self.file_access_supported = True
        self.input_directory = os.path.abspath(input_directory) if input_directory else None
        self.output_directory = os.path.abspath(output_directory) if output_directory else None
        try:
            if self.input_directory and self.output_directory:
                common = os.path.commonpath([self.input_directory, self.output_directory])
                if common in {self.input_directory, self.output_directory}:
                    raise E2eeError("input_output_directories_must_be_separate")
            if self.input_directory or self.output_directory:
                if sys.platform != "linux":
                    raise E2eeError("safe_file_access_unavailable")
                filesystem = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
                self._roots.callback(os.close, filesystem)
                for name, path in (("_input", self.input_directory), ("_output", self.output_directory)):
                    if path is not None:
                        descriptor = _open_beneath(
                            filesystem, path.lstrip("/") or ".", os.O_RDONLY | os.O_DIRECTORY
                        )
                        self._roots.callback(os.close, descriptor)
                        setattr(self, name, descriptor)
                if self._input is not None and self._output is not None:
                    left, right = os.fstat(self._input), os.fstat(self._output)
                    if (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino):
                        raise E2eeError("input_output_directories_must_be_separate")
        except E2eeError as error:
            self._roots.close()
            self._input = self._output = None
            if error.code != "safe_file_access_unavailable":
                raise
            self.file_access_supported = False
        except BaseException:
            self._roots.close()
            raise

    def input_name(self, path: str) -> str:
        if not self.file_access_supported:
            raise E2eeError("safe_file_access_unavailable")
        if self._input is None:
            raise E2eeError("input_directory_not_granted")
        return _relative(path).name

    @contextmanager
    def input(self, path: str) -> Iterator[BinaryIO]:
        self.input_name(path)
        descriptor = _open_beneath(self._input, str(_relative(path)), os.O_RDONLY | os.O_NONBLOCK)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise E2eeError("input_must_be_regular_file")
            stream = os.fdopen(descriptor, "rb")
        except BaseException:
            os.close(descriptor)
            raise
        with stream:
            yield stream

    @contextmanager
    def output(self, path: str) -> Iterator[GrantedOutput]:
        if not self.file_access_supported:
            raise E2eeError("safe_file_access_unavailable")
        if self._output is None:
            raise E2eeError("output_directory_not_granted")
        output = GrantedOutput(self._output, _relative(path))
        try:
            yield output
        finally:
            output.close()

    def close(self) -> None:
        self._roots.close()
