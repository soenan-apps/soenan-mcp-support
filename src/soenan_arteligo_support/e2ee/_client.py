from __future__ import annotations

from ._api import GeneratedAPI
from ._crypto import E2eeCrypto, E2eeError
from ._oauth import OAuthSession
from ._session import DeviceSession
from ._storage import SecureStore, SystemSecureStore


def open_session(
    *,
    account_origin: str,
    arteligo_origin: str,
    profile: str = "default",
    store: SecureStore | None = None,
) -> DeviceSession:
    protected = store or SystemSecureStore(profile)
    oauth = OAuthSession(
        account_origin=account_origin, arteligo_origin=arteligo_origin, store=protected
    )
    api = GeneratedAPI(oauth)
    response = api.call("getProductSession")
    if (
        response.get("kind") != "authenticated"
        or response.get("authenticated") is not True
    ):
        raise E2eeError("authentication_or_terms_required")
    subject = response.get("user", {}).get("id")
    if not isinstance(subject, str) or not subject:
        raise E2eeError("invalid_account_session")
    session = DeviceSession(
        api, E2eeCrypto(), protected, origin=oauth.arteligo_origin, subject=subject
    )
    session.refresh()
    return session
