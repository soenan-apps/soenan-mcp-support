from __future__ import annotations

import secrets
import json
from typing import Any

from ._crypto import E2eeError
from ._directory import EncryptedDirectory, initial_directory
from ._records import EncryptedRecords


def _write_bytes(writes: list[dict[str, Any]]) -> int:
    return len(json.dumps(writes, ensure_ascii=False, separators=(",", ":")).encode())


def migrate_directory(
    records: EncryptedRecords, scope: str, *, maximum_batches: int = 64
) -> dict[str, Any]:
    """Advance a durable client-side migration without holding the whole tree in memory."""
    if not 1 <= maximum_batches <= 1024:
        raise E2eeError("invalid_batch")
    session = records.session
    metadata = session.scope_metadata(scope, refresh=True)
    epoch = metadata["key_epoch"]
    status = session.api.call("e2eeGetMigration", scope_id=scope)["migration"] or {}
    checkpoint_id = status.get("checkpoint_record_id")
    if checkpoint_id is None or status.get("state") == "aborted":
        project = records.read(scope, [scope])[scope]
        if project["value"].get("directory", {}).get("format") == 2:
            return {"phase": "done", "complete": True}
        root, writes = initial_directory()
        checkpoint_id = "dmg_" + secrets.token_hex(16)
        migration_id = "dm_" + secrets.token_hex(16)
        value = {
            "format": 2,
            "type": "migration",
            "phase": "headers",
            "root": root,
            "after_record_id": None,
            "source_record_id": None,
            "remaining_indices": [],
        }
        writes.append(
            {
                "record_id": checkpoint_id,
                "kind": "directory",
                "expected_revision": 0,
                "value": value,
            }
        )
        records.write(
            scope,
            key_epoch=epoch,
            records=writes,
            maintenance={
                "action": "begin",
                "migration_id": migration_id,
                "expected_checkpoint_revision": 0,
                "checkpoint_record_id": checkpoint_id,
                "created_record_ids": [
                    item["record_id"]
                    for item in writes
                    if item["record_id"] != checkpoint_id
                ],
            },
        )
    else:
        migration_id = status["migration_id"]
        if status.get("state") == "aborting":
            raise E2eeError("migration_aborting")

    for _ in range(maximum_batches):
        checkpoint = records.read(scope, [checkpoint_id])[checkpoint_id]
        value = checkpoint["value"]
        if value.get("format") != 2 or value.get("type") != "migration":
            raise E2eeError("invalid_directory")
        phase = value["phase"]
        if phase == "done":
            return {"phase": phase, "complete": True}
        writes: list[dict[str, Any]] = []
        preconditions: list[dict[str, Any]] = []
        revived_headers: list[str] = []
        following = dict(value)
        source = None
        if value["source_record_id"] is not None:
            source = records.read(scope, [value["source_record_id"]]).get(
                value["source_record_id"]
            )
            if source is None or source["deleted"]:
                raise E2eeError("revision_conflict")
        else:
            page = records.current(
                scope, kind="directory", after_record_id=value["after_record_id"]
            )
            source = next(
                (
                    item
                    for item in page["records"]
                    if not item["deleted"] and item["value"].get("format") != 2
                ),
                None,
            )
            if source is not None:
                following["source_record_id"] = source["record_id"]
                following["remaining_indices"] = [
                    index
                    for index, entry in enumerate(source["value"]["entries"])
                    if entry.get("deletedAt") is None
                    and (phase != "headers" or entry["kind"] == "folder")
                ]
            elif page["has_more"]:
                following["after_record_id"] = page["next_record_id"]
            else:
                following["after_record_id"] = None
                following["phase"] = {
                    "headers": "entries",
                    "entries": "cleanup",
                    "cleanup": "done",
                }[phase]
                if phase == "entries":
                    status = (
                        session.api.call("e2eeGetMigration", scope_id=scope)[
                            "migration"
                        ]
                        or {}
                    )
                    if not status.get("source_scan_complete", True):
                        following = dict(value)
                        records.write(
                            scope,
                            key_epoch=epoch,
                            records=[
                                {
                                    "record_id": checkpoint_id,
                                    "kind": "directory",
                                    "expected_revision": checkpoint["revision"],
                                    "value": following,
                                }
                            ],
                            maintenance={
                                "action": "progress",
                                "migration_id": migration_id,
                                "expected_checkpoint_revision": checkpoint["revision"],
                                "checkpoint_record_id": checkpoint_id,
                                "created_record_ids": [],
                            },
                        )
                        continue
                    project = records.read(scope, [scope])[scope]
                    writes.append(
                        {
                            "record_id": scope,
                            "kind": "project",
                            "expected_revision": project["revision"],
                            "value": {
                                **project["value"],
                                "directory": {"format": 2, "root": value["root"]},
                            },
                        }
                    )
        if source is not None:
            entries = source["value"]["entries"]
            indices = following["remaining_indices"]
            if phase == "cleanup":
                writes.append(
                    {
                        "record_id": source["record_id"],
                        "kind": "directory",
                        "expected_revision": source["revision"],
                        "value": {},
                        "deleted": True,
                    }
                )
                indices = []
            elif phase == "headers":
                chosen = []
                existing_headers = (
                    records.read(
                        scope, [entries[index]["id"] for index in indices[:64]]
                    )
                    if indices
                    else {}
                )
                for index in indices[:64]:
                    entry = entries[index]
                    _, initial = initial_directory()
                    leaf, header = initial
                    header["record_id"] = entry["id"]
                    previous = existing_headers.get(entry["id"])
                    if previous is not None:
                        if previous["kind"] != "directory" or not previous["deleted"]:
                            raise E2eeError("invalid_directory")
                        header["expected_revision"] = previous["revision"]
                    header["value"].update(
                        entry=entry, parent=entry.get("parentFolderId") or value["root"]
                    )
                    candidate = writes + [leaf, header]
                    if writes and _write_bytes(candidate) > 300 * 1024:
                        break
                    writes = candidate
                    chosen.append(index)
                    if previous is not None:
                        revived_headers.append(entry["id"])
                indices = indices[len(chosen) :]
            elif indices:
                parent = entries[indices[0]].get("parentFolderId")
                chosen = [
                    index
                    for index in indices
                    if entries[index].get("parentFolderId") == parent
                ][:64]
                while True:
                    writes, preconditions = EncryptedDirectory(
                        records, scope, root_id=value["root"]
                    ).insertion([entries[index] for index in chosen])
                    if _write_bytes(writes) <= 300 * 1024 or len(chosen) == 1:
                        break
                    chosen = chosen[: len(chosen) // 2]
                indices = [index for index in indices if index not in chosen]
            following["remaining_indices"] = indices
            if not indices:
                following["after_record_id"] = source["record_id"]
                following["source_record_id"] = None
        writes.append(
            {
                "record_id": checkpoint_id,
                "kind": "directory",
                "expected_revision": checkpoint["revision"],
                "value": following,
            }
        )
        maintenance = None
        if phase in {"headers", "entries"}:
            maintenance = {
                "action": "complete"
                if phase == "entries" and following["phase"] == "cleanup"
                else "progress",
                "migration_id": migration_id,
                "expected_checkpoint_revision": checkpoint["revision"],
                "checkpoint_record_id": checkpoint_id,
                "created_record_ids": revived_headers
                + [
                    item["record_id"]
                    for item in writes
                    if item["expected_revision"] == 0
                    and item["record_id"] != checkpoint_id
                ],
            }
        records.write(
            scope,
            key_epoch=epoch,
            records=writes,
            preconditions=preconditions,
            maintenance=maintenance,
        )
    return {
        "phase": following["phase"],
        "complete": following["phase"] == "done",
        "migration_id": migration_id,
        "checkpoint_record_id": checkpoint_id,
    }


def abort_directory_migration(
    records: EncryptedRecords, scope: str, *, maximum_batches: int = 64
) -> dict[str, Any]:
    """Remove only staged migration records, retaining the published legacy index."""
    if not 1 <= maximum_batches <= 1024:
        raise E2eeError("invalid_batch")
    session = records.session
    epoch = session.scope_metadata(scope, refresh=True)["key_epoch"]
    for _ in range(maximum_batches):
        status = session.api.call("e2eeGetMigration", scope_id=scope)["migration"]
        if status is None or status["state"] == "aborted":
            return {"phase": "aborted", "complete": True}
        if status["state"] == "complete":
            raise E2eeError("migration_already_published")
        checkpoint_id = status["checkpoint_record_id"]
        page = session.api.call(
            "e2eeGetMigrationCreated",
            scope_id=scope,
            migration_id=status["migration_id"],
            limit=128,
        )
        identifiers = page["record_ids"]
        if (
            len(identifiers) > 128
            or len(set(identifiers)) != len(identifiers)
            or checkpoint_id in identifiers
        ):
            raise E2eeError("invalid_directory")
        opened = records.read(scope, [checkpoint_id, *identifiers])
        checkpoint = opened.get(checkpoint_id)
        if (
            checkpoint is None
            or checkpoint["revision"] != status["checkpoint_revision"]
        ):
            raise E2eeError("revision_conflict")
        if (
            checkpoint["value"].get("format") != 2
            or checkpoint["value"].get("type") != "migration"
        ):
            raise E2eeError("invalid_directory")
        writes = []
        for identifier in identifiers:
            record = opened.get(identifier)
            if (
                record is None
                or record["kind"] != "directory"
                or record["deleted"]
                or record["value"].get("format") != 2
                or record["value"].get("type") not in {"folder", "branch", "leaf"}
            ):
                raise E2eeError("invalid_directory")
            writes.append(
                {
                    "record_id": identifier,
                    "kind": "directory",
                    "expected_revision": record["revision"],
                    "value": {},
                    "deleted": True,
                }
            )
        final = not page["has_more"]
        writes.append(
            {
                "record_id": checkpoint_id,
                "kind": "directory",
                "expected_revision": checkpoint["revision"],
                "value": {} if final else checkpoint["value"],
                "deleted": final,
            }
        )
        records.write(
            scope,
            key_epoch=epoch,
            records=writes,
            maintenance={
                "action": "abort",
                "migration_id": status["migration_id"],
                "expected_checkpoint_revision": checkpoint["revision"],
                "checkpoint_record_id": checkpoint_id,
                "created_record_ids": [],
            },
        )
        if final:
            return {"phase": "aborted", "complete": True}
    return {"phase": "aborting", "complete": False}
