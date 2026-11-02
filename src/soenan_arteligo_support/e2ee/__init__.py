"""Trusted local Arteligo client; secret material never crosses the MCP boundary."""

from ._client import open_session
from ._conversations import EncryptedConversations
from ._core import CryptoCore
from ._crypto import E2eeError
from ._directory import EncryptedDirectory
from ._invitations import approve_invitation, confirm_project_owner, create_invitation, request_invitation, revoke_invitation
from ._records import EncryptedRecords
from ._session import DeviceSession
from ._signed_commands import AcceptedCommand
from ._storage import CredentialItem, ProfileSecureStore, SecureStore, SystemSecureStore

__all__ = [
    "AcceptedCommand",
    "CredentialItem",
    "ProfileSecureStore",
    "DeviceSession",
    "CryptoCore",
    "E2eeError",
    "EncryptedConversations",
    "EncryptedDirectory",
    "EncryptedRecords",
    "SecureStore",
    "SystemSecureStore",
    "open_session",
    "approve_invitation",
    "confirm_project_owner",
    "create_invitation",
    "request_invitation",
    "revoke_invitation",
]
