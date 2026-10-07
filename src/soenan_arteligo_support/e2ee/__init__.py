"""Trusted local Arteligo client; secret material never crosses the MCP boundary."""

from ._client import open_session
from ._conversations import EncryptedConversations
from ._crypto import E2eeCrypto, E2eeError
from ._directory import EncryptedDirectory
from ._directory_migration import abort_directory_migration, migrate_directory
from ._records import EncryptedRecords
from ._session import DeviceSession
from ._storage import SecureStore, SystemSecureStore

__all__ = [
    "DeviceSession",
    "E2eeCrypto",
    "E2eeError",
    "EncryptedConversations",
    "EncryptedDirectory",
    "EncryptedRecords",
    "SecureStore",
    "SystemSecureStore",
    "abort_directory_migration",
    "migrate_directory",
    "open_session",
]
