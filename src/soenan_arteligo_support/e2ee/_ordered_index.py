from __future__ import annotations

from bisect import bisect_right
from collections.abc import Callable, Iterator
from typing import Any

from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._crypto import E2eeError
from ._directory import _key, _split


class OrderedIndex:
    """One operation over the shared encrypted ordered tree."""

    def __init__(
        self,
        read: Callable,
        mint_id: Callable[[], str],
        kind: str,
        incarnation: str,
    ):
        self.read, self.mint_id, self.kind = read, mint_id, kind
        self.loaded: dict[str, dict[str, Any]] = {}
        self.writes: dict[str, dict[str, Any]] = {}
        self.incarnation = incarnation

    def node(self, reference: domain.RecordReference) -> dict[str, Any]:
        identifier = reference.id
        staged = self.writes.get(identifier)
        record = (
            {
                **staged,
                "revision": staged["expected_revision"] + 1,
                "payload_type": "content",
            }
            if staged
            else self.loaded.get(identifier)
        )
        if record is None:
            record = self.read([identifier]).get(identifier)
            if record is not None:
                self.loaded[identifier] = record
        if (
            record is None
            or record["payload_type"] != "content"
            or record["kind"] != self.kind
            or record["revision"] != reference.revision
            or record["incarnation"] != reference.incarnation
        ):
            raise E2eeError("revision_conflict")
        value = record["value"]
        if not isinstance(value, (domain.OrderedIndexLeaf, domain.OrderedIndexBranch)):
            raise E2eeError("invalid_conversation_index")
        if isinstance(value, domain.OrderedIndexBranch):
            keys = [_key(item.first) for item in value.children]
        else:
            keys = [_key(item) for item in value.entries]
        branch = isinstance(value, domain.OrderedIndexBranch)
        if keys != sorted(set(keys)) or (branch and not keys):
            raise E2eeError("invalid_conversation_index")
        return record

    def check_range(
        self,
        node: domain.OrderedIndexLeaf | domain.OrderedIndexBranch,
        expected_first: tuple[bytes, bytes] | None = None,
        before: tuple[bytes, bytes] | None = None,
    ) -> None:
        if isinstance(node, domain.OrderedIndexLeaf):
            keys = [_key(item) for item in node.entries]
        else:
            keys = [_key(item.first) for item in node.children]
        if (expected_first is not None and (not keys or keys[0] != expected_first)) or (
            before is not None and keys and keys[-1] >= before
        ):
            raise E2eeError("invalid_conversation_index")

    def walk(
        self,
        reference: domain.RecordReference,
        after: tuple[bytes, bytes] | None = None,
        ancestors: frozenset[str] = frozenset(),
        expected_first: tuple[bytes, bytes] | None = None,
        before: tuple[bytes, bytes] | None = None,
    ) -> Iterator[domain.OrderedIndexEntry]:
        node = self.node(reference)["value"]
        if reference.id in ancestors:
            raise E2eeError("invalid_conversation_index")
        self.check_range(node, expected_first, before)
        if isinstance(node, domain.OrderedIndexLeaf):
            for entry in node.entries:
                if after is None or _key(entry) > after:
                    value = domain.OrderedIndexEntry()
                    value.CopyFrom(entry)
                    yield value
            return
        children = node.children
        start = (
            max(0, bisect_right([_key(child.first) for child in children], after) - 1)
            if after
            else 0
        )
        for index in range(start, len(children)):
            child = children[index]
            following = (
                _key(children[index + 1].first) if index + 1 < len(children) else before
            )
            yield from self.walk(
                child.node,
                after,
                ancestors | {reference.id},
                _key(child.first),
                following,
            )

    def page(
        self,
        root: domain.RecordReference | None,
        *,
        after: tuple[str, str] | None = None,
        limit: int = 100,
    ) -> tuple[list[domain.OrderedIndexEntry], tuple[str, str] | None]:
        if type(limit) is not int or limit < 1:
            raise E2eeError("invalid_cursor")
        entries = []
        if root is not None:
            key = (
                _key(domain.OrderedEntryKey(name=after[0], id=after[1]))
                if after
                else None
            )
            for entry in self.walk(root, key):
                entries.append(entry)
                if len(entries) > limit:
                    break
        more = len(entries) > limit
        values = entries[:limit]
        cursor = (values[-1].key.name, values[-1].key.id) if more else None
        return values, cursor

    def save(
        self,
        identifier: str,
        value: domain.OrderedIndexLeaf | domain.OrderedIndexBranch,
    ) -> domain.RecordReference:
        previous = self.loaded.get(identifier)
        self.writes[identifier] = {
            "record_id": identifier,
            "kind": self.kind,
            "expected_revision": previous["revision"] if previous else 0,
            "incarnation": previous["incarnation"] if previous else self.incarnation,
            "value": value,
        }
        return domain.RecordReference(
            id=identifier,
            revision=self.writes[identifier]["expected_revision"] + 1,
            incarnation=self.writes[identifier]["incarnation"],
        )

    def store_node(
        self, identifier: str, node: domain.OrderedIndexLeaf | domain.OrderedIndexBranch
    ) -> list[domain.OrderedIndexChild]:
        children = []
        if isinstance(node, domain.OrderedIndexBranch):
            for index, piece in enumerate(_split(list(node.children))):
                ref = self.save(
                    identifier if index == 0 else self.mint_id(),
                    domain.OrderedIndexBranch(children=piece),
                )
                children.append(
                    domain.OrderedIndexChild(first=piece[0].first, node=ref)
                )
        else:
            for index, piece in enumerate(_split(list(node.entries))):
                ref = self.save(
                    identifier if index == 0 else self.mint_id(),
                    domain.OrderedIndexLeaf(entries=piece),
                )
                children.append(domain.OrderedIndexChild(first=piece[0].key, node=ref))
        return children

    def insert(
        self,
        reference: domain.RecordReference,
        entry: domain.OrderedIndexEntry,
        ancestors: frozenset[str] = frozenset(),
    ) -> list[domain.OrderedIndexChild]:
        if reference.id in ancestors:
            raise E2eeError("invalid_conversation_index")
        record = self.node(reference)
        node = record["value"]
        if isinstance(node, domain.OrderedIndexLeaf):
            entries = list(node.entries)
            if any(_key(value) == _key(entry) for value in entries):
                raise E2eeError("revision_conflict")
            entries.insert(
                bisect_right([_key(value) for value in entries], _key(entry)), entry
            )
            return self.store_node(
                record["record_id"], domain.OrderedIndexLeaf(entries=entries)
            )
        children = list(node.children)
        index = max(
            0, bisect_right([_key(child.first) for child in children], _key(entry)) - 1
        )
        self.check_range(
            self.node(children[index].node)["value"], _key(children[index].first)
        )
        children[index : index + 1] = self.insert(
            children[index].node, entry, ancestors | {reference.id}
        )
        return self.store_node(
            record["record_id"], domain.OrderedIndexBranch(children=children)
        )

    def mutation(
        self, root: domain.RecordReference | None, entry: domain.OrderedIndexEntry
    ) -> tuple[domain.RecordReference, list[dict[str, Any]]]:
        if root is None:
            root = self.save(self.mint_id(), domain.OrderedIndexLeaf())
        children = self.insert(root, entry)
        while len(children) > 1:
            children = self.store_node(
                self.mint_id(), domain.OrderedIndexBranch(children=children)
            )
        return children[0].node, list(self.writes.values())
