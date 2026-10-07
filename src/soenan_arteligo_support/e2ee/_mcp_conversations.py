from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

import anyio
from anyio import CapacityLimiter, WouldBlock
from pydantic import AfterValidator, BaseModel, Field

from ._conversation_context import MAX_INTEGER
from ._conversations import EncryptedConversations
from ._crypto import E2eeError
from ._records import EncryptedRecords

Identifier = Annotated[str, Field(min_length=1, max_length=120)]
MessageID = Annotated[str, Field(pattern=r"^cmsg_[0-9a-f]{32}$")]
ChatOperationID = Annotated[
    str, Field(min_length=16, max_length=128, pattern=r"^[!-~]+$")
]
Revision = Annotated[int, Field(ge=1, le=MAX_INTEGER)]
Position = Annotated[int, Field(ge=0, le=MAX_INTEGER)]
PageLimit = Annotated[int, Field(ge=1, le=100)]
EventLimit = Annotated[int, Field(ge=1, le=200)]
Body = Annotated[str, Field(max_length=4096)]
ChatBody = Annotated[str, Field(max_length=8000)]
References = Annotated[list[dict[str, Any]], Field(max_length=10)]


def timestamp(value):
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


Timestamp = Annotated[
    str, Field(min_length=1, max_length=64), AfterValidator(timestamp)
]


class ConversationCursor(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=65536)]
    id: Identifier

    def key(self):
        return self.name, self.id


