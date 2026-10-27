from __future__ import annotations

from ._api import GeneratedAPI
from ._crypto import E2eeCrypto, E2eeError
from ._oauth import ProfileVault
from ._session import DeviceSession
from ._storage import ProfileSecureStore, SystemSecureStore


def open_session(
    *,
    account_origin: str,
    arteligo_origin: str,
    profile: str = "default",
    store: ProfileSecureStore | None = None,
    recover: bool = False,
    maintain_owner_access: bool = True,
) -> DeviceSession:
    protected = store or SystemSecureStore(profile)
    vault = ProfileVault(
        account_origin=account_origin, arteligo_origin=arteligo_origin, store=protected
    )
    credentials = vault.bind()
    api = GeneratedAPI(credentials)
    response = api.call("getProductSession")
    if (
        response.get("kind") != "authenticated"
        or response.get("authenticated") is not True
    ):
        raise E2eeError("authentication_or_terms_required")
    subject = response.get("user", {}).get("id")
    if not isinstance(subject, str) or not subject:
        raise E2eeError("invalid_account_session")
    credentials.check_current()
    session = DeviceSession(
        api, E2eeCrypto(), protected, origin=credentials.arteligo_origin,
        subject=subject,
    )
    try:
        session.refresh()
    except E2eeError as error:
        if not recover or error.code not in {"untrusted_device", "untrusted_recovery"}:
            session.lock()
            raise
        session.state = "pending_approval"
    except BaseException:
        session.lock()
        raise
    if maintain_owner_access and session.state == "approved" and not session.recovery_replacement_pending:
        try:
            session.owner_access.maintain()
        except BaseException:
            session.lock()
            raise
    return session
