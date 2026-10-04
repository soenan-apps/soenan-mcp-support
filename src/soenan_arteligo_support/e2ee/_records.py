from __future__ import annotations

import json
import secrets
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
    ) -> dict[str, Any]:
        if (
            kind not in KINDS
            or expected_revision < 0
            or key_epoch < 1
            or not isinstance(value, dict)
        ):
            raise E2eeError("invalid_record")
        key = self.session.scope_key(scope, key_epoch)
        data_key = self.crypto.key()
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
            packed = {
                "wrapped_key": self.crypto.seal(key, data_key, key_aad),
                "payload": self.crypto.seal(data_key, plaintext, payload_aad),
            }
            return {
                "record_id": record_id,
                "kind": kind,
                "expected_revision": expected_revision,
                "key_epoch": key_epoch,
                "deleted": deleted,
                "ciphertext": encode(
                    json.dumps(packed, separators=(",", ":")).encode()
                ),
            }
        finally:
            for secret in (key, data_key, plaintext, key_aad, payload_aad):
                wipe(secret)

    def open(self, scope: str, wire: dict[str, Any]) -> dict[str, Any]:
        signed = wire["signed_command"]
        if signed.get("device_id") != wire.get("author_device_id"):
            raise E2eeError("invalid_author")
        device = self.session.device(scope, signed["device_id"])
        raw_body = decode(signed.get("body_bytes"))
        try:
            unverified = json.loads(raw_body)
        finally:
            wipe(raw_body)
        operation = "project_create" if "project_id" in unverified else "records_write"
        body = self.crypto.verify(device["signing_public_key"], operation, signed)
        if body.get("scope_id", body.get("project_id")) != scope:
            raise E2eeError("invalid_record_scope")
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
        data_key = bytearray()
        plaintext = bytearray()
        try:
            packed = json.loads(decode(wire["ciphertext"]))
            data_key = self.crypto.open(
                key,
                packed["wrapped_key"],
                self._context(
                    "arteligo.record-key",
                    scope,
                    wire["record_id"],
                    wire["kind"],
                    wire["key_epoch"],
                    wire["revision"],
                ),
            )
            plaintext = self.crypto.open(
                data_key,
                packed["payload"],
                self._context(
                    "arteligo.record",
                    scope,
                    wire["record_id"],
                    wire["kind"],
                    wire["key_epoch"],
                    wire["revision"],
                ),
            )
            value = json.loads(plaintext)
            if not isinstance(value, dict):
                raise E2eeError("invalid_record")
            return {
                "record_id": wire["record_id"],
                "kind": wire["kind"],
                "revision": wire["revision"],
                "key_epoch": wire["key_epoch"],
                "deleted": wire["deleted"],
                "author_device_id": device["device_id"],
                "author_subject": device["account_subject"],
                "value": value,
            }
        finally:
            for secret in (key, data_key, plaintext):
                wipe(secret)

    def page(self, scope: str, *, after: int = 0, limit: int = 128) -> dict[str, Any]:
        self.session.require_approved()
        if not 1 <= limit <= 256 or after < 0:
            raise E2eeError("invalid_cursor")
        page = self.session.api.call(
            "e2eeGetRecords", scope_id=scope, after=after, limit=limit
        )
        opened = [self.open(scope, value) for value in page["records"]]
        cursor = page["cursor"]
        if cursor < after or (page["has_more"] and cursor <= after):
            raise E2eeError("invalid_cursor")
        return {"records": opened, "cursor": cursor, "has_more": page["has_more"]}

    def write(
        self, scope: str, *, key_epoch: int, records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        self.session.require_approved()
        if not 1 <= len(records) <= 256 or len(
            {value["record_id"] for value in records}
        ) != len(records):
            raise E2eeError("invalid_batch")
        writes = [self.seal(scope, key_epoch=key_epoch, **value) for value in records]
        result = self.session.command(
            "e2eeWriteRecords",
            "records_write",
            {"scope_id": scope, "records": writes},
            scope_id=scope,
        )
        expected = {value["record_id"]: value for value in writes}
        opened: dict[str, dict[str, Any]] = {}
        previous_cursor = -1
        for page_index in range(16):
            for wire in result["records"]:
                wanted = expected.get(wire["record_id"])
                if wanted is None:
                    continue
                if wire.get("revision") != wanted["expected_revision"] + 1 or any(
                    wire.get(field) != wanted[field]
                    for field in ("kind", "key_epoch", "deleted", "ciphertext")
                ):
                    continue
                verified = self.open(scope, wire)
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
    ) -> str:
        self.session.require_approved()
        if owner_org is None or participation_policy not in {"private", "organization"}:
            raise E2eeError("invalid_project_policy")
        if self.session.recovery is None:
            raise E2eeError("recovery_missing")
        scope = "prj_" + secrets.token_hex(16)
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
                organization = next(
                    (
                        item
                        for item in self.session.api.call("e2eeListOrganizations")[
                            "projects"
                        ]
                        if item["project_id"] == owner_org
                    ),
                    None,
                )
                if organization is None:
                    raise E2eeError("organization_approval_required")
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
                        )
                    )
                finally:
                    wipe(org_key)
            record = self.seal(
                scope,
                record_id=scope,
                kind="project",
                expected_revision=0,
                key_epoch=1,
                value={**value, "id": scope, "slug": scope[4:]},
            )
            self.session.command(
                "e2eeCreateProject",
                "project_create",
                {
                    "project_id": scope,
                    "owner_org": owner_org,
                    "participation_policy": participation_policy,
                    "envelopes": envelopes,
                    "records": [record],
                },
            )
            return scope
        finally:
            wipe(key)
