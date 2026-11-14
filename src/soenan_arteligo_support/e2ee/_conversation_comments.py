from __future__ import annotations

from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._conversation_context import (
    MAX_INTEGER,
    M,
    conflict_retry,
    number,
    reference,
    text,
    verify_actor,
    write,
)
from ._conversation_text import TextOperations, target_type, valid_body
from ._crypto import E2eeError
from ._records import ReadRecord
from ._signed_commands import AcceptedCommand


def comment_target(
    identifier: str, revision: int, incarnation: str, *, expected: int | None = None
) -> crypto.TargetHead:
    return crypto.TargetHead(
        id=identifier,
        revision=revision,
        incarnation=incarnation,
        expected_revision=revision - 1 if expected is None else expected,
    )


def comment_binding(
    item: app.CommentViewItem,
    *,
    operation: str,
    value_id: str,
    value_revision: int,
) -> app.CommentRevisionBinding:
    binding = app.CommentRevisionBinding(
        thread_id=item.thread_id,
        comment_id=item.comment_id,
        revision=item.revision,
        value_id=value_id,
        value_revision=value_revision,
        origin=item.origin,
        thread_head=item.thread_head,
        body_head=item.body_head,
        text_revisions=list(item.text_revisions[-1:]),
        anchor_id=item.anchor_id,
        sequence=item.sequence,
        reply_sequence=item.reply_sequence,
        operation=operation,
        parent_comment_id=item.parent_comment_id,
    )
    if item.HasField("resolution"):
        binding.resolution.CopyFrom(item.resolution)
    return binding


