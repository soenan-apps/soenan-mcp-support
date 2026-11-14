from __future__ import annotations

from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._conversation_context import ConversationContext, number, text, write
from ._crypto import E2eeError


def valid_body(original, body):
    value = original["value"]
    return isinstance(body, str) and bool(
        body.strip() or (isinstance(value, domain.ReplyOrigin) and value.references)
    )


def target_type(value):
    return (
        domain.TEXT_TARGET_TYPE_REPLY
        if isinstance(value, domain.ReplyOrigin)
        else domain.TEXT_TARGET_TYPE_COMMENT
    )


class TextOperations(ConversationContext):
    def _initial_text_head(self, identifier, target, head_id):
        return write(
            head_id,
            "comment",
            domain.TextHead(
                original=domain.RecordReference(
                    id=identifier,
                    revision=1,
                    incarnation=self.records.operation_id,
                ),
                target_type=domain.TEXT_TARGET_TYPE_REPLY
                if target == "reply"
                else domain.TEXT_TARGET_TYPE_COMMENT,
                text_revision=1,
            ),
        )

    def _text_edit(self, record, original):
        result = self._record(record, "comment", domain.TextRevision, immutable=True)
        value = result["value"]
        if (
            result["record_id"] != "ctxt_" + text(value.operation_id)
            or result["author_subject"] != original["author_subject"]
            or value.author_account_subject != original["author_subject"]
            or value.original
            != domain.RecordReference(
                id=original["record_id"],
                revision=1,
                incarnation=original["incarnation"],
            )
            or value.target_type != target_type(original["value"])
            or value.body_head_id != original["value"].body_head_id
            or not valid_body(original, value.body)
        ):
            raise E2eeError("invalid_conversation_text")
        number(value.text_revision, 2)
        return result

    def _text_context(self, original, head, edits):
        self._header(head, "comment", domain.TextHead)
        value = head["value"]
        revision = number(value.text_revision, 1)
        ref = value.last_edit if value.HasField("last_edit") else None
        if (
            head["author_subject"] != original["author_subject"]
            or head["record_id"] != original["value"].body_head_id
            or value.target_type != target_type(original["value"])
            or value.original
            != domain.RecordReference(
                id=original["record_id"],
                revision=1,
                incarnation=original["incarnation"],
            )
            or head["revision"] != revision
            or ((ref is not None) if revision == 1 else (ref is None))
            or (ref is not None and ref.revision != 1)
        ):
            raise E2eeError("invalid_conversation_text")
        edit = None
        if ref is not None:
            edit = self._text_edit(edits.get(ref.id), original)
            if (
                edit["value"].text_revision != revision
                or ref.incarnation != edit["incarnation"]
            ):
                raise E2eeError("invalid_conversation_text")
        return {"original": original, "head": head, "edit": edit}

    def _comment_view(self, context) -> domain.CommentView:
        value = domain.CommentView(
            id=context["original"]["record_id"],
            origin=context["original"]["value"],
            text_head=context["head"]["value"],
        )
        if context["edit"]:
            value.latest_edit.CopyFrom(context["edit"]["value"])
        return value

    def _reply_view(self, context) -> domain.ReplyView:
        value = domain.ReplyView(
            id=context["original"]["record_id"],
            origin=context["original"]["value"],
            text_head=context["head"]["value"],
        )
        if context["edit"]:
            value.latest_edit.CopyFrom(context["edit"]["value"])
        return value
