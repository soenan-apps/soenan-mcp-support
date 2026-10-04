from __future__ import annotations

import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import secrets
import threading
import time
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode, urlsplit
import webbrowser

import httpx

from ._crypto import E2eeError, encode
from ._storage import SecureStore

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


class OAuthSession:
    def __init__(
        self,
        *,
        account_origin: str,
        arteligo_origin: str,
        store: SecureStore,
        transport: httpx.BaseTransport | None = None,
    ):
        self.account_origin = origin(account_origin)
        self.arteligo_origin = origin(arteligo_origin)
        self.resource = self.arteligo_origin + "/api"
        self.store = store
        self._storage_key = (
            "oauth:"
            + hashlib.sha256(
                (self.account_origin + "\n" + self.resource).encode()
            ).hexdigest()
        )
        self._transport = transport
        self._lock = threading.Lock()

    def _token(self, body: dict[str, str]) -> dict[str, Any]:
        try:
            with httpx.Client(
                timeout=30, follow_redirects=False, transport=self._transport
            ) as client:
                response = client.post(
                    self.account_origin + "/oauth/token",
                    data={
                        "client_id": CLIENT_ID,
                        "resource": self.resource,
                        **body,
                    },
                )
                if response.status_code != 200 or len(response.content) > 32768:
                    raise E2eeError("authentication_required")
                value = response.json()
                if (
                    value.get("token_type") != "Bearer"
                    or value.get("scope") != "arteligo:app"
                    or not isinstance(value.get("access_token"), str)
                    or not isinstance(value.get("refresh_token"), str)
                    or not isinstance(value.get("access_expires_at"), int)
                ):
                    raise E2eeError("invalid_token_response")
                self.store.write(
                    self._storage_key, json.dumps(value, separators=(",", ":"))
                )
                return value
        except (httpx.HTTPError, ValueError, KeyError):
            raise E2eeError("authentication_unavailable") from None

    def access_token(self) -> str:
        with self._lock:
            raw = self.store.read(self._storage_key)
            if raw is None:
                raise E2eeError("authentication_required")
            try:
                token = json.loads(raw)
                if token["access_expires_at"] <= time.time() + 15:
                    token = self._token(
                        {
                            "grant_type": "refresh_token",
                            "refresh_token": token["refresh_token"],
                        }
                    )
                return token["access_token"]
            except (ValueError, KeyError, TypeError):
                raise E2eeError("authentication_required") from None

    def login(
        self,
        *,
        open_browser: Callable[[str], Any] = webbrowser.open,
        timeout: float = 300,
    ) -> None:
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
                    parsed.path == "/oauth/callback"
                    and query.get("state") == [state]
                    and query.get("iss") == [expected_issuer]
                    and len(query.get("code", [])) == 1
                    and 1 <= len(query["code"][0]) <= 2048
                    and self.headers.get("Host")
                    == f"127.0.0.1:{self.server.server_port}"
                )
                self.send_response(200 if valid else 400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(
                    (
                        "認証できました。この画面を閉じてください。"
                        if valid
                        else "認証を確認できませんでした。"
                    ).encode()
                )
                if valid:
                    received["code"] = query["code"][0]
                    completed.set()

        server = HTTPServer(("127.0.0.1", 0), Callback)
        server.timeout = timeout
        redirect = f"http://127.0.0.1:{server.server_port}/oauth/callback"
        url = (
            self.account_origin
            + "/oauth/authorize?"
            + urlencode(
                {
                    "response_type": "code",
                    "client_id": CLIENT_ID,
                    "redirect_uri": redirect,
                    "resource": self.resource,
                    "scope": "arteligo:app",
                    "state": state,
                    "code_challenge": encode(
                        hashlib.sha256(verifier.encode()).digest()
                    ),
                    "code_challenge_method": "S256",
                }
            )
        )
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            if open_browser(url) is False:
                raise E2eeError("browser_unavailable")
            if not completed.wait(timeout):
                raise E2eeError("authentication_timeout")
            self._token(
                {
                    "grant_type": "authorization_code",
                    "code": received["code"],
                    "redirect_uri": redirect,
                    "code_verifier": verifier,
                }
            )
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)
            received.clear()

    def logout(self) -> None:
        raw = self.store.read(self._storage_key)
        if raw is None:
            return
        try:
            token = json.loads(raw)
            with httpx.Client(
                timeout=30, follow_redirects=False, transport=self._transport
            ) as client:
                response = client.post(
                    self.account_origin + "/oauth/revoke",
                    data={
                        "client_id": CLIENT_ID,
                        "resource": self.resource,
                        "token": token["refresh_token"],
                    },
                )
                if response.status_code not in {200, 204}:
                    raise E2eeError("authentication_unavailable")
        except (httpx.HTTPError, ValueError, KeyError):
            raise E2eeError("authentication_unavailable") from None
        self.store.delete(self._storage_key)
