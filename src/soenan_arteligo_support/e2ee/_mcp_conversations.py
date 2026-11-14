from __future__ import annotations

from typing import Annotated, Any, Literal

import anyio
from google.protobuf.json_format import ParseDict, ParseError
from google.protobuf.timestamp_pb2 import Timestamp as TimestampMessage
from pydantic import Field
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ._conversation_context import MAX_INTEGER
from ._conversations import EncryptedConversations
from ._crypto import E2eeError
from ._records import EncryptedRecords

_WIRE_IDENTIFIER_BYTES = 128
_IDENTIFIER_PATTERN = r"^[A-Za-z0-9_-]+$"
Identifier = Annotated[
    str,
    Field(min_length=1, max_length=_WIRE_IDENTIFIER_BYTES, pattern=_IDENTIFIER_PATTERN),
]
MessageID = Annotated[str, Field(pattern=r"^cmsg_[0-9a-f]{32}$")]
ChatOperationID = Annotated[
    str,
    Field(
        min_length=1,
        max_length=_WIRE_IDENTIFIER_BYTES - len("cevt_"),
        pattern=_IDENTIFIER_PATTERN,
    ),
]
Revision = Annotated[int, Field(ge=1, le=MAX_INTEGER)]
Position = Annotated[int, Field(ge=0, le=MAX_INTEGER)]
PageLimit = Annotated[int, Field(ge=1)]
EventLimit = Annotated[int, Field(ge=1)]
Body = str
ChatBody = str
References = list[dict[str, Any]]


Timestamp = Annotated[str, Field(min_length=1)]


def _parse_message(value, message):
    try:
        ParseDict(value, message)
    except (ParseError, ValueError, TypeError):
        raise E2eeError("invalid_request") from None
    if not message.IsInitialized() or any(
        message.WhichOneof(oneof.name) is None for oneof in message.DESCRIPTOR.oneofs
    ):
        raise E2eeError("invalid_request")
    return message


