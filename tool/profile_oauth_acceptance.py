"""Exercise installed profile credentials against owned Account and SecretService."""
from __future__ import annotations

import argparse
import base64
from contextlib import nullcontext
from dataclasses import asdict
import hashlib
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import parse_qs, urlsplit

import httpx

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))

from soenan_arteligo_support.e2ee import (
    DeviceSession, E2eeCrypto, E2eeError, EncryptedRecords, SystemSecureStore, open_session,
)
from soenan_arteligo_support.e2ee._api import GeneratedAPI
from soenan_arteligo_support.e2ee._oauth import (
    AccessOnly, ProfileVault, Ready, RefreshUncertain, RevokePending, SignedOut,
)


class IntegrationFailure(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def require(value: bool, code: str) -> None:
    if not value:
        raise IntegrationFailure(code)


def emit(scenario: str, **values) -> None:
    print(json.dumps({"scenario": scenario, **values}, sort_keys=True), flush=True)


def claims(token: str) -> dict:
    component = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(component + "=" * (-len(component) % 4)))


class ActualTransport(httpx.BaseTransport):
    def __init__(self, certificate: str, relay: str | None = None):
        self.certificate, self.relay = certificate, relay
        self.events: list[dict] = []

    def handle_request(self, request):
        original = request
        if self.relay and request.url.path in {"/oauth/token", "/oauth/revoke"}:
            request = httpx.Request(
                request.method, self.relay + request.url.path,
                headers=request.headers, content=request.content,
            )
        event = {"path": original.url.path, "status": None}
        if original.url.path == "/oauth/token":
            event["grant_type"] = parse_qs(original.content.decode())["grant_type"][0]
        self.events.append(event)
        with httpx.HTTPTransport(verify=self.certificate, trust_env=False) as actual:
            response = actual.handle_request(request)
            response.read()
        event["status"] = response.status_code
        return response


class PrivateSecretService:
    def __init__(self, daemon: Path, libraries: Path):
        self.root = Path(tempfile.mkdtemp(prefix="redesign-m20-native-"))
        self.daemon_path, self.libraries = daemon, libraries
        self.password = secrets.token_hex(48).encode()
        self.bus = self.daemon = None
        self.logs = []
        self.original_environment = dict(os.environ)
        self.environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
            PYTHON_KEYRING_BACKEND="keyring.backends.SecretService.Keyring",
            LD_LIBRARY_PATH=str(libraries))
        for name in ("home", "data", "config", "cache", "runtime"):
            (self.root / name).mkdir(mode=0o700)
        for variable, directory in (("HOME", "home"), ("XDG_DATA_HOME", "data"),
            ("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache"),
            ("XDG_RUNTIME_DIR", "runtime")):
            self.environment[variable] = str(self.root / directory)
        for name in ("DBUS_SESSION_BUS_ADDRESS", "GNOME_KEYRING_CONTROL", "SSH_AUTH_SOCK", "SECRET_BACKEND"):
            self.environment.pop(name, None)
        self.start()

    def start(self):
        runtime = self.root / "runtime"
        control = runtime / "keyring"
        control.mkdir(mode=0o700, exist_ok=True)
        bus_log = (self.root / f"dbus-{len(self.logs)}.stderr.log").open("wb")
        self.logs.append(bus_log)
        self.bus = subprocess.Popen([
            "dbus-daemon", "--session", "--nofork", "--print-address=1",
            "--address=unix:path=" + str(runtime / "bus"),
        ], env=self.environment, stdout=subprocess.PIPE, stderr=bus_log)
        address = self.bus.stdout.readline().decode().strip()
        require(address.startswith("unix:path=" + str(runtime / "bus")), "private_bus_address_mismatch")
        self.environment["DBUS_SESSION_BUS_ADDRESS"] = address
        daemon_log = (self.root / f"keyring-{len(self.logs)}.stderr.log").open("wb")
        self.logs.append(daemon_log)
        self.daemon = subprocess.Popen([
            str(self.daemon_path), "--foreground", "--unlock", "--components=secrets",
            "--control-directory=" + str(control),
        ], cwd=self.root, env=self.environment, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=daemon_log)
        self.daemon.stdin.write(self.password)
        self.daemon.stdin.close()
        output = self.daemon.stdout.readline().decode().strip()
        require(output == "GNOME_KEYRING_CONTROL=" + str(control), "private_keyring_control_mismatch")
        self.environment["GNOME_KEYRING_CONTROL"] = str(control)
        result = subprocess.run([
            str(self.daemon_path), "--start", "--components=secrets",
            "--control-directory=" + str(control),
        ], env=self.environment, cwd=self.root, capture_output=True, timeout=20)
        require(result.returncode == 0, "private_keyring_initialization_failed")
        subprocess.run(["gdbus", "wait", "--session", "--timeout", "10", "org.freedesktop.secrets"],
            env=self.environment, check=True, capture_output=True, timeout=15)
        os.environ.update(self.environment)

    def stop(self):
        for process in (self.daemon, self.bus):
            if process is not None:
                process.terminate()
                process.wait(timeout=15)
        self.daemon = self.bus = None

    def restart(self):
        self.stop()
        shutil.rmtree(self.root / "runtime")
        (self.root / "runtime").mkdir(mode=0o700)
        self.start()

    def close(self):
        self.stop()
        for stream in self.logs:
            stream.close()
        self.password = b""
        for name in ("home", "data", "config", "cache", "runtime"):
            shutil.rmtree(self.root / name)
        os.environ.clear()
        os.environ.update(self.original_environment)
        emit("native_cleanup", processes_stopped=True, protected_owned_data_removed=True,
            logs_root=str(self.root), stable_coordination_files_unlinked=False)


