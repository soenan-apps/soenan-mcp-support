from __future__ import annotations

import re
from hashlib import sha256

from google.protobuf.timestamp_pb2 import Timestamp
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._conversation_context import (
    ConversationContext,
    chat_header_id,
    conflict_retry,
    descending,
    number,
    reference,
)
from ._crypto import E2eeError
from ._signed_commands import AcceptedCommand


class ChatOperations(ConversationContext):
    def _event_view(self, record):
        if record["kind"] != "chat_message":
            raise E2eeError("invalid_conversation")
        view = domain.ChatEventView(
            id=record["record_id"],
            project_id=self.scope,
            message_id=record["record_id"],
            revision=record["revision"],
            sequence=record["cursor"],
            incarnation=record["incarnation"],
        )
        if record["payload_type"] == "deletion":
            view.author_membership_id = record["author_subject"]
            view.actor_membership_id = record["author_subject"]
            view.client_operation_id = record["operation_id"]
            view.committed_at.seconds = record["committed_at"]
            view.deletion.SetInParent()
        else:
            value = self._record(record, "chat_message", domain.ChatMessage)["value"]
            if (
                value.author_membership_id != record["author_subject"]
                or value.actor_membership_id != record["author_subject"]
            ):
                raise E2eeError("invalid_conversation_author")
            view.author_membership_id = value.author_membership_id
            view.actor_membership_id = value.actor_membership_id
            view.client_operation_id = value.client_operation_id
            view.committed_at.CopyFrom(value.committed_at)
            view.message.CopyFrom(value)
        return view

    @conflict_retry
    def chat_messages(self, *, before_sequence=None, limit=100):
        if type(limit) is not int or limit < 1:
            raise E2eeError("invalid_cursor")
        if before_sequence is not None:
            number(before_sequence, 1)
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        entries, following = self._index("chat").page(
            reference(header["value"].messages),
            after=(descending(before_sequence), "\uffff")
            if before_sequence is not None
            else None,
            limit=limit,
        )
        selected = self._read(entry.key.id for entry in entries)
        messages = []
        previous = before_sequence
        for entry in entries:
            if entry.key.name != descending(entry.sequence) or (
                previous is not None and entry.sequence >= previous
            ):
                raise E2eeError("invalid_conversation_index")
            previous = entry.sequence
            record = selected.get(entry.key.id)
            if record is None:
                continue
            view = self._event_view(record)
            if view.WhichOneof("state") == "message" and (
                view.message.sent_sequence != entry.sequence
            ):
                raise E2eeError("invalid_conversation_index")
            messages.append(
                domain.ChatMessageView(
                    latest=view,
                    verified_through_sequence=header["cursor"],
                )
            )
        self._same_records([header])
        return {
            "messages": messages,
            "next_before_sequence": entries[-1].sequence if following else None,
            "latest_sequence": header["cursor"],
        }

    def chat_message(self, message_id):
        record = self._read([message_id]).get(message_id)
        if record is None:
            return None
        view = self._event_view(record)
        return domain.ChatMessageView(
            latest=view,
            verified_through_sequence=view.sequence,
        )

    def chat_events(self, *, after=0, snapshot_epoch=0, limit=200):
        number(after)
        if type(limit) is not int or limit < 1:
            raise E2eeError("invalid_cursor")
        page = self.records._page(
            self.scope,
            view="changes",
            kind="chat_message",
            cursor=str(after),
            snapshot_epoch=snapshot_epoch,
            limit=limit,
        )
        return {
            "events": [
                self._event_view(record)
                for record in sorted(
                    page["records"], key=lambda record: record["cursor"]
                )
            ],
            "latest_sequence": page["cursor"],
            "has_more": page["has_more"],
            "snapshot_epoch": page["snapshot_epoch"],
            "retention_floor": page["retention_floor"],
        }

    def chat_operation(
        self,
        operation_id,
        *,
        message_id=None,
        type=None,
        revision=None,
        incarnation=None,
        command=None,
    ):
        page = self.records._page(
            self.scope,
            view="receipt",
            value_id=operation_id,
        )
        receipts = [
            receipt
            for receipt in page["receipts"]
            if receipt.operation_id == operation_id
        ]
        if not receipts:
            return None
        if len(receipts) != 1:
            raise E2eeError("invalid_conversation_operation")
        receipt = receipts[0]
        matches = [
            self._event_view(record)
            for record in page["records"]
            if record["kind"] == "chat_message"
        ]
        if matches:
            if len(matches) != 1 or matches[0].client_operation_id != operation_id:
                raise E2eeError("invalid_conversation_operation")
            result = matches[0]
        else:
            if message_id is None or revision is None or not incarnation:
                raise E2eeError("operation_context_required")
            heads = [head for head in receipt.heads if head.id == message_id]
            if len(heads) != 1:
                raise E2eeError("invalid_conversation_operation")
            head = heads[0]
            result = domain.ChatEventView(
                id=head.id,
                project_id=self.scope,
                message_id=head.id,
                revision=head.revision,
                incarnation=head.incarnation,
                client_operation_id=operation_id,
            )
            result.receipt.SetInParent()
        if message_id is not None and (
            result.message_id != message_id
            or result.revision != revision
            or result.incarnation != incarnation
        ):
            raise E2eeError("idempotency_conflict")
        heads = [head for head in receipt.heads if head.id == result.message_id]
        if len(heads) != 1 or (
            heads[0].revision != result.revision
            or heads[0].incarnation != result.incarnation
        ):
            raise E2eeError("invalid_conversation_operation")
        if command is not None:
            mutation = crypto.MutationBody.FromString(command.body)
            if (
                mutation.operation_id != operation_id
                or sha256(command.body).digest() != receipt.mutation_digest
                or list(mutation.target_heads) != list(receipt.heads)
            ):
                raise E2eeError("invalid_conversation_operation")
            removed = {
                crypto.RecordDeletionBody.FromString(signed.body).id
                for signed in mutation.deletions
            }
            accepted_type = (
                domain.CHAT_EVENT_TYPE_DELETED
                if result.message_id in removed
                else domain.CHAT_EVENT_TYPE_SENT
                if heads[0].expected_revision == 0
                else domain.CHAT_EVENT_TYPE_EDITED
            )
            if (
                type is not None
                and accepted_type
                != {
                    "sent": domain.CHAT_EVENT_TYPE_SENT,
                    "edited": domain.CHAT_EVENT_TYPE_EDITED,
                    "deleted": domain.CHAT_EVENT_TYPE_DELETED,
                }[type]
            ):
                raise E2eeError("idempotency_conflict")
            if result.WhichOneof("state") == "receipt":
                result.receipt.type = accepted_type
        return result

    @conflict_retry
    def write_chat(
        self,
        *,
        type: str,
        message_id: str,
        operation_id: str,
        committed_at: Timestamp,
        body: str | None = None,
        references: list[domain.ProjectReference] | None = None,
        expected_revision: int | None = None,
        expected_incarnation: str | None = None,
    ) -> domain.ChatEventView | AcceptedCommand:
        references = [] if references is None else references
        if (
            type not in {"sent", "edited", "deleted"}
            or re.fullmatch(r"cmsg_[0-9a-f]{32}", message_id) is None
            or re.fullmatch(r"[A-Za-z0-9_-]{1,123}", operation_id) is None
            or ((type == "deleted") != (body is None))
            or (type != "sent" and references)
            or (
                type != "sent"
                and (expected_revision is None or not expected_incarnation)
            )
            or (type == "sent" and body == "" and not references)
        ):
            raise E2eeError("invalid_request")
        expected = 0 if type == "sent" else number(expected_revision, 1)
        pending = self.records.session.pending_command(self.scope)
        if pending is not None:
            command = crypto.MutationBody.FromString(pending.body)
            if command.operation_id != operation_id:
                raise E2eeError("record_publication_pending")
            outcome = self.records.resume_write(self.scope)
            if isinstance(outcome, AcceptedCommand):
                return outcome
        accepted = self.chat_operation(
            operation_id,
            command=pending,
            message_id=message_id,
            type=type,
            revision=expected + 1,
            incarnation=operation_id if type == "sent" else expected_incarnation,
        )
        if accepted is not None:
            expected_state = "deletion" if type == "deleted" else "message"
            if (
                accepted.message_id != message_id
                or accepted.WhichOneof("state") not in {expected_state, "receipt"}
                or (
                    type != "sent"
                    and (
                        accepted.revision != expected + 1
                        or accepted.incarnation != expected_incarnation
                    )
                )
                or (type == "sent" and accepted.revision != 1)
                or (
                    accepted.WhichOneof("state") == "message"
                    and accepted.message.body != body
                )
                or (
                    type == "sent"
                    and accepted.WhichOneof("state") == "message"
                    and accepted.message.references != references
                )
                or (
                    accepted.WhichOneof("state") == "receipt"
                    and accepted.receipt.HasField("type")
                    and accepted.receipt.type
                    != {
                        "sent": domain.CHAT_EVENT_TYPE_SENT,
                        "edited": domain.CHAT_EVENT_TYPE_EDITED,
                        "deleted": domain.CHAT_EVENT_TYPE_DELETED,
                    }[type]
                )
            ):
                raise E2eeError("idempotency_conflict")
            return accepted
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        current = self._read([message_id]).get(message_id)
        if type == "sent":
            if current is not None:
                raise E2eeError("idempotency_conflict")
            revision = 0
            incarnation = operation_id
        else:
            if current is None or current["payload_type"] != "content":
                raise E2eeError("message_not_found")
            self._event_view(current)
            if current["author_subject"] != self.subject:
                raise E2eeError("not_message_author")
            if (
                current["revision"] != expected_revision
                or current["incarnation"] != expected_incarnation
            ):
                raise E2eeError("revision_conflict")
            revision, incarnation = current["revision"], current["incarnation"]
            if type == "edited" and not body and not current["value"].references:
                raise E2eeError("invalid_request")
        writes, deletions = [], []
        if type == "deleted":
            deletions.append(
                {
                    "record_id": message_id,
                    "kind": "chat_message",
                    "expected_revision": revision,
                    "incarnation": incarnation,
                    "committed_at": committed_at.seconds,
                }
            )
        else:
            sequence = header["value"].sequence + 1
            value = domain.ChatMessage(
                author_membership_id=self.subject,
                actor_membership_id=self.subject,
                client_operation_id=operation_id,
                sequence=sequence,
                references=references
                if current is None
                else current["value"].references,
                body=body,
                committed_at=committed_at,
                sent_sequence=sequence
                if current is None
                else current["value"].sent_sequence,
                created_at=committed_at
                if current is None
                else current["value"].created_at,
            )
            writes.append(
                {
                    "record_id": message_id,
                    "kind": "chat_message",
                    "expected_revision": revision,
                    "incarnation": incarnation,
                    "value": value,
                }
            )
        updated = domain.ChatHeader()
        updated.CopyFrom(header["value"])
        updated.sequence += 1
        if type == "sent":
            index = self._index("chat")
            index.incarnation = operation_id
            root, index_writes = index.mutation(
                reference(updated.messages),
                domain.OrderedIndexEntry(
                    key=domain.OrderedEntryKey(
                        name=descending(updated.sequence), id=message_id
                    ),
                    sequence=updated.sequence,
                ),
            )
            updated.messages.CopyFrom(root)
            writes.extend(index_writes)
        writes.append(
            {
                "record_id": header["record_id"],
                "kind": "chat",
                "expected_revision": header["revision"],
                "incarnation": header["incarnation"],
                "value": updated,
            }
        )
        self.checkpoint()
        outcome = self.records.write(
            self.scope,
            records=writes,
            deletions=deletions,
            operation_id=operation_id,
        )
        if isinstance(outcome, AcceptedCommand):
            return outcome
        self.checkpoint()
        return next(
            self._event_view(record)
            for record in outcome
            if record["record_id"] == message_id
        )

    def chat_message_history(self, message_id):
        before, epoch, snapshot = 0, 0, 0
        history = None
        while True:
            self.checkpoint()
            page = self.records.history(
                self.scope,
                message_id,
                before=before,
                snapshot_epoch=epoch,
                limit=200,
                snapshot_cursor=snapshot,
            )
            epoch = page["snapshot_epoch"]
            snapshot = page["snapshot_cursor"]
            for record in page["records"]:
                view = self._event_view(record)
                if history is not None:
                    previous = history[1]
                    if (
                        view.revision != previous.revision - 1
                        or view.incarnation != previous.incarnation
                        or view.author_membership_id != previous.author_membership_id
                    ):
                        raise E2eeError("invalid_conversation_history")
                history = (view, view) if history is None else (history[0], view)
            if not page["has_more"]:
                break
            before = page["cursor"]
        if history is None:
            return None
        latest, previous = history
        if latest.WhichOneof("state") == "message" and previous.revision != 1:
            raise E2eeError("invalid_conversation_history")
        return domain.ChatMessageView(
            latest=latest,
            verified_through_sequence=latest.sequence,
        )
