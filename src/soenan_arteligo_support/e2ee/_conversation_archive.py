from __future__ import annotations

from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._conversation_chat import (
    ChatOperations,
    event_message_id,
    event_revision,
    event_type,
)
from ._conversation_comments import CommentOperations
from ._conversation_context import number, reference, text
from ._crypto import E2eeError


class ArchiveOperations(ChatOperations, CommentOperations):
    def archive(self, *, snapshot_cursor=None):
        """Explicitly reconstruct a frozen archive, rejecting an incomplete proof population.

        Large exports can consume records.immutable_kind pages directly instead.
        """
        records = {}
        for kind in ("chat", "comment"):
            after = ""
            while True:
                self.checkpoint()
                page = self.records.immutable_kind(
                    self.scope, kind, after=after, snapshot_cursor=snapshot_cursor
                )
                snapshot_cursor = page["snapshot_cursor"]
                for record in page["records"]:
                    identifier = record["record_id"]
                    if identifier in records:
                        raise E2eeError("invalid_conversation_archive")
                    records[identifier] = record
                if not page["has_more"]:
                    break
                after = page["cursor"]
        return {**self.archive_snapshot(records), "snapshot_cursor": snapshot_cursor}

    def archive_snapshot(self, records):
        events, comments, replies, resolutions, edits, helpers = (
            [],
            {},
            {},
            {},
            {},
            set(),
        )
        for record in records.values():
            self.checkpoint()
            self._record(record, record["kind"], immutable=True)
            value = record["value"]
            if record["kind"] == "chat" and isinstance(
                value, (domain.ChatOrigin, domain.ChatEvent)
            ):
                events.append(self._chat_event(record))
            elif record["kind"] == "chat" and isinstance(
                value, (domain.ChatOperation, domain.ChatTerminal)
            ):
                self._record(record, "chat", value.__class__, immutable=True)
                helpers.add(record["record_id"])
            elif record["kind"] == "comment" and isinstance(
                value, domain.CommentOrigin
            ):
                comments[record["record_id"]] = self._comment_record(
                    record, domain.CommentOrigin
                )
            elif record["kind"] == "comment" and isinstance(value, domain.ReplyOrigin):
                reply = self._comment_record(record, domain.ReplyOrigin)
                replies.setdefault(text(value.parent_comment_id), []).append(reply)
            elif record["kind"] == "comment" and isinstance(
                value, domain.ResolutionEvent
            ):
                parent = text(value.original.id)
                resolution = self._resolution_record(record, parent)
                if (
                    parent not in resolutions
                    or resolutions[parent]["cursor"] < record["cursor"]
                ):
                    resolutions[parent] = resolution
            elif record["kind"] == "comment" and isinstance(value, domain.TextRevision):
                edits.setdefault(text(value.original.id), []).append(record)
            else:
                raise E2eeError("invalid_conversation_archive")
        events.sort(key=lambda record: number(record["value"].sequence, 1))
        latest, origins = {}, {}
        for sequence, event in enumerate(events, 1):
            self.checkpoint()
            value, identifier = event["value"], event_message_id(event)
            previous = latest.get(identifier)
            if value.sequence != sequence:
                raise E2eeError("invalid_conversation_archive")
            if previous is None:
                if (
                    not isinstance(value, domain.ChatOrigin)
                    or event["record_id"] != identifier
                ):
                    raise E2eeError("invalid_conversation_archive")
                origins[identifier] = event
            else:
                origin = origins[identifier]
                if (
                    event_type(previous["value"]) == domain.CHAT_EVENT_TYPE_DELETED
                    or isinstance(value, domain.ChatOrigin)
                    or event_revision(value) != event_revision(previous["value"]) + 1
                    or value.message_head_id != origin["value"].message_head_id
                    or event["author_subject"] != origin["author_subject"]
                ):
                    raise E2eeError("invalid_conversation_archive")
            binding_id = "cop_" + value.client_operation_id
            binding = self._record(
                records.get(binding_id), "chat", domain.ChatOperation, immutable=True
            )
            if (
                binding["value"].event_id != event["record_id"]
                or binding["value"].message_id != identifier
                or binding["value"].type != event_type(value)
                or binding["author_subject"] != event["author_subject"]
                or binding_id not in helpers
            ):
                raise E2eeError("invalid_conversation_archive")
            helpers.remove(binding_id)
            latest[identifier] = event
        for identifier, original in origins.items():
            terminal_id = text(original["value"].terminal_record_id)
            terminal, last = records.get(terminal_id), latest[identifier]
            if terminal is None:
                if event_type(last["value"]) == domain.CHAT_EVENT_TYPE_DELETED:
                    raise E2eeError("invalid_conversation_archive")
                continue
            self._record(terminal, "chat", domain.ChatTerminal, immutable=True)
            marker = terminal["value"]
            if (
                event_type(last["value"]) != domain.CHAT_EVENT_TYPE_DELETED
                or terminal["author_subject"] != original["author_subject"]
                or reference(marker.original)
                != domain.RecordReference(id=identifier, revision=1)
                or marker.message_head_id != original["value"].message_head_id
                or reference(marker.delete_event)
                != domain.RecordReference(id=last["record_id"], revision=1)
                or marker.message_revision != event_revision(last["value"])
                or terminal_id not in helpers
            ):
                raise E2eeError("invalid_conversation_archive")
            helpers.remove(terminal_id)
        if (
            helpers
            or replies.keys() - comments.keys()
            or resolutions.keys() - comments.keys()
        ):
            raise E2eeError("invalid_conversation_archive")
        text_origins = {
            **comments,
            **{
                record["record_id"]: record
                for group in replies.values()
                for record in group
            },
        }
        if edits.keys() - text_origins.keys():
            raise E2eeError("invalid_conversation_archive")
        comment_views: dict[str, domain.CommentView] = {}
        reply_views: dict[str, domain.ReplyView] = {}
        for identifier, original in text_origins.items():
            self.checkpoint()
            text(original["value"].body_head_id)
            revision, cursor, last = 1, original["cursor"], None
            for record in sorted(
                edits.get(identifier, []),
                key=lambda record: number(record["value"].text_revision, 2),
            ):
                edit = self._text_edit(record, original)
                revision += 1
                if edit["value"].text_revision != revision or edit["cursor"] <= cursor:
                    raise E2eeError("invalid_conversation_archive")
                cursor, last = edit["cursor"], edit
            head = domain.TextHead(
                original=domain.RecordReference(id=identifier, revision=1),
                target_type=domain.TEXT_TARGET_TYPE_REPLY
                if isinstance(original["value"], domain.ReplyOrigin)
                else domain.TEXT_TARGET_TYPE_COMMENT,
                text_revision=revision,
            )
            if last:
                head.last_edit.CopyFrom(
                    domain.RecordReference(id=last["record_id"], revision=1)
                )
            context = {"original": original, "head": {"value": head}, "edit": last}
            if isinstance(original["value"], domain.ReplyOrigin):
                reply_views[identifier] = self._reply_view(context)
            else:
                comment_views[identifier] = self._comment_view(context)
        threads = []
        for sequence, original in enumerate(
            sorted(
                comments.values(),
                key=lambda record: number(record["value"].sequence, 1),
            ),
            1,
        ):
            self.checkpoint()
            if original["value"].sequence != sequence:
                raise E2eeError("invalid_conversation_archive")
            identifier = original["record_id"]
            children = sorted(
                replies.get(identifier, []),
                key=lambda record: number(record["value"].sequence, 1),
            )
            if any(
                child["value"].sequence != index
                for index, child in enumerate(children, 1)
            ):
                raise E2eeError("invalid_conversation_archive")
            value = comment_views[identifier]
            value.thread_head.CopyFrom(
                domain.ThreadHead(
                    original=domain.RecordReference(id=identifier, revision=1),
                    reply_count=len(children),
                )
            )
            if identifier in resolutions:
                resolution = resolutions[identifier]
                value.resolution.CopyFrom(resolution["value"])
                value.thread_head.resolution.CopyFrom(
                    domain.RecordReference(id=resolution["record_id"], revision=1)
                )
            value.replies.extend(reply_views[child["record_id"]] for child in children)
            value.has_more_replies = False
            threads.append(value)
        return {
            "events": [
                self._event_view(
                    event["record_id"],
                    origins[event_message_id(event)]["value"],
                    event["value"],
                )
                for event in events
            ],
            "comments": threads,
        }
