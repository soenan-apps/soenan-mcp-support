from __future__ import annotations

import secrets
import json
from google.protobuf.message import DecodeError

from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from ._crypto import E2eeError
from ._session import DeviceSession
from ._signed_commands import AcceptedCommand

KINDS = frozenset({"project", "directory", "file_metadata", "file_upload", "file_preview_upload", "submission", "comment", "chat", "stage", "schedule"})
BINARY_KINDS = frozenset({"file_metadata", "file_upload", "file_preview_upload"})


class EncryptedRecords:
    def __init__(self, session: DeviceSession):
        self.session = session
        self.last_receipt = None

    @staticmethod
    def _payload(value):
        if isinstance(value, bytes):
            return value
        try:
            return app.ValueContent(json=json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()).SerializeToString()
        except (ValueError, TypeError):
            raise E2eeError("invalid_record") from None

    @staticmethod
    def _record(value):
        result = {"record_id": value.id, "revision": value.revision,
            "key_epoch": value.protection_key.generation, "protection_key": value.protection_key,
            "kind": value.kind, "deleted": value.deleted, "immutable": value.immutable,
            "author_device_id": value.author_device_id, "author_subject": value.author_subject,
            "cursor": value.cursor}
        if value.deleted and not value.plaintext:
            result["payload_type"] = "deletion_marker"
        else:
            result["payload_type"] = "historical_encrypted_deletion" if value.deleted else "content"
            try:
                result["value"] = bytes(value.plaintext) if value.kind in BINARY_KINDS else json.loads(app.ValueContent.FromString(value.plaintext).json)
            except (DecodeError, ValueError, UnicodeError):
                raise E2eeError("invalid_record") from None
        return result

    def _open_page(self, scope, page):
        heads = {(head.id, head.revision): head for head in page.heads}
        result = []
        for value in self.session.open_bundle(page.bundle):
            record = self._record(value)
            head = heads.get((value.id, value.revision))
            if head is not None:
                record["cursor"] = int(head.cursor or 0)
            result.append(record)
        return result

    def read(self, scope: str, record_ids: list[str]):
        page = self.session.read_bundle(scope, view="by_ids", value_ids=record_ids)
        return {value["record_id"]: value for value in self._open_page(scope, page)}

    def read_many(self, scopes):
        return {scope: {"records": self.read(scope, ids)} for scope, ids in scopes.items()}

    def _page(self, scope, **query):
        page = self.session.read_bundle(scope, **query)
        return {"records": self._open_page(scope, page), "cursor": int(page.cursor or 0) if query.get("view") != "current" else page.cursor,
            "has_more": page.has_more, "next_record_id": page.cursor, "snapshot_cursor": page.snapshot_cursor}

    def current(self, scope, *, kind=None, after_record_id=None, limit=256):
        return self._page(scope, view="current", kind=kind or "", cursor=after_record_id or "", limit=limit)

    def immutable_kind(self, scope, kind, *, after=0, snapshot_cursor=None, limit=256):
        return self._page(scope, view="page", kind=kind, cursor=str(after), limit=limit,
            immutable_only=True, snapshot_cursor=snapshot_cursor or 0)

    def changes(self, scope, *, after=0, limit=256):
        return self._page(scope, view="changes", cursor=str(after), limit=limit)

    def page(self, scope, *, after=0, limit=128):
        return self._page(scope, view="page", cursor=str(after), limit=limit)

    def history(self, scope, record_id, *, before=0, limit=128):
        return self._page(scope, view="history", value_id=record_id, cursor=str(before) if before else "", limit=limit)

    def write(self, scope, *, records, preconditions=None, object_effects=None, deleted_objects=None, files=None, comments=None):
        snapshot = self.session.read_bundle(scope)
        project, bundle = snapshot.project, snapshot.bundle
        if project.project_id != scope:
            raise E2eeError("invalid_response")
        audience = None
        if project.key_distribution_revision != project.distribution_revision:
            audience = self.session.audience(project.group_id, scope)
            project = next((item for item in audience.projects if item.project_id == scope), None)
            if project is None:
                raise E2eeError("invalid_response")
            bundle = audience.bundle
        key = project.protection_key
        create_keys, deliveries = [], []
        policy = None
        if project.key_distribution_revision != project.distribution_revision:
            key = crypto.KeyRef(id=key.id, generation=key.generation + 1)
            create_keys = [key]
            deliveries = [crypto.DeliveryMutation(target=key, recipient=member.receiver) for member in audience.members]
            policy = app.ProjectPolicyBinding(project_id=scope, group_id=project.group_id, shared=project.shared,
                current_protection_key=key, expected_distribution_revision=project.distribution_revision,
                prepare_owner_deliveries=True)
        values = []
        heads = []
        author_device_id = self.session.device_id
        for draft in records:
            if draft["kind"] not in KINDS:
                raise E2eeError("invalid_record")
            values.append(crypto.ValueMutation(id=draft["record_id"], expected_revision=draft["expected_revision"],
                protection_key=key, plaintext=self._payload(draft.get("value", {})), kind=draft["kind"],
                deleted=draft.get("deleted", False), immutable=draft.get("immutable", False)))
            heads.append(app.RecordHead(id=draft["record_id"], revision=draft["expected_revision"] + 1,
                kind=draft["kind"], deleted=draft.get("deleted", False), immutable=draft.get("immutable", False),
                author_device_id=author_device_id))
        binding = app.RecordMutationBinding(heads=heads,
            preconditions=[app.RecordPrecondition(id=p["record_id"], expected_revision=p["expected_revision"], require_live=p.get("require_live", False)) for p in preconditions or []],
            deleted_objects=deleted_objects or [], object_effects=object_effects or [], files=files or [], comments=comments or [])
        if policy is not None:
            binding.project_policy.CopyFrom(policy)
        self.session.prepare(scope, values=values, create_keys=create_keys, deliveries=deliveries,
            binding=binding.SerializeToString(), bundle=bundle)
        return self.resume_write(scope)

    def resume_write_for(self, scope, record_ids):
        command = self.session.pending_command(scope)
        if command is None:
            return None
        body = crypto.MutationBody.FromString(command.body)
        if not set(record_ids) <= {head.id for head in body.target_heads}:
            raise E2eeError("record_publication_pending")
        return self.resume_write(scope)

    def resume_write(self, scope):
        command = self.session.pending_command(scope)
        response, opened = self.session.commit(scope)
        self.last_receipt = response.receipt
        try:
            return [self._record(value) for value in opened.values]
        except Exception as error:
            return AcceptedCommand(command, {"kind": "committed"}, error)

    def create_project(self, *, value, owner_org=None, participation_policy="private", project_id=None):
        from ._directory import initial_directory
        from ._conversation_context import initial_records
        if not owner_org or participation_policy not in {"private", "organization"}:
            raise E2eeError("invalid_project_policy")
        identifier = project_id or "prj_" + secrets.token_hex(16)
        key = crypto.KeyRef(id="pk_" + secrets.token_hex(16), generation=1)
        directory_id, drafts = initial_directory()
        drafts.extend(initial_records(identifier))
        payload = {**value, "id": identifier, "slug": identifier, "directory": {"format": 2, "root": directory_id}}
        drafts.append({"record_id": identifier, "kind": "project", "expected_revision": 0, "value": payload})
        audience = self.session.audience(owner_org, identifier)
        values = [crypto.ValueMutation(id=d["record_id"], expected_revision=0, protection_key=key,
            plaintext=self._payload(d["value"]), kind=d["kind"]) for d in drafts]
        author_device_id = self.session.device_id
        binding = app.RecordMutationBinding(project_policy=app.ProjectPolicyBinding(project_id=identifier,
            group_id=owner_org, shared=participation_policy == "organization", current_protection_key=key,
            prepare_owner_deliveries=True), heads=[app.RecordHead(id=d["record_id"], revision=1,
                kind=d["kind"], author_device_id=author_device_id) for d in drafts])
        deliveries = [crypto.DeliveryMutation(target=key, recipient=m.receiver) for m in audience.members]
        command = self.session.prepare(identifier, values=values, deliveries=deliveries, create_keys=[key], binding=binding.SerializeToString(), bundle=audience.bundle)
        request = app.ProjectCreateRequest(project_id=identifier, group_id=owner_org,
            shared=participation_policy == "organization", protection_key=key,
            mutation=app.CommitCryptoRequest(project_id=identifier, command=command))
        self.session.commit(identifier, operation="createCryptoProject", request=request)
        return identifier
