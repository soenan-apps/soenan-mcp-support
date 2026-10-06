"""Trusted local Arteligo client; secret material never crosses the MCP boundary."""

from ._client import open_session
from ._crypto import E2eeCrypto, E2eeError
from ._records import EncryptedRecords
from ._directory import EncryptedDirectory
from ._directory_migration import abort_directory_migration, migrate_directory
from ._session import DeviceSession
from ._storage import SecureStore, SystemSecureStore

__all__ = [
    "DeviceSession",
    "E2eeCrypto",
    "E2eeError",
    "EncryptedRecords",
    "EncryptedDirectory",
    "migrate_directory",
    "abort_directory_migration",
    "SecureStore",
    "SystemSecureStore",
    "open_session",
]
