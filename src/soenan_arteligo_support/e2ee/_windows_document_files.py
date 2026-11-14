from __future__ import annotations

import ctypes as c
import os
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from ctypes import wintypes as w
from pathlib import PureWindowsPath
from typing import cast

from ._credential_lock import windows_security


class _FileInformation(c.Structure):
    _fields_ = [
        ("attributes", w.DWORD),
        ("creation", w.FILETIME),
        ("access", w.FILETIME),
        ("write", w.FILETIME),
        ("volume", w.DWORD),
        ("size_high", w.DWORD),
        ("size_low", w.DWORD),
        ("links", w.DWORD),
        ("index_high", w.DWORD),
        ("index_low", w.DWORD),
    ]


class _Acl(c.Structure):
    _fields_ = [
        ("revision", w.BYTE),
        ("reserved", w.BYTE),
        ("size", w.WORD),
        ("count", w.WORD),
        ("reserved2", w.WORD),
    ]


class _AllowedAce(c.Structure):
    _fields_ = [
        ("kind", w.BYTE),
        ("flags", w.BYTE),
        ("size", w.WORD),
        ("mask", w.DWORD),
        ("sid", w.DWORD),
    ]


class _WindowsFileHandles:
    _path: str

    def __init__(self, resources: ExitStack):
        self._kernel, self._security, self._attributes, self._sid, self._user = (
            resources.enter_context(windows_security())
        )
        kernel, security = self._kernel, self._security
        kernel.CreateFileW.argtypes = [
            w.LPCWSTR,
            w.DWORD,
            w.DWORD,
            c.POINTER(type(self._attributes)),
            w.DWORD,
            w.DWORD,
            w.HANDLE,
        ]
        kernel.CreateFileW.restype = w.HANDLE
        kernel.CreateDirectoryW.argtypes = [
            w.LPCWSTR,
            c.POINTER(type(self._attributes)),
        ]
        kernel.CreateDirectoryW.restype = w.BOOL
        kernel.GetFileType.argtypes = [w.HANDLE]
        kernel.GetFileType.restype = w.DWORD
        kernel.GetFileInformationByHandle.argtypes = [
            w.HANDLE,
            c.POINTER(_FileInformation),
        ]
        kernel.GetFileInformationByHandle.restype = w.BOOL
        kernel.GetDriveTypeW.argtypes = [w.LPCWSTR]
        kernel.GetDriveTypeW.restype = w.UINT
        kernel.GetVolumeInformationW.argtypes = [
            w.LPCWSTR,
            w.LPWSTR,
            w.DWORD,
            c.POINTER(w.DWORD),
            c.POINTER(w.DWORD),
            c.POINTER(w.DWORD),
            w.LPWSTR,
            w.DWORD,
        ]
        kernel.GetVolumeInformationW.restype = w.BOOL
        kernel.FlushFileBuffers.argtypes = [w.HANDLE]
        kernel.FlushFileBuffers.restype = w.BOOL
        security.GetSecurityInfo.argtypes = [
            w.HANDLE,
            c.c_int,
            w.DWORD,
            c.POINTER(w.LPVOID),
            c.POINTER(w.LPVOID),
            c.POINTER(w.LPVOID),
            c.POINTER(w.LPVOID),
            c.POINTER(w.LPVOID),
        ]
        security.GetSecurityInfo.restype = w.DWORD
        security.GetSecurityDescriptorControl.argtypes = [
            w.LPVOID,
            c.POINTER(w.WORD),
            c.POINTER(w.DWORD),
        ]
        security.GetSecurityDescriptorControl.restype = w.BOOL
        security.GetAce.argtypes = [w.LPVOID, w.DWORD, c.POINTER(w.LPVOID)]
        security.GetAce.restype = w.BOOL
        security.EqualSid.argtypes = [w.LPVOID, w.LPVOID]
        security.EqualSid.restype = w.BOOL

    def _validate_volume(self, local: PureWindowsPath) -> None:
        kernel = self._kernel
        if kernel.GetDriveTypeW(local.anchor) != 3:
            raise PermissionError
        filesystem, flags = c.create_unicode_buffer(32), w.DWORD()
        if not kernel.GetVolumeInformationW(
            local.anchor,
            None,
            0,
            None,
            None,
            c.byref(flags),
            filesystem,
            len(filesystem),
        ):
            raise c.WinError(c.get_last_error())
        # NTFS write-through requests flush the file's metadata as well as its data.
        if filesystem.value != "NTFS" or not flags.value & 0x8:
            raise PermissionError

    def _open(
        self,
        path: str,
        *,
        directory: bool = False,
        create: bool = False,
    ):
        access = 0x20080 if directory else 0x80020000
        if create:
            access = 0x40020080
        handle = self._kernel.CreateFileW(
            path,
            access,
            1,
            c.byref(self._attributes),
            1 if create else 3,
            0x00200000
            | (0x02000000 if directory else 0)
            | (0x80000000 if create else 0),
            None,
        )
        if handle == w.HANDLE(-1).value:
            raise c.WinError(c.get_last_error())
        return handle

    def _validate(
        self, handle, *, directory: bool = False, private: bool = True
    ) -> None:
        info = _FileInformation()
        if not self._kernel.GetFileInformationByHandle(handle, c.byref(info)):
            raise c.WinError(c.get_last_error())
        if (
            self._kernel.GetFileType(handle) != 1
            or info.attributes & 0x400
            or bool(info.attributes & 0x10) != directory
            or (not directory and info.links != 1)
        ):
            raise PermissionError
        if not private:
            return
        self._validate_security(handle)

    def _validate_security(self, handle, *, object_type: int = 1) -> None:
        owner, dacl, descriptor = w.LPVOID(), w.LPVOID(), w.LPVOID()
        result = self._security.GetSecurityInfo(
            handle,
            object_type,
            0x5,
            c.byref(owner),
            None,
            c.byref(dacl),
            None,
            c.byref(descriptor),
        )
        if result:
            raise c.WinError(result)
        try:
            control, revision = w.WORD(), w.DWORD()
            if not self._security.GetSecurityDescriptorControl(
                descriptor, c.byref(control), c.byref(revision)
            ):
                raise c.WinError(c.get_last_error())
            if (
                not owner
                or not self._security.EqualSid(owner, self._sid)
                or not dacl
                or not control.value & 0x1000
                or c.cast(dacl, c.POINTER(_Acl)).contents.count != 1
            ):
                raise PermissionError
            ace = w.LPVOID()
            if not self._security.GetAce(dacl, 0, c.byref(ace)):
                raise c.WinError(c.get_last_error())
            allowed = c.cast(ace, c.POINTER(_AllowedAce)).contents
            if (
                allowed.kind != 0
                or allowed.flags != 0
                or allowed.mask
                not in {
                    0x10000000,
                    0x1F01FF if object_type == 1 else 0x1F0001,
                }
                or not self._security.EqualSid(
                    c.addressof(allowed) + _AllowedAce.sid.offset, self._sid
                )
            ):
                raise PermissionError
        finally:
            self._kernel.LocalFree(descriptor)

    @contextmanager
    def _file(self, name: str, *, create: bool = False) -> Iterator[int]:
        handle = self._open(os.path.join(self._path, name), create=create)
        try:
            self._validate(handle)
            yield handle
        finally:
            self._kernel.CloseHandle(handle)

    @contextmanager
    def _stream(self, handle, *, write: bool = False):
        import msvcrt

        self._kernel.DuplicateHandle.argtypes = [
            w.HANDLE,
            w.HANDLE,
            w.HANDLE,
            c.POINTER(w.HANDLE),
            w.DWORD,
            w.BOOL,
            w.DWORD,
        ]
        self._kernel.DuplicateHandle.restype = w.BOOL
        process = self._kernel.GetCurrentProcess()
        duplicate = w.HANDLE()
        if not self._kernel.DuplicateHandle(
            process, handle, process, c.byref(duplicate), 0, False, 2
        ):
            raise c.WinError(c.get_last_error())
        duplicate_handle = cast(int, duplicate.value)
        try:
            descriptor = msvcrt.open_osfhandle(
                duplicate_handle,
                (os.O_WRONLY if write else os.O_RDONLY) | os.O_BINARY,
            )
        except BaseException:
            self._kernel.CloseHandle(duplicate)
            raise
        try:
            stream = os.fdopen(descriptor, "wb" if write else "rb")
        except BaseException:
            os.close(descriptor)
            raise
        with stream:
            yield stream
