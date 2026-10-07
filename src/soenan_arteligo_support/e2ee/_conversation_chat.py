from __future__ import annotations

import re

from ._conversation_context import (
    CHAT_HEADER,
    FORMAT,
    ascending,
    conflict_retry,
    descending,
    number,
    reference,
    text,
    write,
)
from ._crypto import E2eeError


def valid_chat_body(body):
    return (
        isinstance(body, str)
        and len(body) <= 8000
        and all(
            character in "\t\n\r" or (ord(character) >= 32 and ord(character) != 127)
            for character in body
        )
    )


def valid_chat_references(references):
    if not isinstance(references, list) or len(references) > 10:
        return False
    keys = {
        "file": "fileId",
        "stage": "stageId",
        "comment": "commentId",
        "comment_reply": "replyId",
    }
    identities = set()
    for item in references:
        if not isinstance(item, dict):
            return False
        kind = item.get("kind")
        key = keys.get(kind) if isinstance(kind, str) else None
        identifier = item.get(key) if key else None
        if (
            not isinstance(identifier, str)
            or not identifier
            or (kind, identifier) in identities
        ):
            return False
        identities.add((kind, identifier))
    return True


class ChatOperations:
    def _chat_event(self, record):
        record = self._record(record, "chat", "event", immutable=True)
        value = record["value"]
        kind = value.get("type")
        message = text(value.get("messageId"))
        operation = text(value.get("clientOperationId"))
        if (
            value.get("format") != FORMAT
            or value.get("projectId") != self.scope
            or kind not in {"sent", "edited", "deleted"}
            or record["record_id"]
            != (message if kind == "sent" else "cevt_" + operation)
            or value.get("actorMembershipId") != record["author_subject"]
            or value.get("authorMembershipId") != record["author_subject"]
            or not valid_chat_references(value.get("references"))
            or (
                value.get("body") is not None
                if kind == "deleted"
                else not valid_chat_body(value.get("body"))
            )
        ):
            raise E2eeError("invalid_conversation_event")
        number(value.get("sequence"), 1)
        number(value.get("revision"), 1)
        text(value.get("messageHeadId"))
        return record

    def _message_contexts(self, ids, originals=None):
        originals = {
            **(originals or {}),
            **self._read(
                identifier for identifier in ids if identifier not in (originals or {})
            ),
        }
        wanted = set()
        for identifier in ids:
            original = self._chat_event(originals.get(identifier))
            value = original["value"]
            if (
                original["record_id"] != identifier
                or value["type"] != "sent"
                or value["revision"] != 1
            ):
                raise E2eeError("invalid_conversation_origin")
            wanted.update(
                (text(value.get("messageHeadId")), text(value.get("terminalRecordId")))
            )
        heads = self._read(wanted)
        latest_ids = set()
        for identifier in ids:
            head = self._header(
                heads.get(originals[identifier]["value"]["messageHeadId"]),
                "chat",
                "message_head",
            )
            ref = reference(head["value"].get("lastEvent"))
            if ref is None or ref["revision"] != 1:
                raise E2eeError("invalid_conversation_event")
            latest_ids.add(ref["id"])
        events = {**originals, **self._read(latest_ids - originals.keys())}
        return {
            identifier: {
                "original": originals[identifier],
                "head": heads[originals[identifier]["value"]["messageHeadId"]],
                "latest": events[
                    heads[originals[identifier]["value"]["messageHeadId"]]["value"][
                        "lastEvent"
                    ]["id"]
                ],
                "terminal": heads.get(
                    originals[identifier]["value"]["terminalRecordId"]
                ),
            }
            for identifier in ids
        }

    def _latest_message(self, context):
        original, head = context["original"], context["head"]
        latest = self._chat_event(context["latest"])
        origin, value, event = original["value"], head["value"], latest["value"]
        revision = number(value.get("messageRevision"), 1)
        if (
            head["author_subject"] != original["author_subject"]
            or head["revision"] != revision
            or value.get("messageId") != original["record_id"]
            or head["record_id"] != origin["messageHeadId"]
            or reference(value.get("original"))
            != {"id": original["record_id"], "revision": 1}
            or reference(value.get("lastEvent"))
            != {"id": latest["record_id"], "revision": 1}
            or event["revision"] != revision
            or event["messageId"] != original["record_id"]
            or event["messageHeadId"] != head["record_id"]
            or latest["author_subject"] != original["author_subject"]
            or event["sequence"] < origin["sequence"]
            or (
                latest["record_id"] != original["record_id"] or event["type"] != "sent"
                if revision == 1
                else event["type"] == "sent" or event["references"]
            )
        ):
            raise E2eeError("invalid_conversation_origin")
        terminal = context["terminal"]
        if terminal is None:
            if event["type"] == "deleted":
                raise E2eeError("invalid_conversation_terminal")
        else:
            self._record(terminal, "chat", "terminal", immutable=True)
            marker = terminal["value"]
            if (
                terminal["record_id"] != origin["terminalRecordId"]
                or terminal["author_subject"] != original["author_subject"]
                or marker.get("format") != FORMAT
                or marker.get("messageId") != original["record_id"]
                or marker.get("messageHeadId") != head["record_id"]
                or reference(marker.get("deleteEvent"))
                != {"id": latest["record_id"], "revision": 1}
                or marker.get("messageRevision") != revision
                or event["type"] != "deleted"
            ):
                raise E2eeError("invalid_conversation_terminal")
        return event

    def _verify_endpoint(self, context, endpoint):
        latest = self._latest_message(context)
        endpoint = self._chat_event(endpoint)
        event, original = endpoint["value"], context["original"]
        revision = event["revision"]
        if (
            endpoint["author_subject"] != original["author_subject"]
            or event["messageId"] != original["record_id"]
            or event["messageHeadId"] != context["head"]["record_id"]
            or revision > latest["revision"]
            or not original["value"]["sequence"]
            <= event["sequence"]
            <= latest["sequence"]
            or (
                revision == latest["revision"]
                and (
                    endpoint["record_id"] != context["latest"]["record_id"]
                    or event != latest
                )
            )
            or (
                endpoint["record_id"] != original["record_id"]
                or event["type"] != "sent"
                if revision == 1
                else event["type"] == "sent" or event["references"]
            )
            or (
                event["type"] == "deleted"
                and (
                    context["terminal"] is None
                    or reference(context["terminal"]["value"].get("deleteEvent"))
                    != {"id": endpoint["record_id"], "revision": 1}
                )
            )
        ):
            raise E2eeError("invalid_conversation_endpoint")
        return event

    def _check_chat_header(self, header):
        self._same_records([header])

    @conflict_retry
    def chat_messages(self, *, before_sequence=None, limit=100):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise E2eeError("invalid_cursor")
        if before_sequence is not None:
            number(before_sequence, 1)
        header = self._load_header(CHAT_HEADER, "chat", "chat_header")
        latest = number(header["value"].get("sequence"))
        entries, following = self._index("chat").page(
            reference(header["value"].get("messages")),
            after=(descending(before_sequence), "\uffff")
            if before_sequence is not None
            else None,
            limit=limit,
        )
        ids, previous = set(), None
        for entry in entries:
            sequence = number(entry.get("sequence"), 1)
            if (
                sequence > latest
                or entry.get("name") != descending(sequence)
                or (previous is not None and sequence >= previous)
                or (before_sequence is not None and sequence >= before_sequence)
            ):
                raise E2eeError("invalid_conversation_index")
            previous = sequence
            ids.add(text(entry.get("id")))
        if len(ids) != len(entries):
            raise E2eeError("invalid_conversation_index")
        contexts = self._message_contexts(ids)
        messages = []
        for entry in entries:
            context = contexts[entry["id"]]
            origin = context["original"]["value"]
            event = self._latest_message(context)
            if (
                origin["sequence"] != entry["sequence"]
                or context["head"]["record_id"] != entry.get("headID")
                or event["sequence"] > latest
            ):
                raise E2eeError("invalid_conversation_index")
            messages.append(
                {
                    **event,
                    "references": origin["references"],
                    "sentSequence": origin["sequence"],
                    "sentAt": origin["committedAt"],
                }
            )
        self._page_size(messages)
        self._check_chat_header(header)
        return {
            "messages": messages,
            "next_before_sequence": entries[-1]["sequence"] if following else None,
            "latest_sequence": latest,
        }

    @conflict_retry
    def chat_message(self, message_id):
        header = self._load_header(CHAT_HEADER, "chat", "chat_header")
        originals = self._read([message_id])
        if message_id not in originals:
            self._check_chat_header(header)
            return None
        context = self._message_contexts({message_id}, originals)[message_id]
        event = self._latest_message(context)
        if event["sequence"] > number(header["value"].get("sequence")):
            raise E2eeError("invalid_conversation_event")
        self._check_chat_header(header)
        origin = context["original"]["value"]
        return {
            **event,
            "references": origin["references"],
            "sentSequence": origin["sequence"],
            "sentAt": origin["committedAt"],
            "verifiedThroughSequence": header["value"]["sequence"],
        }

    @conflict_retry
    def chat_events(self, *, after=0, limit=200):
        number(after)
        if type(limit) is not int or not 1 <= limit <= 200:
            raise E2eeError("invalid_cursor")
        header = self._load_header(CHAT_HEADER, "chat", "chat_header")
        latest = number(header["value"].get("sequence"))
        if after > latest:
            raise E2eeError("invalid_cursor")
        entries, following = self._index("chat").page(
            reference(header["value"].get("events")),
            after=(ascending(after), "\uffff"),
            limit=limit,
        )
        records = self._read(text(entry.get("id")) for entry in entries)
        events, sequence = [], after
        for entry in entries:
            sequence += 1
            event = self._chat_event(records.get(entry["id"]))
            if (
                entry.get("sequence") != sequence
                or entry.get("name") != ascending(sequence)
                or sequence > latest
                or event["value"]["sequence"] != sequence
            ):
                raise E2eeError("invalid_conversation_index")
            events.append(event)
        if (following is None and sequence != latest) or (
            following is not None and sequence == latest
        ):
            raise E2eeError("invalid_conversation_index")
        contexts = self._message_contexts(
            {event["value"]["messageId"] for event in events}
        )
        previous_revisions = {}
        for event in events:
            identifier = event["value"]["messageId"]
            revision = event["value"]["revision"]
            if (
                identifier in previous_revisions
                and revision != previous_revisions[identifier] + 1
            ):
                raise E2eeError("invalid_conversation_history")
            previous_revisions[identifier] = revision
        values = [
            self._verify_endpoint(contexts[event["value"]["messageId"]], event)
            for event in events
        ]
        self._page_size(values)
        self._check_chat_header(header)
        return {
            "events": values,
            "latest_sequence": latest,
            "has_more": following is not None,
        }

    @conflict_retry
    def chat_operation(self, operation_id):
        header = self._load_header(CHAT_HEADER, "chat", "chat_header")
        binding = self._read(["cop_" + text(operation_id)]).get("cop_" + operation_id)
        if binding is None:
            self._check_chat_header(header)
            return None
        self._record(binding, "chat", "operation", immutable=True)
        value = binding["value"]
        event = self._chat_event(
            self._read([text(value.get("eventID"))]).get(value["eventID"])
        )
        message = event["value"]["messageId"]
        if (
            value.get("format") != FORMAT
            or value.get("messageId") != message
            or value.get("type") != event["value"]["type"]
            or binding["author_subject"] != event["author_subject"]
            or event["author_subject"] != self.subject
            or event["value"]["clientOperationId"] != operation_id
        ):
            raise E2eeError("invalid_conversation_operation")
        result = self._verify_endpoint(
            self._message_contexts({message})[message], event
        )
        self._check_chat_header(header)
        return result

    @conflict_retry
    def write_chat(
        self,
        *,
        type,
        message_id,
        operation_id,
        committed_at,
        body=None,
        references=None,
        expected_revision=None,
    ):
        references = [] if references is None else references
        text(message_id)
        text(operation_id)
        if (
            type not in {"sent", "edited", "deleted"}
            or re.fullmatch(r"cmsg_[0-9a-f]{32}", message_id) is None
            or not 16 <= len(operation_id) <= 128
            or any(not 33 <= ord(character) <= 126 for character in operation_id)
            or ((type == "deleted") != (body is None))
            or (type != "deleted" and not valid_chat_body(body))
            or not valid_chat_references(references)
            or (type != "sent" and references)
            or (type == "sent" and body == "" and not references)
        ):
            raise E2eeError("invalid_request")
        event_id = message_id if type == "sent" else "cevt_" + operation_id
        binding_id = "cop_" + operation_id
        prior = self._read([event_id, binding_id])
        if binding_id in prior:
            binding = self._record(
                prior[binding_id], "chat", "operation", immutable=True
            )
            value = binding["value"]
            if (
                value.get("format") != FORMAT
                or binding["author_subject"] != self.subject
                or value.get("eventID") != event_id
                or value.get("messageId") != message_id
                or value.get("type") != type
                or event_id not in prior
            ):
                raise E2eeError("idempotency_conflict")
        elif event_id in prior:
            raise E2eeError("invalid_conversation_operation")
        if event_id in prior:
            existing = self._chat_event(prior[event_id])
            value = existing["value"]
            if (
                value["actorMembershipId"] != self.subject
                or value["type"] != type
                or value["messageId"] != message_id
                or value["clientOperationId"] != operation_id
                or value["body"] != body
                or (
                    type != "sent"
                    and (
                        expected_revision is None
                        or value["revision"] != expected_revision + 1
                    )
                )
                or (type == "sent" and value["references"] != references)
            ):
                raise E2eeError("idempotency_conflict")
            return self._verify_endpoint(
                self._message_contexts({message_id})[message_id], existing
            )
        header = self._load_header(CHAT_HEADER, "chat", "chat_header")
        sequence = number(header["value"].get("sequence")) + 1
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
                and not context["original"]["value"]["references"]
            ):
                raise E2eeError("invalid_request")
            if previous["sequence"] >= sequence:
                raise E2eeError("invalid_conversation_event")
            if previous["authorMembershipId"] != self.subject:
                raise E2eeError("not_message_author")
            if previous["type"] == "deleted":
                raise E2eeError("message_state_changed")
            if previous["revision"] != expected_revision:
                raise E2eeError("revision_conflict")
            head_id = context["head"]["record_id"]
            terminal_id = context["original"]["value"]["terminalRecordId"]
        revision = number(previous["revision"] if previous else 0) + 1
        event = {
            "format": FORMAT,
            "recordType": "event",
            "type": type,
            "projectId": self.scope,
            "sequence": sequence,
            "messageId": message_id,
            "messageHeadId": head_id,
            **({"terminalRecordId": terminal_id} if type == "sent" else {}),
            "authorMembershipId": self.subject,
            "actorMembershipId": self.subject,
            "clientOperationId": operation_id,
            "revision": revision,
            "references": references if type == "sent" else [],
            "body": body,
            "committedAt": committed_at,
        }
        own_root, own_writes = self._index("chat").mutation(
            reference(context["head"]["value"].get("events")) if context else None,
            {
                "name": ascending(revision),
                "id": event_id,
                "revision": revision,
                "sequence": sequence,
            },
        )
        events_root, events_writes = self._index("chat").mutation(
            reference(header["value"].get("events")),
            {"name": ascending(sequence), "id": event_id, "sequence": sequence},
        )
        messages_root, messages_writes = (
            self._index("chat").mutation(
                reference(header["value"].get("messages")),
                {
                    "name": descending(sequence),
                    "id": message_id,
                    "headID": head_id,
                    "sequence": sequence,
                },
            )
            if type == "sent"
            else (reference(header["value"].get("messages")), [])
        )
        writes = [
            write(event_id, "chat", event, immutable=True),
            write(
                binding_id,
                "chat",
                {
                    "format": FORMAT,
                    "recordType": "operation",
                    "eventID": event_id,
                    "messageId": message_id,
                    "type": type,
                },
                immutable=True,
            ),
            write(
                head_id,
                "chat",
                {
                    "format": FORMAT,
                    "recordType": "message_head",
                    "messageId": message_id,
                    "original": {"id": message_id, "revision": 1},
                    "messageRevision": revision,
                    "lastEvent": {"id": event_id, "revision": 1},
                    "events": own_root,
                },
                revision=context["head"]["revision"] if context else 0,
            ),
            *own_writes,
            *events_writes,
            *messages_writes,
            write(
                CHAT_HEADER,
                "chat",
                {
                    **header["value"],
                    "sequence": sequence,
                    "events": events_root,
                    "messages": messages_root,
                },
                revision=header["revision"],
            ),
        ]
        if type == "deleted":
            writes.append(
                write(
                    terminal_id,
                    "chat",
                    {
                        "format": FORMAT,
                        "recordType": "terminal",
                        "messageId": message_id,
                        "messageHeadId": head_id,
                        "deleteEvent": {"id": event_id, "revision": 1},
                        "messageRevision": revision,
                    },
                    immutable=True,
                )
            )
        self._write(
            writes,
            [{"record_id": message_id, "expected_revision": 1}] if context else [],
        )
        return event

    @conflict_retry
    def chat_message_history(self, message_id):
        """Explicitly verify every revision without retaining the full history."""
        header = self._load_header(CHAT_HEADER, "chat", "chat_header")
        context = self._message_contexts({message_id})[message_id]
        self._latest_message(context)
        total = context["head"]["value"]["messageRevision"]
        after, revision, sequence, previous = None, 0, 0, None
        while revision < total:
            entries, following = self._index("chat").page(
                reference(context["head"]["value"].get("events")),
                after=after,
                limit=200,
            )
            if not entries:
                raise E2eeError("invalid_conversation_history")
            records = self._read(entry["id"] for entry in entries)
            for entry in entries:
                record = self._chat_event(records.get(entry["id"]))
                value = self._verify_endpoint(context, record)
                revision += 1
                if (
                    entry.get("name") != ascending(revision)
                    or entry.get("revision") != revision
                    or entry.get("sequence") != value["sequence"]
                    or value["revision"] != revision
                    or value["sequence"] <= sequence
                    or (previous and previous["type"] == "deleted")
                ):
                    raise E2eeError("invalid_conversation_history")
                sequence, previous = value["sequence"], value
            if (
                (revision == total and following is not None)
                or revision > total
                or (revision < total and following is None)
            ):
                raise E2eeError("invalid_conversation_history")
            after = following
            self.checkpoint()
        self._check_chat_header(header)
        return previous
