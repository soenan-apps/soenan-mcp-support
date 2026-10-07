"""Local, disposable E2EE directory fixture through an existing browser session.

Only public fixture identities and byte counts are written. Device material travels over anonymous
parent/child pipes and remains in memory. Bucket objects are deliberately absent;
the fixture measures signed metadata, directory pages, and browser list rendering.
"""

from __future__ import annotations

import argparse
import io
import json
import secrets
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from _browser_fixture_session import BrowserBridge, connect

from soenan_arteligo_support.e2ee._crypto import E2eeError, decode, wipe
from soenan_arteligo_support.e2ee._directory import EncryptedDirectory, _fits
from soenan_arteligo_support.e2ee._records import EncryptedRecords
from soenan_arteligo_support.transfer._crypto import build_encryption_plan
from soenan_arteligo_support.transfer._workflow import key_aad


def save_manifest(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def file_record(session, scope, sequence, run_id, timestamp, project_key):
    file_id = f"fil_{run_id}_{sequence:06d}"
    name = f"fixture-{sequence:06d}.txt"
    object_id = str(uuid.uuid4())
    body = b"Arteligo metadata fixture\n"
    data_key = session.crypto.key()
    try:
        wrapped = session.crypto.seal(
            project_key, data_key, key_aad(scope, 1, object_id)
        )
        plan = build_encryption_plan(
            io.BytesIO(body),
            project_id=scope,
            file_id=file_id,
            object_id=object_id,
            epoch=1,
            data_key=data_key,
            wrapped_nonce=bytes(decode(wrapped["nonce"])),
            wrapped_data_key=bytes(decode(wrapped["ciphertext"])),
            plaintext_size=len(body),
        )
        manifest = plan.manifest()
    finally:
        wipe(data_key)
    entry = {
        "id": "ent_" + file_id,
        "kind": "file",
        "name": name,
        "fileId": file_id,
        "parentFolderId": None,
        "projectId": scope,
        "revision": 1,
        "createdAt": timestamp,
        "updatedAt": timestamp,
        "deletedAt": None,
        "file": {
            "id": file_id,
            "originalFilename": name,
            "sizeBytes": len(body),
            "createdAt": timestamp,
            "sourceState": "available",
            "media": {"kind": "text"},
        },
        "breadcrumbs": [],
    }
    value = {
        "uploadId": object_id,
        "keyEpoch": 1,
        "source": manifest,
        "sourceState": "ready",
        "entryIntent": {"parentFolderId": None, "name": name},
        "filename": name,
        "mimeType": "text/plain",
        "file": {
            "projectId": scope,
            "fileId": file_id,
            "entryId": entry["id"],
            "encryptedObjectId": object_id,
            "createdBy": session.subject,
            "fileKind": "project_file",
            "originalFilename": name,
            "originalPlaintextSize": len(body),
            "mimeType": "text/plain",
            "createdAt": timestamp,
            "updatedAt": timestamp,
        },
    }
    return {
        "record_id": file_id,
        "kind": "file",
        "expected_revision": 0,
        "value": value,
    }, entry


def node(entries, *, branch=False):
    identifier = "dpg_" + secrets.token_hex(16)
    value = {
        "format": 2,
        "type": "branch" if branch else "leaf",
        "children" if branch else "entries": entries,
    }
    if not _fits(value):
        raise E2eeError("fixture_node_size_exceeded")
    first = (
        entries[0]["first"]
        if branch
        else {key: entries[0][key] for key in ("name", "id")}
    )
    return (
        {
            "record_id": identifier,
            "kind": "directory",
            "expected_revision": 0,
            "value": value,
        },
        {"first": first, "node": {"id": identifier, "revision": 1}},
    )


def measure_file_cost(records, scope, record, file_count, path):
    response = records.session.api.call(
        "e2eeReadRecords",
        body={
            "scopes": [{"scope_id": scope, "record_ids": [record["record_id"]]}],
            "include_keys": False,
        },
    )
    reference = response["scopes"][0]["records"][0]
    records.open(scope, reference, commands=response["commands"])
    proof = response["commands"][reference["command_id"]]
    raw_body = decode(proof["command"]["body_bytes"])
    signed_body = json.loads(raw_body)
    signed_record = signed_body["records"][reference["ordinal"]]
    ciphertext = decode(signed_record["ciphertext"])
    binary_v2 = ciphertext[:1] == b"\x02"
    packed = None if binary_v2 else json.loads(ciphertext)

    def size(value):
        return len(records.crypto.canonical(value))

    fields = [
        {
            "field": name,
            "value_json_bytes": size(value),
            "named_field_json_bytes": size({name: value}),
        }
        for name, value in record["value"].items()
    ]
    fields.sort(key=lambda item: item["named_field_json_bytes"], reverse=True)
    report = {
        "version": 2,
        "ciphertext_envelope_version": 2 if binary_v2 else 1,
        "plaintext_json_bytes": size(record["value"]),
        "decoded_ciphertext_packed_bytes": len(ciphertext),
        "ciphertext_base64_bytes": len(signed_record["ciphertext"]),
        "aead_payload_bytes": len(ciphertext) - 73 if binary_v2 else len(decode(packed["payload"]["ciphertext"])),
        "wrapped_key_bytes": 48 if binary_v2 else len(decode(packed["wrapped_key"]["ciphertext"])),
        "signed_record_json_bytes": size(signed_record),
        "signed_body_bytes": len(raw_body),
        "signed_command_json_bytes": size(proof["command"]),
        "signed_body_record_count": len(signed_body["records"]),
        "file_count": file_count,
        "signed_body_bytes_per_record": len(raw_body) / len(signed_body["records"]),
        "signed_body_bytes_per_file_including_leaf": len(raw_body) / file_count,
        "top_level_fields": fields,
        "source_fields": [
            {"field": name, "value_json_bytes": size(value)}
            for name, value in record["value"]["source"].items()
        ],
        "directory_entry_json_bytes": (
            size(record["value"]["directoryEntry"])
            if "directoryEntry" in record["value"]
            else 0
        ),
    }
    save_manifest(path, report)


def create_fixture_project(session, organization, path, origin, entries, title_prefix):
    if path.exists():
        raise E2eeError("fixture_manifest_exists")
    records = EncryptedRecords(session)
    run_id = secrets.token_hex(12)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    title = f"{title_prefix} ({run_id[:8]})"
    scope = "prj_" + secrets.token_hex(16)
    manifest = {
        "version": 1,
        "origin": origin.rstrip("/"),
        "run_id": run_id,
        "scope_id": scope,
        "owner_subject": session.subject,
        "title": title,
        "path": "/projects/" + scope,
        "entries": entries,
        "file_prefix": "fil_" + run_id + "_",
        "entry_name": "fixture-NNNNNN.txt",
        "created_at": timestamp,
        "written_entries": 0,
        "state": "creating",
        "limitation": "Cryptographically valid metadata only; no Bucket objects. Downloads are not tested.",
    }
    save_manifest(path, manifest)
    records.create_project(
        project_id=scope,
        owner_org=organization,
        value={
            "title": title,
            "participationPolicy": "private",
            "status": "active",
            "progress": 0.0,
            "responsibility": {"revision": 0, "waitingOn": None},
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "deadlineDate": None,
            "brief": {},
            "members": [],
        },
    )
    project = recover_creation_proof(session, manifest)
    manifest["state"] = "building"
    save_manifest(path, manifest)
    return manifest, project


def recover_creation_proof(session, manifest):
    records = EncryptedRecords(session)
    scope = manifest["scope_id"]
    if manifest["owner_subject"] != session.subject:
        raise E2eeError("fixture_owner_changed")
    project = records.read(scope, [scope])[scope]
    if project["value"].get("title") != manifest["title"]:
        raise E2eeError("fixture_identity_changed")
    proof_page = session.api.call(
        "e2eeReadRecords",
        body={
            "scopes": [{"scope_id": scope, "record_ids": [scope]}],
            "include_keys": False,
        },
    )
    reference = proof_page["scopes"][0]["records"][0]
    proof = proof_page["commands"][reference["command_id"]]
    if reference["record_id"] != scope or proof["operation"] != "project_create":
        raise E2eeError("fixture_creation_proof_invalid")
    records.open(scope, reference, commands=proof_page["commands"])
    if (
        manifest.get("project_create_command_id", reference["command_id"])
        != reference["command_id"]
    ):
        raise E2eeError("fixture_creation_proof_invalid")
    manifest["project_create_command_id"] = reference["command_id"]
    return project


def prepare(session, organization, args):
    manifest, project = create_fixture_project(
        session,
        organization,
        args.manifest,
        args.origin,
        args.entries,
        f"Metadata benchmark {args.entries:,}",
    )
    records = EncryptedRecords(session)
    scope, run_id, timestamp = (
        manifest["scope_id"],
        manifest["run_id"],
        manifest["created_at"],
    )
    root = project["value"]["directory"]["root"]
    header = records.read(scope, [root])[root]
    key = session.scope_key(scope, 1)
    children = []
    started = time.monotonic()
    try:
        for start in range(0, args.entries, 64):
            writes, entries = [], []
            for sequence in range(start, min(start + 64, args.entries)):
                record, entry = file_record(
                    session, scope, sequence, run_id, timestamp, key
                )
                writes.append(record)
                entries.append(entry)
            leaf, child = node(entries)
            records.write(scope, key_epoch=1, records=[*writes, leaf])
            if start == 0:
                cost_path = args.manifest.with_name(
                    args.manifest.stem + "-file-cost.json"
                )
                measure_file_cost(records, scope, writes[0], len(writes), cost_path)
                manifest["file_cost_artifact"] = cost_path.name
            children.append(child)
            manifest["written_entries"] = start + len(entries)
            if start % 1024 == 0 or manifest["written_entries"] == args.entries:
                manifest["elapsed_seconds"] = round(time.monotonic() - started, 3)
                save_manifest(args.manifest, manifest)
                print(
                    json.dumps(
                        {
                            "written_entries": manifest["written_entries"],
                            "elapsed_seconds": manifest["elapsed_seconds"],
                        }
                    ),
                    flush=True,
                )
    finally:
        wipe(key)
    while len(children) > 1:
        next_level, writes = [], []
        for start in range(0, len(children), 64):
            record, child = node(children[start : start + 64], branch=True)
            writes.append(record)
            next_level.append(child)
        for start in range(0, len(writes), 32):
            records.write(scope, key_epoch=1, records=writes[start : start + 32])
        children = next_level
    records.write(
        scope,
        key_epoch=1,
        records=[
            {
                "record_id": root,
                "kind": "directory",
                "expected_revision": header["revision"],
                "value": {**header["value"], "root": children[0]["node"]},
            },
            {
                "record_id": header["value"]["root"]["id"],
                "kind": "directory",
                "expected_revision": 1,
                "deleted": True,
                "value": {},
            },
        ],
    )
    manifest["overview_fixture_scopes"] = []
    manifest["overview_fixture_manifests"] = []
    for index in range(1, args.overview_projects):
        relative = Path(args.manifest.stem + "-overview") / f"{index:02d}.json"
        manifest["overview_fixture_manifests"].append(str(relative))
        save_manifest(args.manifest, manifest)
        child_path = args.manifest.parent / relative
        child, _ = create_fixture_project(
            session,
            organization,
            child_path,
            args.origin,
            0,
            f"Overview benchmark {index:02d}",
        )
        child["state"] = "ready"
        save_manifest(child_path, child)
        manifest["overview_fixture_scopes"].append(child["scope_id"])
        save_manifest(args.manifest, manifest)
    manifest.update(state="ready", elapsed_seconds=round(time.monotonic() - started, 3))
    save_manifest(args.manifest, manifest)
    return manifest


def check(session, bridge, manifest):
    records = EncryptedRecords(session)
    directory = EncryptedDirectory(records, manifest["scope_id"])
    measurements = []
    cursor = None
    for _ in range(2):
        requests, size = bridge.requests, bridge.response_bytes
        started = time.monotonic()
        page = directory.page(limit=100, cursor=cursor)
        measurements.append(
            {
                "entries": len(page["entries"]),
                "seconds": round(time.monotonic() - started, 4),
                "requests": bridge.requests - requests,
                "response_bytes": bridge.response_bytes - size,
            }
        )
        cursor = page["cursor"]
        if cursor is None:
            break
    return measurements


def archive(session, manifest, path):
    scope = manifest["scope_id"]
    if manifest["owner_subject"] != session.subject:
        raise E2eeError("fixture_owner_changed")
    recover_creation_proof(session, manifest)
    save_manifest(path, manifest)
    session.command(
        "e2eeArchiveProject", "project_archive", {"project_id": scope}, scope_id=scope
    )
    manifest["state"] = "archived"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--action", choices=["prepare", "check", "archive"], default="prepare"
    )
    parser.add_argument("--cdp-url", required=True)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--node", default="node")
    parser.add_argument("--entries", type=int, default=100000)
    parser.add_argument("--overview-projects", type=int, default=50)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if (
        urlsplit(args.cdp_url).hostname not in {"127.0.0.1", "localhost"}
        or not urlsplit(args.origin).hostname.endswith(".local.soenan.dev")
        or not 1 <= args.entries <= 1000000
        or not 1 <= args.overview_projects <= 100
    ):
        raise E2eeError("local_fixture_target_required")
    bridge = BrowserBridge(args)
    session = None
    try:
        session, organization = connect(bridge)
        manifest = (
            prepare(session, organization, args)
            if args.action == "prepare"
            else json.loads(args.manifest.read_text())
        )
        if (
            manifest.get("version") != 1
            or manifest.get("origin") != bridge.arteligo_origin
        ):
            raise E2eeError("fixture_origin_mismatch")
        if args.action == "archive":
            archive(session, manifest, args.manifest)
            measurements = manifest.get("sdk_pages", [])
        else:
            measurements = check(session, bridge, manifest)
            manifest["sdk_pages"] = measurements
        save_manifest(args.manifest, manifest)
        print(
            json.dumps(
                {
                    "scope_id": manifest["scope_id"],
                    "state": manifest["state"],
                    "manifest": str(args.manifest),
                    "sdk_pages": measurements,
                }
            ),
            flush=True,
        )
    finally:
        if session is not None:
            session.lock()
            session.store.values.clear()
        bridge.stop()


if __name__ == "__main__":
    try:
        main()
    except E2eeError as error:
        print(json.dumps({"error": error.code}), file=sys.stderr)
        sys.exit(1)
    except Exception:  # noqa: BLE001 - A traceback can expose the in-memory device bundle.
        print(json.dumps({"error": "fixture_failed"}), file=sys.stderr)
        sys.exit(1)