class AccountActor:
    def __init__(self, stack, certificate: str, inputs: dict):
        self.stack, self.certificate = stack, certificate
        self.email, self.password, self.subject = inputs["email"], inputs["password"], inputs["subject"]
        self.organization = inputs["organization"]
        self.protected_identity_path = inputs.get("protected_identity_path")
        require(inputs.get("owned_disposable_identity") is True
            and self.email.startswith("m20-") and self.email.endswith("@local.invalid"),
            "explicit_owned_m20_identity_required")
        self.cookie = ""
        self.expires_at = 0
        self.lock = threading.Lock()
        self.client = httpx.Client(verify=certificate, trust_env=False, follow_redirects=False, timeout=30)

    def cookie_header(self):
        with self.lock:
            if self.expires_at <= time.time():
                self.cookie = self.stack._sign_in_account_fixture(
                    label="M20 independent actor", email=self.email, password=self.password,
                )
                verified = self.client.get(self.stack.account_origin + "/api/auth/session",
                    headers={"cookie": self.cookie})
                require(verified.status_code == 200 and verified.json().get("authenticated") is True,
                    "actual_account_identity_not_authenticated")
                parsed = SimpleCookie()
                parsed.load(self.cookie)
                value = claims(parsed["__Host-soenan_session"].value)
                require(value["sub"] == self.subject, "independent_actor_subject_changed")
                self.expires_at = value["exp"]
            return self.cookie

    def authorize(self, url: str, ready=None, release=None):
        target = urlsplit(url)
        require(target.scheme + "://" + target.netloc == self.stack.account_origin
            and target.path == "/oauth/authorize", "authorization_origin_changed")
        with httpx.Client(verify=self.certificate, trust_env=False, follow_redirects=False, timeout=30) as browser:
            response = browser.get(url, headers={"cookie": self.cookie_header(),
                "sec-fetch-site": "none", "sec-fetch-mode": "navigate", "sec-fetch-dest": "document"})
            require(response.status_code == 302, "actual_account_authorization_not_redirected")
            callback = urlsplit(response.headers["location"])
            require(callback.scheme == "http" and callback.hostname == "127.0.0.1"
                and callback.path == "/oauth/callback", "actual_account_callback_target_invalid")
            if ready is not None:
                ready.set()
            if release is not None:
                require(release.wait(90), "owned_browser_callback_gate_timeout")
            require(browser.get(response.headers["location"]).status_code == 200, "actual_callback_rejected")
        return True

    def accept_product_terms(self, context):
        api = GeneratedAPI(context, transport=ActualTransport(self.certificate))
        product = api.call("getProductSession")
        if product.get("kind") == "termsAcceptanceRequired":
            terms = product["requiredTerms"]
            require(hashlib.sha256(terms["body"].encode()).hexdigest() == terms["bodySha256"], "actual_product_terms_digest_changed")
            response = self.client.put(self.stack.arteligo_origin + "/api/session/terms-acceptance",
                headers={"authorization": "Bearer " + context.access_token()},
                json={"termsVersionId": terms["id"]})
            require(response.status_code == 200 and response.json().get("kind") == "authenticated",
                "actual_product_terms_acceptance_failed")
        else:
            require(product.get("kind") == "authenticated", "actual_product_session_not_authenticated")

    def close_owned_identity(self):
        headers = {"cookie": self.cookie_header(), "origin": self.stack.account_origin,
            "sec-fetch-site": "same-origin"}
        response = self.client.get(self.stack.account_origin + "/api/organizations", headers=headers)
        require(response.status_code == 200, "owned_organization_cleanup_read_failed")
        organizations = response.json()["organizations"]
        require(len(organizations) == 1 and organizations[0]["organizationId"] == self.organization
            and "organization:close" in organizations[0]["permissions"],
            "owned_identity_cleanup_scope_unconfirmed")
        result = self.client.request("DELETE",
            self.stack.account_origin + "/api/organizations/" + self.organization, headers=headers)
        require(result.status_code == 200 and result.json().get("outcome") in {"applied", "idempotent"},
            "owned_personal_organization_cleanup_failed")
        result = self.client.request("DELETE", self.stack.account_origin + "/api/account",
            headers=headers, json={"currentPassword": self.password})
        require(result.status_code == 204, "owned_account_cleanup_failed")
        if self.protected_identity_path is not None:
            Path(self.protected_identity_path).unlink()
        emit("owned_identity_cleanup", personal_organization_closed=True, account_closed=True,
            native_logout_claimed_all_families=False)

    def close(self):
        self.client.close()
        self.password = self.cookie = ""


class Relay:
    def __init__(self, account: str, certificate: str, mode: str):
        self.received = threading.Event()
        self.committed = threading.Event()
        self.release = threading.Event()
        self.events: list[dict] = []
        self.errors: list[str] = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                event = {"path": self.path, "upstream_dispatched": False, "status": None,
                    "grant_type": parse_qs(body.decode()).get("grant_type", ["revoke"])[0]}
                owner.events.append(event)
                owner.received.set()
                if mode == "hold_before":
                    owner.release.wait(90)
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                try:
                    with httpx.Client(verify=certificate, trust_env=False, follow_redirects=False, timeout=30) as upstream:
                        event["upstream_dispatched"] = True
                        response = upstream.post(account + self.path, content=body,
                            headers={"content-type": self.headers["Content-Type"]})
                    event["status"] = response.status_code
                    if self.path == "/oauth/token" and response.status_code == 200:
                        event["family"] = claims(response.json()["access_token"])["sid"]
                    owner.committed.set()
                    if mode in {"drop_after", "hold_after"}:
                        owner.release.wait(90)
                    if mode == "drop_after":
                        self.connection.shutdown(socket.SHUT_RDWR)
                        self.connection.close()
                        return
                    self.send_response(response.status_code)
                    self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                    self.send_header("Content-Length", str(len(response.content)))
                    self.end_headers()
                    self.wfile.write(response.content)
                except Exception as error:
                    owner.errors.append(type(error).__name__)
                    self.connection.close()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self):
        return "http://127.0.0.1:" + str(self.server.server_port)

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


