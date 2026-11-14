"""Trusted local Arteligo client; secret material never crosses the MCP boundary."""

from ._client import open_session
from ._conversations import EncryptedConversations
from ._core import CryptoCore
from ._crypto import E2eeError
from ._directory import EncryptedDirectory
from ._file_profile_store import FileProfileStore
from ._invitations import (
    approve_invitation,
    confirm_project_owner,
    create_invitation,
    request_invitation,
    revoke_invitation,
)
from ._records import EncryptedRecords
from ._session import DeviceSession
from ._signed_commands import AcceptedCommand
from ._storage import CredentialItem, ProfileStore

__all__ = [
    "AcceptedCommand",
    "CredentialItem",
    "CryptoCore",
    "DeviceSession",
    "E2eeError",
    "EncryptedConversations",
    "EncryptedDirectory",
    "EncryptedRecords",
    "FileProfileStore",
    "ProfileStore",
    "approve_invitation",
    "confirm_project_owner",
    "create_invitation",
    "open_session",
    "request_invitation",
    "revoke_invitation",
]
