from __future__ import annotations

import re
from typing import cast

from google.protobuf.timestamp_pb2 import Timestamp
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._conversation_context import (
    ConversationContext,
    ascending,
    chat_header_id,
    conflict_retry,
    descending,
    number,
    reference,
    text,
    write,
)
from ._crypto import E2eeError
from ._records import ReadRecord
from ._signed_commands import AcceptedCommand


def event_type(value):
    if isinstance(value, domain.ChatOrigin):
        return domain.CHAT_EVENT_TYPE_SENT
    return (
        domain.CHAT_EVENT_TYPE_DELETED
        if value.WhichOneof("change") == "deleted"
        else domain.CHAT_EVENT_TYPE_EDITED
    )


def event_revision(value):
    return 1 if isinstance(value, domain.ChatOrigin) else value.message_revision


def event_message_id(record):
    value = record["value"]
    return (
        record["record_id"]
        if isinstance(value, domain.ChatOrigin)
        else value.original.id
    )


class ChatOperations(ConversationContext):
    def _event_view(self, identifier, origin, event):
        value = domain.ChatEventView(
            id=identifier,
            project_id=self.scope,
            message_id=identifier
            if isinstance(event, domain.ChatOrigin)
            else event.original.id,
            origin=origin,
        )
        if isinstance(event, domain.ChatEvent):
            value.event.CopyFrom(event)
        return value

    def _chat_event(
        self, record
    ) -> ReadRecord[domain.ChatOrigin] | ReadRecord[domain.ChatEvent]:
        record = self._record(record, "chat", immutable=True)
        value = record["value"]
        event_record: ReadRecord[domain.ChatOrigin] | ReadRecord[domain.ChatEvent]
        match value:
            case domain.ChatOrigin():
                event_record = cast("ReadRecord[domain.ChatOrigin]", record)
                text(value.terminal_record_id)
            case domain.ChatEvent():
                event_record = cast("ReadRecord[domain.ChatEvent]", record)
                number(value.message_revision, 2)
                if (
                    value.original.revision != 1
                    or record["record_id"] != "cevt_" + value.client_operation_id
                ):
                    raise E2eeError("invalid_conversation_event")
            case _:
                raise E2eeError("invalid_conversation")
        if (
            value.actor_membership_id != record["author_subject"]
            or value.author_membership_id != record["author_subject"]
        ):
            raise E2eeError("invalid_conversation_event")
        number(value.sequence, 1)
        text(value.client_operation_id)
        text(value.message_head_id)
        return event_record

    def _message_contexts(self, ids, originals=None):
        originals = {
            **(originals or {}),
            **self._read(
                identifier for identifier in ids if identifier not in (originals or {})
            ),
        }
        wanted = set()
        origins: dict[str, ReadRecord[domain.ChatOrigin]] = {}
        for identifier in ids:
            original = self._chat_event(originals.get(identifier))
            value = original["value"]
            if original["record_id"] != identifier or not isinstance(
                value, domain.ChatOrigin
            ):
                raise E2eeError("invalid_conversation_origin")
            origins[identifier] = cast("ReadRecord[domain.ChatOrigin]", original)
            wanted.update((value.message_head_id, value.terminal_record_id))
        heads = self._read(wanted)
        message_heads: dict[str, ReadRecord[domain.ChatMessageHead]] = {}
        latest_ids = set()
        for identifier in ids:
            head = self._header(
                heads.get(origins[identifier]["value"].message_head_id),
                "chat",
                domain.ChatMessageHead,
            )
            message_heads[identifier] = head
            ref = reference(head["value"].last_event)
            if ref is None or ref.revision != 1:
                raise E2eeError("invalid_conversation_event")
            latest_ids.add(ref.id)
        events = {**originals, **self._read(latest_ids - originals.keys())}
        return {
            identifier: {
                "original": origins[identifier],
                "head": message_heads[identifier],
                "latest": events[message_heads[identifier]["value"].last_event.id],
                "terminal": heads.get(origins[identifier]["value"].terminal_record_id),
            }
            for identifier in ids
        }

    def _latest_message(self, context):
        original, head = context["original"], context["head"]
        latest = self._chat_event(context["latest"])
        origin, value, event = original["value"], head["value"], latest["value"]
        revision = number(value.message_revision, 1)
        if (
            head["author_subject"] != original["author_subject"]
            or head["revision"] != revision
            or head["record_id"] != origin.message_head_id
            or reference(value.original)
            != domain.RecordReference(id=original["record_id"], revision=1)
            or reference(value.last_event)
            != domain.RecordReference(id=latest["record_id"], revision=1)
            or event_revision(event) != revision
            or event_message_id(latest) != original["record_id"]
            or event.message_head_id != head["record_id"]
            or latest["author_subject"] != original["author_subject"]
            or event.sequence < origin.sequence
            or (
                latest["record_id"] != original["record_id"]
                or not isinstance(event, domain.ChatOrigin)
                if revision == 1
                else isinstance(event, domain.ChatOrigin)
            )
        ):
            raise E2eeError("invalid_conversation_origin")
        terminal = context["terminal"]
        if terminal is None:
            if event_type(event) == domain.CHAT_EVENT_TYPE_DELETED:
                raise E2eeError("invalid_conversation_terminal")
        else:
            self._record(terminal, "chat", domain.ChatTerminal, immutable=True)
            marker = terminal["value"]
            if (
                terminal["record_id"] != origin.terminal_record_id
                or terminal["author_subject"] != original["author_subject"]
                or reference(marker.original)
                != domain.RecordReference(id=original["record_id"], revision=1)
                or marker.message_head_id != head["record_id"]
                or reference(marker.delete_event)
                != domain.RecordReference(id=latest["record_id"], revision=1)
                or marker.message_revision != revision
                or event_type(event) != domain.CHAT_EVENT_TYPE_DELETED
            ):
                raise E2eeError("invalid_conversation_terminal")
        return event

    def _verify_endpoint(self, context, endpoint):
        latest = self._latest_message(context)
        endpoint = self._chat_event(endpoint)
        event, original = endpoint["value"], context["original"]
        revision = event_revision(event)
        if (
            endpoint["author_subject"] != original["author_subject"]
            or event_message_id(endpoint) != original["record_id"]
            or event.message_head_id != context["head"]["record_id"]
            or revision > event_revision(latest)
            or not original["value"].sequence <= event.sequence <= latest.sequence
            or (
                revision == event_revision(latest)
                and (
                    endpoint["record_id"] != context["latest"]["record_id"]
                    or event != latest
                )
            )
            or (
                endpoint["record_id"] != original["record_id"]
                or not isinstance(event, domain.ChatOrigin)
                if revision == 1
                else isinstance(event, domain.ChatOrigin)
            )
            or (
                event_type(event) == domain.CHAT_EVENT_TYPE_DELETED
                and (
                    context["terminal"] is None
                    or reference(context["terminal"]["value"].delete_event)
                    != domain.RecordReference(id=endpoint["record_id"], revision=1)
                )
            )
        ):
            raise E2eeError("invalid_conversation_endpoint")
        return event

    def _check_chat_header(self, header):
        self._same_records([header])

    @conflict_retry
    def chat_messages(self, *, before_sequence=None, limit=100):
        if type(limit) is not int or limit < 1:
            raise E2eeError("invalid_cursor")
        if before_sequence is not None:
            number(before_sequence, 1)
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        latest = number(header["value"].sequence)
        entries, following = self._index("chat").page(
            reference(header["value"].messages),
            after=(descending(before_sequence), "\uffff")
            if before_sequence is not None
            else None,
            limit=limit,
        )
        ids, previous = set(), None
        for entry in entries:
            sequence = number(entry.sequence, 1)
            if (
                sequence > latest
                or entry.key.name != descending(sequence)
                or (previous is not None and sequence >= previous)
                or (before_sequence is not None and sequence >= before_sequence)
            ):
                raise E2eeError("invalid_conversation_index")
            previous = sequence
            ids.add(text(entry.key.id))
        if len(ids) != len(entries):
            raise E2eeError("invalid_conversation_index")
        contexts = self._message_contexts(ids)
        messages = []
        for entry in entries:
            context = contexts[entry.key.id]
            origin = context["original"]["value"]
            event = self._latest_message(context)
            if (
                origin.sequence != entry.sequence
                or context["head"]["record_id"] != entry.head_id
                or event.sequence > latest
            ):
                raise E2eeError("invalid_conversation_index")
            messages.append(
                domain.ChatMessageView(
                    latest=self._event_view(
                        context["latest"]["record_id"], origin, event
                    ),
                    verified_through_sequence=latest,
                )
            )
        self._check_chat_header(header)
        return {
            "messages": messages,
            "next_before_sequence": entries[-1].sequence if following else None,
            "latest_sequence": latest,
        }

    @conflict_retry
    def chat_message(self, message_id):
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        originals = self._read([message_id])
        if message_id not in originals:
            self._check_chat_header(header)
            return None
        context = self._message_contexts({message_id}, originals)[message_id]
        event = self._latest_message(context)
        if event.sequence > number(header["value"].sequence):
            raise E2eeError("invalid_conversation_event")
        self._check_chat_header(header)
        return domain.ChatMessageView(
            latest=self._event_view(
                context["latest"]["record_id"], context["original"]["value"], event
            ),
            verified_through_sequence=header["value"].sequence,
        )

    @conflict_retry
    def chat_events(self, *, after=0, limit=200):
        number(after)
        if type(limit) is not int or limit < 1:
            raise E2eeError("invalid_cursor")
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        latest = number(header["value"].sequence)
        if after > latest:
            raise E2eeError("invalid_cursor")
        entries, following = self._index("chat").page(
            reference(header["value"].events),
            after=(ascending(after), "\uffff"),
            limit=limit,
        )
        records = self._read(text(entry.key.id) for entry in entries)
        events, sequence = [], after
        for entry in entries:
            sequence += 1
            event = self._chat_event(records.get(entry.key.id))
            if (
                entry.sequence != sequence
                or entry.key.name != ascending(sequence)
                or sequence > latest
                or event["value"].sequence != sequence
            ):
                raise E2eeError("invalid_conversation_index")
            events.append(event)
        if (following is None and sequence != latest) or (
            following is not None and sequence == latest
        ):
            raise E2eeError("invalid_conversation_index")
        contexts = self._message_contexts({event_message_id(event) for event in events})
        previous_revisions = {}
        for event in events:
            identifier, revision = (
                event_message_id(event),
                event_revision(event["value"]),
            )
            if (
                identifier in previous_revisions
                and revision != previous_revisions[identifier] + 1
            ):
                raise E2eeError("invalid_conversation_history")
            previous_revisions[identifier] = revision
        values = [
            self._event_view(
                event["record_id"],
                contexts[event_message_id(event)]["original"]["value"],
                self._verify_endpoint(contexts[event_message_id(event)], event),
            )
            for event in events
        ]
        self._check_chat_header(header)
        return {
            "events": values,
            "latest_sequence": latest,
            "has_more": following is not None,
        }

    @conflict_retry
    def chat_operation(self, operation_id):
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        binding = self._read(["cop_" + text(operation_id)]).get("cop_" + operation_id)
        if binding is None:
            self._check_chat_header(header)
            return None
        binding = self._record(binding, "chat", domain.ChatOperation, immutable=True)
        value = binding["value"]
        event = self._chat_event(self._read([text(value.event_id)]).get(value.event_id))
        message = event_message_id(event)
        if (
            value.message_id != message
            or value.type != event_type(event["value"])
            or binding["author_subject"] != event["author_subject"]
            or event["author_subject"] != self.subject
            or event["value"].client_operation_id != operation_id
        ):
            raise E2eeError("invalid_conversation_operation")
        context = self._message_contexts({message})[message]
        result = self._verify_endpoint(context, event)
        self._check_chat_header(header)
        return self._event_view(
            event["record_id"], context["original"]["value"], result
        )

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
    ) -> domain.ChatEventView | AcceptedCommand:
        references = [] if references is None else references
        if (
            type not in {"sent", "edited", "deleted"}
            or not isinstance(message_id, str)
            or re.fullmatch(r"cmsg_[0-9a-f]{32}", message_id) is None
            or not isinstance(operation_id, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{1,123}", operation_id) is None
            or ((type == "deleted") != (body is None))
            or (type != "sent" and references)
            or (type == "sent" and body == "" and not references)
        ):
            raise E2eeError("invalid_request")
        kind = {
            "sent": domain.CHAT_EVENT_TYPE_SENT,
            "edited": domain.CHAT_EVENT_TYPE_EDITED,
            "deleted": domain.CHAT_EVENT_TYPE_DELETED,
        }[type]
        event_id = message_id if type == "sent" else "cevt_" + operation_id
        binding_id = "cop_" + operation_id
        prior = self._read([event_id, binding_id])
        if binding_id in prior:
            binding = self._record(
                prior[binding_id], "chat", domain.ChatOperation, immutable=True
            )
            value = binding["value"]
            if (
                binding["author_subject"] != self.subject
                or value.event_id != event_id
                or value.message_id != message_id
                or value.type != kind
                or event_id not in prior
            ):
                raise E2eeError("idempotency_conflict")
        elif event_id in prior:
            raise E2eeError("invalid_conversation_operation")
        if event_id in prior:
            existing = self._chat_event(prior[event_id])
            value = existing["value"]
            stored_body = (
                value.body
                if isinstance(value, domain.ChatOrigin)
                else (
                    value.edited.body
                    if value.WhichOneof("change") == "edited"
                    else None
                )
            )
            if (
                value.actor_membership_id != self.subject
                or event_type(value) != kind
                or event_message_id(existing) != message_id
                or value.client_operation_id != operation_id
                or stored_body != body
                or (
                    type != "sent"
                    and (
                        expected_revision is None
                        or event_revision(value) != expected_revision + 1
                    )
                )
                or (
                    isinstance(value, domain.ChatOrigin)
                    and value.references != references
                )
            ):
                raise E2eeError("idempotency_conflict")
            context = self._message_contexts({message_id})[message_id]
            verified = self._verify_endpoint(context, existing)
            return self._event_view(
                existing["record_id"], context["original"]["value"], verified
            )
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        sequence = number(header["value"].sequence) + 1
        number(sequence, 1)
        context, previous = None, None
        if type == "sent":
            head_id, terminal_id = self.mint_id(), self.mint_id()
        else:
            originals = self._read([message_id])
            if message_id not in originals:
                raise E2eeError("message_not_found")
            context = self._message_contexts({message_id}, originals)[message_id]
            previous = self._latest_message(context)
            if (
                type == "edited"
                and body == ""
                and not context["original"]["value"].references
            ):
                raise E2eeError("invalid_request")
            if previous.sequence >= sequence:
                raise E2eeError("invalid_conversation_event")
            if previous.author_membership_id != self.subject:
                raise E2eeError("not_message_author")
            if event_type(previous) == domain.CHAT_EVENT_TYPE_DELETED:
                raise E2eeError("message_state_changed")
            if event_revision(previous) != expected_revision:
                raise E2eeError("revision_conflict")
            head_id = context["head"]["record_id"]
            terminal_id = context["original"]["value"].terminal_record_id
        revision = number(event_revision(previous) if previous else 0) + 1
        original_ref = domain.RecordReference(id=message_id, revision=1)
        if type == "sent":
            event = domain.ChatOrigin(
                message_head_id=head_id,
                terminal_record_id=terminal_id,
                author_membership_id=self.subject,
                actor_membership_id=self.subject,
                client_operation_id=operation_id,
                sequence=sequence,
                references=references,
                body=body,
                committed_at=committed_at,
            )
        else:
            event = domain.ChatEvent(
                original=original_ref,
                message_head_id=head_id,
                author_membership_id=self.subject,
                actor_membership_id=self.subject,
                client_operation_id=operation_id,
                sequence=sequence,
                message_revision=revision,
                committed_at=committed_at,
            )
            if body is not None:
                event.edited.body = body
            else:
                event.deleted.SetInParent()
        own_root, own_writes = self._index("chat").mutation(
            reference(context["head"]["value"].events) if context else None,
            domain.OrderedIndexEntry(
                key=domain.OrderedEntryKey(name=ascending(revision), id=event_id),
                message_revision=revision,
                sequence=sequence,
            ),
        )
        events_root, events_writes = self._index("chat").mutation(
            reference(header["value"].events),
            domain.OrderedIndexEntry(
                key=domain.OrderedEntryKey(name=ascending(sequence), id=event_id),
                sequence=sequence,
            ),
        )
        messages_root, messages_writes = (
            self._index("chat").mutation(
                reference(header["value"].messages),
                domain.OrderedIndexEntry(
                    key=domain.OrderedEntryKey(
                        name=descending(sequence), id=message_id
                    ),
                    head_id=head_id,
                    sequence=sequence,
                ),
            )
            if type == "sent"
            else (reference(header["value"].messages), [])
        )
        updated_header = domain.ChatHeader(sequence=sequence, events=events_root)
        if messages_root is not None:
            updated_header.messages.CopyFrom(messages_root)
        writes = [
            write(event_id, "chat", event, immutable=True),
            write(
                binding_id,
                "chat",
                domain.ChatOperation(
                    event_id=event_id, message_id=message_id, type=kind
                ),
                immutable=True,
            ),
            write(
                head_id,
                "chat",
                domain.ChatMessageHead(
                    original=original_ref,
                    message_revision=revision,
                    last_event=domain.RecordReference(id=event_id, revision=1),
                    events=own_root,
                ),
                revision=context["head"]["revision"] if context else 0,
            ),
            *own_writes,
            *events_writes,
            *messages_writes,
            write(
                chat_header_id(self.scope),
                "chat",
                updated_header,
                revision=header["revision"],
            ),
        ]
        if type == "deleted":
            writes.append(
                write(
                    terminal_id,
                    "chat",
                    domain.ChatTerminal(
                        original=original_ref,
                        message_head_id=head_id,
                        delete_event=domain.RecordReference(id=event_id, revision=1),
                        message_revision=revision,
                    ),
                    immutable=True,
                )
            )
        outcome = self._write(
            writes,
            [app.RecordPrecondition(id=message_id, expected_revision=1)]
            if context
            else [],
        )
        if isinstance(outcome, AcceptedCommand):
            return outcome
        return self._event_view(
            event_id, context["original"]["value"] if context else event, event
        )

    @conflict_retry
    def chat_message_history(self, message_id):
        """Explicitly verify every revision without retaining the full history."""
        header = self._load_header(
            chat_header_id(self.scope), "chat", domain.ChatHeader
        )
        context = self._message_contexts({message_id})[message_id]
        self._latest_message(context)
        total = context["head"]["value"].message_revision
        after, revision, sequence, previous = None, 0, 0, None
        while revision < total:
            entries, following = self._index("chat").page(
                reference(context["head"]["value"].events),
                after=after,
                limit=200,
            )
            if not entries:
                raise E2eeError("invalid_conversation_history")
            records = self._read(entry.key.id for entry in entries)
            for entry in entries:
                record = self._chat_event(records.get(entry.key.id))
                value = self._verify_endpoint(context, record)
                revision += 1
                if (
                    entry.key.name != ascending(revision)
                    or entry.message_revision != revision
                    or entry.sequence != value.sequence
                    or event_revision(value) != revision
                    or value.sequence <= sequence
                    or (
                        previous
                        and event_type(previous) == domain.CHAT_EVENT_TYPE_DELETED
                    )
                ):
                    raise E2eeError("invalid_conversation_history")
                sequence, previous = value.sequence, value
            if (
                (revision == total and following is not None)
                or revision > total
                or (revision < total and following is None)
            ):
                raise E2eeError("invalid_conversation_history")
            after = following
            self.checkpoint()
        self._check_chat_header(header)
        return domain.ChatMessageView(
            latest=self._event_view(
                context["latest"]["record_id"], context["original"]["value"], previous
            ),
            verified_through_sequence=header["value"].sequence,
        )
