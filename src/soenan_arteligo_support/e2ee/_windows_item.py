from __future__ import annotations

import ctypes as c
from ctypes import wintypes as w

PREFIX = b"soenan:oauth:v2\x00"
_LOCALE_NAME_INVARIANT = ""
_LCMAP_UPPERCASE = 0x00000200


def canonical_target(target: str) -> str:
    if not target or "\0" in target:
        raise OSError
    source_length = len(target.encode("utf-16-le")) // 2
    api = c.WinDLL("kernel32", use_last_error=True)
    api.LCMapStringEx.argtypes = [
        w.LPCWSTR, w.DWORD, w.LPCWSTR, c.c_int, w.LPWSTR, c.c_int,
        w.LPVOID, w.LPVOID, w.LPARAM,
    ]
    api.LCMapStringEx.restype = c.c_int
    # Default filesystem casing avoids Python's and linguistic folding's extra equivalences.
    size = api.LCMapStringEx(
        _LOCALE_NAME_INVARIANT, _LCMAP_UPPERCASE, target, source_length,
        None, 0, None, None, 0,
    )
    if not size:
        raise c.WinError(c.get_last_error())
    mapped = c.create_unicode_buffer(size)
    written = api.LCMapStringEx(
        _LOCALE_NAME_INVARIANT, _LCMAP_UPPERCASE, target, source_length,
        mapped, size, None, None, 0,
    )
    if not written:
        raise c.WinError(c.get_last_error())
    return c.wstring_at(mapped, written)


class _Credential(c.Structure):
    _fields_ = [
        ("Flags", w.DWORD), ("Type", w.DWORD), ("TargetName", w.LPWSTR),
        ("Comment", w.LPWSTR), ("LastWritten", w.FILETIME),
        ("CredentialBlobSize", w.DWORD), ("CredentialBlob", c.POINTER(c.c_ubyte)),
        ("Persist", w.DWORD), ("AttributeCount", w.DWORD), ("Attributes", w.LPVOID),
        ("TargetAlias", w.LPWSTR), ("UserName", w.LPWSTR),
    ]


def replace(target: str, username: str, value: str, persistence: int, *,
            oauth: bool, protected: bool = False) -> None:
    api = c.WinDLL("advapi32", use_last_error=True)
    pointer = c.POINTER(_Credential)
    api.CredReadW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, c.POINTER(pointer)]
    api.CredReadW.restype = w.BOOL
    api.CredWriteW.argtypes = [pointer, w.DWORD]
    api.CredWriteW.restype = w.BOOL
    api.CredFree.argtypes = [w.LPVOID]
    api.CredFree.restype = None
    existing = pointer()
    try:
        if api.CredReadW(target, 1, 0, c.byref(existing)):
            if existing.contents.UserName != username:
                raise OSError
            credential = _Credential.from_buffer_copy(existing.contents)
        else:
            status = c.get_last_error()
            if status != 1168:
                raise c.WinError(status)
            credential = _Credential(Type=1, TargetName=target, UserName=username,
                Comment="Stored using python-keyring", Persist=persistence)
        raw = PREFIX + value.encode("utf-8") if oauth else value.encode("utf-16-le")
        if protected and len(raw) > 2560:
            raise OSError
        blob = c.create_string_buffer(raw)
        credential.CredentialBlob = c.cast(blob, c.POINTER(c.c_ubyte))
        credential.CredentialBlobSize = len(raw)
        if oauth or protected:
            credential.Persist = 2
        if not api.CredWriteW(c.byref(credential), 0):
            raise c.WinError(c.get_last_error())
    finally:
        if existing:
            api.CredFree(existing)
