"""Trusted local Arteligo client; secret material never crosses the MCP boundary."""

from ._admission import AdmissionResult
from ._client import open_session
from ._conversations import EncryptedConversations
from ._crypto import E2eeCrypto, E2eeError
from ._directory import EncryptedDirectory
from ._owner_access import OwnerAccess, OwnerAuthorityHead
from ._records import EncryptedRecords
from ._session import DeviceSession
from ._storage import CredentialItem, ProfileSecureStore, SecureStore, SystemSecureStore

__all__ = [
    "AdmissionResult",
    "CredentialItem",
    "ProfileSecureStore",
    "DeviceSession",
    "E2eeCrypto",
    "E2eeError",
    "EncryptedConversations",
    "EncryptedDirectory",
    "EncryptedRecords",
    "OwnerAccess",
    "OwnerAuthorityHead",
    "SecureStore",
    "SystemSecureStore",
    "open_session",
]
