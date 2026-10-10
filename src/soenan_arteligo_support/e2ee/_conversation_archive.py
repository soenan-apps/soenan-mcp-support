from __future__ import annotations

from ._conversation_context import FORMAT, number, reference, text
from ._crypto import E2eeError


class ArchiveOperations:
    def archive(self, *, snapshot_cursor=None):
        """Explicitly reconstruct a frozen archive, rejecting an incomplete proof population.

        Large exports can consume records.immutable_kind pages directly instead.
        """
        records = {}
        for kind in ("chat", "comment"):
            after = 0
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
            if value.get("format") != FORMAT:
                raise E2eeError("content_format_update_required")
            kind = (record["kind"], value.get("recordType"))
            if kind == ("chat", "event"):
                events.append(self._chat_event(record))
            elif kind in {("chat", "operation"), ("chat", "terminal")}:
                helpers.add(record["record_id"])
            elif kind == ("comment", "comment"):
                comments[record["record_id"]] = self._comment_record(record, "comment")
            elif kind == ("comment", "reply"):
                reply = self._comment_record(record, "reply")
                replies.setdefault(text(value.get("parentCommentId")), []).append(reply)
            elif kind == ("comment", "resolution"):
                parent = text(value.get("parentCommentId"))
                resolution = self._resolution_record(record, parent)
                if (
                    parent not in resolutions
                    or resolutions[parent]["cursor"] < record["cursor"]
                ):
                    resolutions[parent] = resolution
            elif kind == ("comment", "text_edit"):
                edits.setdefault(text(value.get("targetID")), []).append(record)
            else:
                raise E2eeError("invalid_conversation_archive")
        events.sort(key=lambda record: number(record["value"]["sequence"], 1))
        latest, origins = {}, {}
        for sequence, event in enumerate(events, 1):
            self.checkpoint()
            value, identifier = event["value"], event["value"]["messageId"]
            previous = latest.get(identifier)
            if value["sequence"] != sequence:
                raise E2eeError("invalid_conversation_archive")
            if previous is None:
                if (
                    value["type"] != "sent"
                    or value["revision"] != 1
                    or event["record_id"] != identifier
                ):
                    raise E2eeError("invalid_conversation_archive")
                origins[identifier] = event
            else:
                origin = origins[identifier]
                if (
                    previous["value"]["type"] == "deleted"
                    or value["type"] == "sent"
                    or value["revision"] != previous["value"]["revision"] + 1
                    or value["messageHeadId"] != origin["value"]["messageHeadId"]
                    or event["author_subject"] != origin["author_subject"]
                    or value["references"]
                ):
                    raise E2eeError("invalid_conversation_archive")
            binding_id = "cop_" + value["clientOperationId"]
            binding = self._record(
                records.get(binding_id), "chat", "operation", immutable=True
            )
            if (
                binding["value"].get("eventID") != event["record_id"]
                or binding["value"].get("messageId") != identifier
                or binding["value"].get("type") != value["type"]
                or binding["author_subject"] != event["author_subject"]
                or binding_id not in helpers
            ):
                raise E2eeError("invalid_conversation_archive")
            helpers.remove(binding_id)
            latest[identifier] = event
        for identifier, original in origins.items():
            terminal_id = text(original["value"].get("terminalRecordId"))
            terminal, last = records.get(terminal_id), latest[identifier]
            if terminal is None:
                if last["value"]["type"] == "deleted":
                    raise E2eeError("invalid_conversation_archive")
                continue
            self._record(terminal, "chat", "terminal", immutable=True)
            marker = terminal["value"]
            if (
                last["value"]["type"] != "deleted"
                or terminal["author_subject"] != original["author_subject"]
                or marker.get("messageId") != identifier
                or marker.get("messageHeadId") != original["value"]["messageHeadId"]
                or reference(marker.get("deleteEvent"))
                != {"id": last["record_id"], "revision": 1}
                or marker.get("messageRevision") != last["value"]["revision"]
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
        views = {}
        for identifier, original in text_origins.items():
            self.checkpoint()
            text(original["value"].get("bodyHeadId"))
            revision, cursor, last = 1, original["cursor"], None
            for record in sorted(
                edits.get(identifier, []),
                key=lambda record: number(record["value"].get("revision"), 2),
            ):
                edit = self._text_edit(record, original)
                revision += 1
                if edit["value"]["revision"] != revision or edit["cursor"] <= cursor:
                    raise E2eeError("invalid_conversation_archive")
                cursor, last = edit["cursor"], edit
            views[identifier] = {
                **original["value"],
                "body": last["value"]["body"] if last else original["value"]["body"],
                "revision": revision,
                **({"editedAt": last["value"]["committedAt"]} if last else {}),
            }
        threads = []
        for sequence, original in enumerate(
            sorted(
                comments.values(),
                key=lambda record: number(record["value"].get("sequence"), 1),
            ),
            1,
        ):
            self.checkpoint()
            if original["value"]["sequence"] != sequence:
                raise E2eeError("invalid_conversation_archive")
            identifier = original["record_id"]
            children = sorted(
                replies.get(identifier, []),
                key=lambda record: number(record["value"].get("sequence"), 1),
            )
            if any(
                child["value"]["sequence"] != index
                for index, child in enumerate(children, 1)
            ):
                raise E2eeError("invalid_conversation_archive")
            threads.append(
                {
                    **views[identifier],
                    "resolved": resolutions[identifier]["value"]["resolved"]
                    if identifier in resolutions
                    else False,
                    "replies": [views[child["record_id"]] for child in children],
                    "replyCount": len(children),
                    "hasMoreReplies": False,
                }
            )
        return {"events": [event["value"] for event in events], "comments": threads}
