from __future__ import annotations

from contextlib import ExitStack, contextmanager
import ctypes
import hashlib
import os
import stat
import sys
from typing import Iterator

@contextmanager
def private_directory(name: str) -> Iterator[int]:
    import pwd

    home = pwd.getpwuid(os.getuid()).pw_dir
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    if not os.path.isabs(home):
        raise PermissionError
    with ExitStack() as handles:
        parent = os.open("/", flags)
        handles.callback(os.close, parent)
        for part in home.split("/"):
            if not part:
                continue
            if part in {".", ".."}:
                raise PermissionError
            parent = os.open(part, flags, dir_fd=parent)
            handles.callback(os.close, parent)
            info = os.fstat(parent)
            if info.st_uid not in {0, os.getuid()} or info.st_mode & 0o022:
                raise PermissionError
        if os.fstat(parent).st_uid != os.getuid():
            raise PermissionError
        with private_subdirectory(parent, name) as directory:
            yield directory


@contextmanager
def private_subdirectory(parent: int, name: str) -> Iterator[int]:
    try:
        os.mkdir(name, mode=0o700, dir_fd=parent)
        os.fsync(parent)
    except FileExistsError:
        pass
    directory = os.open(
        name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
        dir_fd=parent,
    )
    try:
        validate_private_handle(directory, directory=True)
        yield directory
    finally:
        os.close(directory)


def validate_private_handle(descriptor: int, *, directory: bool = False) -> None:
    info = os.fstat(descriptor)
    if (
        info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) != (0o700 if directory else 0o600)
        or not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode))
        or (not directory and info.st_nlink != 1)
    ):
        raise PermissionError
    if sys.platform == "darwin":
        libc = ctypes.CDLL(None, use_errno=True)
        libc.acl_get_fd_np.argtypes = [ctypes.c_int, ctypes.c_int]
        libc.acl_get_fd_np.restype = ctypes.c_void_p
        libc.acl_get_entry.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
        libc.acl_free.argtypes = [ctypes.c_void_p]
        acl = libc.acl_get_fd_np(descriptor, 0x100)
        if not acl:
            raise PermissionError
        try:
            entry = ctypes.c_void_p()
            if libc.acl_get_entry(acl, 0, ctypes.byref(entry)) != -1:
                raise PermissionError
        finally:
            libc.acl_free(acl)


@contextmanager
def credential_lock(service: str, name: str) -> Iterator[None]:
    if sys.platform == "win32":
        with _windows_lock():
            yield
        return
    import fcntl
    with private_directory(".soenan-credential-locks") as directory:
        digest = hashlib.sha256((service + "\n" + name).encode()).hexdigest()
        lock_fd = os.open(
            digest, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o600, dir_fd=directory,
        )
        try:
            validate_private_handle(lock_fd)
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(lock_fd)


@contextmanager
def windows_security():
    from ctypes import wintypes as w

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    security = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.LocalFree.argtypes = [w.HLOCAL]
    kernel.LocalFree.restype = w.HLOCAL
    security.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, ctypes.POINTER(w.HANDLE)]
    security.GetTokenInformation.argtypes = [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD, ctypes.POINTER(w.DWORD)]
    security.ConvertSidToStringSidW.argtypes = [w.LPVOID, ctypes.POINTER(w.LPWSTR)]
    security.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [w.LPCWSTR, w.DWORD, ctypes.POINTER(w.LPVOID), ctypes.POINTER(w.DWORD)]

    class Attributes(ctypes.Structure):
        _fields_ = [("length", w.DWORD), ("descriptor", w.LPVOID), ("inherit", w.BOOL)]

    token = w.HANDLE()
    sid_string = w.LPWSTR()
    descriptor = w.LPVOID()
    try:
        if not security.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
            raise ctypes.WinError(ctypes.get_last_error())
        size = w.DWORD()
        security.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
        info = ctypes.create_string_buffer(size.value)
        if not security.GetTokenInformation(token, 1, info, size, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        sid = ctypes.cast(info, ctypes.POINTER(w.LPVOID))[0]
        if not security.ConvertSidToStringSidW(sid, ctypes.byref(sid_string)):
            raise ctypes.WinError(ctypes.get_last_error())
        user = sid_string.value
        if not security.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            f"O:{user}D:P(A;;GA;;;{user})", 1, ctypes.byref(descriptor), None
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        attributes = Attributes(ctypes.sizeof(Attributes), descriptor, False)
        yield kernel, security, attributes, sid, user
    finally:
        if descriptor:
            kernel.LocalFree(descriptor)
        if sid_string:
            kernel.LocalFree(ctypes.cast(sid_string, w.HLOCAL))
        if token:
            kernel.CloseHandle(token)


@contextmanager
def _windows_lock() -> Iterator[None]:
    from ctypes import wintypes as w

    with windows_security() as (kernel, _, attributes, _, user):
        kernel.CreateMutexW.argtypes = [ctypes.POINTER(type(attributes)), w.BOOL, w.LPCWSTR]
        kernel.CreateMutexW.restype = w.HANDLE
        kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        kernel.WaitForSingleObject.restype = w.DWORD
        kernel.ReleaseMutex.argtypes = [w.HANDLE]
        # All names share the legacy service slot, and Windows names ignore case.
        mutex = kernel.CreateMutexW(
            ctypes.byref(attributes), False,
            "Global\\SoenanCredential-" + hashlib.sha256(user.encode()).hexdigest(),
        )
        if not mutex:
            raise ctypes.WinError(ctypes.get_last_error())
        acquired = False
        try:
            result = kernel.WaitForSingleObject(mutex, 0xFFFFFFFF)
            if result not in (0, 0x80):
                raise ctypes.WinError(ctypes.get_last_error())
            acquired = True
            # The caller always reloads, including after native mutex abandonment.
            yield
        finally:
            if acquired:
                kernel.ReleaseMutex(mutex)
            kernel.CloseHandle(mutex)
