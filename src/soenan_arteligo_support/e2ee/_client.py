from __future__ import annotations

from ._api import GeneratedAPI
from ._oauth import ProfileVault
from ._session import DeviceSession
from ._storage import ProfileSecureStore, SystemSecureStore


def open_session(
    *,
    account_origin: str,
    arteligo_origin: str,
    profile: str = "default",
    store: ProfileSecureStore | None = None,
) -> DeviceSession:
    protected = store or SystemSecureStore(profile)
    vault = ProfileVault(
        account_origin=account_origin, arteligo_origin=arteligo_origin, store=protected
    )
    credentials = vault.bind()
    api = GeneratedAPI(credentials)
    subject = credentials.subject()
    session = DeviceSession(
        api, protected, origin=credentials.arteligo_origin, subject=subject
    )
    try:
        settings = session.settings()
        if session.device_id:
            session.open_bundle(settings.bundle)
        return session
    except BaseException:
        session.lock()
        raise
