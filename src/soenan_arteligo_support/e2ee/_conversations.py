"""Bounded local decryption and signed operations over generated domain messages."""

from ._conversation_archive import ArchiveOperations


class EncryptedConversations(ArchiveOperations):
    """Use one project scope, keep no plaintext cache, and stop at each checkpoint.

    Writers commit origins, heads, indexes and operation proofs in one CAS batch.
    Missing headers require a coordinated client update or explicit local reset.
    """