def register_conversation_tools(server, run):
    worker = CapacityLimiter(1)

    async def invoke(operation):
        try:
            worker.acquire_nowait()
        except WouldBlock:
            from mcp.server.fastmcp.exceptions import ToolError

            raise ToolError("local_operation_busy") from None
        try:
            return await anyio.to_thread.run_sync(run, operation)
        finally:
            worker.release()

    def cursor_page(result):
        key = result["next_key"]
        return {**result, "next_key": {"name": key[0], "id": key[1]} if key else None}

    def conversations(session, project):
        return EncryptedConversations(
            EncryptedRecords(session),
            project,
            checkpoint=anyio.from_thread.check_cancelled,
        )

    def actor(session, display_name):
        return {
            "kind": "member",
            "member": {
                "membershipId": session.subject,
                "userId": session.subject,
                "displayName": display_name,
            },
        }

    def value(session, body, references, display_name, created_at, anchor=None):
        if not body.strip() and not references:
            raise E2eeError("invalid_request")
        return {
            "author": actor(session, display_name),
            "body": body,
            "references": references,
            "createdAt": created_at,
            **({"anchor": anchor} if anchor is not None else {}),
        }

    @server.tool()
    async def arteligo_chat_messages(
        project_id: Identifier,
        before_sequence: Revision | None = None,
        limit: PageLimit = 100,
    ) -> dict[str, Any]:
        """Read a verified newest-first chat page without enumerating edit history."""
        return await invoke(
            lambda session: conversations(session, project_id).chat_messages(
                before_sequence=before_sequence, limit=limit
            )
        )

    @server.tool()
    async def arteligo_chat_events(
        project_id: Identifier, after: Position = 0, limit: EventLimit = 200
    ) -> dict[str, Any]:
        """Read a bounded contiguous event page after the saved sequence."""
        return await invoke(
            lambda session: conversations(session, project_id).chat_events(
                after=after, limit=limit
            )
        )

    @server.tool()
    async def arteligo_chat_message(
        project_id: Identifier, message_id: MessageID
    ) -> dict[str, Any]:
        """Read one signed current message, including a terminal deletion proof."""
        return await invoke(
            lambda session: {
                "message": conversations(session, project_id).chat_message(message_id)
            }
        )

    @server.tool()
    async def arteligo_chat_message_history(
        project_id: Identifier, message_id: MessageID
    ) -> dict[str, Any]:
        """Explicitly verify every message revision and return the verified final event."""
        return await invoke(
            lambda session: conversations(session, project_id).chat_message_history(
                message_id
            )
        )

    @server.tool()
    async def arteligo_chat_operation(
        project_id: Identifier, operation_id: ChatOperationID
    ) -> dict[str, Any]:
        """Confirm an immutable operation after a lost response, reusing its operation ID."""
        return await invoke(
            lambda session: {
                "event": conversations(session, project_id).chat_operation(operation_id)
            }
        )

    @server.tool()
    async def arteligo_chat_send(
        project_id: Identifier,
        message_id: MessageID,
        operation_id: ChatOperationID,
        body: ChatBody,
        committed_at: Timestamp,
        references: References | None = None,
    ) -> dict[str, Any]:
        """Send a chat message and indexes atomically; retain both IDs for retries."""
        return await invoke(
            lambda session: conversations(session, project_id).write_chat(
                type="sent",
                message_id=message_id,
                operation_id=operation_id,
                body=body,
                references=references,
                committed_at=committed_at,
            )
        )

    @server.tool()
    async def arteligo_chat_edit(
        project_id: Identifier,
        message_id: MessageID,
        operation_id: ChatOperationID,
        expected_revision: Revision,
        body: ChatBody,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Edit a message authored by this account using its current content revision."""
        return await invoke(
            lambda session: conversations(session, project_id).write_chat(
                type="edited",
                message_id=message_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                body=body,
                committed_at=committed_at,
            )
        )

    @server.tool()
    async def arteligo_chat_delete(
        project_id: Identifier,
        message_id: MessageID,
        operation_id: ChatOperationID,
        expected_revision: Revision,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Append an immutable deletion event and terminal proof in the same batch."""
        return await invoke(
            lambda session: conversations(session, project_id).write_chat(
                type="deleted",
                message_id=message_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                committed_at=committed_at,
            )
        )

    @server.tool()
    async def arteligo_comment_threads(
        project_id: Identifier,
        anchor: dict[str, Any] | None = None,
        after: ConversationCursor | None = None,
        limit: PageLimit = 100,
    ) -> dict[str, Any]:
        """Read a verified comment page, optionally restricted to one encrypted anchor."""
        return await invoke(
            lambda session: cursor_page(
                conversations(session, project_id).comment_threads(
                    anchor=anchor, after=after.key() if after else None, limit=limit
                )
            )
        )

    @server.tool()
    async def arteligo_comment_thread(
        project_id: Identifier, comment_id: Identifier
    ) -> dict[str, Any]:
        """Read a current comment body, reply count and resolution without fetching replies."""
        return await invoke(
            lambda session: {
                "comment": conversations(session, project_id).comment_thread(comment_id)
            }
        )

    @server.tool()
    async def arteligo_comment_replies(
        project_id: Identifier,
        comment_id: Identifier,
        after: ConversationCursor | None = None,
        limit: PageLimit = 100,
    ) -> dict[str, Any]:
        """Read one contiguous verified reply page and the total reply count."""
        return await invoke(
            lambda session: cursor_page(
                conversations(session, project_id).comment_replies(
                    comment_id, after=after.key() if after else None, limit=limit
                )
            )
        )

    @server.tool()
    async def arteligo_comment_reply(
        project_id: Identifier, reply_id: Identifier
    ) -> dict[str, Any]:
        """Read one reply and verify its membership in the signed parent index."""
        return await invoke(
            lambda session: {
                "reply": conversations(session, project_id).comment_reply(reply_id)
            }
        )

    @server.tool()
    async def arteligo_comment_create(
        project_id: Identifier,
        comment_id: Identifier,
        body: Body,
        anchor: dict[str, Any],
        created_at: Timestamp,
        display_name: str = "",
    ) -> dict[str, Any]:
        """Create an immutable comment, body head and thread index atomically."""
        return await invoke(
            lambda session: conversations(session, project_id).create_comment(
                comment_id, value(session, body, [], display_name, created_at, anchor)
            )
        )

    @server.tool()
    async def arteligo_comment_reply_create(
        project_id: Identifier,
        reply_id: Identifier,
        comment_id: Identifier,
        body: Body,
        created_at: Timestamp,
        references: References | None = None,
        display_name: str = "",
    ) -> dict[str, Any]:
        """Create a reply and update its parent index atomically; retain the reply ID for retries."""
        return await invoke(
            lambda session: conversations(session, project_id).create_reply(
                reply_id,
                parent_id=comment_id,
                value=value(session, body, references or [], display_name, created_at),
            )
        )

    @server.tool()
    async def arteligo_comment_edit(
        project_id: Identifier,
        comment_id: Identifier,
        operation_id: Identifier,
        expected_revision: Revision,
        body: Body,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Append a signed comment edit, preserving its immutable origin and author."""
        return await invoke(
            lambda session: conversations(session, project_id).edit_comment(
                comment_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                body=body,
                committed_at=committed_at,
            )
        )

    @server.tool()
    async def arteligo_comment_reply_edit(
        project_id: Identifier,
        reply_id: Identifier,
        comment_id: Identifier,
        operation_id: Identifier,
        expected_revision: Revision,
        body: Body,
        committed_at: Timestamp,
    ) -> dict[str, Any]:
        """Append a signed reply edit after verifying its author and parent."""
        return await invoke(
            lambda session: conversations(session, project_id).edit_reply(
                reply_id,
                parent_id=comment_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                body=body,
                committed_at=committed_at,
            )
        )

    @server.tool()
    async def arteligo_comment_resolution(
        project_id: Identifier,
        comment_id: Identifier,
        resolved: bool,
        operation_id: Identifier,
        display_name: str = "",
    ) -> dict[str, Any]:
        """Append a signed resolution event and update the comment head atomically."""
        return await invoke(
            lambda session: conversations(session, project_id).set_resolution(
                comment_id,
                resolved=resolved,
                operation_id=operation_id,
                actor=actor(session, display_name),
            )
        )
