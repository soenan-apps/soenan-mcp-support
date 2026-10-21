"""Trusted local Arteligo client; secret material never crosses the MCP boundary."""

from ._client import open_session
from ._conversations import EncryptedConversations
from ._crypto import E2eeCrypto, E2eeError
from ._directory import EncryptedDirectory
from ._records import EncryptedRecords
from ._session import DeviceSession
from ._storage import CredentialItem, ProfileSecureStore, SecureStore, SystemSecureStore

__all__ = [
    "CredentialItem",
    "ProfileSecureStore",
    "DeviceSession",
    "E2eeCrypto",
    "E2eeError",
    "EncryptedConversations",
    "EncryptedDirectory",
    "EncryptedRecords",
    "SecureStore",
    "SystemSecureStore",
    "open_session",
]
