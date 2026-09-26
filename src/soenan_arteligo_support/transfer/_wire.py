from __future__ import annotations

from typing import Any


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def is_base64url(value: str) -> bool:
    return bool(value) and all(
        character.isascii() and (character.isalnum() or character in "-_")
        for character in value
    )
