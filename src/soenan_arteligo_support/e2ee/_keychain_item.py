from __future__ import annotations

from contextlib import ExitStack
import ctypes as c
from ctypes.util import find_library


def replace(service: str, name: str, value: str, *, protected: bool = False) -> None:
    security = c.CDLL(find_library("Security"))
    core = c.CDLL(find_library("CoreFoundation"))
    pointer = c.c_void_p
    core.CFRelease.argtypes = [pointer]
    core.CFStringCreateWithCString.argtypes = [pointer, c.c_char_p, c.c_uint32]
    core.CFStringCreateWithCString.restype = pointer
    core.CFDataCreate.argtypes = [pointer, pointer, c.c_long]
    core.CFDataCreate.restype = pointer
    core.CFDictionaryCreate.argtypes = [pointer, pointer, pointer, c.c_long, pointer, pointer]
    core.CFDictionaryCreate.restype = pointer
    security.SecItemUpdate.argtypes = [pointer, pointer]
    security.SecItemUpdate.restype = c.c_int32
    security.SecItemAdd.argtypes = [pointer, pointer]
    security.SecItemAdd.restype = c.c_int32
    security.SecItemCopyMatching.argtypes = [pointer, c.POINTER(pointer)]
    security.SecItemCopyMatching.restype = c.c_int32

    def constant(name: str):
        return pointer.in_dll(security, name)

    with ExitStack() as resources:
        def own(value):
            if not value:
                raise MemoryError
            resources.callback(core.CFRelease, value)
            return value

        def text(value: str):
            return own(core.CFStringCreateWithCString(None, value.encode(), 0x08000100))

        def dictionary(entries):
            keys = (pointer * len(entries))(*(constant(key) for key in entries))
            values = (pointer * len(entries))(*entries.values())
            return own(core.CFDictionaryCreate(
                None, keys, values, len(entries),
                c.byref(c.c_byte.in_dll(core, "kCFTypeDictionaryKeyCallBacks")),
                c.byref(c.c_byte.in_dll(core, "kCFTypeDictionaryValueCallBacks")),
            ))

        query = {
            "kSecClass": constant("kSecClassGenericPassword"),
            "kSecAttrService": text(service),
            "kSecAttrAccount": text(name),
        }
        raw = value.encode()
        data = own(core.CFDataCreate(None, raw, len(raw)))
        update = {"kSecValueData": data}
        if protected:
            update["kSecAttrSynchronizable"] = pointer.in_dll(core, "kCFBooleanFalse")
        existing = pointer()
        result = security.SecItemCopyMatching(dictionary({
            **query,
            "kSecMatchLimit": constant("kSecMatchLimitOne"),
            "kSecReturnPersistentRef": pointer.in_dll(core, "kCFBooleanTrue"),
        }), c.byref(existing))
        if result == -25300:
            result = security.SecItemAdd(dictionary({**query, **update}), None)
        elif result == 0:
            own(existing)
            result = security.SecItemUpdate(
                dictionary({"kSecValuePersistentRef": existing}),
                dictionary(update),
            )
        if result != 0:
            raise OSError
