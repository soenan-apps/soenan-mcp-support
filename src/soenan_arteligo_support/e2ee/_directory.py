from __future__ import annotations

import secrets
from bisect import bisect_right
from collections.abc import Iterator
from typing import Any, TypeVar, cast

from google.protobuf.message import Message
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._crypto import E2eeError
from ._records import EncryptedRecords, ReadRecord
from ._signed_commands import AcceptedCommand


def _id() -> str:
    return "dpg_" + secrets.token_hex(16)


def _entry_values(entry: domain.ProjectEntry) -> domain.ProjectEntryValues:
    return entry.folder if entry.WhichOneof("entry") == "folder" else entry.file.values


def _key(
    entry: domain.ProjectEntry | domain.OrderedEntryKey | domain.OrderedIndexEntry,
) -> tuple[bytes, bytes]:
    if isinstance(entry, domain.ProjectEntry):
        name, identifier = _entry_values(entry).name, entry.id
    else:
        key = entry.key if isinstance(entry, domain.OrderedIndexEntry) else entry
        name, identifier = key.name, key.id
    return name.encode("utf-16-be"), identifier.encode("utf-16-be")


T = TypeVar("T")


def _split(items: list[T]) -> list[list[T]]:
    pieces = [items]
    while any(len(piece) > 64 for piece in pieces):
        refined = []
        for piece in pieces:
            if len(piece) <= 64:
                refined.append(piece)
            else:
                middle = len(piece) // 2
                refined.extend((piece[:middle], piece[middle:]))
        pieces = refined
    return pieces


def _fits(
    value: domain.DirectoryLeaf | domain.OrderedIndexLeaf | domain.OrderedIndexBranch,
) -> bool:
    items = (
        value.children
        if isinstance(value, domain.OrderedIndexBranch)
        else value.entries
    )
    return len(items) <= 64


def initial_directory(incarnation: str) -> tuple[str, list[dict[str, Any]]]:
    header, leaf = _id(), _id()
    return header, [
        {
            "record_id": leaf,
            "kind": "directory",
            "expected_revision": 0,
            "value": domain.DirectoryLeaf(),
        },
        {
            "record_id": header,
            "kind": "directory",
            "expected_revision": 0,
            "value": domain.DirectoryFolder(
                root=domain.RecordReference(
                    id=leaf, revision=1, incarnation=incarnation
                )
            ),
        },
    ]


