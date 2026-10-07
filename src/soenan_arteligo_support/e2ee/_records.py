from __future__ import annotations

import json
import secrets
import time
from typing import Any

from ._crypto import E2eeError, decode, encode, wipe
from ._session import DeviceSession

KINDS = frozenset(
    {
        "project",
        "directory",
        "file",
        "preview",
        "submission",
        "comment",
        "chat",
        "stage",
        "schedule",
    }
)


class EncryptedRecords:
    def __init__(self, session: DeviceSession):
        self.session = session
        self.crypto = session.crypto

    def _context(
        self, domain: str, scope: str, record: str, kind: str, epoch: int, revision: int
    ) -> bytearray:
        return self.crypto.canonical(
            {
                "v": 1,
                "domain": domain,
                "scope_id": scope,
                "record_id": record,
                "kind": kind,
                "key_epoch": epoch,
                "revision": revision,
            }
        )

    def seal(
        self,
        scope: str,
        *,
        record_id: str,
        kind: str,
        expected_revision: int,
        key_epoch: int,
        value: dict[str, Any],
        deleted: bool = False,
        immutable: bool = False,
    ) -> dict[str, Any]:
        if (
            kind not in KINDS
            or expected_revision < 0
            or key_epoch < 1
            or not isinstance(value, dict)
        ):
            raise E2eeError("invalid_record")
        key = self.session.scope_key(scope, key_epoch)
        plaintext = self.crypto.canonical(value)
        key_aad = self._context(
            "arteligo.record-key",
            scope,
            record_id,
            kind,
            key_epoch,
            expected_revision + 1,
        )
        payload_aad = self._context(
            "arteligo.record", scope, record_id, kind, key_epoch, expected_revision + 1
        )
        try:
            if len(plaintext) > 512 * 1024:
                raise E2eeError("record_too_large")
            return {
                "record_id": record_id,
                "kind": kind,
                "expected_revision": expected_revision,
                "key_epoch": key_epoch,
                "deleted": deleted,
                **({"immutable": True} if immutable else {}),
                "ciphertext": self.crypto.seal_record(
                    key, value, key_aad, payload_aad, kind
                ),
            }
        finally:
            for secret in (key, plaintext, key_aad, payload_aad):
                wipe(secret)

    def open(
        self,
        scope: str,
        wire: dict[str, Any],
        *,
        commands: dict[str, Any] | None = None,
        verified: dict[tuple[str, ...], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        proof = (commands or {}).get(wire.get("command_id"))
        if proof is not None:
            signed = proof["command"]
            operation = proof["operation"]
        else:
            signed = wire.get("signed_command")
            if signed is None:
                raise E2eeError("invalid_record_signature")
            raw_body = decode(signed.get("body_bytes"))
            try:
                unverified = json.loads(raw_body)
            finally:
                wipe(raw_body)
            operation = (
                "project_create" if "project_id" in unverified else "records_write"
            )
        if operation not in {"project_create", "records_write"}:
            raise E2eeError("invalid_record_signature")
        if signed.get("device_id") != wire.get("author_device_id"):
            raise E2eeError("invalid_author")
        device = self.session.device(scope, signed["device_id"])
        cache_key = (
            operation,
            signed["device_id"],
            signed["body_bytes"],
            signed["signature"],
        )
        body = verified.get(cache_key) if verified is not None else None
        if body is None:
            body = self.crypto.verify(device["signing_public_key"], operation, signed)
            if verified is not None:
                verified[cache_key] = body
        if body.get("scope_id", body.get("project_id")) != scope:
            raise E2eeError("invalid_record_scope")
        if proof is not None:
            ordinal = wire.get("ordinal")
            values = body.get("records", [])
            if type(ordinal) is not int or not 0 <= ordinal < len(values):
                raise E2eeError("invalid_record_signature")
            match = values[ordinal]
            if match.get("record_id") != wire["record_id"]:
                raise E2eeError("invalid_record_signature")
            wire = {**wire, "ciphertext": match["ciphertext"]}
            matches = [match]
        else:
            matches = [
                value
                for value in body.get("records", [])
                if value.get("record_id") == wire["record_id"]
            ]
        if len(matches) != 1:
            raise E2eeError("invalid_record_signature")
        match = matches[0]
        if (
            any(
                match.get(field) != wire.get(field)
                for field in ("ciphertext", "kind", "key_epoch")
            )
            or match.get("expected_revision", -1) + 1 != wire["revision"]
            or match.get("deleted", False) != wire.get("deleted", False)
        ):
            raise E2eeError("invalid_record_signature")
        key = self.session.scope_key(scope, wire["key_epoch"])
        key_aad = self._context(
            "arteligo.record-key",
            scope,
            wire["record_id"],
            wire["kind"],
            wire["key_epoch"],
            wire["revision"],
        )
        payload_aad = self._context(
            "arteligo.record",
            scope,
            wire["record_id"],
            wire["kind"],
            wire["key_epoch"],
            wire["revision"],
        )
        try:
            try:
                value = self.crypto.open_record(
                    key, wire["ciphertext"], key_aad, payload_aad, wire["kind"]
                )
            except E2eeError as error:
                if error.code in {"invalid_input", "unsupported_version"}:
                    raise E2eeError("invalid_record") from None
                raise
            return {
                "record_id": wire["record_id"],
                "cursor": wire["cursor"],
                "kind": wire["kind"],
                "revision": wire["revision"],
                "key_epoch": wire["key_epoch"],
                "deleted": wire["deleted"],
                "immutable": match.get("immutable", False) is True,
                "author_device_id": device["device_id"],
                "author_subject": device["account_subject"],
                "value": value,
            }
        finally:
            for secret in (key, key_aad, payload_aad):
                wipe(secret)

    def _open_page(self, scope: str, page: dict[str, Any]) -> list[dict[str, Any]]:
        context = page.get("key_context")
        if context is not None:
            for bundle in context.get("key_scopes", []) + context.get("scopes", []):
                if "error" not in bundle:
                    self.session.receive_read_bundle(bundle)
        verified: dict[tuple[str, ...], dict[str, Any]] = {}
        return [
            self.open(scope, wire, commands=page.get("commands"), verified=verified)
            for wire in page["records"]
        ]

    def read(self, scope: str, record_ids: list[str]) -> dict[str, dict[str, Any]]:
        result = self.read_many({scope: record_ids})[scope]
        if "error" in result:
            raise E2eeError(result["error"])
        return {record["record_id"]: record for record in result["records"]}

    def read_many(self, scopes: dict[str, list[str]]) -> dict[str, dict[str, Any]]:
        self.session.require_approved()
        if (
            not 1 <= len(scopes) <= 32
            or sum(map(len, scopes.values())) > 256
            or any(len(ids) != len(set(ids)) for ids in scopes.values())
        ):
            raise E2eeError("invalid_batch")
        pending = {scope: list(ids) for scope, ids in scopes.items()}
        results = {scope: {"records": [], "missing_record_ids": []} for scope in scopes}
        for _ in range(257):
            response = self.session.api.call(
                "e2eeReadRecords",
                body={
                    "scopes": [
                        {"scope_id": scope, "record_ids": ids}
                        for scope, ids in pending.items()
                    ],
                    "include_keys": True,
                },
            )
            returned = response["scopes"]
            if {value["scope_id"] for value in returned} != set(pending) or len(
                returned
            ) != len(pending):
                raise E2eeError("invalid_response")
            for bundle in response.get("key_scopes", []):
                if "error" not in bundle:
                    self.session.receive_read_bundle(bundle)
            verified: dict[tuple[str, ...], dict[str, Any]] = {}
            following = {}
            for item in returned:
                scope = item["scope_id"]
                if "error" in item:
                    results[scope] = {"error": item["error"]}
                    continue
                ids = pending[scope]
                remaining = item["remaining_record_ids"]
                missing = item["missing_record_ids"]
                returned_ids = [wire["record_id"] for wire in item["records"]]
                accounted = remaining + missing + returned_ids
                if sorted(accounted) != sorted(ids) or len(accounted) != len(
                    set(accounted)
                ):
                    raise E2eeError("invalid_response")
                try:
                    self.session.receive_read_bundle(item)
                    opened = [
                        self.open(
                            scope,
                            wire,
                            commands=response["commands"],
                            verified=verified,
                        )
                        for wire in item["records"]
                    ]
                except E2eeError as error:
                    results[scope] = {"error": error.code}
                    continue
                except (ValueError, KeyError, TypeError, AttributeError):
                    results[scope] = {"error": "invalid_record"}
                    continue
                results[scope]["records"].extend(opened)
                results[scope]["missing_record_ids"].extend(missing)
                results[scope]["metadata"] = item["metadata"]
                if remaining:
                    following[scope] = remaining
            if not following:
                return results
            if sum(map(len, following.values())) >= sum(map(len, pending.values())):
                raise E2eeError("read_limit_exceeded")
            pending = following
        raise E2eeError("read_limit_exceeded")

    def current(
        self,
        scope: str,
        *,
        kind: str | None = None,
        after_record_id: str | None = None,
        limit: int = 256,
    ) -> dict[str, Any]:
        self.session.require_approved()
        if not 1 <= limit <= 256 or (kind is not None and kind not in KINDS):
            raise E2eeError("invalid_cursor")
        parameters: dict[str, Any] = {"scope_id": scope, "limit": limit}
        if kind is not None:
            parameters["kind"] = kind
        if after_record_id is not None:
            parameters["after_record_id"] = after_record_id
        page = self.session.api.call("e2eeGetCurrent", **parameters)
        opened = self._open_page(scope, page)
        ids = [record["record_id"] for record in opened]
        if ids != sorted(set(ids)) or any(
            identifier <= (after_record_id or "") for identifier in ids
        ):
            raise E2eeError("invalid_cursor")
        cursor = page.get("next_record_id")
        if page["has_more"] and (not ids or cursor != ids[-1]):
            raise E2eeError("invalid_cursor")
        return {**page, "records": opened, "commands": {}, "next_record_id": cursor}

    def immutable_kind(
        self,
        scope: str,
        kind: str,
        *,
        after: int = 0,
        snapshot_cursor: int | None = None,
        limit: int = 256,
    ) -> dict[str, Any]:
        """Read immutable records in cursor order, keeping the first snapshot cursor."""
        self.session.require_approved()
        if (
            kind not in KINDS
            or type(after) is not int
            or after < 0
            or type(limit) is not int
            or not 1 <= limit <= 256
            or (
                snapshot_cursor is not None
                and (type(snapshot_cursor) is not int or snapshot_cursor < after)
            )
        ):
            raise E2eeError("invalid_cursor")
        parameters = {"scope_id": scope, "kind": kind, "after": after, "limit": limit}
        if snapshot_cursor is not None:
            parameters["snapshot_cursor"] = snapshot_cursor
        page = self.session.api.call("e2eeGetImmutable", **parameters)
        opened = self._open_page(scope, page)
        snapshot, cursor = page["snapshot_cursor"], page["cursor"]
        cursors = [record["cursor"] for record in opened]
        if (
            type(snapshot) is not int
            or snapshot < after
            or type(cursor) is not int
            or (snapshot_cursor is not None and snapshot != snapshot_cursor)
            or cursors != sorted(set(cursors))
            or any(not after < item <= snapshot for item in cursors)
            or cursor != (cursors[-1] if cursors else after)
            or (page["has_more"] and (not cursors or cursor >= snapshot))
            or len(opened) > limit
            or any(
                record["kind"] != kind
                or record["deleted"]
                or not record["immutable"]
                or record["revision"] != 1
                for record in opened
            )
        ):
            raise E2eeError("invalid_cursor")
        return {**page, "records": opened, "commands": {}}

    def changes(
        self, scope: str, *, after: int = 0, limit: int = 256
    ) -> dict[str, Any]:
        self.session.require_approved()
        if after < 0 or not 1 <= limit <= 256:
            raise E2eeError("invalid_cursor")
        page = self.session.api.call(
            "e2eeGetChanges", scope_id=scope, after=after, limit=limit
        )
        if page["cursor"] < after or (page["has_more"] and page["cursor"] <= after):
            raise E2eeError("invalid_cursor")
        return page

    def page(self, scope: str, *, after: int = 0, limit: int = 128) -> dict[str, Any]:
        self.session.require_approved()
        if not 1 <= limit <= 256 or after < 0:
            raise E2eeError("invalid_cursor")
        page = self.session.api.call(
            "e2eeGetRecords", scope_id=scope, after=after, limit=limit
        )
        opened = self._open_page(scope, page)
        cursor = page["cursor"]
        if cursor < after or (page["has_more"] and cursor <= after):
            raise E2eeError("invalid_cursor")
        return {"records": opened, "cursor": cursor, "has_more": page["has_more"]}

    def write(
        self,
        scope: str,
        *,
        key_epoch: int,
        records: list[dict[str, Any]],
        preconditions: list[dict[str, Any]] | None = None,
        maintenance: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        self.session.require_approved()
        if not 1 <= len(records) <= 256 or len(
            {value["record_id"] for value in records}
        ) != len(records):
            raise E2eeError("invalid_batch")
        writes = [self.seal(scope, key_epoch=key_epoch, **value) for value in records]
        body = {
            "scope_id": scope,
            "records": writes,
            "format_version": 3
            if any(w["kind"] in {"chat", "comment"} for w in writes)
            else 2,
            "expires_at": int(time.time()) + 29 * 86400,
            "preconditions": preconditions or [],
        }
        if maintenance is not None:
            body["maintenance"] = maintenance
        result = self.session.command(
            "e2eeWriteRecords",
            "records_write",
            body,
            scope_id=scope,
        )
        expected = {value["record_id"]: value for value in writes}
        opened: dict[str, dict[str, Any]] = {}
        previous_cursor = -1
        for page_index in range(16):
            verified_commands: dict[tuple[str, ...], dict[str, Any]] = {}
            for wire in result["records"]:
                wanted = expected.get(wire["record_id"])
                if wanted is None:
                    continue
                if wire.get("revision") != wanted["expected_revision"] + 1 or any(
                    wire.get(field) != wanted[field]
                    for field in ("kind", "key_epoch", "deleted")
                ):
                    continue
                command = result.get("commands", {}).get(wire.get("command_id"))
                signed = command["command"] if command else wire.get("signed_command")
                if signed is None:
                    raise E2eeError("invalid_record_signature")
                verified = self.open(
                    scope,
                    wire,
                    commands=result.get("commands"),
                    verified=verified_commands,
                )
                signed_body = next(
                    value
                    for key, value in verified_commands.items()
                    if key[1:]
                    == (signed["device_id"], signed["body_bytes"], signed["signature"])
                )
                if not any(value == wanted for value in signed_body.get("records", [])):
                    raise E2eeError("invalid_record_signature")
                if verified["author_device_id"] != self.session.device_id:
                    raise E2eeError("invalid_record_signature")
                opened[wire["record_id"]] = verified
            if len(opened) == len(expected):
                return [opened[value["record_id"]] for value in writes]
            cursor = result["cursor"]
            if not result["has_more"] or cursor <= previous_cursor:
                raise E2eeError("incomplete_write_response")
            if page_index == 15:
                raise E2eeError("catchup_limit_exceeded")
            previous_cursor = cursor
            result = self.session.api.call(
                "e2eeGetRecords", scope_id=scope, after=cursor, limit=256
            )
        raise E2eeError("catchup_limit_exceeded")

    def create_project(
        self,
        *,
        value: dict[str, Any],
        owner_org: str | None = None,
        participation_policy: str = "private",
        project_id: str | None = None,
    ) -> str:
        self.session.require_approved()
        if owner_org is None or participation_policy not in {"private", "organization"}:
            raise E2eeError("invalid_project_policy")
        if self.session.recovery is None:
            raise E2eeError("recovery_missing")
        scope = project_id if project_id is not None else "prj_" + secrets.token_hex(16)
        if (
            not isinstance(scope, str)
            or not scope.startswith("prj_")
            or not 5 <= len(scope) <= 128
        ):
            raise E2eeError("invalid_project_id")
        key = self.crypto.key()
        try:
            self.session._remember(scope, 1, key)
            recipients = [
                (
                    self.session.device_id,
                    "device",
                    self.session.public["encryption_public_key"],
                ),
                (
                    self.session.recovery["recovery_id"],
                    "recovery",
                    self.session.recovery["encryption_public_key"],
                ),
            ]
            envelopes = [
                self.session.wrap_key(
                    scope,
                    1,
                    key,
                    recipient=identifier,
                    kind=kind,
                    public_key=public_key,
                )
                for identifier, kind, public_key in recipients
            ]
            if participation_policy == "organization":
                if owner_org is None:
                    raise E2eeError("organization_required")
                organization = self.session.scope_metadata(owner_org)
                org_key = self.session.scope_key(owner_org, organization["key_epoch"])
                try:
                    org_public = self.crypto.execute(
                        {
                            "op": "public_keys",
                            "encryption_secret_key": encode(org_key),
                            "signing_secret_key": encode(bytes(32)),
                        }
                    )["encryption_public_key"]
                    envelopes.append(
                        self.session.wrap_key(
                            scope,
                            1,
                            key,
                            recipient=owner_org,
                            kind="organization",
                            public_key=org_public,
                            organization_epoch=organization["key_epoch"],
                        )
                    )
                finally:
                    wipe(org_key)
            from ._conversation_context import initial_records
            from ._directory import initial_directory

            root, directory_records = initial_directory()
            record = self.seal(
                scope,
                record_id=scope,
                kind="project",
                expected_revision=0,
                key_epoch=1,
                value={
                    "lastStageVersion": 0,
                    **value,
                    "id": scope,
                    "slug": scope[4:],
                    "directory": {"format": 2, "root": root},
                },
            )
            self.session.command(
                "e2eeCreateProject",
                "project_create",
                {
                    "project_id": scope,
                    "owner_org": owner_org,
                    "participation_policy": participation_policy,
                    "envelopes": envelopes,
                    "records": [record]
                    + [
                        self.seal(scope, key_epoch=1, **item)
                        for item in [*directory_records, *initial_records()]
                    ],
                },
            )
            return scope
        finally:
            wipe(key)
