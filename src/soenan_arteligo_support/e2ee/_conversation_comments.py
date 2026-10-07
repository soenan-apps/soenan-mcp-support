from __future__ import annotations

from ._conversation_context import (
    COMMENT_HEADER,
    FORMAT,
    anchor_key,
    ascending,
    conflict_retry,
    descending,
    number,
    reference,
    text,
    verify_actor,
    write,
)
from ._crypto import E2eeError


class CommentOperations:
    def _comment_record(self, record, record_type):
        result = self._record(record, "comment", record_type, immutable=True)
        if (
            result["value"].get("format") != FORMAT
            or result["value"].get("id") != result["record_id"]
        ):
            raise E2eeError("invalid_conversation_comment")
        verify_actor(result, "author")
        return result

    def _resolution_record(self, record, parent_id):
        result = self._record(record, "comment", "resolution", immutable=True)
        value = result["value"]
        if (
            value.get("format") != FORMAT
            or value.get("parentCommentId") != parent_id
            or type(value.get("resolved")) is not bool
            or result["record_id"] != "cres_" + text(value.get("operationID"))
        ):
            raise E2eeError("invalid_conversation_resolution")
        verify_actor(result, "actor")
        return result

    def _thread_contexts(self, ids, originals=None):
        originals = {
            **(originals or {}),
            **self._read(set(ids) - (originals or {}).keys()),
        }
        wanted = set()
        for identifier in ids:
            original = self._comment_record(originals.get(identifier), "comment")
            wanted.update(
                (
                    text(original["value"].get("threadHeadId")),
                    text(original["value"].get("bodyHeadId")),
                )
            )
        heads = self._read(wanted)
        refs = set()
        for identifier in ids:
            original = originals[identifier]
            head = self._header(
                heads.get(original["value"]["threadHeadId"]), "comment", "thread_head"
            )
            if head["value"].get("commentId") != identifier or reference(
                head["value"].get("original")
            ) != {"id": identifier, "revision": 1}:
                raise E2eeError("invalid_conversation_comment")
            number(head["value"].get("replyCount"))
            reference(head["value"].get("replies"))
            body = self._header(
                heads.get(original["value"]["bodyHeadId"]), "comment", "text_head"
            )
            for ref in (
                reference(head["value"].get("resolution")),
                reference(body["value"].get("lastEdit")),
            ):
                if ref:
                    if ref["revision"] != 1:
                        raise E2eeError("invalid_conversation_comment")
                    refs.add(ref["id"])
        events = self._read(refs)
        texts = self._text_contexts(
            {identifier: originals[identifier] for identifier in ids},
            {**heads, **events},
        )
        result = {}
        for identifier in ids:
            original = originals[identifier]
            head = heads[original["value"]["threadHeadId"]]
            ref = reference(head["value"].get("resolution"))
            result[identifier] = {
                "comment": original,
                "head": head,
                "text": texts[identifier],
                "resolution": self._resolution_record(events.get(ref["id"]), identifier)
                if ref
                else None,
            }
        return result

    def _thread_view(self, context):
        count = number(context["head"]["value"]["replyCount"])
        return {
            **self._text_view(context["text"]),
            "resolved": context["resolution"]["value"]["resolved"]
            if context["resolution"]
            else False,
            "replies": [],
            "replyCount": count,
            "hasMoreReplies": count > 0,
        }

    def _check_thread_heads(self, contexts):
        self._same_records(
            [
                record
                for context in contexts
                for record in (context["head"], context["text"]["head"])
            ]
        )

    @conflict_retry
    def comment_thread(self, identifier):
        originals = self._read([identifier])
        if identifier not in originals:
            return None
        context = self._thread_contexts({identifier}, originals)[identifier]
        result = self._thread_view(context)
        self._check_thread_heads([context])
        return result

    @conflict_retry
    def comment_threads(self, *, anchor=None, after=None, limit=100):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise E2eeError("invalid_cursor")
        header = self._load_header(COMMENT_HEADER, "comment", "comment_header")
        key = anchor_key(anchor) if anchor is not None else None
        if key is not None and after and not after[0].startswith(key + "\0"):
            raise E2eeError("invalid_cursor")
        entries, following = self._index("comment").page(
            reference(header["value"].get("threads")),
            after=after or ((key + "\0", "") if key is not None else None),
            limit=limit,
        )
        selected = []
        for entry in entries:
            if key is not None and entry.get("anchorKey") != key:
                break
            selected.append(entry)
        ids = {text(entry.get("id")) for entry in selected}
        if len(ids) != len(selected):
            raise E2eeError("invalid_conversation_index")
        contexts = self._thread_contexts(ids)
        threads = []
        for entry in selected:
            context = contexts[entry["id"]]
            sequence = number(context["comment"]["value"].get("sequence"), 1)
            original_key = anchor_key(context["comment"]["value"].get("anchor"))
            if (
                entry.get("headID") != context["head"]["record_id"]
                or entry.get("sequence") != sequence
                or entry.get("anchorKey") != original_key
                or entry.get("name") != original_key + "\0" + descending(sequence)
                or sequence > number(header["value"].get("sequence"))
            ):
                raise E2eeError("invalid_conversation_index")
            threads.append(self._thread_view(context))
        self._page_size(threads)
        self._same_records([header])
        self._check_thread_heads(contexts.values())
        return {
            "threads": threads,
            "next_key": following if len(selected) == len(entries) else None,
        }

    @conflict_retry
    def comment_replies(self, parent_id, *, after=None, limit=100):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise E2eeError("invalid_cursor")
        context = self._thread_contexts({parent_id})[parent_id]
        total = number(context["head"]["value"]["replyCount"])
        try:
            prior = number(int(after[0]), 1) if after else 0
        except (ValueError, TypeError):
            raise E2eeError("invalid_cursor") from None
        entries, following = self._index("comment").page(
            reference(context["head"]["value"].get("replies")), after=after, limit=limit
        )
        records = self._read(text(entry.get("id")) for entry in entries)
        originals = {
            entry["id"]: self._comment_record(records.get(entry["id"]), "reply")
            for entry in entries
        }
        contexts = self._text_contexts(originals)
        replies, sequence = [], prior
        for entry in entries:
            original = originals[entry["id"]]
            sequence += 1
            if (
                original["value"].get("parentCommentId") != parent_id
                or original["value"].get("sequence") != sequence
                or entry.get("sequence") != sequence
                or entry.get("name") != ascending(sequence)
            ):
                raise E2eeError("invalid_conversation_index")
            replies.append(self._text_view(contexts[entry["id"]]))
        if (following is None and sequence != total) or (
            following is not None and sequence == total
        ):
            raise E2eeError("invalid_conversation_index")
        self._page_size(replies)
        self._check_thread_heads([context])
        self._same_records([value["head"] for value in contexts.values()])
        return {"replies": replies, "next_key": following, "total_count": total}

    @conflict_retry
    def comment_reply(self, identifier):
        originals = self._read([identifier])
        if identifier not in originals:
            return None
        original = self._comment_record(originals[identifier], "reply")
        parent_id, sequence = (
            text(original["value"].get("parentCommentId")),
            number(original["value"].get("sequence"), 1),
        )
        parent = self._thread_contexts({parent_id})[parent_id]
        entries, _ = self._index("comment").page(
            reference(parent["head"]["value"].get("replies")),
            after=(ascending(sequence), ""),
            limit=1,
        )
        if (
            not entries
            or entries[0].get("id") != identifier
            or entries[0].get("sequence") != sequence
            or entries[0].get("name") != ascending(sequence)
            or sequence > number(parent["head"]["value"]["replyCount"])
        ):
            raise E2eeError("invalid_conversation_index")
        context = self._text_contexts({identifier: original})[identifier]
        self._check_thread_heads([parent])
        self._same_records([context["head"]])
        return self._text_view(context)

    def _same_comment_input(self, record, value):
        generated = {
            "format",
            "recordType",
            "id",
            "threadHeadId",
            "bodyHeadId",
            "sequence",
            "parentCommentId",
            "createdAt",
            "author",
        }
        content = lambda item: {
            key: value for key, value in item.items() if key not in generated
        }
        return record["author_subject"] == self.subject and content(
            record["value"]
        ) == content(value)

    def _validate_author(self, value):
        verify_actor({"value": value, "author_subject": self.subject}, "author")

    @conflict_retry
    def create_comment(self, identifier, value):
        text(identifier)
        self._validate_author(value)
        existing = self._read([identifier]).get(identifier)
        if existing:
            original = self._comment_record(existing, "comment")
            if not self._same_comment_input(original, value):
                raise E2eeError("idempotency_conflict")
            return self.comment_thread(identifier)
        header = self._load_header(COMMENT_HEADER, "comment", "comment_header")
        sequence = number(header["value"].get("sequence")) + 1
        number(sequence, 1)
        key = anchor_key(value.get("anchor"))
        head_id, body_id = self.mint_id(), self.mint_id()
        original = {
            **value,
            "format": FORMAT,
            "recordType": "comment",
            "id": identifier,
            "threadHeadId": head_id,
            "bodyHeadId": body_id,
            "sequence": sequence,
        }
        root, nodes = self._index("comment").mutation(
            reference(header["value"].get("threads")),
            {
                "name": key + "\0" + descending(sequence),
                "id": identifier,
                "headID": head_id,
                "anchorKey": key,
                "sequence": sequence,
            },
        )
        self._write(
            [
                write(identifier, "comment", original, immutable=True),
                self._initial_text_head(identifier, "comment", body_id),
                write(
                    head_id,
                    "comment",
                    {
                        "format": FORMAT,
                        "recordType": "thread_head",
                        "commentId": identifier,
                        "original": {"id": identifier, "revision": 1},
                        "replies": None,
                        "replyCount": 0,
                        "resolution": None,
                    },
                ),
                *nodes,
                write(
                    COMMENT_HEADER,
                    "comment",
                    {**header["value"], "sequence": sequence, "threads": root},
                    revision=header["revision"],
                ),
            ]
        )
        return {
            **original,
            "resolved": False,
            "replies": [],
            "replyCount": 0,
            "hasMoreReplies": False,
            "revision": 1,
        }

    @conflict_retry
    def create_reply(self, identifier, *, parent_id, value):
        text(identifier)
        self._validate_author(value)
        existing = self._read([identifier]).get(identifier)
        if existing:
            original = self._comment_record(existing, "reply")
            if original["value"].get(
                "parentCommentId"
            ) != parent_id or not self._same_comment_input(original, value):
                raise E2eeError("idempotency_conflict")
            self._thread_contexts({parent_id})
            return self.comment_reply(identifier)
        context = self._thread_contexts({parent_id})[parent_id]
        sequence = number(context["head"]["value"]["replyCount"]) + 1
        number(sequence, 1)
        body_id = self.mint_id()
        original = {
            **value,
            "format": FORMAT,
            "recordType": "reply",
            "parentCommentId": parent_id,
            "id": identifier,
            "sequence": sequence,
            "bodyHeadId": body_id,
        }
        root, nodes = self._index("comment").mutation(
            reference(context["head"]["value"].get("replies")),
            {"name": ascending(sequence), "id": identifier, "sequence": sequence},
        )
        self._write(
            [
                write(identifier, "comment", original, immutable=True),
                self._initial_text_head(identifier, "reply", body_id),
                *nodes,
                write(
                    context["head"]["record_id"],
                    "comment",
                    {
                        **context["head"]["value"],
                        "replyCount": sequence,
                        "replies": root,
                    },
                    revision=context["head"]["revision"],
                ),
            ],
            [{"record_id": parent_id, "expected_revision": 1}],
        )
        return {**original, "revision": 1}

    @conflict_retry
    def set_resolution(self, parent_id, *, resolved, actor, operation_id):
        text(operation_id)
        if type(resolved) is not bool:
            raise E2eeError("invalid_request")
        verify_actor(
            {"value": {"actor": actor}, "author_subject": self.subject}, "actor"
        )
        event_id = "cres_" + operation_id
        existing = self._read([event_id]).get(event_id)
        if existing:
            record = self._resolution_record(existing, parent_id)
            if (
                record["author_subject"] != self.subject
                or record["value"]["operationID"] != operation_id
                or record["value"]["resolved"] != resolved
            ):
                raise E2eeError("idempotency_conflict")
            return self.comment_thread(parent_id)
        context = self._thread_contexts({parent_id})[parent_id]
        event = {
            "format": FORMAT,
            "recordType": "resolution",
            "parentCommentId": parent_id,
            "resolved": resolved,
            "operationID": operation_id,
            "actor": actor,
        }
        self._write(
            [
                write(event_id, "comment", event, immutable=True),
                write(
                    context["head"]["record_id"],
                    "comment",
                    {
                        **context["head"]["value"],
                        "resolution": {"id": event_id, "revision": 1},
                    },
                    revision=context["head"]["revision"],
                ),
            ],
            [{"record_id": parent_id, "expected_revision": 1}],
        )
        return {**self._thread_view(context), "resolved": resolved}
