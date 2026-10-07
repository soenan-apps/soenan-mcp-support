"""Bounded local decryption and signed conversation operations for format 3."""

from ._conversation_archive import ArchiveOperations
from ._conversation_chat import ChatOperations
from ._conversation_comments import CommentOperations
from ._conversation_context import ConversationContext
from ._conversation_text import TextOperations


class EncryptedConversations(
    ChatOperations,
    CommentOperations,
    TextOperations,
    ArchiveOperations,
    ConversationContext,
):
    """Use one project scope, keep no plaintext cache, and stop at each checkpoint.

    Writers commit origins, heads, indexes and operation proofs in one CAS batch.
    Missing format-3 headers require a coordinated client update or explicit local reset.
    """
