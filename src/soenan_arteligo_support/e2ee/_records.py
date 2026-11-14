from __future__ import annotations

import secrets
import time
import uuid
from typing import Generic, Literal, TypeVar

from google.protobuf.message import DecodeError, EncodeError, Message
from soenan.account.crypto.v1 import crypto_pb2 as shared
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain
from typing_extensions import NotRequired, TypedDict

from ._crypto import E2eeError
from ._record_kinds_generated import RECORD_KINDS, record_body_allows_kind
from ._session import DeviceSession
from ._signed_commands import AcceptedCommand

RecordMessage = TypeVar("RecordMessage", bound=Message)


class ReadRecord(TypedDict, Generic[RecordMessage]):
    record_id: str
    revision: int
    incarnation: str
    key_epoch: NotRequired[int]
    protection_key: NotRequired[shared.KeyRef]
    kind: str
    immutable: NotRequired[bool]
    author_device_id: str
    author_subject: str
    cursor: int
    payload_type: Literal["deletion", "content"]
    value: NotRequired[RecordMessage]
    expected_revision: NotRequired[int]
    operation_id: NotRequired[str]
    committed_at: NotRequired[int]


_BODY_FIELDS = {
    field.message_type.full_name: field
    for field in domain.RecordContent.DESCRIPTOR.oneofs_by_name["body"].fields
}


def _validate_body(value: Message, *, required: bool = True) -> None:
    if required and not value.IsInitialized():
        raise E2eeError("invalid_record")

    def visit(message: Message) -> None:
        if any(
            message.WhichOneof(oneof.name) is None
            for oneof in message.DESCRIPTOR.oneofs
        ):
            raise E2eeError("invalid_record")
        for field, child in message.ListFields():
            if field.message_type is not None:
                if field.is_repeated:
                    for item in child:
                        visit(item)
                else:
                    visit(child)

    visit(value)