class LoginAttempt:
    def __init__(self, vault, actor):
        self.ready, self.release = threading.Event(), threading.Event()
        self.outcome = None

        def run():
            try:
                vault.login(open_browser=lambda url: actor.authorize(url, self.ready, self.release))
                self.outcome = "published"
            except E2eeError as error:
                self.outcome = error.code
            except Exception as error:
                self.outcome = type(error).__name__
                self.ready.set()

        self.thread = threading.Thread(target=run)
        self.thread.start()
        require(self.ready.wait(40) and self.outcome is None, "actual_browser_wait_not_reached")

    def finish(self):
        self.release.set()
        self.thread.join(45)
        require(not self.thread.is_alive(), "actual_browser_attempt_not_joined")
        return self.outcome


def make_vault(inputs, profile, transport=None):
    return ProfileVault(account_origin=inputs["account"], arteligo_origin=inputs["arteligo"],
        store=SystemSecureStore(profile), transport=transport)


def worker(inputs):
    transport = ActualTransport(inputs["certificate"], inputs.get("relay"))
    vault = make_vault(inputs, inputs["profile"], transport)
    session = None
    try:
        context = vault.bind()
        if inputs["action"] == "session":
            api = GeneratedAPI(context, transport=transport)
            product = api.call("getProductSession")
            context.check_current()
            require(product.get("kind") == "authenticated", "worker_product_session_invalid")
            session = DeviceSession(api, E2eeCrypto(), vault.store,
                origin=inputs["arteligo"], subject=product["user"]["id"])
            require(session.refresh() == "approved", "worker_device_not_approved")
        token = context.access_token()
        return {"outcome": "usable", "identity": context.identity,
            "family": claims(token)["sid"], "events": transport.events}
    except E2eeError as error:
        return {"outcome": error.code, "events": transport.events}
    finally:
        if session is not None:
            session.lock()


def start_worker(inputs):
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write(json.dumps(inputs).encode())
    process.stdin.close()
    process.stdin = None
    return process


def finish_worker(process):
    output, diagnostic = process.communicate(timeout=90)
    require(process.returncode == 0 and not diagnostic, "real_worker_failed")
    return json.loads(output)


def snapshot(vault):
    with vault.store.credential(vault._storage_key) as item:
        return vault._load(item)


def owner_family(stack, family):
    from scripts.soenan_cli.integrations import docker

    require(len(family) == 36 and family.startswith("asf_")
        and all(value in "0123456789abcdef" for value in family[4:]), "invalid_public_family_claim")
    postgres = stack.account_postgres
    sql = "BEGIN READ ONLY; SELECT json_build_object('generation',f.current_refresh_generation,'revoked',f.revoked_at IS NOT NULL,'revoked_at',f.revoked_at,'proofs',(SELECT count(*) FROM public.account_session_refresh_tokens t WHERE t.family_id=f.family_id),'consumed',(SELECT count(*) FROM public.account_session_refresh_tokens t WHERE t.family_id=f.family_id AND t.consumed_at IS NOT NULL)) FROM public.account_session_families f JOIN public.account_client_grants g ON g.family_id=f.family_id WHERE g.client_id='arteligo-native-cli' AND f.family_id='" + family + "'; COMMIT;"
    result = subprocess.run(docker.command("exec", "-i", postgres.container, "psql", "-X", "-qAt",
        "-U", postgres.user, "-d", postgres.database), input=sql.encode(), env=docker.environment(),
        capture_output=True, timeout=30)
    require(result.returncode == 0, "actual_account_family_observation_failed")
    return json.loads(result.stdout)


def other_items(store, excluded):
    collection = store._backend.get_preferred_collection()
    try:
        result = {}
        for item in collection.search_items(store._backend._query(store._service, None)):
            attributes = item.get_attributes()
            name = attributes["username"]
            if name != excluded:
                result[name] = hashlib.sha256(item.get_secret()).hexdigest()
        return result
    finally:
        collection.connection.close()


def wait_until(timestamp):
    time.sleep(max(0, timestamp - time.time()))


