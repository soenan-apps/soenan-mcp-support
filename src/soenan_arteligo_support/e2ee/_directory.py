from __future__ import annotations

import json
import secrets
from bisect import bisect_right
from collections.abc import Iterator
from typing import Any

from ._crypto import E2eeError
from ._records import EncryptedRecords


def _id() -> str:
    return "dpg_" + secrets.token_hex(16)


def _key(entry: dict[str, Any]) -> tuple[bytes, bytes]:
    return entry["name"].encode("utf-16-be"), entry["id"].encode("utf-16-be")


def _fits(value: dict[str, Any]) -> bool:
    items = value.get("entries", value.get("children", []))
    return (
        len(items) <= 64
        and len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode())
        <= 65536
    )


def initial_directory() -> tuple[str, list[dict[str, Any]]]:
    header, leaf = _id(), _id()
    return header, [
        {
            "record_id": leaf,
            "kind": "directory",
            "expected_revision": 0,
            "value": {"format": 2, "type": "leaf", "entries": []},
        },
        {
            "record_id": header,
            "kind": "directory",
            "expected_revision": 0,
            "value": {
                "format": 2,
                "type": "folder",
                "entry": None,
                "parent": None,
                "root": {"id": leaf, "revision": 1},
            },
        },
    ]


class EncryptedDirectory:
    """Read and update only the encrypted paths of one folder index."""

    def __init__(
        self, records: EncryptedRecords, scope: str, *, root_id: str | None = None
    ):
        self.records, self.scope = records, scope
        self.root_id = root_id
        self._loaded: dict[str, dict[str, Any]] = {}
        self._writes: dict[str, dict[str, Any]] = {}

    def _load(self, identifier: str, revision: int | None = None) -> dict[str, Any]:
        staged = self._writes.get(identifier)
        record = (
            {**staged, "revision": staged["expected_revision"] + 1, "deleted": False}
            if staged is not None
            else self._loaded.get(identifier)
        )
        if record is None:
            record = self.records.read(self.scope, [identifier]).get(identifier)
            if record is None or record["deleted"]:
                raise E2eeError("not_found")
            self._loaded[identifier] = record
        if revision is not None and record["revision"] != revision:
            raise E2eeError("revision_conflict")
        return record

    def _folder(self, folder_id: str | None) -> dict[str, Any]:
        if folder_id is None:
            if self.root_id is not None:
                folder_id = self.root_id
            else:
                project = self._load(self.scope)
                directory = project["value"].get("directory", {})
                if directory.get("format") != 2:
                    raise E2eeError("directory_migration_required")
                folder_id = directory["root"]
        folder = self._load(folder_id)
        value = folder["value"]
        if (
            folder["kind"] != "directory"
            or value.get("format") != 2
            or value.get("type") != "folder"
        ):
            raise E2eeError("invalid_directory")
        return folder

    def _node(self, reference: dict[str, Any]) -> dict[str, Any]:
        record = self._load(reference["id"], reference["revision"])
        if record["kind"] != "directory" or record["value"].get("format") != 2:
            raise E2eeError("invalid_directory")
        value = record["value"]
        if value.get("type") not in {"branch", "leaf"} or not _fits(value):
            raise E2eeError("invalid_directory")
        items = (
            value["entries"]
            if value["type"] == "leaf"
            else [item["first"] for item in value["children"]]
        )
        keys = [_key(item) for item in items]
        if keys != sorted(set(keys)) or (value["type"] == "branch" and not keys):
            raise E2eeError("invalid_directory")
        return record

    def _entries(
        self,
        reference: dict[str, Any],
        after: tuple[bytes, bytes] | None,
        depth: int = 0,
    ) -> Iterator[dict[str, Any]]:
        if depth >= 32:
            raise E2eeError("invalid_directory")
        node = self._node(reference)["value"]
        if node["type"] == "leaf":
            for entry in node["entries"]:
                if after is None or _key(entry) > after:
                    yield entry
            return
        children = node["children"]
        start = (
            max(
                0, bisect_right([_key(child["first"]) for child in children], after) - 1
            )
            if after
            else 0
        )
        for child in children[start:]:
            yield from self._entries(child["node"], after, depth + 1)

    def page(
        self,
        *,
        folder_id: str | None = None,
        limit: int = 100,
        cursor: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        attempts = 3 if cursor is None else 1
        for attempt in range(attempts):
            try:
                return self._page(folder_id=folder_id, limit=limit, cursor=cursor)
            except E2eeError as error:
                if error.code != "revision_conflict" or attempt + 1 == attempts:
                    raise
            finally:
                self._loaded.clear()
                self._writes.clear()
        raise E2eeError("revision_conflict")

    def _page(
        self, *, folder_id: str | None, limit: int, cursor: dict[str, Any] | None
    ) -> dict[str, Any]:
        if not 1 <= limit <= 200:
            raise E2eeError("invalid_cursor")
        self._loaded.clear()
        folder = self._folder(folder_id)
        if cursor is not None and (
            cursor.get("folder_id") != folder["record_id"]
            or cursor.get("revision") != folder["revision"]
        ):
            raise E2eeError("revision_conflict")
        after = _key(cursor["last"]) if cursor is not None else None
        entries = []
        for entry in self._entries(folder["value"]["root"], after):
            entries.append(entry)
            if len(entries) > limit:
                break
        latest = self.records.read(self.scope, [folder["record_id"]]).get(
            folder["record_id"]
        )
        if (
            latest is None
            or latest["deleted"]
            or latest["revision"] != folder["revision"]
        ):
            raise E2eeError("revision_conflict")
        more = len(entries) > limit
        entries = entries[:limit]
        following = (
            {
                "folder_id": folder["record_id"],
                "revision": folder["revision"],
                "last": {key: entries[-1][key] for key in ("name", "id")},
            }
            if more
            else None
        )
        self._loaded.clear()
        return {
            "entries": entries,
            "cursor": following,
            "has_more": more,
            "folder_id": folder["record_id"],
            "revision": folder["revision"],
        }

    def _save(self, identifier: str, value: dict[str, Any]) -> dict[str, Any]:
        previous = self._loaded.get(identifier)
        revision = previous["revision"] if previous else 0
        self._writes[identifier] = {
            "record_id": identifier,
            "kind": "directory",
            "expected_revision": revision,
            "value": value,
        }
        return {"id": identifier, "revision": revision + 1}

    def _store_node(
        self, identifier: str, node: dict[str, Any]
    ) -> list[dict[str, Any]]:
        field = "entries" if node["type"] == "leaf" else "children"
        items = node[field]
        pieces = [items]
        while any(not _fits({**node, field: piece}) for piece in pieces):
            refined = []
            for piece in pieces:
                if _fits({**node, field: piece}):
                    refined.append(piece)
                elif len(piece) < 2:
                    raise E2eeError("directory_entry_too_large")
                else:
                    middle = len(piece) // 2
                    refined.extend((piece[:middle], piece[middle:]))
            pieces = refined
        children = []
        for index, piece in enumerate(pieces):
            ref = self._save(
                identifier if index == 0 else _id(), {**node, field: piece}
            )
            first = piece[0] if field == "entries" else piece[0]["first"]
            children.append(
                {"first": {key: first[key] for key in ("name", "id")}, "node": ref}
            )
        return children

    def _insert(
        self, reference: dict[str, Any], entry: dict[str, Any], depth: int = 0
    ) -> list[dict[str, Any]]:
        if depth >= 32:
            raise E2eeError("invalid_directory")
        record = self._node(reference)
        node = record["value"]
        if node["type"] == "leaf":
            items = list(node["entries"])
            if any(
                value["name"] == entry["name"] or value["id"] == entry["id"]
                for value in items
            ):
                raise E2eeError("entry_exists")
            items.insert(
                bisect_right([_key(value) for value in items], _key(entry)), entry
            )
            return self._store_node(record["record_id"], {**node, "entries": items})
        children = list(node["children"])
        index = max(
            0,
            bisect_right([_key(child["first"]) for child in children], _key(entry)) - 1,
        )
        children[index : index + 1] = self._insert(
            children[index]["node"], entry, depth + 1
        )
        return self._store_node(record["record_id"], {**node, "children": children})

    def insertion(
        self, entries: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        try:
            return self._insertion(entries)
        finally:
            self._loaded.clear()
            self._writes.clear()

    def _insertion(
        self, entries: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if (
            not entries
            or len(entries) > 64
            or len({entry.get("parentFolderId") for entry in entries}) != 1
        ):
            raise E2eeError("invalid_batch")
        self._loaded.clear()
        self._writes.clear()
        folder = self._folder(entries[0].get("parentFolderId"))
        preconditions = []
        ancestor = folder
        seen = set()
        while True:
            identifier = ancestor["record_id"]
            if identifier in seen or len(seen) >= 512:
                raise E2eeError("invalid_directory")
            seen.add(identifier)
            preconditions.append(
                {
                    "record_id": identifier,
                    "expected_revision": ancestor["revision"],
                    "require_live": True,
                }
            )
            parent = ancestor["value"]["parent"]
            if parent is None:
                break
            ancestor = self._folder(parent)
        root = folder["value"]["root"]
        for entry in entries:
            first = next(
                self._entries(root, (entry["name"].encode("utf-16-be"), b"")), None
            )
            if first is not None and first["name"] == entry["name"]:
                raise E2eeError("entry_exists")
            children = self._insert(root, entry)
            while len(children) > 1:
                children = self._store_node(
                    _id(), {"format": 2, "type": "branch", "children": children}
                )
            root = children[0]["node"]
        self._save(folder["record_id"], {**folder["value"], "root": root})
        writes = list(self._writes.values())
        self._loaded.clear()
        self._writes.clear()
        return writes, preconditions

    def insert(
        self,
        entry: dict[str, Any],
        *,
        key_epoch: int,
        additional_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        writes, preconditions = self.insertion([entry])
        return self.records.write(
            self.scope,
            key_epoch=key_epoch,
            records=additional_records + writes,
            preconditions=preconditions,
        )