class CommentOperations(TextOperations):
    def _comment_anchor_id(self, anchor):
        case = anchor.WhichOneof("target")
        if case is None:
            raise E2eeError("invalid_conversation")
        return text(getattr(anchor, case))

    def _comment_snapshot(
        self,
        *,
        identifier="",
        ids=(),
        anchor=None,
        after: domain.CommentCursor | None = None,
        limit=100,
    ):
        if type(limit) is not int or limit < 1:
            raise E2eeError("invalid_cursor")
        if after is not None and (
            not 1 <= after.sequence <= MAX_INTEGER
            or not 1 <= len(after.id) <= 128
            or any(
                not (
                    "a" <= char <= "z"
                    or "A" <= char <= "Z"
                    or "0" <= char <= "9"
                    or char in "_-"
                )
                for char in after.id
            )
        ):
            raise E2eeError("invalid_cursor")
        if ids and (after is not None or anchor is not None):
            raise E2eeError("invalid_request")
        self.checkpoint()
        anchor_id = self._comment_anchor_id(anchor) if anchor is not None else ""
        response = self.records.session.read_bundle(
            self.scope,
            view="comments",
            value_id=identifier,
            value_ids=ids,
            comment_anchor_id=anchor_id,
            comment_cursor=after,
            limit=limit,
        )
        records = {
            record["record_id"]: record
            for record in self.records._open_page(self.scope, response)
        }
        self.checkpoint()
        for item in response.comments:
            if not item.parent_comment_id:
                original = self._comment_record(
                    self._comment_reference(records, item.origin), domain.CommentOrigin
                )
                if item.anchor_id != self._comment_anchor_id(original["value"].anchor):
                    raise E2eeError("invalid_conversation_comment")
        return response, records

    @staticmethod
    def _comment_item(
        response: app.ReadCryptoResponse, identifier: str
    ) -> app.CommentViewItem | None:
        return next(
            (item for item in response.comments if item.comment_id == identifier), None
        )

    def _comment_reference(self, records, target):
        record = records.get(target.id)
        if (
            record is None
            or record["revision"] != target.revision
            or record["incarnation"] != target.incarnation
        ):
            raise E2eeError("invalid_conversation_comment")
        return record

    def _comment_record(self, record, record_type: type[M]) -> ReadRecord[M]:
        result = self._record(record, "comment", record_type, immutable=True)
        verify_actor(result, "author")
        return result

    def _resolution_record(self, record, parent_id, incarnation):
        result = self._record(record, "comment", domain.ResolutionEvent, immutable=True)
        value = result["value"]
        if value.original != domain.RecordReference(
            id=parent_id, revision=1, incarnation=incarnation
        ) or result["record_id"] != "cres_" + text(value.operation_id):
            raise E2eeError("invalid_conversation_resolution")
        verify_actor(result, "actor")
        return result

    def _snapshot_text(self, response, records, item):
        original = self._comment_record(
            self._comment_reference(records, item.origin),
            domain.ReplyOrigin if item.parent_comment_id else domain.CommentOrigin,
        )
        value = original["value"]
        if original["record_id"] != item.comment_id or original["value"].sequence != (
            item.reply_sequence if item.parent_comment_id else item.sequence
        ):
            raise E2eeError("invalid_conversation_comment")
        if isinstance(value, domain.ReplyOrigin):
            root = self._comment_item(response, item.thread_id)
            if (
                root is None
                or root.comment_id != item.parent_comment_id
                or value.parent_comment_id != item.parent_comment_id
                or item.anchor_id != root.anchor_id
                or item.sequence != root.sequence
            ):
                raise E2eeError("invalid_conversation_comment")
        head = self._comment_reference(records, item.body_head)
        if head["record_id"] != original["value"].body_head_id:
            raise E2eeError("invalid_conversation_text")
        context = self._text_context(original, head, records)
        edit = context["edit"]
        latest = item.text_revisions[-1] if item.text_revisions else None
        if (edit is None) != (latest is None) or (
            edit is not None
            and latest is not None
            and (
                latest.id != edit["record_id"]
                or latest.revision != edit["revision"]
                or latest.incarnation != edit["incarnation"]
            )
        ):
            raise E2eeError("invalid_conversation_text")
        return context

    def _snapshot_thread(self, response, records, item):
        if item is None or item.parent_comment_id or item.thread_id != item.comment_id:
            raise E2eeError("invalid_conversation_comment")
        context = self._snapshot_text(response, records, item)
        original = context["original"]
        head = self._header(
            self._comment_reference(records, item.thread_head),
            "comment",
            domain.ThreadHead,
        )
        if head["record_id"] != original["value"].thread_head_id or head[
            "value"
        ].original != domain.RecordReference(
            id=item.comment_id, revision=1, incarnation=original["incarnation"]
        ):
            raise E2eeError("invalid_conversation_comment")
        number(head["value"].reply_count)
        ref = (
            reference(head["value"].resolution)
            if head["value"].HasField("resolution")
            else None
        )
        if (ref is None) != (not item.HasField("resolution")) or (
            ref is not None
            and (
                ref.revision != 1
                or ref.id != item.resolution.id
                or ref.revision != item.resolution.revision
                or ref.incarnation != item.resolution.incarnation
            )
        ):
            raise E2eeError("invalid_conversation_resolution")
        resolution = (
            self._resolution_record(
                self._comment_reference(records, item.resolution),
                item.comment_id,
                original["incarnation"],
            )
            if ref
            else None
        )
        return {
            "comment": original,
            "head": head,
            "text": context,
            "resolution": resolution,
        }

    def _thread_view(self, context) -> domain.CommentView:
        value = self._comment_view(context["text"])
        value.thread_head.CopyFrom(context["head"]["value"])
        value.has_more_replies = context["head"]["value"].reply_count > 0
        if context["resolution"]:
            value.resolution.CopyFrom(context["resolution"]["value"])
        return value

    def comment_thread(self, identifier):
        response, records = self._comment_snapshot(ids=[identifier])
        item = self._comment_item(response, identifier)
        return (
            self._thread_view(self._snapshot_thread(response, records, item))
            if item is not None
            else None
        )

    def comment_threads(
        self, *, anchor=None, after: domain.CommentCursor | None = None, limit=100
    ):
        response, records = self._comment_snapshot(
            anchor=anchor, after=after, limit=limit
        )
        threads = []
        previous = after
        for item in response.comments:
            if not item.parent_comment_id:
                context = self._snapshot_thread(response, records, item)
                if anchor is not None and item.anchor_id != self._comment_anchor_id(
                    anchor
                ):
                    raise E2eeError("invalid_conversation_comment")
                if item.sequence < 1 or (
                    previous is not None
                    and (
                        item.sequence < previous.sequence
                        or (
                            item.sequence == previous.sequence
                            and item.comment_id <= previous.id
                        )
                    )
                ):
                    raise E2eeError("invalid_conversation_index")
                threads.append(self._thread_view(context))
                previous = domain.CommentCursor(
                    sequence=item.sequence, id=item.comment_id
                )
        following = (
            response.next_comment_cursor
            if response.HasField("next_comment_cursor")
            else None
        )
        if following is not None and (not threads or following != previous):
            raise E2eeError("invalid_conversation_index")
        return {"threads": threads, "next_key": following}

    def comment_replies(
        self, parent_id, *, after: domain.CommentCursor | None = None, limit=100
    ):
        response, records = self._comment_snapshot(
            identifier=parent_id, after=after, limit=limit
        )
        root = self._comment_item(response, parent_id)
        if root is None:
            raise E2eeError("comment_not_found")
        context = self._snapshot_thread(response, records, root)
        sequence = after.sequence if after is not None else 0
        last = None
        replies = []
        for item in response.comments:
            if item.parent_comment_id:
                sequence += 1
                if (
                    item.parent_comment_id != parent_id
                    or item.reply_sequence != sequence
                ):
                    raise E2eeError("invalid_conversation_index")
                replies.append(
                    self._reply_view(self._snapshot_text(response, records, item))
                )
                last = domain.CommentCursor(sequence=sequence, id=item.comment_id)
        total = number(context["head"]["value"].reply_count)
        following = (
            response.next_comment_cursor
            if response.HasField("next_comment_cursor")
            else None
        )
        if (
            sequence > total
            or (following is None and sequence != total)
            or (
                following is not None
                and (last is None or following != last or sequence >= total)
            )
        ):
            raise E2eeError("invalid_conversation_index")
        return {"replies": replies, "next_key": following, "total_count": total}

    def comment_reply(self, identifier):
        response, records = self._comment_snapshot(ids=[identifier])
        item = self._comment_item(response, identifier)
        if item is None:
            return None
        if not item.parent_comment_id:
            raise E2eeError("invalid_conversation_comment")
        root = self._comment_item(response, item.thread_id)
        context = self._snapshot_thread(response, records, root)
        if (
            item.parent_comment_id != context["comment"]["record_id"]
            or item.reply_sequence > context["head"]["value"].reply_count
        ):
            raise E2eeError("invalid_conversation_comment")
        return self._reply_view(self._snapshot_text(response, records, item))

    def _same_comment_input(self, record, value):
        current = type(value)()
        current.CopyFrom(record["value"])
        for field in (
            "thread_head_id",
            "body_head_id",
            "sequence",
            "created_at",
            "author",
        ):
            if field in current.DESCRIPTOR.fields_by_name:
                current.ClearField(field)
        expected = type(value)()
        expected.CopyFrom(value)
        for field in (
            "thread_head_id",
            "body_head_id",
            "sequence",
            "created_at",
            "author",
        ):
            if field in expected.DESCRIPTOR.fields_by_name:
                expected.ClearField(field)
        return record["author_subject"] == self.subject and current == expected

    @conflict_retry
    def create_comment(
        self,
        identifier,
        *,
        body,
        anchor,
        author,
        created_at,
        time_span=None,
        region=None,
        tag=None,
    ):
        text(identifier)
        if not isinstance(body, str) or not body.strip():
            raise E2eeError("invalid_request")
        original = domain.CommentOrigin(
            body=body, anchor=anchor, author=author, created_at=created_at
        )
        for name, value in (("time_span", time_span), ("region", region)):
            if value is not None:
                getattr(original, name).CopyFrom(value)
        if tag is not None:
            original.tag = tag
        verify_actor({"value": original, "author_subject": self.subject}, "author")
        response, records = self._comment_snapshot(ids=[identifier])
        existing = self._comment_item(response, identifier)
        if existing is not None:
            context = self._snapshot_thread(response, records, existing)
            if not self._same_comment_input(context["comment"], original):
                raise E2eeError("idempotency_conflict")
            return self._thread_view(context)
        original.sequence = number(response.latest_comment_sequence) + 1
        number(original.sequence, 1)
        original.thread_head_id, original.body_head_id = self.mint_id(), self.mint_id()
        incarnation = self.records.operation_id
        item = app.CommentViewItem(
            thread_id=identifier,
            comment_id=identifier,
            revision=1,
            origin=comment_target(identifier, 1, incarnation),
            thread_head=comment_target(original.thread_head_id, 1, incarnation),
            body_head=comment_target(original.body_head_id, 1, incarnation),
            anchor_id=self._comment_anchor_id(anchor),
            sequence=original.sequence,
        )
        outcome = self._write(
            [
                write(identifier, "comment", original, immutable=True),
                self._initial_text_head(identifier, "comment", original.body_head_id),
                write(
                    original.thread_head_id,
                    "comment",
                    domain.ThreadHead(
                        original=domain.RecordReference(
                            id=identifier, revision=1, incarnation=incarnation
                        ),
                        reply_count=0,
                    ),
                ),
            ],
            comments=[
                comment_binding(
                    item, operation="create", value_id=identifier, value_revision=1
                )
            ],
        )
        if isinstance(outcome, AcceptedCommand):
            return outcome
        return domain.CommentView(
            id=identifier,
            origin=original,
            text_head=domain.TextHead(
                original=domain.RecordReference(
                    id=identifier, revision=1, incarnation=incarnation
                ),
                target_type=domain.TEXT_TARGET_TYPE_COMMENT,
                text_revision=1,
            ),
            thread_head=domain.ThreadHead(
                original=domain.RecordReference(
                    id=identifier, revision=1, incarnation=incarnation
                ),
                reply_count=0,
            ),
            has_more_replies=False,
        )

    @conflict_retry
    def create_reply(
        self, identifier, *, parent_id, body, references, author, created_at
    ):
        text(identifier)
        if not isinstance(body, str) or not (body.strip() or references):
            raise E2eeError("invalid_request")
        original = domain.ReplyOrigin(
            parent_comment_id=parent_id,
            body=body,
            references=references,
            author=author,
            created_at=created_at,
        )
        verify_actor({"value": original, "author_subject": self.subject}, "author")
        response, records = self._comment_snapshot(
            identifier=parent_id, ids=[identifier]
        )
        root = self._comment_item(response, parent_id)
        if root is None:
            raise E2eeError("comment_not_found")
        context = self._snapshot_thread(response, records, root)
        existing = self._comment_item(response, identifier)
        if existing is not None:
            current = self._snapshot_text(response, records, existing)
            if existing.parent_comment_id != parent_id or not self._same_comment_input(
                current["original"], original
            ):
                raise E2eeError("idempotency_conflict")
            return self._reply_view(current)
        original.sequence = number(context["head"]["value"].reply_count) + 1
        number(original.sequence, 1)
        original.body_head_id = self.mint_id()
        incarnation = self.records.operation_id
        updated = app.CommentViewItem()
        updated.CopyFrom(root)
        updated.revision += 1
        head = context["head"]
        updated.thread_head.CopyFrom(
            comment_target(head["record_id"], head["revision"] + 1, head["incarnation"])
        )
        item = app.CommentViewItem(
            thread_id=parent_id,
            comment_id=identifier,
            revision=1,
            origin=comment_target(identifier, 1, incarnation),
            thread_head=updated.thread_head,
            body_head=comment_target(original.body_head_id, 1, incarnation),
            anchor_id=root.anchor_id,
            sequence=root.sequence,
            reply_sequence=original.sequence,
            parent_comment_id=parent_id,
        )
        new_head = domain.ThreadHead()
        new_head.CopyFrom(head["value"])
        new_head.reply_count = original.sequence
        outcome = self._write(
            [
                write(identifier, "comment", original, immutable=True),
                self._initial_text_head(identifier, "reply", original.body_head_id),
                write(
                    head["record_id"],
                    "comment",
                    new_head,
                    revision=head["revision"],
                    incarnation=head["incarnation"],
                ),
            ],
            [
                app.RecordPrecondition(
                    id=parent_id,
                    expected_revision=1,
                    incarnation=context["comment"]["incarnation"],
                )
            ],
            comments=[
                comment_binding(
                    updated,
                    operation="reply",
                    value_id=head["record_id"],
                    value_revision=head["revision"] + 1,
                ),
                comment_binding(
                    item, operation="reply", value_id=identifier, value_revision=1
                ),
            ],
        )
        return (
            outcome
            if isinstance(outcome, AcceptedCommand)
            else domain.ReplyView(
                id=identifier,
                origin=original,
                text_head=domain.TextHead(
                    original=domain.RecordReference(
                        id=identifier, revision=1, incarnation=incarnation
                    ),
                    target_type=domain.TEXT_TARGET_TYPE_REPLY,
                    text_revision=1,
                ),
            )
        )

    @conflict_retry
    def set_resolution(self, parent_id, *, resolved, actor, operation_id):
        if type(resolved) is not bool:
            raise E2eeError("invalid_request")
        text(operation_id)
        event = domain.ResolutionEvent(
            original=domain.RecordReference(id=parent_id, revision=1, incarnation=""),
            resolved=resolved,
            operation_id=operation_id,
            actor=actor,
        )
        verify_actor({"value": event, "author_subject": self.subject}, "actor")
        event_id = "cres_" + operation_id
        response, records = self._comment_snapshot(identifier=parent_id, ids=[event_id])
        root = self._comment_item(response, parent_id)
        if root is None:
            raise E2eeError("comment_not_found")
        context = self._snapshot_thread(response, records, root)
        event.original.incarnation = context["comment"]["incarnation"]
        if event_id in records:
            record = self._resolution_record(
                records[event_id], parent_id, context["comment"]["incarnation"]
            )
            if (
                record["author_subject"] != self.subject
                or record["value"].resolved != resolved
            ):
                raise E2eeError("idempotency_conflict")
            return self._thread_view(context)
        head = context["head"]
        updated = app.CommentViewItem()
        updated.CopyFrom(root)
        updated.revision += 1
        updated.thread_head.CopyFrom(
            comment_target(head["record_id"], head["revision"] + 1, head["incarnation"])
        )
        updated.resolution.CopyFrom(
            comment_target(event_id, 1, self.records.operation_id)
        )
        new_head = domain.ThreadHead()
        new_head.CopyFrom(head["value"])
        new_head.resolution.CopyFrom(
            domain.RecordReference(
                id=event_id, revision=1, incarnation=self.records.operation_id
            )
        )
        outcome = self._write(
            [
                write(event_id, "comment", event, immutable=True),
                write(
                    head["record_id"],
                    "comment",
                    new_head,
                    revision=head["revision"],
                    incarnation=head["incarnation"],
                ),
            ],
            [
                app.RecordPrecondition(
                    id=parent_id,
                    expected_revision=1,
                    incarnation=context["comment"]["incarnation"],
                )
            ],
            comments=[
                comment_binding(
                    updated, operation="resolve", value_id=event_id, value_revision=1
                )
            ],
        )
        if isinstance(outcome, AcceptedCommand):
            return outcome
        value = self._thread_view(context)
        value.thread_head.CopyFrom(new_head)
        value.resolution.CopyFrom(event)
        return value

    @conflict_retry
    def _edit_text(
        self,
        identifier,
        target,
        operation_id,
        expected_revision,
        body,
        committed_at,
        parent_id=None,
    ):
        number(expected_revision, 1)
        text(operation_id)
        event_id = "ctxt_" + operation_id
        response, records = self._comment_snapshot(
            identifier=identifier, ids=[event_id]
        )
        item = self._comment_item(response, identifier)
        if item is None:
            raise E2eeError("comment_not_found")
        context = self._snapshot_text(response, records, item)
        original = context["original"]
        expected_type = (
            domain.ReplyOrigin if target == "reply" else domain.CommentOrigin
        )
        if not isinstance(original["value"], expected_type):
            raise E2eeError("invalid_request")
        root = self._comment_item(response, item.thread_id)
        self._snapshot_thread(response, records, root)
        if not valid_body(original, body):
            raise E2eeError("invalid_request")
        if original["author_subject"] != self.subject:
            raise E2eeError("not_comment_author")
        if target == "reply" and original["value"].parent_comment_id != parent_id:
            raise E2eeError("comment_parent_mismatch")
        if event_id in records:
            event = self._text_edit(records[event_id], original)["value"]
            if (
                event.operation_id != operation_id
                or event.text_revision != expected_revision + 1
                or event.body != body
            ):
                raise E2eeError("idempotency_conflict")
            return
        head = context["head"]
        revision = head["value"].text_revision
        if revision != expected_revision:
            raise E2eeError("revision_conflict")
        event = domain.TextRevision(
            original=domain.RecordReference(
                id=identifier, revision=1, incarnation=original["incarnation"]
            ),
            target_type=target_type(original["value"]),
            body_head_id=head["record_id"],
            operation_id=operation_id,
            text_revision=revision + 1,
            author_account_subject=self.subject,
            body=body,
            committed_at=committed_at,
        )
        updated = app.CommentViewItem()
        updated.CopyFrom(item)
        updated.revision += 1
        updated.body_head.CopyFrom(
            comment_target(head["record_id"], head["revision"] + 1, head["incarnation"])
        )
        del updated.text_revisions[:]
        updated.text_revisions.append(
            comment_target(event_id, 1, self.records.operation_id)
        )
        new_head = domain.TextHead()
        new_head.CopyFrom(head["value"])
        new_head.text_revision = revision + 1
        new_head.last_edit.CopyFrom(
            domain.RecordReference(
                id=event_id, revision=1, incarnation=self.records.operation_id
            )
        )
        return self._write(
            [
                write(event_id, "comment", event, immutable=True),
                write(
                    head["record_id"],
                    "comment",
                    new_head,
                    revision=head["revision"],
                    incarnation=head["incarnation"],
                ),
            ],
            [
                app.RecordPrecondition(
                    id=identifier,
                    expected_revision=1,
                    incarnation=original["incarnation"],
                )
            ],
            comments=[
                comment_binding(
                    updated, operation="edit", value_id=event_id, value_revision=1
                )
            ],
        )

    def edit_comment(
        self, identifier, *, operation_id, expected_revision, body, committed_at
    ):
        outcome = self._edit_text(
            identifier, "comment", operation_id, expected_revision, body, committed_at
        )
        return (
            outcome
            if isinstance(outcome, AcceptedCommand)
            else self.comment_thread(identifier)
        )

    def edit_reply(
        self,
        identifier,
        *,
        parent_id,
        operation_id,
        expected_revision,
        body,
        committed_at,
    ):
        outcome = self._edit_text(
            identifier,
            "reply",
            operation_id,
            expected_revision,
            body,
            committed_at,
            parent_id,
        )
        return (
            outcome
            if isinstance(outcome, AcceptedCommand)
            else self.comment_reply(identifier)
        )
