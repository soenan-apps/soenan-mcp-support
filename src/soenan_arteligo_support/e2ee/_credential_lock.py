from __future__ import annotations

from contextlib import contextmanager
import ctypes
import hashlib
import os
import stat
import sys
from typing import Iterator


@contextmanager
def credential_lock(service: str, name: str) -> Iterator[None]:
    if sys.platform == "win32":
        with _windows_lock():
            yield
        return
    import fcntl
    import pwd

    home = pwd.getpwuid(os.getuid()).pw_dir
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    home_fd = os.open(home, flags)
    directory_fd = None
    lock_fd = None
    try:
        try:
            os.mkdir(".soenan-credential-locks", mode=0o700, dir_fd=home_fd)
        except FileExistsError:
            pass
        directory_fd = os.open(".soenan-credential-locks", flags, dir_fd=home_fd)
        info = os.fstat(directory_fd)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise PermissionError
        digest = hashlib.sha256((service + "\n" + name).encode()).hexdigest()
        lock_fd = os.open(
            digest,
            os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o600,
            dir_fd=directory_fd,
        )
        info = os.fstat(lock_fd)
        if (
            info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
        ):
            raise PermissionError
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        yield
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
        if directory_fd is not None:
            os.close(directory_fd)
        os.close(home_fd)


@contextmanager
def _windows_lock() -> Iterator[None]:
    from ctypes import wintypes as w

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    security = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.LocalFree.argtypes = [w.HLOCAL]
    security.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, ctypes.POINTER(w.HANDLE)]
    security.GetTokenInformation.argtypes = [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD, ctypes.POINTER(w.DWORD)]
    security.ConvertSidToStringSidW.argtypes = [w.LPVOID, ctypes.POINTER(w.LPWSTR)]
    security.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [w.LPCWSTR, w.DWORD, ctypes.POINTER(w.LPVOID), ctypes.POINTER(w.DWORD)]

    class Attributes(ctypes.Structure):
        _fields_ = [("length", w.DWORD), ("descriptor", w.LPVOID), ("inherit", w.BOOL)]

    kernel.CreateMutexW.argtypes = [ctypes.POINTER(Attributes), w.BOOL, w.LPCWSTR]
    kernel.CreateMutexW.restype = w.HANDLE
    kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
    kernel.WaitForSingleObject.restype = w.DWORD
    kernel.ReleaseMutex.argtypes = [w.HANDLE]
    token = w.HANDLE()
    sid_string = w.LPWSTR()
    descriptor = w.LPVOID()
    mutex = None
    acquired = False
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
            f"D:P(A;;GA;;;{user})", 1, ctypes.byref(descriptor), None
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        attributes = Attributes(ctypes.sizeof(Attributes), descriptor, False)
        # All names share the legacy service slot, and Windows names ignore case.
        mutex = kernel.CreateMutexW(
            ctypes.byref(attributes), False,
            "Global\\SoenanCredential-" + hashlib.sha256(user.encode()).hexdigest(),
        )
        if not mutex:
            raise ctypes.WinError(ctypes.get_last_error())
        result = kernel.WaitForSingleObject(mutex, 0xFFFFFFFF)
        if result not in (0, 0x80):
            raise ctypes.WinError(ctypes.get_last_error())
        acquired = True
        # The caller always reloads, including after native mutex abandonment.
        yield
    finally:
        if acquired:
            kernel.ReleaseMutex(mutex)
        if mutex:
            kernel.CloseHandle(mutex)
        if descriptor:
            kernel.LocalFree(descriptor)
        if sid_string:
            kernel.LocalFree(ctypes.cast(sid_string, w.HLOCAL))
        if token:
            kernel.CloseHandle(token)
