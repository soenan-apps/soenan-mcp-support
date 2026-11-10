# Generated from RecordContent record_kind options; do not modify.
_BODY_KINDS: dict[str, frozenset[str]] = {
    "project": frozenset(("project",)),
    "stage": frozenset(("stage",)),
    "comment_origin": frozenset(("comment",)),
    "reply_origin": frozenset(("comment",)),
    "thread_head": frozenset(("comment",)),
    "text_head": frozenset(("comment",)),
    "text_revision": frozenset(("comment",)),
    "resolution": frozenset(("comment",)),
    "directory_folder": frozenset(("directory",)),
    "directory_file": frozenset(("directory",)),
    "directory_leaf": frozenset(("directory",)),
    "index_branch": frozenset(("directory", "chat")),
    "index_leaf": frozenset(("directory", "chat")),
    "directory_operations": frozenset(("directory",)),
    "directory_deletion": frozenset(("directory",)),
    "directory_deletion_stack": frozenset(("directory",)),
    "chat_header": frozenset(("chat",)),
    "chat_origin": frozenset(("chat",)),
    "chat_event": frozenset(("chat",)),
    "chat_message_head": frozenset(("chat",)),
    "chat_operation": frozenset(("chat",)),
    "chat_terminal": frozenset(("chat",)),
    "schedule": frozenset(("schedule",)),
    "file_metadata": frozenset(("file_metadata",)),
    "file_upload": frozenset(("file_upload",)),
    "preview_upload": frozenset(("file_preview_upload",)),
}
RECORD_KINDS = frozenset(kind for kinds in _BODY_KINDS.values() for kind in kinds)


def record_body_allows_kind(body: str, kind: str) -> bool:
    return body in _BODY_KINDS and kind in _BODY_KINDS[body]
