from __future__ import annotations

from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._conversation_chat import ChatOperations
from ._conversation_comments import CommentOperations
from ._conversation_context import number, text
from ._crypto import E2eeError


class ArchiveOperations(ChatOperations, CommentOperations):
    def archive(self, *, snapshot_cursor=None, snapshot_epoch=0):
        """Read a frozen record snapshot, including live chat messages."""
        records = {}
        chat_events = []
        for kind in ("chat_message", "comment"):
            after = ""
            while True:
                self.checkpoint()
                page = self.records._page(
                    self.scope,
                    view="page",
                    kind=kind,
                    cursor=after,
                    snapshot_cursor=snapshot_cursor or 0,
                    snapshot_epoch=snapshot_epoch,
                    immutable_only=kind == "comment",
                    limit=256,
                )
                snapshot_cursor = page["snapshot_cursor"]
                snapshot_epoch = page["snapshot_epoch"]
                for record in page["records"]:
                    identifier = record["record_id"]
                    if identifier in records:
                        raise E2eeError("invalid_conversation_archive")
                    records[identifier] = record
                    if kind == "chat_message":
                        before = 0
                        while True:
                            self.checkpoint()
                            history = self.records.history(
                                self.scope,
                                identifier,
                                before=before,
                                snapshot_epoch=snapshot_epoch,
                                snapshot_cursor=snapshot_cursor,
                            )
                            chat_events.extend(
                                self._event_view(item) for item in history["records"]
                            )
                            if not history["has_more"]:
                                break
                            before = history["cursor"]
                if not page["has_more"]:
                    break
                after = page["cursor"]
        return {
            **self.archive_snapshot(records, chat_events=chat_events),
            "snapshot_cursor": snapshot_cursor,
            "snapshot_epoch": snapshot_epoch,
        }

    def archive_snapshot(self, records, *, chat_events=None):
        events, comments, replies, resolutions, edits = [], {}, {}, {}, {}
        for record in records.values():
            self.checkpoint()
            if record["kind"] == "chat_message":
                if chat_events is None:
                    events.append(self._event_view(record))
                continue
            self._record(record, "comment", immutable=True)
            value = record["value"]
            if record["kind"] == "comment" and isinstance(value, domain.CommentOrigin):
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
                resolution = self._resolution_record(
                    record,
                    parent,
                    records[parent]["incarnation"],
                )
                if (
                    parent not in resolutions
                    or resolutions[parent]["cursor"] < record["cursor"]
                ):
                    resolutions[parent] = resolution
            elif record["kind"] == "comment" and isinstance(value, domain.TextRevision):
                edits.setdefault(text(value.original.id), []).append(record)
            else:
                raise E2eeError("invalid_conversation_archive")
        if chat_events is not None:
            events = chat_events
        events.sort(key=lambda event: event.sequence)
        if replies.keys() - comments.keys() or resolutions.keys() - comments.keys():
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
                original=domain.RecordReference(
                    id=identifier,
                    revision=1,
                    incarnation=original["incarnation"],
                ),
                target_type=domain.TEXT_TARGET_TYPE_REPLY
                if isinstance(original["value"], domain.ReplyOrigin)
                else domain.TEXT_TARGET_TYPE_COMMENT,
                text_revision=revision,
            )
            if last:
                head.last_edit.CopyFrom(
                    domain.RecordReference(
                        id=last["record_id"],
                        revision=1,
                        incarnation=last["incarnation"],
                    )
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
                    original=domain.RecordReference(
                        id=identifier,
                        revision=1,
                        incarnation=original["incarnation"],
                    ),
                    reply_count=len(children),
                )
            )
            if identifier in resolutions:
                resolution = resolutions[identifier]
                value.resolution.CopyFrom(resolution["value"])
                value.thread_head.resolution.CopyFrom(
                    domain.RecordReference(
                        id=resolution["record_id"],
                        revision=1,
                        incarnation=resolution["incarnation"],
                    )
                )
            value.replies.extend(reply_views[child["record_id"]] for child in children)
            value.has_more_replies = False
            threads.append(value)
        return {
            "events": events,
            "comments": threads,
        }