class EncryptedDirectory:
    """Read and update only the encrypted paths of one folder index."""

    def __init__(self, records: EncryptedRecords, scope: str):
        self.records, self.scope = records, scope
        self._loaded: dict[str, ReadRecord[Message]] = {}
        self._writes: dict[str, dict[str, Any]] = {}

    def _load(
        self, identifier: str, revision: int | None = None
    ) -> dict[str, Any] | ReadRecord[Message]:
        staged = self._writes.get(identifier)
        record = (
            {
                **staged,
                "revision": staged["expected_revision"] + 1,
                "payload_type": "content",
            }
            if staged is not None
            else self._loaded.get(identifier)
        )
        if record is None:
            record = self.records.read(self.scope, [identifier]).get(identifier)
            if record is None or record["payload_type"] != "content":
                raise E2eeError("not_found")
            self._loaded[identifier] = record
        if revision is not None and record["revision"] != revision:
            raise E2eeError("revision_conflict")
        return record

    def _folder(
        self, folder_id: str | None
    ) -> dict[str, Any] | ReadRecord[domain.DirectoryFolder]:
        if folder_id is None:
            project = self._load(self.scope)
            if not isinstance(project["value"], domain.ProjectRootContent):
                raise E2eeError("invalid_directory")
            folder_id = project["value"].directory.root
        folder = self._load(folder_id)
        if folder["kind"] != "directory" or not isinstance(
            folder["value"], domain.DirectoryFolder
        ):
            raise E2eeError("invalid_directory")
        return cast("dict[str, Any] | ReadRecord[domain.DirectoryFolder]", folder)

    def _node(
        self, reference: domain.RecordReference
    ) -> dict[str, Any] | ReadRecord[domain.DirectoryLeaf | domain.OrderedIndexBranch]:
        record = self._load(reference.id, reference.revision)
        if record["incarnation"] != reference.incarnation:
            raise E2eeError("revision_conflict")
        value = record["value"]
        if record["kind"] != "directory" or not isinstance(
            value, (domain.DirectoryLeaf, domain.OrderedIndexBranch)
        ):
            raise E2eeError("invalid_directory")
        branch = isinstance(value, domain.OrderedIndexBranch)
        items = [item.first for item in value.children] if branch else value.entries
        keys = [_key(item) for item in items]
        if keys != sorted(set(keys)) or (branch and not keys):
            raise E2eeError("invalid_directory")
        return cast(
            "dict[str, Any] | ReadRecord[domain.DirectoryLeaf | domain.OrderedIndexBranch]",
            record,
        )

    def _entries(
        self,
        reference: domain.RecordReference,
        after: tuple[bytes, bytes] | None,
        ancestors: frozenset[str] = frozenset(),
    ) -> Iterator[domain.ProjectEntry]:
        if reference.id in ancestors:
            raise E2eeError("invalid_directory")
        node = self._node(reference)["value"]
        if isinstance(node, domain.DirectoryLeaf):
            for entry in node.entries:
                if after is None or _key(entry) > after:
                    yield entry
            return
        children = node.children
        start = (
            max(0, bisect_right([_key(child.first) for child in children], after) - 1)
            if after
            else 0
        )
        for child in children[start:]:
            yield from self._entries(child.node, after, ancestors | {reference.id})

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
        if type(limit) is not int or limit < 1:
            raise E2eeError("invalid_cursor")
        self._loaded.clear()
        folder = self._folder(folder_id)
        if cursor is not None and (
            cursor.get("folder_id") != folder["record_id"]
            or cursor.get("revision") != folder["revision"]
            or cursor.get("incarnation") != folder["incarnation"]
        ):
            raise E2eeError("revision_conflict")
        after = _key(cursor["last"]) if cursor is not None else None
        entries = []
        for entry in self._entries(folder["value"].root, after):
            entries.append(entry)
            if len(entries) > limit:
                break
        latest = self.records.read(self.scope, [folder["record_id"]]).get(
            folder["record_id"]
        )
        if (
            latest is None
            or latest["payload_type"] != "content"
            or latest["revision"] != folder["revision"]
            or latest["incarnation"] != folder["incarnation"]
        ):
            raise E2eeError("revision_conflict")
        more = len(entries) > limit
        entries = entries[:limit]
        following = (
            {
                "folder_id": folder["record_id"],
                "revision": folder["revision"],
                "incarnation": folder["incarnation"],
                "last": domain.OrderedEntryKey(
                    name=_entry_values(entries[-1]).name, id=entries[-1].id
                ),
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
            "incarnation": folder["incarnation"],
        }

    def _save(
        self,
        identifier: str,
        value: domain.DirectoryLeaf
        | domain.OrderedIndexBranch
        | domain.DirectoryFolder,
    ) -> domain.RecordReference:
        previous = self._loaded.get(identifier)
        revision = previous["revision"] if previous else 0
        self._writes[identifier] = {
            "record_id": identifier,
            "kind": "directory",
            "expected_revision": revision,
            "incarnation": previous["incarnation"]
            if previous
            else self.records.operation_id,
            "value": value,
        }
        return domain.RecordReference(
            id=identifier,
            revision=revision + 1,
            incarnation=self._writes[identifier]["incarnation"],
        )

    def _store_node(
        self, identifier: str, node: domain.DirectoryLeaf | domain.OrderedIndexBranch
    ) -> list[domain.OrderedIndexChild]:
        children = []
        if isinstance(node, domain.OrderedIndexBranch):
            for index, piece in enumerate(_split(list(node.children))):
                value = domain.OrderedIndexBranch(children=piece)
                ref = self._save(identifier if index == 0 else _id(), value)
                children.append(
                    domain.OrderedIndexChild(first=piece[0].first, node=ref)
                )
        else:
            for index, piece in enumerate(_split(list(node.entries))):
                leaf = domain.DirectoryLeaf(entries=piece)
                ref = self._save(identifier if index == 0 else _id(), leaf)
                first = domain.OrderedEntryKey(
                    name=_entry_values(piece[0]).name, id=piece[0].id
                )
                children.append(domain.OrderedIndexChild(first=first, node=ref))
        return children

    def _insert(
        self,
        reference: domain.RecordReference,
        entry: domain.ProjectEntry,
        ancestors: frozenset[str] = frozenset(),
    ) -> list[domain.OrderedIndexChild]:
        if reference.id in ancestors:
            raise E2eeError("invalid_directory")
        record = self._node(reference)
        node = record["value"]
        if isinstance(node, domain.DirectoryLeaf):
            items = list(node.entries)
            if any(
                _entry_values(value).name == _entry_values(entry).name
                or value.id == entry.id
                for value in items
            ):
                raise E2eeError("entry_exists")
            items.insert(
                bisect_right([_key(value) for value in items], _key(entry)), entry
            )
            return self._store_node(
                record["record_id"], domain.DirectoryLeaf(entries=items)
            )
        children = list(node.children)
        index = max(
            0, bisect_right([_key(child.first) for child in children], _key(entry)) - 1
        )
        children[index : index + 1] = self._insert(
            children[index].node, entry, ancestors | {reference.id}
        )
        return self._store_node(
            record["record_id"], domain.OrderedIndexBranch(children=children)
        )

    def insertion(
        self, entries: list[domain.ProjectEntry]
    ) -> tuple[list[dict[str, Any]], list[app.RecordPrecondition]]:
        try:
            return self._insertion(entries)
        finally:
            self._loaded.clear()
            self._writes.clear()

    def _insertion(
        self, entries: list[domain.ProjectEntry]
    ) -> tuple[list[dict[str, Any]], list[app.RecordPrecondition]]:
        parents = {
            values.parent_folder_id if values.HasField("parent_folder_id") else None
            for values in map(_entry_values, entries)
        }
        if not entries or len(parents) != 1:
            raise E2eeError("invalid_batch")
        self._loaded.clear()
        self._writes.clear()
        folder = self._folder(parents.pop())
        preconditions = []
        ancestor = folder
        seen = set()
        while True:
            identifier = ancestor["record_id"]
            if identifier in seen:
                raise E2eeError("invalid_directory")
            seen.add(identifier)
            preconditions.append(
                app.RecordPrecondition(
                    id=identifier,
                    expected_revision=ancestor["revision"],
                    require_live=True,
                    incarnation=ancestor["incarnation"],
                )
            )
            if not ancestor["value"].HasField("parent"):
                break
            ancestor = self._folder(ancestor["value"].parent)
        root = folder["value"].root
        for entry in entries:
            name = _entry_values(entry).name
            first = next(self._entries(root, (name.encode("utf-16-be"), b"")), None)
            if first is not None and _entry_values(first).name == name:
                raise E2eeError("entry_exists")
            children = self._insert(root, entry)
            while len(children) > 1:
                children = self._store_node(
                    _id(), domain.OrderedIndexBranch(children=children)
                )
            root = children[0].node
        updated = domain.DirectoryFolder()
        updated.CopyFrom(folder["value"])
        updated.root.CopyFrom(root)
        self._save(folder["record_id"], updated)
        writes = list(self._writes.values())
        self._loaded.clear()
        self._writes.clear()
        return writes, preconditions

    def insert(
        self,
        entry: domain.ProjectEntry,
        *,
        operation_id: str,
        additional_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]] | AcceptedCommand:
        self.records.operation_id = operation_id
        writes, preconditions = self.insertion([entry])
        return self.records.write(
            self.scope,
            records=additional_records + writes,
            preconditions=preconditions,
            operation_id=operation_id,
        )