def source_hashes():
    root = WORKSPACE / "soenan-mcp-support"
    paths = [path for directory in (root / "src", root / "generated") for path in directory.rglob("*.py")]
    paths.extend((root / "tool").glob("*.py"))
    paths.extend(WORKSPACE / "scripts/soenan_cli/operations" / name for name in (
        "develop_capacity_fixtures.py", "develop_capacity_scenario.py",
        "develop_capacity_scenario_run.py", "develop_capacity_recovery.py",
        "develop_capacity_sdk.py", "develop_capacity_owned.py",
        "local_dev.py",
    ))
    return {str(path.relative_to(WORKSPACE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def oauth_native_item(vault):
    collection = vault.store._backend.get_preferred_collection()
    try:
        items = list(collection.search_items(vault.store._backend._query(
            vault.store._service, vault._storage_key)))
        require(len(items) == 1, "native_credential_item_not_unique")
        return items[0].item_path
    finally:
        collection.connection.close()


def request_evidence(events):
    return [{**{key: value for key, value in event.items() if key != "family"},
        **({"family_sha256": hashlib.sha256(event["family"].encode()).hexdigest()}
            if "family" in event else {})} for event in events]


class HeldReadTransport(ActualTransport):
    def __init__(self, certificate):
        super().__init__(certificate)
        self.path = None
        self.received = threading.Event()
        self.release = threading.Event()

    def handle_request(self, request):
        response = super().handle_request(request)
        if request.url.path == self.path:
            self.path = None
            self.received.set()
            require(self.release.wait(90), "owned_scope_read_gate_timeout")
        return response

    def arm(self, path):
        self.path = path
        self.received.clear()
        self.release.clear()


def share_project(owner, recipient, scope):
    from soenan_arteligo_support.e2ee._crypto import encode, wipe
    owner.reconcile_keys()

    binding = owner.crypto.keypair()
    invitation = secrets.token_urlsafe(24)
    request_id = secrets.token_urlsafe(24)
    public = owner.public
    message = "\n".join(("arteligo-e2ee-invitation-owner-v1", invitation,
        owner.subject, owner.device_id, public["encryption_public_key"],
        public["signing_public_key"])).encode()
    signature = owner.crypto.execute({"op": "sign_bytes",
        "secret_key": binding["signing_secret_key"], "bytes": encode(message)})["signature"]
    owner.command("e2eeCreateInvitation", "invitation_create", {
        "invitation_id": invitation, "project_id": scope, "role": "viewer",
        "expires_at": int(time.time()) + 1800,
        "binding_public_key": binding["signing_public_key"], "binding_signature": signature})
    recovery = {key: recipient.recovery[key] for key in (
        "recovery_id", "encryption_public_key", "signing_public_key", "generation")}
    public = recipient.public
    message = "\n".join(("arteligo-e2ee-invitation-binding-v1", invitation,
        recipient.subject, recipient.device_id, public["encryption_public_key"],
        public["signing_public_key"], recovery["recovery_id"],
        recovery["encryption_public_key"], recovery["signing_public_key"])).encode()
    signature = recipient.crypto.execute({"op": "sign_bytes",
        "secret_key": binding["signing_secret_key"], "bytes": encode(message)})["signature"]
    recipient.command("e2eeRequestInvitation", "invitation_request", {
        "request_id": request_id, "invitation_id": invitation,
        "account_subject": recipient.subject, "device": public,
        "recovery": recovery, "binding_signature": signature}, invitation_id=invitation)
    metadata = owner.scope_metadata(scope, refresh=True)
    epoch = metadata["key_epoch"]
    key = owner.scope_key(scope, epoch)
    try:
        envelopes = [owner.wrap_key(scope, epoch, key,
            recipient=identifier, kind=kind, public_key=public_key)
            for identifier, kind, public_key in (
                (recipient.device_id, "device", recipient.public["encryption_public_key"]),
                (recovery["recovery_id"], "recovery", recovery["encryption_public_key"]))]
        result = owner.command("e2eeApproveInvitation", "invitation_approve",
            {"request_id": request_id, "key_epoch": epoch, "envelopes": envelopes},
            request_id=request_id)
        require(result["state"] == "joined", "owned_project_peer_not_joined")
    finally:
        wipe(key)
        binding.clear()
    recipient.endorse(owner.public, owner.recovery)


def verify_project_scope(stack, inputs, owner, scope):
    identity = provision_identity(stack, inputs["certificate"])
    actor = AccountActor(stack, inputs["certificate"], identity)
    transport = HeldReadTransport(inputs["certificate"])
    vault = make_vault(inputs, "m20-scope-" + secrets.token_hex(16), transport)
    session = None
    pending = None
    adapter_errors = {}

    class ObservedAPI(GeneratedAPI):
        def call(self, operation, *, body=None, **parameters):
            try:
                return super().call(operation, body=body, **parameters)
            except E2eeError as error:
                adapter_errors[threading.get_ident()] = error
                raise

    try:
        vault.login(open_browser=actor.authorize)
        actor.accept_product_terms(vault.bind())
        session = DeviceSession(ObservedAPI(vault.bind(), transport=transport),
            E2eeCrypto(), vault.store, origin=inputs["arteligo"], subject=actor.subject)
        require(session.refresh() == "needs_setup", "scope_peer_not_fresh")
        draft = session.prepare_setup()
        session.finish_setup(draft)
        draft.clear()
        records = EncryptedRecords(session)
        control = records.create_project(value={"name": "M20 unrelated authorized scope"},
            owner_org=actor.organization)
        records.write(control, key_epoch=1, records=[{"record_id": "control",
            "kind": "schedule", "expected_revision": 0, "value": {"retained": True}}])
        share_project(owner, session, scope)
        require(records.read(scope, ["profile_acceptance"])["profile_acceptance"]["value"]
            == {"accepted": True}, "scope_peer_initial_read_failed")
        retained_device = dict(session._device)
        retained_key = bytes(session.scope_key(control, 1))
        try:
            records.write(scope, key_epoch=1, records=[{"record_id": "viewer_denied",
                "kind": "schedule", "expected_revision": 0, "value": {"must_not_commit": True}}])
            raise IntegrationFailure("viewer_write_unexpectedly_admitted")
        except E2eeError as error:
            require(error.code == "access_denied", "viewer_write_denial_not_ambiguous")
        require(any(identity[0] == scope for identity in session._scope_keys),
            "write_only_denial_erased_project_read_keys")
        records.read(scope, ["profile_acceptance"])

        def revoke():
            owner.command("e2eeRemoveMember", "member_remove",
                {"project_id": scope, "account_subject": session.subject}, scope_id=scope)

        revoke()
        results = records.read_many({scope: ["profile_acceptance"], control: ["control"]})
        require(results[scope].get("error") == "project_access_denied",
            "actual_batch_project_read_denial_missing")
        require(results[control]["records"][0]["value"] == {"retained": True},
            "batch_denial_broke_other_scope")
        require(not any(identity[0] == scope for identity in session._scope_keys)
            and scope not in session._key_bundles, "denied_scope_keys_retained")
        require(session._device == retained_device
            and bytes(session.scope_key(control, 1)) == retained_key,
            "scope_denial_wiped_unrelated_device_or_key")

        share_project(owner, session, scope)
        records.read(scope, ["profile_acceptance"])
        revoke()
        transport.arm("/api/e2ee/scopes/" + scope)
        failures = []

        def old_denial():
            try:
                session.scope_metadata(scope, refresh=True)
            except E2eeError as error:
                failures.append(error)

        pending = threading.Thread(target=old_denial)
        pending.start()
        require(transport.received.wait(30), "real_denied_scope_response_not_held")
        result = records.read_many({scope: ["profile_acceptance"]})
        require(result[scope].get("error") == "project_access_denied",
            "current_batch_scope_denial_missing")
        share_project(owner, session, scope)
        records.read(scope, ["profile_acceptance"])
        current_owner = session._scope_metadata[scope]
        transport.release.set()
        pending.join(40)
        require(not pending.is_alive() and len(failures) == 1
            and failures[0].code == "project_access_denied", "old_http_denial_not_preserved")
        require(failures[0] is adapter_errors.get(pending.ident),
            "original_http_error_object_replaced")
        require(session._scope_metadata.get(scope) is current_owner
            and any(identity[0] == scope for identity in session._scope_keys),
            "old_http_denial_wiped_reauthorized_scope")

        transport.arm("/api/e2ee/records/read")
        observed = []
        def old_success():
            try:
                observed.append(records.read_many({scope: ["profile_acceptance"]}))
            except E2eeError as error:
                observed.append({scope: {"error": error.code}})
        pending = threading.Thread(target=old_success)
        pending.start()
        require(transport.received.wait(30), "real_successful_scope_response_not_held")
        revoke()
        result = records.read_many({scope: ["profile_acceptance"]})
        require(result[scope].get("error") == "project_access_denied",
            "current_scope_denial_missing_before_late_success")
        transport.release.set()
        pending.join(40)
        require(not pending.is_alive() and observed
            and observed[0][scope].get("error") == "scope_read_superseded",
            "late_success_adopted_retired_scope_material")
        require(not any(identity[0] == scope for identity in session._scope_keys),
            "late_success_republished_denied_scope_key")
        require(records.read(control, ["control"])["control"]["value"] == {"retained": True},
            "late_scope_retirement_broke_other_project")
        emit("captured_project_scope", batch_denial_targeted=True,
            original_http_denial_preserved=True, old_denial_cannot_wipe_regrant=True,
            late_success_cannot_adopt_retired_material=True,
            unrelated_project_and_device_retained=True, normal_membership_owner=True)
    finally:
        transport.release.set()
        if pending is not None and pending.is_alive():
            pending.join(40)
        if session is not None:
            session.lock()
        vault.logout()
        actor.close_owned_identity()
        actor.close()


def provision_identity(stack, certificate, *, manual_term_seconds=3600, billing_context=None):
    from scripts.soenan_cli.operations.develop_capacity_fixtures import _Provisioner
    from scripts.soenan_cli.operations.develop_capacity_scenario_run import save

    identity = {"email": "m20-" + secrets.token_hex(12) + "@local.invalid",
        "password": secrets.token_urlsafe(32), "owned_disposable_identity": True}
    descriptor, protected_path = tempfile.mkstemp(prefix="redesign-m20-owned-", suffix=".json")
    identity["protected_identity_path"] = protected_path
    with os.fdopen(descriptor, "w") as protected:
        json.dump(identity, protected)
    emit("owned_identity_recovery", protected_identity_path=protected_path)
    receipt = "bin/soenan:M20 independent native profile acceptance"
    issued = stack._compose("--profile", "tools", "run", "--rm", "--no-deps", "-T",
        "csm-bootstrap", "csm-admin", "invitation-bootstrap-create", receipt, capture=True)
    match = re.fullmatch(r"invitation\.state=completed id=([0-9a-f-]{36}) code=([A-Z2-7]{32})",
        issued.stdout.strip()) if issued.returncode == 0 else None
    require(match is not None, "owned_invitation_creation_failed")
    invitation, code = match.groups()
    identity["invitation_id"] = invitation
    save(Path(protected_path), identity)
    client = httpx.Client(verify=certificate, trust_env=False, timeout=30)
    operator = httpx.Client(verify=certificate, trust_env=False, timeout=30)
    csm = httpx.Client(verify=certificate, trust_env=False, timeout=30)

    def request(session, method, origin, path, body=None, expected=200, csrf=False):
        headers = {"origin": origin, "sec-fetch-site": "same-origin"}
        if csrf:
            headers["X-CSM-CSRF"] = session.cookies["csm_csrf"]
        response = session.request(method, origin + path, json=body, headers=headers)
        require(response.status_code == expected, "owned_provision_http_" + str(response.status_code))
        return response

    try:
        terms = request(client, "GET", stack.account_origin,
            "/api/legal-terms/account/current").json()
        challenge = request(client, "POST", stack.account_origin, "/api/auth/sign-up",
            {"email": identity["email"], "password": identity["password"],
             "displayName": "M20 independent acceptance", "termsVersionId": terms["id"],
             "invitationCode": code}, expected=202).json()
        otp = stack._latest_local_otp(recipient=identity["email"], purpose="signup_verification")
        verified = request(client, "POST", stack.account_origin, "/api/auth/sign-up/otp",
            {"challengeId": challenge["challengeId"], "code": otp}).json()
        require(verified.get("status") == "verified", "owned_signup_not_verified")
        identity["subject"] = claims(client.cookies["__Host-soenan_session"])["sub"]
        save(Path(protected_path), identity)
        organizations = request(client, "GET", stack.account_origin, "/api/organizations").json()["organizations"]
        require(len(organizations) == 1, "owned_personal_organization_not_unique")
        identity["organization"] = organizations[0]["organizationId"]
        save(Path(protected_path), identity)
        protected = stack._read_secrets()
        cookie = stack._sign_in_account_fixture(label="M20 independent setup operator",
            email=protected["fixture_owner_email"], password=protected["fixture_owner_password"])
        protected.clear()
        parsed = SimpleCookie()
        parsed.load(cookie)
        for name, value in parsed.items():
            operator.cookies.set(name, value.value)
        launch = request(csm, "GET", stack.csm_origin, "/auth/start", expected=303)
        target = launch.headers["location"]
        require(target.startswith(stack.account_origin + "/oauth/authorize?"), "owned_csm_authorize_origin")
        authorized = operator.get(target)
        require(authorized.status_code == 302, "owned_csm_authorization_failed")
        callback = authorized.headers["location"]
        require(callback.startswith(stack.csm_origin + "/auth/callback?"), "owned_csm_callback_origin")
        completed = csm.get(callback)
        require(completed.status_code == 303 and "csm_session" in csm.cookies,
            "owned_csm_session_failed")

        class LocalBilling(_Provisioner):
            def csm_json(self, method, url, *, cookies, csrf=False, body=None):
                from urllib.parse import urlsplit
                parsed = urlsplit(url)
                path = parsed.path + ("?" + parsed.query if parsed.query else "")
                return request(csm, method, stack.csm_origin, path, body, csrf=csrf).json()

        def billing_progress(value):
            identity["billing"] = value["evidence"]
            save(Path(protected_path), identity)
        billing = LocalBilling(csm, run_id="m20-" + secrets.token_hex(12), delay=0,
            progress=billing_progress)
        with billing_context(identity) if billing_context is not None else nullcontext():
            billing.manual_billing({}, identity["organization"], 1, term_seconds=manual_term_seconds)
        request(client, "POST", stack.account_origin, "/api/organizations/seats/arteligo/assign",
            {"organizationId": identity["organization"], "targetSubject": identity["subject"]})
        save(Path(protected_path), identity)
        request(csm, "POST", stack.csm_origin, "/api/invitations/" + invitation + "/revoke",
            {}, expected=204, csrf=True)
        emit("owned_identity_provisioned", ordinary_invitation=True, local_otp_capture=True,
            canonical_manual_billing=True, seat_assigned=True, external_provider_write=False)
        return identity
    except BaseException:
        if "organization" in identity:
            cleanup = AccountActor(stack, certificate, identity)
            try:
                cleanup.close_owned_identity()
            finally:
                cleanup.close()
        raise
    finally:
        if "csm_session" in csm.cookies:
            request(csm, "POST", stack.csm_origin, "/api/sign-out", csrf=True)
        for session in (operator, client):
            if "__Host-soenan_session" in session.cookies:
                request(session, "POST", stack.account_origin, "/api/auth/sign-out", expected=204)
        client.close()
        operator.close()
        csm.close()


def run(args, identity):
    from scripts.soenan_cli.core.workspace import read_configuration
    from scripts.soenan_cli.core.env import REPO_ROOT
    from scripts.soenan_cli.operations.local_dev import LocalDevelopmentStack

    require(sys.platform.startswith("linux"), "linux_native_acceptance_host_required")
    workspace = read_configuration(args.workspace_config, expected_root=REPO_ROOT)
    stack = LocalDevelopmentStack(workspace=workspace, workspace_config=args.workspace_config)
    require(args.workspace_config.resolve() != (WORKSPACE / ".local/config/workspace.json").resolve(),
        "explicit_disposable_workspace_required")
    require(urlsplit(stack.account_origin).hostname.endswith(".localhost"), "owned_local_account_required")
    if identity.get("provision_owned_identity") is True:
        identity = provision_identity(stack, str(args.certificate))
    require(identity["subject"] not in {
        "acct_" + __import__("uuid").UUID(value).hex for key, value in stack._read_secrets().items()
        if key in {"fixture_owner_user_id", "fixture_participant_user_id"}
    }, "independent_account_identity_required")
    spec = importlib.util.find_spec("soenan_arteligo_support.e2ee._oauth")
    require(not Path(spec.origin).resolve().is_relative_to(WORKSPACE / "soenan-mcp-support"),
        "installed_wheel_required")
    installed = Path(spec.origin).parent
    source = WORKSPACE / "soenan-mcp-support/src/soenan_arteligo_support/e2ee"
    for path in source.glob("*.py"):
        require(hashlib.sha256(path.read_bytes()).digest()
            == hashlib.sha256((installed / path.name).read_bytes()).digest(),
            "installed_wheel_does_not_match_frozen_source")
    frozen = source_hashes()
    actor = AccountActor(stack, str(args.certificate), identity)
    native = PrivateSecretService(args.secret_service_daemon, args.native_libraries)
    os.environ["SSL_CERT_FILE"] = str(args.certificate)
    os.environ["NO_PROXY"] = "*"
    inputs = {"account": stack.account_origin, "arteligo": stack.arteligo_origin,
        "certificate": str(args.certificate)}
    profiles = {name: "m20-" + secrets.token_hex(16) for name in
        ("primary", "independent", "legacy", "loss", "kill", "save", "code")}
    vaults = {name: make_vault(inputs, profile, ActualTransport(str(args.certificate)))
        for name, profile in profiles.items() if name != "legacy"}
    sessions = []
    relays = []
    children = []
    recovery_code = ""
    legacy = None
    try:
        for name, vault in vaults.items():
            vault.login(open_browser=actor.authorize)
            actor.accept_product_terms(vault.bind())
        primary = open_session(account_origin=inputs["account"], arteligo_origin=inputs["arteligo"], profile=profiles["primary"])
        sessions.append(primary)
        require(primary.subject == actor.subject and primary.state == "needs_setup", "fresh_independent_e2ee_actor_required")
        draft = primary.prepare_setup()
        recovery_code = draft["code"]
        primary.finish_setup(draft)
        draft.clear()
        records = EncryptedRecords(primary)
        scope = records.create_project(value={"name": "M20 protected profile admission"}, owner_org=actor.organization)
        records.write(scope, key_epoch=1, records=[{"record_id": "profile_acceptance", "kind": "schedule",
            "expected_revision": 0, "value": {"accepted": True}}])
        verify_project_scope(stack, inputs, primary, scope)
        held = []
        for _ in range(3):
            session = open_session(account_origin=inputs["account"], arteligo_origin=inputs["arteligo"], profile=profiles["primary"])
            sessions.append(session)
            session.scope_key(scope, 1)
            held.append(session)
        secondary = open_session(account_origin=inputs["account"], arteligo_origin=inputs["arteligo"], profile=profiles["independent"])
        sessions.append(secondary)
        secondary.accept_approval(primary.approve(secondary.enroll()))
        require(secondary.refresh() == "approved", "independent_profile_device_approval_failed")
        secondary.scope_key(scope, 1)
        original = snapshot(vaults["primary"])
        primary_native_item = oauth_native_item(vaults["primary"])
        original_family = claims(original.state.pair.access_token)["sid"]
        preserved = other_items(vaults["primary"].store, vaults["primary"]._storage_key)
        independent_record = snapshot(vaults["independent"])
        legacy = make_vault(inputs, profiles["legacy"], ActualTransport(str(args.certificate)))
        with legacy.store.credential(legacy._storage_key) as item:
            item.replace(json.dumps(asdict(original.state.pair), separators=(",", ":")))
        legacy_native_item = oauth_native_item(legacy)
        emit("normal_approved_actor", real_native_device=True, real_project_key_cached=True,
            fresh_device_sessions=len(held), protected_unrelated_items=len(preserved))

        code_vault = vaults["code"]
        prior = snapshot(code_vault)
        relay = Relay(inputs["account"], inputs["certificate"], "drop_after")
        relays.append(relay)
        uncertain = make_vault(inputs, profiles["code"], ActualTransport(inputs["certificate"], relay.url))
        attempt = LoginAttempt(uncertain, actor)
        attempt.release.set()
        require(relay.committed.wait(30), "actual_code_exchange_not_committed")
        unknown_family = relay.events[0]["family"]
        require(owner_family(stack, unknown_family)["generation"] == 1, "unknown_code_family_not_observed")
        relay.release.set()
        attempt.thread.join(40)
        require(not attempt.thread.is_alive() and attempt.outcome == "authentication_login_uncertain", "code_exchange_unknown_not_reported")
        current = snapshot(code_vault)
        require(current.identity == prior.identity and current.state == prior.state, "unknown_code_exchange_destroyed_prior_authentication")
        actor.accept_product_terms(code_vault.bind())
        code_vault.logout()
        require(not owner_family(stack, unknown_family)["revoked"], "known_logout_claimed_unknown_family_revocation")
        emit("code_response_loss", outcome=attempt.outcome, prior_complete_authentication_retained=True,
            actual_requests=relay.events, unknown_family_remains=True, persistent_unknown_registry=False)
        relay.close()

        native.stop()
        try:
            vaults["save"].bind()
            raise RuntimeError("unavailable_native_store_admitted_credentials")
        except E2eeError as error:
            require(error.code == "secure_store_unavailable", "native_unavailability_not_reported")
        native.restart()
        require(isinstance(snapshot(vaults["save"]).state, Ready), "native_unavailability_replaced_credentials")
        emit("native_unavailable_before_handoff", token_requests=0, ready_preserved=True)

        wait_until(original.state.pair.access_expires_at - 17)
        browser = LoginAttempt(vaults["primary"], actor)
        wait_until(original.state.pair.access_expires_at - 14)
        for _ in range(2):
            child = start_worker({**inputs, "profile": profiles["primary"], "action": "session"})
            children.append(child)
        results = [finish_worker(child) for child in children[-2:]]
        token_events = [event for result in results for event in result["events"] if event["path"] == "/oauth/token"]
        require(all(result["outcome"] == "usable" and result["identity"] == original.identity
            and result["family"] == original_family for result in results), "concurrent_bound_sessions_changed_identity")
        require(len(token_events) == 1 and token_events[0]["status"] == 200, "refresh_not_single_handoff")
        observed = owner_family(stack, original_family)
        require(observed["generation"] == 2 and observed["proofs"] == 2 and observed["consumed"] == 1
            and not observed["revoked"], "actual_refresh_family_state_incorrect")
        legacy_context = legacy.bind()
        actor.accept_product_terms(legacy_context)
        require(isinstance(snapshot(legacy).state, AccessOnly), "legacy_raw_became_refreshable")
        require(oauth_native_item(legacy) == legacy_native_item, "legacy_native_item_was_recreated")
        for session in held:
            session.require_approved()
        require(browser.finish() == "published", "rotation_superseded_browser_intent")
        for session, operation in zip(held, ("sign", "key", "recovery")):
            try:
                if operation == "sign":
                    session.sign("device_revoke", {"device_id": session.device_id})
                elif operation == "key":
                    session.scope_key(scope, 1)
                else:
                    session.restore(recovery_code)
                raise RuntimeError("stale_cached_secret_operation_admitted")
            except E2eeError as error:
                require(error.code == "authentication_superseded", "stale_cached_secret_wrong_refusal")
                require(session._device is None and not session._scope_keys, "observed_supersession_did_not_lock_keys")
        require(oauth_native_item(vaults["primary"]) == primary_native_item,
            "credential_native_item_was_recreated")
        require(other_items(vaults["primary"].store, vaults["primary"]._storage_key) == preserved,
            "credential_transition_changed_other_protected_names")
        require(snapshot(vaults["independent"]) == independent_record, "other_profile_credentials_changed")
        secondary.scope_key(scope, 1)
        emit("concurrent_refresh_and_cached_devices", natural_token_expiry=True, actual_token_requests=token_events,
            owner_state=observed, rotation_identity_stable=True, browser_wait_outside_lock=True,
            stale_cached_sign_key_recovery_refused=True, unrelated_protected_names_unchanged=True,
            independent_profile_usable=True)

        first = LoginAttempt(vaults["primary"], actor)
        second = LoginAttempt(vaults["primary"], actor)
        require(second.finish() == "published" and first.finish() == "authentication_superseded", "latest_started_browser_login_did_not_win")
        before = len(vaults["primary"]._transport.events)
        pending = LoginAttempt(vaults["primary"], actor)
        current_family = claims(vaults["primary"].bind().access_token())["sid"]
        vaults["primary"].logout()
        require(pending.finish() == "authentication_superseded", "logout_did_not_fence_browser_callback")
        after = vaults["primary"]._transport.events[before:]
        require(not any(event["path"] == "/oauth/token" for event in after), "stale_browser_code_exchanged")
        require(owner_family(stack, current_family)["revoked"], "actual_logout_family_not_revoked")
        secondary.scope_key(scope, 1)
        emit("login_logout_races", latest_started_wins=True, stale_callback_exchange_count=0,
            known_family_revoked=True, other_profile_usable=True)

        wait_until(original.state.pair.access_expires_at + 1)
        before = len(legacy._transport.events)
        try:
            legacy_context.access_token()
            raise RuntimeError("expired_legacy_access_admitted")
        except E2eeError as error:
            require(error.code == "authentication_required", "expired_legacy_wrong_refusal")
        require(len(legacy._transport.events) == before, "legacy_proof_sent_to_refresh")
        revoke_relay = Relay(inputs["account"], inputs["certificate"], "drop_after")
        relays.append(revoke_relay)
        revoke = make_vault(inputs, profiles["legacy"], ActualTransport(inputs["certificate"], revoke_relay.url))
        outcome = []
        def logout_lost():
            try:
                revoke.logout()
                outcome.append("unexpected_success")
            except E2eeError as error:
                outcome.append(error.code)
        thread = threading.Thread(target=logout_lost)
        thread.start()
        require(revoke_relay.committed.wait(30), "historical_revoke_not_acknowledged_by_owner")
        revoked = owner_family(stack, original_family)
        require(revoked["revoked"], "historical_consumed_proof_did_not_revoke_family")
        revoke_relay.release.set()
        thread.join(40)
        require(outcome == ["logout_incomplete"] and isinstance(snapshot(legacy).state, RevokePending), "lost_revoke_obligation_not_retained")
        try:
            legacy.login(open_browser=actor.authorize)
            raise RuntimeError("new_login_overwrote_revoke_pending")
        except E2eeError as error:
            require(error.code == "logout_incomplete", "pending_revoke_wrong_login_refusal")
        legacy.logout()
        require(owner_family(stack, original_family) == revoked, "idempotent_historical_revoke_changed_owner_state")
        emit("legacy_and_historical_revoke", valid_legacy_access_exercised=True, legacy_refresh_requests=0,
            lost_revoke_retained=True, new_login_blocked=True, repeated_actual_revoke_idempotent=True,
            owner_state=revoked)
        revoke_relay.close()

        for name, mode in (("loss", "drop_after"), ("kill", "hold_before"), ("save", "hold_after")):
            vault = vaults[name]
            record = snapshot(vault)
            family = claims(record.state.pair.access_token)["sid"]
            wait_until(record.state.pair.access_expires_at - 14)
            relay = Relay(inputs["account"], inputs["certificate"], mode)
            relays.append(relay)
            child = start_worker({**inputs, "profile": profiles[name], "relay": relay.url, "action": "token"})
            children.append(child)
            require(relay.received.wait(30), "pending_native_handoff_not_received")
            raw = vault.store._backend.get_password(vault.store._service, vault._storage_key)
            require(json.loads(raw)["state"]["kind"] == "RefreshUncertain", "native_pending_not_persisted_before_handoff")
            if name == "kill":
                independent = start_worker({**inputs, "profile": profiles["independent"], "action": "session"})
                children.append(independent)
                require(finish_worker(independent)["outcome"] == "usable", "unrelated_profile_blocked_by_live_item")
                child.kill()
                require(child.wait(timeout=15) == -9, "owned_client_not_sigkilled")
                relay.release.set()
                observed = owner_family(stack, family)
                require(observed["generation"] == 1 and not observed["revoked"], "precommit_kill_reached_actual_account")
                result = {"outcome": "SIGKILL"}
            else:
                require(relay.committed.wait(30), "actual_refresh_response_not_received_by_relay")
                observed = owner_family(stack, family)
                require(observed["generation"] == 2 and observed["consumed"] == 1 and not observed["revoked"], "actual_refresh_commit_not_independently_observed")
                if name == "save":
                    collection = vault.store._backend.get_preferred_collection()
                    try:
                        collection.lock()
                    finally:
                        collection.connection.close()
                relay.release.set()
                result = finish_worker(child)
                require(result["outcome"] == ("secure_store_unavailable" if name == "save" else "authentication_uncertain"), "real_fault_not_reported")
                if name == "save":
                    native.restart()
            relay.close()
            fresh = start_worker({**inputs, "profile": profiles[name], "action": "token"})
            children.append(fresh)
            reloaded = finish_worker(fresh)
            emit("fresh_refresh_observation", fault=name, outcome=reloaded["outcome"],
                actual_requests=request_evidence(reloaded["events"]))
            require(reloaded["outcome"] == "authentication_refresh_uncertain",
                "fresh_process_uncertain_state_unavailable")
            require(not reloaded["events"], "fresh_process_replayed_uncertain_proof")
            require(isinstance(snapshot(vault).state, RefreshUncertain), "uncertain_record_not_retained")
            vault.logout()
            require(owner_family(stack, family)["revoked"], "known_historical_family_cleanup_failed")
            emit("refresh_" + name, real_fault=result["outcome"], actual_requests=relay.events,
                owner_state_at_fault=observed, fresh_process_no_replay=True,
                kernel_lock_released=True, known_family_revoked=True)

        require(source_hashes() == frozen, "shared_source_changed_during_acceptance")
        digest = hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()
        emit("complete", source_manifest_sha256=digest, source_files=len(frozen),
            platform="Linux SecretService", other_platforms_executed=False,
            power_loss_or_roaming_rollback_claimed=False, old_sdk_process_coexistence_claimed=False,
            admitted_content_may_commit=True, cross_process_ram_wipe_claimed=False)
    except BaseException as error:
        emit("first_failure", error=error.code if isinstance(error, (E2eeError, IntegrationFailure))
            else type(error).__name__)
        raise
    finally:
        recovery_code = ""
        for relay in relays:
            relay.close()
        for child in children:
            if child.returncode is None:
                child.terminate()
                child.wait(timeout=15)
        for session in sessions:
            session.lock()
        cleanup_vaults = [*vaults.values(), *([legacy] if legacy is not None else [])]
        for vault in cleanup_vaults:
            try:
                vault.logout()
            except E2eeError as error:
                emit("known_profile_cleanup_unresolved", error=error.code)
        original_failure = sys.exc_info()[1]
        try:
            actor.close_owned_identity()
        except Exception as error:
            emit("owned_identity_cleanup_unresolved", error=error.code
                if isinstance(error, (E2eeError, IntegrationFailure)) else type(error).__name__)
            if original_failure is None:
                raise
        finally:
            actor.close()
            native.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--workspace-config", type=Path)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--secret-service-daemon", type=Path)
    parser.add_argument("--native-libraries", type=Path)
    args = parser.parse_args()
    inputs = json.load(sys.stdin)
    if args.worker:
        print(json.dumps(worker(inputs)), flush=True)
        return
    require(all((args.workspace_config, args.certificate, args.secret_service_daemon, args.native_libraries)),
        "owned_native_integration_inputs_required")
    run(args, inputs)


if __name__ == "__main__":
    main()