def register_conversation_tools(server, run):
    def conversations(session, project):
        return EncryptedConversations(
            EncryptedRecords(session),
            project,
            checkpoint=anyio.from_thread.check_cancelled,
        )

    def actor(session, display_name):
        return domain.MemberActor(
            membership_id=session.subject,
            user_id=session.subject,
            display_name=display_name,
        )

    @server.tool()
    def arteligo_chat_messages(
        project_id: Identifier,
        before_sequence: Revision | None = None,
        limit: PageLimit = 100,
    ) -> dict[str, Any]:
        """Read a verified newest-first chat page without enumerating edit history."""
        return run(
            lambda session: conversations(session, project_id).chat_messages(
                before_sequence=before_sequence, limit=limit
            )
        )

    @server.tool()
    def arteligo_chat_events(
        project_id: Identifier,
        after: Position = 0,
        limit: EventLimit = 200,
        snapshot_epoch: Position = 0,
    ) -> dict[str, Any]:
        """Read verified record changes after the saved cursor and snapshot epoch."""
        return run(
            lambda session: conversations(session, project_id).chat_events(
                after=after,
                limit=limit,
                snapshot_epoch=snapshot_epoch,
            )
        )

    @server.tool()
    def arteligo_chat_message(
        project_id: Identifier, message_id: MessageID
    ) -> dict[str, Any]:
        """Read one current message or its signed body-free deletion proof."""
        return run(
            lambda session: {
                "message": conversations(session, project_id).chat_message(message_id)
            }
        )

    @server.tool()
    def arteligo_chat_message_history(
        project_id: Identifier, message_id: MessageID
    ) -> dict[str, Any]:
        """Explicitly verify every message revision and return the verified final event."""
        return run(
            lambda session: conversations(session, project_id).chat_message_history(
                message_id
            )
        )

    @server.tool()
    def arteligo_chat_operation(
        project_id: Identifier,
        operation_id: ChatOperationID,
        message_id: MessageID,
        type: Literal["sent", "edited", "deleted"],
        revision: Revision,
        incarnation: Identifier,
    ) -> dict[str, Any]:
        """Confirm an accepted command through its common record receipt."""
        return run(
            lambda session: {
                "event": conversations(session, project_id).chat_operation(
                    operation_id,
                    message_id=message_id,
                    type=type,
                    revision=revision,
                    incarnation=incarnation,
                )
            }
        )

    @server.tool()
    def arteligo_chat_send(
        project_id: Identifier,
        message_id: MessageID,
        operation_id: ChatOperationID,
        body: ChatBody,
        committed_at: Timestamp,
        references: References | None = None,
    ) -> dict[str, Any]:
        """Send a chat message and indexes atomically; retain both IDs for retries."""
        return run(
            lambda session: conversations(session, project_id).write_chat(
                type="sent",
                message_id=message_id,
                operation_id=operation_id,
                body=body,
                references=[
                    _parse_message(item, domain.ProjectReference())
                    for item in references or []
                ],
                committed_at=_parse_message(committed_at, TimestampMessage()),
            )
        )

    @server.tool()
    def arteligo_chat_edit(
        project_id: Identifier,
        message_id: MessageID,
        operation_id: ChatOperationID,
        expected_revision: Revision,
        expected_incarnation: Identifier,
        body: ChatBody,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Edit a message authored by this account using its current content revision."""
        return run(
            lambda session: conversations(session, project_id).write_chat(
                type="edited",
                message_id=message_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                expected_incarnation=expected_incarnation,
                body=body,
                committed_at=_parse_message(committed_at, TimestampMessage()),
            )
        )

    @server.tool()
    def arteligo_chat_delete(
        project_id: Identifier,
        message_id: MessageID,
        operation_id: ChatOperationID,
        expected_revision: Revision,
        expected_incarnation: Identifier,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Delete all message revisions with a signed body-free record deletion."""
        return run(
            lambda session: conversations(session, project_id).write_chat(
                type="deleted",
                message_id=message_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                expected_incarnation=expected_incarnation,
                committed_at=_parse_message(committed_at, TimestampMessage()),
            )
        )

    @server.tool()
    def arteligo_comment_threads(
        project_id: Identifier,
        anchor: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        limit: PageLimit = 100,
    ) -> dict[str, Any]:
        """Read a verified comment page, optionally restricted to one encrypted anchor."""
        return run(
            lambda session: conversations(session, project_id).comment_threads(
                anchor=_parse_message(anchor, domain.ReviewAnchor())
                if anchor is not None
                else None,
                after=_parse_message(after, domain.CommentCursor())
                if after is not None
                else None,
                limit=limit,
            )
        )

    @server.tool()
    def arteligo_comment_thread(
        project_id: Identifier, comment_id: Identifier
    ) -> dict[str, Any]:
        """Read a current comment body, reply count and resolution without fetching replies."""
        return run(
            lambda session: {
                "comment": conversations(session, project_id).comment_thread(comment_id)
            }
        )

    @server.tool()
    def arteligo_comment_replies(
        project_id: Identifier,
        comment_id: Identifier,
        after: dict[str, Any] | None = None,
        limit: PageLimit = 100,
    ) -> dict[str, Any]:
        """Read one contiguous verified reply page and the total reply count."""
        return run(
            lambda session: conversations(session, project_id).comment_replies(
                comment_id,
                after=_parse_message(after, domain.CommentCursor())
                if after is not None
                else None,
                limit=limit,
            )
        )

    @server.tool()
    def arteligo_comment_reply(
        project_id: Identifier, reply_id: Identifier
    ) -> dict[str, Any]:
        """Read one reply and verify its membership in the signed parent index."""
        return run(
            lambda session: {
                "reply": conversations(session, project_id).comment_reply(reply_id)
            }
        )

    @server.tool()
    def arteligo_comment_create(
        project_id: Identifier,
        comment_id: Identifier,
        body: Body,
        anchor: dict[str, Any],
        created_at: Timestamp,
        display_name: str = "",
    ) -> dict[str, Any]:
        """Create an immutable comment, body head and thread index atomically."""
        return run(
            lambda session: conversations(session, project_id).create_comment(
                comment_id,
                body=body,
                anchor=_parse_message(anchor, domain.ReviewAnchor()),
                author=actor(session, display_name),
                created_at=_parse_message(created_at, TimestampMessage()),
            )
        )

    @server.tool()
    def arteligo_comment_reply_create(
        project_id: Identifier,
        reply_id: Identifier,
        comment_id: Identifier,
        body: Body,
        created_at: Timestamp,
        references: References | None = None,
        display_name: str = "",
    ) -> dict[str, Any]:
        """Create a reply and update its parent index atomically; retain the reply ID for retries."""
        return run(
            lambda session: conversations(session, project_id).create_reply(
                reply_id,
                parent_id=comment_id,
                body=body,
                references=[
                    _parse_message(item, domain.ProjectReference())
                    for item in references or []
                ],
                author=actor(session, display_name),
                created_at=_parse_message(created_at, TimestampMessage()),
            )
        )

    @server.tool()
    def arteligo_comment_edit(
        project_id: Identifier,
        comment_id: Identifier,
        operation_id: Identifier,
        expected_revision: Revision,
        body: Body,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Append a signed comment edit, preserving its immutable origin and author."""
        return run(
            lambda session: conversations(session, project_id).edit_comment(
                comment_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                body=body,
                committed_at=_parse_message(committed_at, TimestampMessage()),
            )
        )

    @server.tool()
    def arteligo_comment_reply_edit(
        project_id: Identifier,
        reply_id: Identifier,
        comment_id: Identifier,
        operation_id: Identifier,
        expected_revision: Revision,
        body: Body,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Append a signed reply edit after verifying its author and parent."""
        return run(
            lambda session: conversations(session, project_id).edit_reply(
                reply_id,
                parent_id=comment_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                body=body,
                committed_at=_parse_message(committed_at, TimestampMessage()),
            )
        )

    @server.tool()
    def arteligo_comment_resolution(
        project_id: Identifier,
        comment_id: Identifier,
        resolved: bool,
        operation_id: Identifier,
        display_name: str = "",
    ) -> dict[str, Any]:
        """Append a signed resolution event and update the comment head atomically."""
        return run(
            lambda session: conversations(session, project_id).set_resolution(
                comment_id,
                resolved=resolved,
                operation_id=operation_id,
                actor=actor(session, display_name),
            )
        )
