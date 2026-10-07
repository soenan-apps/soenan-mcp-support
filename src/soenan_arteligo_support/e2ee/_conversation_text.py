from __future__ import annotations

from datetime import datetime

from ._conversation_context import (
    FORMAT,
    ascending,
    conflict_retry,
    number,
    reference,
    text,
    write,
)
from ._crypto import E2eeError


def valid_body(original, body):
    return (
        isinstance(body, str)
        and len(body) <= 4096
        and (
            body.strip()
            or (
                original["value"]["recordType"] == "reply"
                and original["value"].get("references")
            )
        )
    )


class TextOperations:
    def _initial_text_head(self, identifier, target_type, head_id):
        return write(
            head_id,
            "comment",
            {
                "format": FORMAT,
                "recordType": "text_head",
                "targetID": identifier,
                "targetType": target_type,
                "original": {"id": identifier, "revision": 1},
                "textRevision": 1,
                "lastEdit": None,
                "edits": None,
            },
        )

    def _text_edit(self, record, original):
        result = self._record(record, "comment", "text_edit", immutable=True)
        value = result["value"]
        try:
            datetime.fromisoformat(value["committedAt"].replace("Z", "+00:00"))
        except (KeyError, AttributeError, ValueError):
            raise E2eeError("invalid_conversation_text") from None
        if (
            value.get("format") != FORMAT
            or result["record_id"] != "ctxt_" + text(value.get("operationID"))
            or result["author_subject"] != original["author_subject"]
            or value.get("authorAccountSubject") != original["author_subject"]
            or value.get("targetID") != original["record_id"]
            or value.get("targetType") != original["value"]["recordType"]
            or value.get("bodyHeadId") != original["value"]["bodyHeadId"]
            or not valid_body(original, value.get("body"))
        ):
            raise E2eeError("invalid_conversation_text")
        number(value.get("revision"), 2)
        return result

    def _text_contexts(self, originals, prefetched=None):
        prefetched = prefetched or {}
        head_ids = {
            text(original["value"].get("bodyHeadId")) for original in originals.values()
        }
        heads = {**prefetched, **self._read(head_ids - prefetched.keys())}
        refs = set()
        for original in originals.values():
            head = self._header(
                heads.get(original["value"]["bodyHeadId"]), "comment", "text_head"
            )
            ref = reference(head["value"].get("lastEdit"))
            if ref:
                if ref["revision"] != 1:
                    raise E2eeError("invalid_conversation_text")
                refs.add(ref["id"])
        edits = {**prefetched, **self._read(refs - prefetched.keys())}
        result = {}
        for identifier, original in originals.items():
            head = heads[original["value"]["bodyHeadId"]]
            value = head["value"]
            revision = number(value.get("textRevision"), 1)
            ref = reference(value.get("lastEdit"))
            if (
                head["author_subject"] != original["author_subject"]
                or head["record_id"] != original["value"]["bodyHeadId"]
                or value.get("targetID") != identifier
                or value.get("targetType") != original["value"]["recordType"]
                or reference(value.get("original")) != {"id": identifier, "revision": 1}
                or head["revision"] != revision
                or ((ref is not None) if revision == 1 else (ref is None))
            ):
                raise E2eeError("invalid_conversation_text")
            edit = self._text_edit(edits.get(ref["id"]), original) if ref else None
            if edit and edit["value"]["revision"] != revision:
                raise E2eeError("invalid_conversation_text")
            result[identifier] = {"original": original, "head": head, "edit": edit}
        return result

    def _text_view(self, context):
        edit = context["edit"]
        return {
            **context["original"]["value"],
            "body": edit["value"]["body"]
            if edit
            else context["original"]["value"]["body"],
            "revision": context["head"]["value"]["textRevision"],
            **({"editedAt": edit["value"]["committedAt"]} if edit else {}),
        }

    @conflict_retry
    def _edit_text(
        self,
        identifier,
        target_type,
        operation_id,
        expected_revision,
        body,
        committed_at,
        parent_id=None,
    ):
        number(expected_revision, 1)
        text(operation_id)
        try:
            datetime.fromisoformat(committed_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            raise E2eeError("invalid_request") from None
        event_id = "ctxt_" + operation_id
        records = self._read([identifier, event_id])
        original = self._comment_record(records.get(identifier), target_type)
        if not valid_body(original, body):
            raise E2eeError("invalid_request")
        if original["author_subject"] != self.subject:
            raise E2eeError("not_comment_author")
        if (
            target_type == "reply"
            and original["value"].get("parentCommentId") != parent_id
        ):
            raise E2eeError("comment_parent_mismatch")
        if event_id in records:
            event = self._text_edit(records[event_id], original)["value"]
            if (
                event.get("operationID") != operation_id
                or event["revision"] != expected_revision + 1
                or event["body"] != body
            ):
                raise E2eeError("idempotency_conflict")
            return
        context = self._text_contexts({identifier: original})[identifier]
        head = context["head"]
        revision = head["value"]["textRevision"]
        if revision != expected_revision:
            raise E2eeError("revision_conflict")
        event = {
            "format": FORMAT,
            "recordType": "text_edit",
            "targetID": identifier,
            "targetType": target_type,
            "bodyHeadId": head["record_id"],
            "operationID": operation_id,
            "revision": revision + 1,
            "authorAccountSubject": self.subject,
            "body": body,
            "committedAt": committed_at,
        }
        root, nodes = self._index("comment").mutation(
            reference(head["value"].get("edits")),
            {"name": ascending(revision + 1), "id": event_id, "revision": revision + 1},
        )
        self._write(
            [
                write(event_id, "comment", event, immutable=True),
                *nodes,
                write(
                    head["record_id"],
                    "comment",
                    {
                        **head["value"],
                        "textRevision": revision + 1,
                        "lastEdit": {"id": event_id, "revision": 1},
                        "edits": root,
                    },
                    revision=head["revision"],
                ),
            ],
            [{"record_id": identifier, "expected_revision": 1}],
        )

    def edit_comment(
        self, identifier, *, operation_id, expected_revision, body, committed_at
    ):
        self._edit_text(
            identifier, "comment", operation_id, expected_revision, body, committed_at
        )
        return self.comment_thread(identifier)

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
        self._edit_text(
            identifier,
            "reply",
            operation_id,
            expected_revision,
            body,
            committed_at,
            parent_id,
        )
        return self.comment_reply(identifier)
