from __future__ import annotations

from soenan_account_identity_client import IdentitySession

from ._api import GeneratedAPI
from ._file_profile_store import FileProfileStore
from ._oauth import ProfileVault
from ._session import DeviceSession
from ._storage import ProfileStore


def open_session(
    *,
    account_origin: str,
    arteligo_origin: str,
    profile: str = "default",
    store: ProfileStore | None = None,
) -> DeviceSession:
    if store is None:
        store = FileProfileStore(profile=profile)
    vault = ProfileVault(
        account_origin=account_origin, arteligo_origin=arteligo_origin, store=store
    )
    credentials = vault.bind()
    api = GeneratedAPI(credentials)
    subject = credentials.subject()
    identity = IdentitySession(
        store,
        origin=credentials.account_origin,
        subject=subject,
        credentials=vault.identity_bind(),
    )
    session = DeviceSession(
        api,
        store,
        origin=credentials.arteligo_origin,
        subject=subject,
        identity=identity,
    )
    try:
        if identity.state == "pending_approval":
            identity.synchronize()
        return session
    except BaseException:
        session.lock()
        raise