class EncryptedRecords:
    def __init__(self, session: DeviceSession):
        self.session = session
        self.last_receipt = None
        self.operation_id = str(uuid.uuid4())

    @staticmethod
    def _payload(value, kind=None):
        if isinstance(value, domain.RecordContent):
            case = value.WhichOneof("body")
            if case is None or (
                kind is not None and not record_body_allows_kind(case, kind)
            ):
                raise E2eeError("invalid_record")
            value = getattr(value, case)
        if not isinstance(value, Message):
            raise E2eeError("invalid_record")
        field = _BODY_FIELDS.get(value.DESCRIPTOR.full_name)
        if field is None or (
            kind is not None and not record_body_allows_kind(field.name, kind)
        ):
            raise E2eeError("invalid_record")
        _validate_body(value, required=False)
        envelope = domain.RecordContent()
        getattr(envelope, field.name).CopyFrom(value)
        try:
            return envelope.SerializeToString()
        except EncodeError:
            raise E2eeError("invalid_record") from None

    @staticmethod
    def _record(value: crypto.OpenedValue) -> ReadRecord[Message]:
        if value.kind not in RECORD_KINDS:
            raise E2eeError("invalid_record")
        try:
            envelope = domain.RecordContent.FromString(value.plaintext)
            case = envelope.WhichOneof("body")
            if case is None or not record_body_allows_kind(case, value.kind):
                raise E2eeError("invalid_record")
            body: Message = getattr(envelope, case)
            _validate_body(body)
        except DecodeError:
            raise E2eeError("invalid_record") from None
        result: ReadRecord[Message] = {
            "record_id": value.id,
            "revision": value.revision,
            "incarnation": value.incarnation,
            "key_epoch": value.protection_key.generation,
            "protection_key": value.protection_key,
            "kind": value.kind,
            "immutable": value.immutable,
            "author_device_id": value.author_device_id,
            "author_subject": value.author_subject,
            "cursor": value.cursor,
            "payload_type": "content",
            "value": body,
        }
        return result

    @staticmethod
    def _deletion(value: crypto.OpenedDeletion) -> ReadRecord[Message]:
        if value.kind not in RECORD_KINDS:
            raise E2eeError("invalid_record")
        return {
            "record_id": value.id,
            "revision": value.revision,
            "expected_revision": value.expected_revision,
            "incarnation": value.incarnation,
            "kind": value.kind,
            "author_device_id": value.author_device_id,
            "author_subject": value.author_subject,
            "payload_type": "deletion",
            "operation_id": value.operation_id,
            "committed_at": value.committed_at,
            "cursor": value.cursor,
        }

    def _open_page(
        self, scope: str, page: app.ReadCryptoResponse
    ) -> list[ReadRecord[Message]]:
        heads = {
            (head.id, head.revision, head.incarnation): head for head in page.heads
        }
        opened = self.session.open_result(page.bundle)
        result = [
            *(self._record(value) for value in opened.values),
            *(self._deletion(value) for value in opened.deletions),
        ]
        for record in result:
            head = heads.get(
                (record["record_id"], record["revision"], record["incarnation"])
            )
            if head is not None:
                record["cursor"] = int(head.cursor or 0)
        return result

    def read(self, scope: str, record_ids: list[str]) -> dict[str, ReadRecord[Message]]:
        page = self.session.read_bundle(scope, view="by_ids", value_ids=record_ids)
        return {value["record_id"]: value for value in self._open_page(scope, page)}

    def read_many(self, scopes):
        return {
            scope: {"records": self.read(scope, ids)} for scope, ids in scopes.items()
        }

    def _page(self, scope, **query):
        page = self.session.read_bundle(scope, **query)
        return {
            "records": self._open_page(scope, page),
            "cursor": int(page.cursor or 0)
            if query["view"] in ("changes", "history")
            else page.cursor,
            "has_more": page.has_more,
            "next_record_id": page.cursor,
            "snapshot_cursor": page.snapshot_cursor,
            "snapshot_epoch": page.snapshot_epoch,
            "receipts": list(page.bundle.commit_receipts),
            "retention_floor": page.retention_floor,
        }

    def current(
        self,
        scope,
        *,
        kind=None,
        after_record_id=None,
        snapshot_epoch=0,
        limit=256,
    ):
        return self._page(
            scope,
            view="current",
            kind=kind or "",
            cursor=after_record_id or "",
            limit=limit,
            snapshot_epoch=snapshot_epoch,
        )

    def immutable_kind(
        self,
        scope,
        kind,
        *,
        after: str = "",
        snapshot_cursor=None,
        snapshot_epoch=0,
        limit=256,
    ):
        return self._page(
            scope,
            view="page",
            kind=kind,
            cursor=after,
            limit=limit,
            immutable_only=True,
            snapshot_cursor=snapshot_cursor or 0,
            snapshot_epoch=snapshot_epoch,
        )

    def changes(self, scope, *, after=0, snapshot_epoch=0, limit=256):
        return self._page(
            scope,
            view="changes",
            cursor=str(after),
            snapshot_epoch=snapshot_epoch,
            limit=limit,
        )

    def page(self, scope, *, after=0, snapshot_epoch=0, limit=128):
        return self.changes(
            scope, after=after, snapshot_epoch=snapshot_epoch, limit=limit
        )

    def history(
        self,
        scope,
        record_id,
        *,
        before=0,
        snapshot_epoch=0,
        snapshot_cursor=0,
        limit=128,
    ):
        return self._page(
            scope,
            view="history",
            value_id=record_id,
            cursor=str(before) if before else "",
            limit=limit,
            snapshot_epoch=snapshot_epoch,
            snapshot_cursor=snapshot_cursor,
        )

    def write(
        self,
        scope,
        *,
        records,
        deletions=(),
        operation_id=None,
        preconditions: list[app.RecordPrecondition] | None = None,
        object_effects=None,
        deleted_objects=None,
        files=None,
        comments=None,
    ):
        for draft in (*records, *deletions):
            if draft["expected_revision"] and not draft.get("incarnation"):
                raise E2eeError("invalid_record")
        for condition in preconditions or ():
            if condition.expected_revision and not condition.incarnation:
                raise E2eeError("invalid_record")
        snapshot = self.session.read_bundle(
            scope,
            view="by_ids",
            value_ids=list(
                dict.fromkeys(
                    [draft["record_id"] for draft in (*records, *deletions)]
                    + [condition.id for condition in preconditions or []]
                )
            ),
        )
        project, bundle = snapshot.project, snapshot.bundle
        if project.project_id != scope:
            raise E2eeError("invalid_response")
        key = project.protection_key
        current = {item["record_id"]: item for item in self._open_page(scope, snapshot)}
        for draft in (*records, *deletions):
            if draft["expected_revision"]:
                selected = current.get(draft["record_id"])
                if (
                    selected is None
                    or selected["payload_type"] != "content"
                    or selected["revision"] != draft["expected_revision"]
                    or draft["incarnation"] != selected["incarnation"]
                ):
                    raise E2eeError("revision_conflict")
        create_keys, deliveries = [], []
        policy = None
        if project.key_distribution_revision != project.distribution_revision:
            audience = self.session.audience(project.group_id, scope)
            project = next(
                (item for item in audience.projects if item.project_id == scope), None
            )
            if project is None:
                raise E2eeError("invalid_response")
            bundle = audience.bundle
            key = project.protection_key
            if project.key_distribution_revision != project.distribution_revision:
                key = shared.KeyRef(id=key.id, generation=key.generation + 1)
                create_keys = [key]
                deliveries = [
                    crypto.DeliveryMutation(target=key, recipient=member.receiver)
                    for member in audience.members
                ]
                policy = app.ProjectPolicyBinding(
                    project_id=scope,
                    group_id=project.group_id,
                    shared=project.shared,
                    current_protection_key=key,
                    expected_distribution_revision=project.distribution_revision,
                    prepare_owner_deliveries=True,
                )
        values = []
        heads = []
        author_device_id = self.session.device_id
        for draft in records:
            if draft["kind"] not in RECORD_KINDS:
                raise E2eeError("invalid_record")
            values.append(
                crypto.ValueMutation(
                    id=draft["record_id"],
                    expected_revision=draft["expected_revision"],
                    protection_key=key,
                    plaintext=self._payload(draft["value"], draft["kind"]),
                    kind=draft["kind"],
                    incarnation=draft.get("incarnation")
                    or operation_id
                    or self.operation_id,
                    immutable=draft.get("immutable", False),
                )
            )
            heads.append(
                app.RecordHead(
                    id=draft["record_id"],
                    revision=draft["expected_revision"] + 1,
                    kind=draft["kind"],
                    content=app.RecordContentHead(),
                    incarnation=draft.get("incarnation")
                    or operation_id
                    or self.operation_id,
                    immutable=draft.get("immutable", False),
                    author_device_id=author_device_id,
                )
            )
        removed = []
        for draft in deletions:
            removed.append(
                crypto.RecordDeletion(
                    id=draft["record_id"],
                    expected_revision=draft["expected_revision"],
                    kind=draft["kind"],
                    incarnation=draft["incarnation"],
                    committed_at=draft.get("committed_at", int(time.time())),
                )
            )
            heads.append(
                app.RecordHead(
                    id=draft["record_id"],
                    revision=draft["expected_revision"] + 1,
                    kind=draft["kind"],
                    incarnation=draft["incarnation"],
                    deletion=app.RecordDeletionHead(),
                    author_device_id=author_device_id,
                )
            )
        binding = app.RecordMutationBinding(
            heads=heads,
            preconditions=preconditions or [],
            deleted_objects=deleted_objects or [],
            object_effects=object_effects or [],
            files=files or [],
            comments=comments or [],
        )
        if policy is not None:
            binding.project_policy.CopyFrom(policy)
        self.session.prepare(
            scope,
            values=values,
            deletions=removed,
            operation_id=operation_id or self.operation_id,
            create_keys=create_keys,
            deliveries=deliveries,
            binding=binding.SerializeToString(),
            bundle=bundle,
        )
        self.operation_id = str(uuid.uuid4())
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
        request = app.CommitCryptoRequest(project_id=scope, command=command)
        response, opened = self.session.commit(
            scope,
            mutation=request,
            send=lambda: self.session.service.commit_crypto(request),
        )
        self.last_receipt = response.receipt
        try:
            return [
                *(self._record(value) for value in opened.values),
                *(self._deletion(value) for value in opened.deletions),
            ]
        except Exception as error:
            return AcceptedCommand(command, {"kind": "committed"}, error)

    def create_project(
        self,
        *,
        value: domain.ProjectInfo,
        owner_org=None,
        participation_policy="private",
        project_id=None,
    ):
        from ._conversation_context import initial_records
        from ._directory import initial_directory

        if not owner_org or participation_policy not in {"private", "organization"}:
            raise E2eeError("invalid_project_policy")
        self.session.initialize_organization(owner_org)
        identifier = project_id or "prj_" + secrets.token_hex(16)
        key = shared.KeyRef(id=identifier, generation=1)
        directory_id, drafts = initial_directory(self.operation_id)
        drafts.extend(initial_records(identifier))
        project = domain.ProjectInfo()
        project.CopyFrom(value)
        project.slug = identifier
        project.created_at.GetCurrentTime()
        project.updated_at.CopyFrom(project.created_at)
        payload = domain.ProjectRootContent(
            project=project,
            last_stage_version=0,
            directory=domain.DirectoryRootReference(root=directory_id),
        )
        drafts.append(
            {
                "record_id": identifier,
                "kind": "project",
                "expected_revision": 0,
                "value": payload,
            }
        )
        audience = self.session.audience(owner_org, "")
        values = [
            crypto.ValueMutation(
                id=d["record_id"],
                expected_revision=0,
                protection_key=key,
                plaintext=self._payload(d["value"], d["kind"]),
                incarnation=self.operation_id,
                kind=d["kind"],
            )
            for d in drafts
        ]
        author_device_id = self.session.device_id
        binding = app.RecordMutationBinding(
            project_policy=app.ProjectPolicyBinding(
                project_id=identifier,
                group_id=owner_org,
                shared=participation_policy == "organization",
                current_protection_key=key,
                prepare_owner_deliveries=True,
            ),
            heads=[
                app.RecordHead(
                    id=d["record_id"],
                    revision=1,
                    kind=d["kind"],
                    author_device_id=author_device_id,
                    content=app.RecordContentHead(),
                    incarnation=self.operation_id,
                )
                for d in drafts
            ],
        )
        deliveries = [
            crypto.DeliveryMutation(target=key, recipient=m.receiver)
            for m in audience.members
            if participation_policy == "organization"
            or m.owner_candidate
            or m.subject == self.session.subject
            or m.role in {"owner", "editor", "viewer"}
        ]
        command = self.session.prepare(
            identifier,
            values=values,
            operation_id=self.operation_id,
            deliveries=deliveries,
            create_keys=[key],
            binding=binding.SerializeToString(),
            bundle=audience.bundle,
        )
        request = app.ProjectCreateRequest(
            project_id=identifier,
            group_id=owner_org,
            shared=participation_policy == "organization",
            protection_key=key,
            mutation=app.CommitCryptoRequest(project_id=identifier, command=command),
        )
        self.session.commit(
            identifier,
            mutation=request.mutation,
            send=lambda: self.session.service.create_crypto_project(request),
            initialize=False,
        )
        self.operation_id = str(uuid.uuid4())
        return identifier
