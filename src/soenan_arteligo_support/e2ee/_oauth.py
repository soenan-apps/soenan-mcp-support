from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import secrets
import threading
import time
from typing import Any, Callable, Protocol
from urllib.parse import parse_qs, urlencode, urlsplit
import webbrowser

import httpx

from ._crypto import E2eeError, encode
from ._storage import CredentialItem, ProfileSecureStore

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
    def arteligo_origin(self) -> str: ...
    def access_token(self) -> str: ...
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

    @classmethod
    def parse(cls, value: Any) -> TokenPair:
        if not isinstance(value, dict) or set(value) != set(cls.__dataclass_fields__):
            raise E2eeError("invalid_token_response")
        if (
            any(type(value[field]) is not str or not value[field] for field in ("access_token", "refresh_token"))
            or value["token_type"] != "Bearer"
            or value["scope"] != "arteligo:app"
            or any(type(value[field]) is not int for field in ("expires_in", "access_expires_at", "refresh_expires_at"))
            or not 1 <= value["expires_in"] <= 300
            or not 1 <= value["access_expires_at"] <= 2**63 - 1
            or not 1 <= value["refresh_expires_at"] <= 2**63 - 1
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
class CredentialRecord:
    identity: str
    login_intent: str | None
    state: CredentialState

    def serialize(self) -> str:
        return json.dumps({
            "version": 2,
            "identity": self.identity,
            "login_intent": self.login_intent,
            "state": {"kind": type(self.state).__name__, **asdict(self.state)},
        }, separators=(",", ":"))

    @classmethod
    def parse(cls, value: Any) -> CredentialRecord:
        if (
            not isinstance(value, dict)
            or set(value) != {"version", "identity", "login_intent", "state"}
            or type(value["version"]) is not int
            or value["version"] != 2
            or type(value["identity"]) is not str
            or not value["identity"]
            or (value["login_intent"] is not None and (type(value["login_intent"]) is not str or not value["login_intent"]))
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
        elif kind == "AccessOnly" and set(raw) == {"kind", "access_token", "access_expires_at", "revoke_proof"}:
            if (
                type(raw["access_token"]) is not str or not raw["access_token"]
                or type(raw["revoke_proof"]) is not str or not raw["revoke_proof"]
                or type(raw["access_expires_at"]) is not int
                or not 1 <= raw["access_expires_at"] <= 2**63 - 1
            ):
                raise E2eeError("credential_state_invalid")
            state = AccessOnly(raw["access_token"], raw["access_expires_at"], raw["revoke_proof"])
        elif kind in {"RefreshUncertain", "RevokePending"} and set(raw) == {"kind", "revoke_proof"} and type(raw["revoke_proof"]) is str and raw["revoke_proof"]:
            state = RefreshUncertain(raw["revoke_proof"]) if kind == "RefreshUncertain" else RevokePending(raw["revoke_proof"])
        else:
            raise E2eeError("credential_state_invalid")
        return cls(value["identity"], value["login_intent"], state)


@dataclass(frozen=True)
class ProfileContext:
    vault: ProfileVault
    identity: str

    @property
    def arteligo_origin(self) -> str:
        return self.vault.arteligo_origin

    def access_token(self) -> str:
        return self.vault._access_token(self.identity)

    def check_current(self) -> None:
        with self.vault.store.credential(self.vault._storage_key) as item:
            self.vault._check(self.vault._load(item), self.identity)


@dataclass(frozen=True)
class LogoutOutcome:
    known_family_revoked: bool


@dataclass(frozen=True, init=False)
class ProfileVault:
    account_origin: str
    arteligo_origin: str
    resource: str
    store: ProfileSecureStore
    _storage_key: str
    _transport: httpx.BaseTransport | None

    def __init__(self, *, account_origin: str, arteligo_origin: str, store: ProfileSecureStore, transport: httpx.BaseTransport | None = None):
        if not callable(getattr(store, "credential", None)):
            raise E2eeError("unsupported_secure_store")
        account = origin(account_origin)
        arteligo = origin(arteligo_origin)
        resource = arteligo + "/api"
        for name, value in {
            "account_origin": account, "arteligo_origin": arteligo,
            "resource": resource, "store": store, "_transport": transport,
            "_storage_key": "oauth:" + hashlib.sha256((account + "\n" + resource).encode()).hexdigest(),
        }.items():
            object.__setattr__(self, name, value)

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
            if isinstance(value, dict) and "version" not in value:
                pair = TokenPair.parse(value)
                record = CredentialRecord(secrets.token_urlsafe(32), None, AccessOnly(
                    pair.access_token, pair.access_expires_at, pair.refresh_token,
                ))
                self._save(item, record)
                return record
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
            with httpx.Client(timeout=30, follow_redirects=False, transport=self._transport) as client:
                response = client.post(self.account_origin + "/oauth/token", data={
                    "client_id": CLIENT_ID, "resource": self.resource, **body,
                })
            if response.status_code == 400:
                try:
                    rejected = response.json()
                except ValueError:
                    raise E2eeError("authentication_uncertain") from None
                if isinstance(rejected, dict) and rejected.get("error") == "invalid_grant":
                    raise E2eeError("authentication_required")
            if response.status_code != 200:
                raise E2eeError("authentication_uncertain")
            try:
                return TokenPair.parse(response.json())
            except ValueError:
                raise E2eeError("invalid_token_response") from None
        except httpx.HTTPError:
            raise E2eeError("authentication_uncertain") from None

    def _access_token(self, identity: str) -> str:
        with self.store.credential(self._storage_key) as item:
            record = self._load(item)
            self._check(record, identity)
            state = record.state
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
            pair = self._token({"grant_type": "refresh_token", "refresh_token": state.pair.refresh_token})
            self._save(item, replace(record, state=Ready(pair)))
            return pair.access_token

    def login(self, *, open_browser: Callable[[str], Any] = webbrowser.open, timeout: float = 300) -> None:
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
            def log_message(self, *_args: Any) -> None:
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
                    and self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"
                )
                self.send_response(200 if valid else 400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                if valid:
                    received["code"] = query["code"][0]
                    completed.set()
                self.wfile.write(("認証できました。この画面を閉じてください。" if valid else "認証を確認できませんでした。").encode())

        server = HTTPServer(("127.0.0.1", 0), Callback)
        redirect = f"http://127.0.0.1:{server.server_port}/oauth/callback"
        url = self.account_origin + "/oauth/authorize?" + urlencode({
            "response_type": "code", "client_id": CLIENT_ID,
            "redirect_uri": redirect, "resource": self.resource,
            "scope": "arteligo:app", "state": state,
            "code_challenge": encode(hashlib.sha256(verifier.encode()).digest()),
            "code_challenge_method": "S256",
        })
        worker = threading.Thread(target=server.serve_forever, daemon=True)
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
                try:
                    pair = self._token({
                        "grant_type": "authorization_code", "code": received.pop("code"),
                        "redirect_uri": redirect, "code_verifier": verifier,
                    })
                    self._save(item, CredentialRecord(
                        secrets.token_urlsafe(32), None, Ready(pair),
                    ))
                except E2eeError as error:
                    if error.code == "authentication_required":
                        raise
                    raise E2eeError("authentication_login_uncertain") from None
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
            received.clear()
            with self.store.credential(self._storage_key) as item:
                current = self._load(item)
                if current.login_intent == intent:
                    self._save(item, replace(current, login_intent=None))

    def logout(self) -> LogoutOutcome:
        with self.store.credential(self._storage_key) as item:
            record = self._load(item)
            state = record.state
            if isinstance(state, SignedOut):
                self._save(item, replace(record, identity=secrets.token_urlsafe(32), login_intent=None))
                return LogoutOutcome(False)
            proof = state.pair.refresh_token if isinstance(state, Ready) else state.revoke_proof
            pending = record if isinstance(state, RevokePending) else replace(
                record, identity=secrets.token_urlsafe(32), login_intent=None, state=RevokePending(proof),
            )
            self._save(item, pending)
            if self._load(item) != pending:
                raise E2eeError("secure_store_unavailable")
            try:
                with httpx.Client(timeout=30, follow_redirects=False, transport=self._transport) as client:
                    response = client.post(self.account_origin + "/oauth/revoke", data={
                        "client_id": CLIENT_ID, "resource": self.resource, "token": proof,
                    })
                if response.status_code != 200:
                    raise E2eeError("logout_incomplete")
            except httpx.HTTPError:
                raise E2eeError("logout_incomplete") from None
            self._save(item, replace(pending, state=SignedOut()))
            return LogoutOutcome(True)
