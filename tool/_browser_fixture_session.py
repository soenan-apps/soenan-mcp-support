"""In-memory browser authentication for disposable local metadata fixtures."""

from __future__ import annotations

import json
import os
import re
import select
import subprocess
import sys
import time
from pathlib import Path

import httpx

from soenan_arteligo_support.e2ee._api import GeneratedAPI
from soenan_arteligo_support.e2ee._crypto import E2eeCrypto, E2eeError
from soenan_arteligo_support.e2ee._session import DeviceSession


class MemoryStore:
    def __init__(self):
        self.values = {}

    def read(self, name):
        return self.values.get(name)

    def write(self, name, value):
        self.values[name] = value

    def delete(self, name):
        self.values.pop(name, None)


class BrowserBridge(httpx.BaseTransport):
    def __init__(self, args):
        self.arteligo_origin = args.origin.rstrip("/")
        self.process = subprocess.Popen(
            [
                args.node,
                str(Path(__file__).with_name("browser_metadata_bridge.cjs")),
                args.cdp_url,
                self.arteligo_origin,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )
        self.requests = 0
        self.response_bytes = 0
        self._pending = bytearray()
        os.set_blocking(self.process.stdin.fileno(), False)

    def access_token(self):
        # The transport uses browser cookies and never forwards this placeholder.
        return "browser-cookie-transport"

    def call(self, command):
        deadline = time.monotonic() + 40
        outgoing = memoryview(
            (json.dumps(command, separators=(",", ":")) + "\n").encode()
        )
        while outgoing:
            remaining = deadline - time.monotonic()
            if (
                remaining <= 0
                or not select.select([], [self.process.stdin], [], remaining)[1]
            ):
                self.stop()
                raise E2eeError("browser_request_timeout")
            written = os.write(self.process.stdin.fileno(), outgoing)
            outgoing = outgoing[written:]
        while b"\n" not in self._pending:
            remaining = deadline - time.monotonic()
            if (
                remaining <= 0
                or not select.select([self.process.stdout], [], [], remaining)[0]
            ):
                self.stop()
                raise E2eeError("browser_request_timeout")
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                raise E2eeError("browser_bridge_unavailable")
            self._pending.extend(chunk)
            if len(self._pending) > 80 * 1024 * 1024:
                self.stop()
                raise E2eeError("browser_response_too_large")
        line, _, self._pending = self._pending.partition(b"\n")
        result = json.loads(line)
        if "error" in result:
            raise E2eeError(result["error"])
        return result["result"]

    def handle_request(self, request):
        command = {
            "action": "request",
            "url": str(request.url),
            "method": request.method,
            "body": request.content.decode(),
        }
        response = self.call(command)
        if response["status"] == 401 and request.url.path != "/auth/refresh":
            self.refresh()
            response = self.call(command)
        self.requests += 1
        self.response_bytes += len(response["body"].encode())
        if response["status"] >= 400:
            diagnostic = {
                "at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "http_status": response["status"],
                "method": request.method,
                "operation": "records_write"
                if request.url.path.endswith("/records")
                else "request",
            }
            request_id = response.get("requestId")
            if isinstance(request_id, str) and re.fullmatch(
                r"[A-Za-z0-9_-]{1,128}", request_id
            ):
                diagnostic["request_id"] = request_id
            try:
                failure = json.loads(response["body"]).get("error")
                code = failure.get("code") if isinstance(failure, dict) else failure
                if isinstance(code, str) and re.fullmatch(r"[a-z_]{1,64}", code):
                    diagnostic["error_code"] = code
            except (ValueError, AttributeError):
                pass
            print(json.dumps(diagnostic), file=sys.stderr, flush=True)
        return httpx.Response(
            response["status"],
            content=response["body"],
            headers={"content-type": "application/json"},
            request=request,
        )

    def refresh(self):
        from arteligo_public_api_client.api.session import refresh_product_session
        from arteligo_public_api_client.client import Client

        with Client(
            base_url=self.arteligo_origin, httpx_args={"transport": self}
        ) as client:
            response = refresh_product_session.sync_detailed(client=client)
        if response.status_code != 200:
            raise E2eeError("authentication_required")

    def close(self):
        # GeneratedAPI closes an HTTP client after each call, not the shared bridge.
        pass

    def stop(self):
        if not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)


def connect(bridge):
    api = GeneratedAPI(bridge, transport=bridge)
    product = api.call("getProductSession")
    if product.get("kind") != "authenticated":
        bridge.refresh()
        product = api.call("getProductSession")
    if product.get("kind") != "authenticated":
        raise E2eeError("authentication_required")
    subject = product["user"]["id"]
    protected = bridge.call({"action": "device", "subject": subject})
    if protected is None:
        raise E2eeError("device_approval_required")
    device = json.loads(protected)
    store = MemoryStore()
    session = DeviceSession(
        api, E2eeCrypto(), store, origin=bridge.arteligo_origin, subject=subject
    )
    store.write(session._storage_key, protected)
    for pinned in device.get("pins", {}).values():
        session.trust.pin_device(pinned)
    recovery = api.call("e2eeGetRecovery")
    recovery_id = recovery["recovery_id"]
    roots = device.get("recovery_roots", {})
    encryption = device.get("recovery_encryption_pins", {})
    if recovery_id in roots or recovery_id in encryption:
        if (
            roots.get(recovery_id) != recovery["signing_public_key"]
            or encryption.get(recovery_id) != recovery["encryption_public_key"]
        ):
            raise E2eeError("recovery_key_changed")
        session.trust.pin_recovery(subject, recovery)
    del protected, device
    session.refresh()
    session.require_approved()
    organizations = product["joinedOrganizations"]
    if not organizations:
        raise E2eeError("organization_required")
    return session, organizations[0]["id"]
