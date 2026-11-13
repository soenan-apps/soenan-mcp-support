from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
import webbrowser
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING, Any, Protocol
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx

from ._crypto import E2eeError, encode
from ._file_profile_store import FileProfileStore
from ._storage import CredentialItem, ProfileStore

if TYPE_CHECKING:
    from account_public_api_client.models.o_auth_device_authorization_response import (
        OAuthDeviceAuthorizationResponse,
    )
    from soenan.account.identity.v1 import identity_pb2 as identity

CLIENT_ID = "arteligo-native-cli"


def origin(raw: str) -> str:
    parsed = urlsplit(raw)
    if (
        parsed.scheme not in {"https", "http"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
        or (
            parsed.scheme == "http"
            and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
        )
    ):
        raise E2eeError("invalid_origin")
    return f"{parsed.scheme}://{parsed.netloc}"


class BoundCredentials(Protocol):
    @property
    def account_origin(self) -> str: ...
    @property
    def arteligo_origin(self) -> str: ...
    def access_token(self) -> str: ...
    def subject(self) -> str: ...
    def check_current(self) -> None: ...


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str
    scope: str
    expires_in: int
    access_expires_at: int
    refresh_expires_at: int
    subject: str
    environment_authorization_id: str | None = None
    environment_authorization_expires_at: int | None = None

    @classmethod
    def parse(cls, value: Any) -> TokenPair:
        required = {
            "access_token",
            "refresh_token",
            "token_type",
            "scope",
            "expires_in",
            "access_expires_at",
            "refresh_expires_at",
            "subject",
        }
        cloud = {
            "environment_authorization_id",
            "environment_authorization_expires_at",
        }
        if not isinstance(value, dict) or set(value) not in (
            required,
            required | cloud,
        ):
            raise E2eeError("invalid_token_response")
        if (
            any(
                type(value[field]) is not str or not value[field]
                for field in ("access_token", "refresh_token", "subject")
            )
            or value["token_type"] != "Bearer"
            or type(value["scope"]) is not str
            or value["scope"]
            not in {"arteligo:app", "account:keys:manage account:keys:receive"}
            or any(
                type(value[field]) is not int
                for field in ("expires_in", "access_expires_at", "refresh_expires_at")
            )
            or not 1 <= value["expires_in"] <= 300
            or not 1 <= value["access_expires_at"] <= 2**63 - 1
            or not 1 <= value["refresh_expires_at"] <= 2**63 - 1
        ):
            raise E2eeError("invalid_token_response")
        if cloud <= set(value) and any(value[key] is not None for key in cloud):
            if (
                type(value["environment_authorization_id"]) is not str
                or not value["environment_authorization_id"]
                or type(value["environment_authorization_expires_at"]) is not int
                or not value["access_expires_at"]
                <= value["environment_authorization_expires_at"]
                or not value["refresh_expires_at"]
                <= value["environment_authorization_expires_at"]
            ):
                raise E2eeError("invalid_token_response")
        return cls(**value)


@dataclass(frozen=True)
class SignedOut:
    pass


@dataclass(frozen=True)
class Ready:
    pair: TokenPair


@dataclass(frozen=True)
class AccessOnly:
    access_token: str
    access_expires_at: int
    revoke_proof: str


@dataclass(frozen=True)
class RefreshUncertain:
    revoke_proof: str


@dataclass(frozen=True)
class RevokePending:
    revoke_proof: str


CredentialState = SignedOut | Ready | AccessOnly | RefreshUncertain | RevokePending


@dataclass(frozen=True)
class EnvironmentAuthorization:
    authorization_id: str
    subject: str
    scope: str
    expires_at: int

    @classmethod
    def parse(cls, value: Any) -> EnvironmentAuthorization:
        if (
            not isinstance(value, dict)
            or set(value) != {"authorization_id", "subject", "scope", "expires_at"}
            or any(
                type(value[key]) is not str or not value[key]
                for key in ("authorization_id", "subject", "scope")
            )
            or type(value["expires_at"]) is not int
            or not 1 <= value["expires_at"] <= 2**63 - 1
        ):
            raise E2eeError("credential_state_invalid")
        return cls(**value)


@dataclass(frozen=True)
class CredentialRecord:
    identity: str
    login_intent: str | None
    state: CredentialState
    environment: EnvironmentAuthorization | None = None

    def serialize(self) -> str:
        return json.dumps(
            {
                "version": 3,
                "identity": self.identity,
                "login_intent": self.login_intent,
                "state": {"kind": type(self.state).__name__, **asdict(self.state)},
                "environment": asdict(self.environment)
                if self.environment is not None
                else None,
            },
            separators=(",", ":"),
        )

    @classmethod
    def parse(cls, value: Any) -> CredentialRecord:
        if (
            not isinstance(value, dict)
            or set(value)
            != {"version", "identity", "login_intent", "state", "environment"}
            or type(value["version"]) is not int
            or value["version"] != 3
            or type(value["identity"]) is not str
            or not value["identity"]
            or (
                value["login_intent"] is not None
                and (
                    type(value["login_intent"]) is not str or not value["login_intent"]
                )
            )
            or not isinstance(value["state"], dict)
        ):
            raise E2eeError("credential_state_invalid")
        raw = value["state"]
        kind = raw.get("kind")
        if type(kind) is not str:
            raise E2eeError("credential_state_invalid")
        if kind == "SignedOut" and set(raw) == {"kind"}:
            state: CredentialState = SignedOut()
        elif kind == "Ready" and set(raw) == {"kind", "pair"}:
            state = Ready(TokenPair.parse(raw["pair"]))
        elif kind == "AccessOnly" and set(raw) == {
            "kind",
            "access_token",
            "access_expires_at",
            "revoke_proof",
        }:
            if (
                type(raw["access_token"]) is not str
                or not raw["access_token"]
                or type(raw["revoke_proof"]) is not str
                or not raw["revoke_proof"]
                or type(raw["access_expires_at"]) is not int
                or not 1 <= raw["access_expires_at"] <= 2**63 - 1
            ):
                raise E2eeError("credential_state_invalid")
            state = AccessOnly(
                raw["access_token"], raw["access_expires_at"], raw["revoke_proof"]
            )
        elif (
            kind in {"RefreshUncertain", "RevokePending"}
            and set(raw) == {"kind", "revoke_proof"}
            and type(raw["revoke_proof"]) is str
            and raw["revoke_proof"]
        ):
            state = (
                RefreshUncertain(raw["revoke_proof"])
                if kind == "RefreshUncertain"
                else RevokePending(raw["revoke_proof"])
            )
        else:
            raise E2eeError("credential_state_invalid")
        environment = (
            EnvironmentAuthorization.parse(value["environment"])
            if value["environment"] is not None
            else None
        )
        if isinstance(state, Ready):
            pair = state.pair
            expected = (
                EnvironmentAuthorization(
                    pair.environment_authorization_id,
                    pair.subject,
                    pair.scope,
                    pair.environment_authorization_expires_at,
                )
                if pair.environment_authorization_id is not None
                and pair.environment_authorization_expires_at is not None
                else None
            )
            if environment != expected:
                raise E2eeError("credential_state_invalid")
        return cls(value["identity"], value["login_intent"], state, environment)


@dataclass(frozen=True)
class ProfileContext:
    vault: ProfileVault
    identity: str

    @property
    def account_origin(self) -> str:
        return self.vault.account_origin

    @property
    def arteligo_origin(self) -> str:
        return self.vault.arteligo_origin

    def access_token(self) -> str:
        return self.vault._access_token(self.identity)

    def subject(self) -> str:
        from ._api import initialize_session_authorization

        with self.vault.store.credential(self.vault._storage_key) as item:
            record = self.vault._load(item)
            self.vault._check(record, self.identity)
            if isinstance(record.state, Ready):
                return record.state.pair.subject
        if self.vault.profile == "account-keys":
            return (
                ProfileVault(
                    account_origin=self.account_origin,
                    arteligo_origin=self.arteligo_origin,
                    store=self.vault.store,
                    transport=self.vault._transport,
                )
                .bind()
                .subject()
            )

        authorization = initialize_session_authorization(
            self.arteligo_origin,
            self.access_token(),
            self.vault._transport,
            organization_ids=[],
            project_ids=[],
        )
        self.check_current()
        return authorization.subject

    def check_current(self) -> None:
        with self.vault.store.credential(self.vault._storage_key) as item:
            self.vault._check(self.vault._load(item), self.identity)

    def account_access_token(self) -> str:
        return self.vault.identity_bind().access_token()


@dataclass(frozen=True)
class LogoutOutcome:
    known_family_revoked: bool


@dataclass(frozen=True, init=False)
class ProfileVault:
    account_origin: str
    arteligo_origin: str
    resource: str
    store: ProfileStore
    _storage_key: str
    _transport: httpx.BaseTransport | None
    profile: str
    client_id: str
    scope: str

    def __init__(
        self,
        *,
        account_origin: str,
        arteligo_origin: str,
        store: ProfileStore | None = None,
        transport: httpx.BaseTransport | None = None,
        profile: str = "arteligo",
    ):
        if store is None:
            store = FileProfileStore()
        if not callable(getattr(store, "credential", None)):
            raise E2eeError("unsupported_profile_store")
        account = origin(account_origin)
        arteligo = origin(arteligo_origin)
        if profile not in {"arteligo", "account-keys"}:
            raise E2eeError("invalid_oauth_profile")
        resource = (
            account + "/api/identity"
            if profile == "account-keys"
            else arteligo + "/api"
        )
        for name, value in {
            "account_origin": account,
            "arteligo_origin": arteligo,
            "resource": resource,
            "store": store,
            "profile": profile,
            "client_id": "account-keys-native-cli"
            if profile == "account-keys"
            else CLIENT_ID,
            "scope": "account:keys:manage account:keys:receive"
            if profile == "account-keys"
            else "arteligo:app",
            "_transport": transport,
            "_storage_key": "oauth:"
            + hashlib.sha256((account + "\n" + resource).encode()).hexdigest(),
        }.items():
            object.__setattr__(self, name, value)

    def identity_vault(self) -> ProfileVault:
        if self.profile == "account-keys":
            return self
        return ProfileVault(
            account_origin=self.account_origin,
            arteligo_origin=self.arteligo_origin,
            store=self.store,
            transport=self._transport,
            profile="account-keys",
        )

    def identity_bind(self) -> ProfileContext:
        return self.identity_vault().bind()

    def environment_authorization(self) -> EnvironmentAuthorization | None:
        with self.store.credential(self._storage_key) as item:
            record = self._load(item)
            if isinstance(record.state, SignedOut):
                return None
            if isinstance(record.state, RevokePending):
                raise E2eeError("logout_incomplete")
            if isinstance(record.state, RefreshUncertain):
                raise E2eeError("authentication_refresh_uncertain")
            if (
                record.environment is not None
                and record.environment.expires_at <= time.time()
            ):
                raise E2eeError("environment_authorization_expired")
            return record.environment

    def login_device(
        self,
        *,
        subject: str,
        authorization_expires_at: int,
        on_verification: Callable[[OAuthDeviceAuthorizationResponse], Any],
        timeout: float = 600,
    ) -> identity.CloudApprovalBinding:
        from ._device_oauth import login_device

        return login_device(
            self,
            subject=subject,
            authorization_expires_at=authorization_expires_at,
            on_verification=on_verification,
            timeout=timeout,
        )

    @staticmethod
    def _save(item: CredentialItem, record: CredentialRecord) -> None:
        raw = record.serialize()
        item.replace(raw)
        if item.read() != raw:
            raise E2eeError("secure_store_unavailable")

    def _load(self, item: CredentialItem) -> CredentialRecord:
        raw = item.read()
        if raw is None:
            record = CredentialRecord(secrets.token_urlsafe(32), None, SignedOut())
            self._save(item, record)
            return record
        try:
            value = json.loads(raw)
            return CredentialRecord.parse(value)
        except (ValueError, TypeError, KeyError):
            raise E2eeError("credential_state_invalid") from None

    @staticmethod
    def _check(record: CredentialRecord, identity: str) -> None:
        if record.identity != identity:
            raise E2eeError("authentication_superseded")

    def bind(self) -> ProfileContext:
        with self.store.credential(self._storage_key) as item:
            record = self._load(item)
            if isinstance(record.state, SignedOut):
                raise E2eeError("authentication_required")
            if isinstance(record.state, RevokePending):
                raise E2eeError("logout_incomplete")
            return ProfileContext(self, record.identity)

    def _token(self, body: dict[str, str]) -> TokenPair:
        try:
            with httpx.Client(
                timeout=30, follow_redirects=False, transport=self._transport
            ) as client:
                response = client.post(
                    self.account_origin + "/oauth/token",
                    data={
                        "client_id": self.client_id,
                        "resource": self.resource,
                        **body,
                    },
                )
            if response.status_code == 400:
                try:
                    rejected = response.json()
                except ValueError:
                    raise E2eeError("authentication_uncertain") from None
                if (
                    isinstance(rejected, dict)
                    and rejected.get("error") == "invalid_grant"
                ):
                    raise E2eeError("authentication_required")
            if response.status_code != 200:
                raise E2eeError("authentication_uncertain")
            try:
                pair = TokenPair.parse(response.json())
                if pair.scope != self.scope:
                    raise E2eeError("invalid_token_response")
                return pair
            except ValueError:
                raise E2eeError("invalid_token_response") from None
        except httpx.HTTPError:
            raise E2eeError("authentication_uncertain") from None

    def _access_token(self, identity: str) -> str:
        with self.store.credential(self._storage_key) as item:
            record = self._load(item)
            self._check(record, identity)
            state = record.state
            if (
                isinstance(state, Ready)
                and state.pair.environment_authorization_expires_at is not None
            ):
                if state.pair.environment_authorization_expires_at <= time.time():
                    raise E2eeError("environment_authorization_expired")
            if isinstance(state, RefreshUncertain):
                raise E2eeError("authentication_refresh_uncertain")
            if isinstance(state, RevokePending):
                raise E2eeError("logout_incomplete")
            if isinstance(state, SignedOut):
                raise E2eeError("authentication_required")
            if isinstance(state, AccessOnly):
                if state.access_expires_at > time.time():
                    return state.access_token
                raise E2eeError("authentication_required")
            if state.pair.access_expires_at > time.time() + 15:
                return state.pair.access_token
            if state.pair.refresh_expires_at <= time.time():
                raise E2eeError("authentication_required")
            pending = replace(record, state=RefreshUncertain(state.pair.refresh_token))
            self._save(item, pending)
            # Reload the acknowledged native item before the one-use handoff.
            if self._load(item) != pending:
                raise E2eeError("secure_store_unavailable")
            try:
                pair = self._token(
                    {
                        "grant_type": "refresh_token",
                        "refresh_token": state.pair.refresh_token,
                    }
                )
            except E2eeError as error:
                if error.code == "authentication_required":
                    self._save(item, replace(record, state=SignedOut()))
                raise
            if (
                pair.environment_authorization_id
                != state.pair.environment_authorization_id
                or pair.environment_authorization_expires_at
                != state.pair.environment_authorization_expires_at
                or pair.subject != state.pair.subject
            ):
                raise E2eeError("invalid_token_response")
            self._save(item, replace(record, state=Ready(pair)))
            return pair.access_token

    def login(
        self,
        *,
        open_browser: Callable[[str], Any] = webbrowser.open,
        timeout: float = 300,
        identity_binding: identity.CloudApprovalBinding | None = None,
    ) -> None:
        intent = secrets.token_urlsafe(32)
        with self.store.credential(self._storage_key) as item:
            record = self._load(item)
            if isinstance(record.state, RevokePending):
                raise E2eeError("logout_incomplete")
            self._save(item, replace(record, login_intent=intent))
        verifier = secrets.token_urlsafe(32)
        state = secrets.token_urlsafe(32)
        received: dict[str, str] = {}
        completed = threading.Event()
        expected_issuer = self.account_origin

        class Callback(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass

            def do_GET(self) -> None:
                parsed = urlsplit(self.path)
                query = parse_qs(parsed.query, keep_blank_values=True)
                valid = (
                    not completed.is_set()
                    and parsed.path == "/oauth/callback"
                    and query.get("state") == [state]
                    and query.get("iss") == [expected_issuer]
                    and len(query.get("code", [])) == 1
                    and bool(query["code"][0])
                    and self.headers.get("Host") == f"127.0.0.1:{server.server_port}"
                )
                self.send_response(200 if valid else 400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                if valid:
                    received["code"] = query["code"][0]
                    completed.set()
                identifier = "oauth-complete" if valid else "oauth-failed"
                message = (
                    "認証できました。この画面を閉じてください。"
                    if valid
                    else "認証を確認できませんでした。"
                )
                self.wfile.write(
                    (
                        '<!doctype html><html lang="ja"><meta charset="utf-8"><title>Arteligo</title>'
                        f'<body><main><p id="{identifier}" role="status">{message}</p></main></body></html>'
                    ).encode()
                )

        server = HTTPServer(("127.0.0.1", 0), Callback)
        redirect = f"http://127.0.0.1:{server.server_port}/oauth/callback"
        url = (
            self.account_origin
            + "/oauth/authorize?"
            + urlencode(
                {
                    "response_type": "code",
                    "client_id": self.client_id,
                    "redirect_uri": redirect,
                    "resource": self.resource,
                    "scope": self.scope,
                    "state": state,
                    "code_challenge": encode(
                        hashlib.sha256(verifier.encode()).digest()
                    ),
                    "code_challenge_method": "S256",
                    **(
                        {"identity_request_id": identity_binding.request_id}
                        if identity_binding is not None
                        else {}
                    ),
                }
            )
        )
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        intent_pending = True
        worker.start()
        try:
            if open_browser(url) is False:
                raise E2eeError("browser_unavailable")
            if not completed.wait(timeout):
                raise E2eeError("authentication_timeout")
            with self.store.credential(self._storage_key) as item:
                record = self._load(item)
                if record.login_intent != intent:
                    raise E2eeError("authentication_superseded")
                if isinstance(record.state, RevokePending):
                    raise E2eeError("logout_incomplete")
                self._save(item, replace(record, login_intent=None))
                intent_pending = False
                try:
                    pair = self._token(
                        {
                            "grant_type": "authorization_code",
                            "code": received.pop("code"),
                            "redirect_uri": redirect,
                            "code_verifier": verifier,
                        }
                    )
                    if identity_binding is not None and (
                        pair.subject != identity_binding.subject
                        or pair.scope != self.scope
                        or pair.environment_authorization_id
                        != identity_binding.request_id
                        or pair.environment_authorization_expires_at
                        != identity_binding.expires_at
                    ):
                        raise E2eeError("invalid_token_response")
                    environment = (
                        EnvironmentAuthorization(
                            pair.environment_authorization_id,
                            pair.subject,
                            pair.scope,
                            pair.environment_authorization_expires_at,
                        )
                        if pair.environment_authorization_id is not None
                        and pair.environment_authorization_expires_at is not None
                        else None
                    )
                    accepted = CredentialRecord(
                        secrets.token_urlsafe(32), None, Ready(pair), environment
                    )
                    self._save(item, accepted)
                except E2eeError as error:
                    if error.code == "authentication_required":
                        raise
                    raise E2eeError("authentication_login_uncertain") from None
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
            received.clear()
            if intent_pending:
                with self.store.credential(self._storage_key) as item:
                    current = self._load(item)
                    if current.login_intent == intent:
                        self._save(item, replace(current, login_intent=None))
        self._access_token(accepted.identity)

    def logout(self) -> LogoutOutcome:
        with self.store.credential(self._storage_key) as item:
            record = self._load(item)
            state = record.state
            if isinstance(state, SignedOut):
                self._save(
                    item,
                    replace(
                        record, identity=secrets.token_urlsafe(32), login_intent=None
                    ),
                )
                return LogoutOutcome(False)
            proof = (
                state.pair.refresh_token
                if isinstance(state, Ready)
                else state.revoke_proof
            )
            pending = (
                record
                if isinstance(state, RevokePending)
                else replace(
                    record,
                    identity=secrets.token_urlsafe(32),
                    login_intent=None,
                    state=RevokePending(proof),
                )
            )
            self._save(item, pending)
            if self._load(item) != pending:
                raise E2eeError("secure_store_unavailable")
            try:
                with httpx.Client(
                    timeout=30, follow_redirects=False, transport=self._transport
                ) as client:
                    response = client.post(
                        self.account_origin + "/oauth/revoke",
                        data={
                            "client_id": self.client_id,
                            "resource": self.resource,
                            "token": proof,
                        },
                    )
                if response.status_code != 200:
                    raise E2eeError("logout_incomplete")
            except httpx.HTTPError:
                raise E2eeError("logout_incomplete") from None
            self._save(item, replace(pending, state=SignedOut()))
            return LogoutOutcome(True)
