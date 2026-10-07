from __future__ import annotations

from bisect import bisect_right
from collections.abc import Callable, Iterator
from copy import deepcopy
from typing import Any

from ._crypto import E2eeError
from ._directory import _fits, _key


class OrderedIndex:
    """One bounded operation over the shared encrypted format-2 tree."""

    def __init__(self, read: Callable, mint_id: Callable[[], str], kind: str):
        self.read, self.mint_id, self.kind = read, mint_id, kind
        self.loaded: dict[str, dict[str, Any]] = {}
        self.writes: dict[str, dict[str, Any]] = {}

    def node(self, reference):
        if (
            not isinstance(reference, dict)
            or set(reference) != {"id", "revision"}
            or not isinstance(reference["id"], str)
            or not 1 <= len(reference["id"]) <= 256
            or type(reference["revision"]) is not int
            or not 1 <= reference["revision"] <= 9_007_199_254_740_991
        ):
            raise E2eeError("invalid_conversation_index")
        identifier = reference["id"]
        staged = self.writes.get(identifier)
        record = (
            {**staged, "revision": staged["expected_revision"] + 1, "deleted": False}
            if staged
            else self.loaded.get(identifier)
        )
        if record is None:
            if len(self.loaded) >= 256:
                raise E2eeError("conversation_read_limit")
            record = self.read([identifier]).get(identifier)
            if record is not None:
                self.loaded[identifier] = record
        if (
            record is None
            or record["deleted"]
            or record["kind"] != self.kind
            or record["revision"] != reference["revision"]
        ):
            raise E2eeError("revision_conflict")
        value = record["value"]
        if value.get("format") != 2 or value.get("type") not in {"branch", "leaf"}:
            raise E2eeError("invalid_conversation_index")
        field = "entries" if value["type"] == "leaf" else "children"
        items = value.get(field)
        if (
            not isinstance(items, list)
            or (field == "children" and not items)
            or not _fits(value)
        ):
            raise E2eeError("invalid_conversation_index")
        try:
            keys = [
                _key(item if field == "entries" else item["first"]) for item in items
            ]
            if field == "children":
                for item in items:
                    ref = item.get("node")
                    if (
                        not isinstance(ref, dict)
                        or set(ref) != {"id", "revision"}
                        or not isinstance(ref["id"], str)
                        or not 1 <= len(ref["id"]) <= 256
                        or type(ref["revision"]) is not int
                        or not 1 <= ref["revision"] <= 9_007_199_254_740_991
                    ):
                        raise E2eeError("invalid_conversation_index")
        except (KeyError, AttributeError, TypeError):
            raise E2eeError("invalid_conversation_index") from None
        if keys != sorted(set(keys)):
            raise E2eeError("invalid_conversation_index")
        return record

    def check_range(self, node, expected_first=None, before=None):
        field = "entries" if node["type"] == "leaf" else "children"
        items = node[field]
        keys = [_key(item if field == "entries" else item["first"]) for item in items]
        if (expected_first is not None and (not keys or keys[0] != expected_first)) or (
            before is not None and keys and keys[-1] >= before
        ):
            raise E2eeError("invalid_conversation_index")

    def walk(
        self,
        reference,
        after=None,
        depth=0,
        ancestors=frozenset(),
        expected_first=None,
        before=None,
    ) -> Iterator[dict]:
        node = self.node(reference)["value"]
        if depth >= 16 or reference["id"] in ancestors:
            raise E2eeError("invalid_conversation_index")
        self.check_range(node, expected_first, before)
        if node["type"] == "leaf":
            for entry in node["entries"]:
                if after is None or _key(entry) > after:
                    yield deepcopy(entry)
            return
        children = node["children"]
        start = (
            max(
                0, bisect_right([_key(child["first"]) for child in children], after) - 1
            )
            if after
            else 0
        )
        for index in range(start, len(children)):
            child = children[index]
            following = (
                _key(children[index + 1]["first"])
                if index + 1 < len(children)
                else before
            )
            yield from self.walk(
                child["node"],
                after,
                depth + 1,
                ancestors | {reference["id"]},
                _key(child["first"]),
                following,
            )

    def page(self, root, *, after=None, limit=100):
        if not 1 <= limit <= 256:
            raise E2eeError("invalid_cursor")
        entries = []
        if root is not None:
            key = _key({"name": after[0], "id": after[1]}) if after else None
            for entry in self.walk(root, key):
                entries.append(entry)
                if len(entries) > limit:
                    break
        more = len(entries) > limit
        values = entries[:limit]
        cursor = (values[-1]["name"], values[-1]["id"]) if more else None
        return values, cursor

    def save(self, identifier, value):
        previous = self.loaded.get(identifier)
        self.writes[identifier] = {
            "record_id": identifier,
            "kind": self.kind,
            "expected_revision": previous["revision"] if previous else 0,
            "value": value,
        }
        if len(self.writes) > 256:
            raise E2eeError("conversation_write_limit")
        return {
            "id": identifier,
            "revision": self.writes[identifier]["expected_revision"] + 1,
        }

    def store_node(self, identifier, node):
        field = "entries" if node["type"] == "leaf" else "children"
        pieces = [node[field]]
        while any(not _fits({**node, field: piece}) for piece in pieces):
            refined = []
            for piece in pieces:
                if _fits({**node, field: piece}):
                    refined.append(piece)
                elif len(piece) < 2:
                    raise E2eeError("conversation_entry_too_large")
                else:
                    middle = len(piece) // 2
                    refined.extend((piece[:middle], piece[middle:]))
            pieces = refined
        children = []
        for index, piece in enumerate(pieces):
            ref = self.save(
                identifier if index == 0 else self.mint_id(), {**node, field: piece}
            )
            first = piece[0] if field == "entries" else piece[0]["first"]
            children.append(
                {"first": {key: first[key] for key in ("name", "id")}, "node": ref}
            )
        return children

    def insert(self, reference, entry, depth=0):
        if depth >= 16:
            raise E2eeError("invalid_conversation_index")
        record = self.node(reference)
        node = record["value"]
        if node["type"] == "leaf":
            entries = list(node["entries"])
            if any(_key(value) == _key(entry) for value in entries):
                raise E2eeError("revision_conflict")
            entries.insert(
                bisect_right([_key(value) for value in entries], _key(entry)), entry
            )
            return self.store_node(record["record_id"], {**node, "entries": entries})
        children = list(node["children"])
        index = max(
            0,
            bisect_right([_key(child["first"]) for child in children], _key(entry)) - 1,
        )
        self.check_range(
            self.node(children[index]["node"])["value"], _key(children[index]["first"])
        )
        children[index : index + 1] = self.insert(
            children[index]["node"], entry, depth + 1
        )
        return self.store_node(record["record_id"], {**node, "children": children})

    def mutation(self, root, entry):
        if root is None:
            root = self.save(
                self.mint_id(), {"format": 2, "type": "leaf", "entries": []}
            )
        children = self.insert(root, deepcopy(entry))
        while len(children) > 1:
            children = self.store_node(
                self.mint_id(), {"format": 2, "type": "branch", "children": children}
            )
        return children[0]["node"], list(self.writes.values())
