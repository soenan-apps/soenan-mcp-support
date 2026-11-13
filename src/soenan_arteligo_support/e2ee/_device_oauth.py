from __future__ import annotations

import hashlib
import json
import secrets
import time
import uuid
from base64 import b64decode, b64encode
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any
from urllib.parse import urlsplit

import httpx
from account_public_api_client.api.o_auth import authorize_o_auth_device
from account_public_api_client.client import Client
from account_public_api_client.models.o_auth_device_authorization_request import (
    OAuthDeviceAuthorizationRequest,
)
from account_public_api_client.models.o_auth_device_authorization_response import (
    OAuthDeviceAuthorizationResponse,
)
from account_public_api_client.models.o_auth_error_response import OAuthErrorResponse
from account_public_api_client.models.o_auth_error_response_error import (
    OAuthErrorResponseError,
)
from google.protobuf.message import DecodeError
from soenan.account.crypto.v1 import crypto_pb2 as account_crypto
from soenan.account.identity.v1 import identity_pb2 as identity
from soenan_account_identity_client import IdentitySession

from ._crypto import E2eeError, decode, encode
from ._oauth import (
    CredentialRecord,
    EnvironmentAuthorization,
    ProfileVault,
    Ready,
    RefreshUncertain,
    RevokePending,
    SignedOut,
    TokenPair,
    origin,
)
from ._storage import CredentialItem


class _Phase(str, Enum):
    PREPARING = "preparing"
    REQUESTING = "requesting"
    WAITING = "waiting"
    INFLIGHT = "inflight"
    COMPLETE = "complete"
    REJECTED = "rejected"


@dataclass(frozen=True)
class _PreparingAuthorization:
    operation_id: str
    subject: str
    authorization_expires_at: int
    intent: str

    def serialize(self) -> str:
        return json.dumps(
            {
                "phase": _Phase.PREPARING.value,
                "operation_id": self.operation_id,
                "subject": self.subject,
                "authorization_expires_at": self.authorization_expires_at,
                "intent": self.intent,
            },
            separators=(",", ":"),
        )

    @classmethod
    def parse(cls, raw: str) -> _PreparingAuthorization | _DeviceAuthorizationFlow:
        try:
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError
            if value.get("phase") != _Phase.PREPARING.value:
                return _DeviceAuthorizationFlow.parse(raw)
            if (
                set(value)
                != {
                    "phase",
                    "operation_id",
                    "subject",
                    "authorization_expires_at",
                    "intent",
                }
                or any(
                    type(value[key]) is not str or not value[key]
                    for key in ("operation_id", "subject", "intent")
                )
                or type(value["authorization_expires_at"]) is not int
                or value["authorization_expires_at"] <= 0
            ):
                raise ValueError
            return cls(
                value["operation_id"],
                value["subject"],
                value["authorization_expires_at"],
                value["intent"],
            )
        except (ValueError, KeyError, TypeError):
            raise E2eeError("device_authorization_corrupt") from None


@dataclass
class _DeviceAuthorizationFlow:
    request: OAuthDeviceAuthorizationRequest
    response: OAuthDeviceAuthorizationResponse | None
    binding: identity.CloudApprovalBinding | None
    phase: _Phase
    intent: str
    poll_expires_at: float
    interval: int

    @classmethod
    def parse(cls, raw: str) -> _DeviceAuthorizationFlow:
        try:
            value = json.loads(raw)
            if (
                not isinstance(value, dict)
                or set(value)
                != {
                    "request",
                    "response",
                    "binding",
                    "phase",
                    "intent",
                    "poll_expires_at",
                    "interval",
                }
                or type(value["intent"]) is not str
                or type(value["poll_expires_at"]) not in {int, float}
                or type(value["interval"]) is not int
            ):
                raise ValueError
            phase = _Phase(value["phase"])
            if phase == _Phase.PREPARING:
                raise ValueError
            request = OAuthDeviceAuthorizationRequest.from_dict(value["request"])
            response = (
                None
                if value["response"] is None
                else OAuthDeviceAuthorizationResponse.from_dict(value["response"])
            )
            binding = (
                None
                if not value["binding"]
                else identity.CloudApprovalBinding.FromString(
                    bytes(decode(value["binding"]))
                )
            )
            if phase not in {_Phase.REQUESTING, _Phase.REJECTED} and (
                response is None or binding is None
            ):
                raise ValueError
            return cls(
                request,
                response,
                binding,
                phase,
                value["intent"],
                value["poll_expires_at"],
                value["interval"],
            )
        except (ValueError, KeyError, TypeError):
            raise E2eeError("device_authorization_corrupt") from None

    def serialize(self) -> str:
        return json.dumps(
            {
                "request": self.request.to_dict(),
                "response": None if self.response is None else self.response.to_dict(),
                "binding": ""
                if self.binding is None
                else encode(self.binding.SerializeToString()),
                "phase": self.phase.value,
                "intent": self.intent,
                "poll_expires_at": self.poll_expires_at,
                "interval": self.interval,
            },
            separators=(",", ":"),
        )


def _verify_device_authorization(
    vault: ProfileVault, binding: identity.CloudApprovalBinding
) -> None:
    if vault.profile != "account-keys" and vault.bind().subject() != binding.subject:
        raise E2eeError("identity_subject_mismatch")
    session = IdentitySession(
        vault.store,
        origin=vault.account_origin,
        subject=binding.subject,
        credentials=vault.identity_bind(),
    )
    try:
        settings = session.settings()
        digest = hashlib.sha256(
            account_crypto.SignedBytes.FromString(binding.pairing_request).body
        ).digest()
        receipt = next(
            (
                item
                for item in settings.bundle.commit_receipts
                if item.operation_id == binding.operation_id
            ),
            None,
        )
        if receipt is None or (
            receipt.mutation_digest != digest
            and digest not in receipt.accepted_document_digests
        ):
            raise E2eeError("identity_receipt_missing")
        session.open_bundle(
            settings.bundle, release_operation_ids=[binding.operation_id]
        )
        session.require_approved()
    finally:
        session.lock()


def _open_device_code(
    vault: ProfileVault,
    flow: _DeviceAuthorizationFlow,
    authorization: OAuthDeviceAuthorizationResponse,
) -> str:
    session = IdentitySession(
        vault.store, origin=vault.account_origin, subject=flow.request.subject
    )
    try:
        sealed = identity.CloudDeviceCodeEnvelope.FromString(
            b64decode(authorization.sealed_device_code.bytes_, validate=True)
        )
        return session.open_cloud_device_code(
            expected_context=identity.CloudDeviceCodeContext(
                client_id=flow.request.client_id, binding=flow.binding
            ),
            sealed_code=sealed,
        )
    except (ValueError, DecodeError):
        raise E2eeError("invalid_device_authorization_response") from None
    finally:
        session.lock()


def _refresh_device_authorization(
    vault: ProfileVault,
    flow: _DeviceAuthorizationFlow,
    credentials: CredentialItem,
    journal: CredentialItem,
) -> None:
    try:
        with Client(
            base_url=vault.account_origin,
            timeout=httpx.Timeout(30),
            follow_redirects=False,
            raise_on_unexpected_status=False,
            httpx_args={"transport": vault._transport},
        ) as client:
            response = authorize_o_auth_device.sync_detailed(
                client=client, body=flow.request
            )
        if response.status_code == 400 and isinstance(
            response.parsed, OAuthErrorResponse
        ):
            if response.parsed.error in {
                OAuthErrorResponseError.ACCESS_DENIED,
                OAuthErrorResponseError.EXPIRED_TOKEN,
            }:
                flow.phase = _Phase.REJECTED
                journal.replace(flow.serialize())
                current = vault._load(credentials)
                vault._save(credentials, replace(current, login_intent=None))
                raise E2eeError("device_authorization_" + response.parsed.error.value)
        if response.status_code != 200:
            raise E2eeError("device_authorization_unavailable")
        authorization = response.parsed
        if not isinstance(authorization, OAuthDeviceAuthorizationResponse):
            raise E2eeError("invalid_device_authorization_response")
        verification = urlsplit(authorization.verification_uri)
        if (
            type(authorization.expires_in) is not int
            or type(authorization.interval) is not int
            or not authorization.sealed_device_code.bytes_
            or not authorization.user_code
            or not authorization.request_id
            or authorization.expires_in < 0
            or authorization.interval <= 0
            or origin(f"{verification.scheme}://{verification.netloc}")
            != vault.account_origin
            or (
                flow.binding is not None
                and authorization.request_id != flow.binding.request_id
            )
        ):
            raise ValueError
        if flow.binding is None:
            flow.binding = identity.CloudApprovalBinding(
                subject=flow.request.subject,
                request_id=authorization.request_id,
                device=identity.Device.FromString(bytes(decode(flow.request.device))),
                scopes=flow.request.scope.split(),
                expires_at=flow.request.authorization_expires_at,
                resource=flow.request.resource,
                profile="account-keys"
                if vault.profile == "account-keys"
                else "native-app",
                pairing_request=b64decode(flow.request.pairing_request, validate=True),
                operation_id=flow.request.operation_id,
                origin=flow.request.origin,
            )
        flow.response = authorization
        flow.phase = _Phase.WAITING
        flow.poll_expires_at = time.time() + authorization.expires_in
        flow.interval = authorization.interval
        journal.replace(flow.serialize())
    except (
        httpx.HTTPError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        DecodeError,
    ):
        raise E2eeError("device_authorization_unavailable") from None


def login_device(
    vault: ProfileVault,
    *,
    subject: str,
    authorization_expires_at: int,
    on_verification: Callable[[OAuthDeviceAuthorizationResponse], Any],
    timeout: float = 600,
) -> identity.CloudApprovalBinding:
    if not subject or authorization_expires_at <= 0 or timeout <= 0:
        raise E2eeError("invalid_device_authorization")
    flow_key = "device-authorization:" + vault._storage_key
    with vault.store.credential(vault._storage_key) as credentials:
        record = vault._load(credentials)
        if isinstance(record.state, RevokePending):
            raise E2eeError("logout_incomplete")
        if isinstance(record.state, RefreshUncertain):
            raise E2eeError("authentication_refresh_uncertain")
        with vault.store.credential(flow_key) as journal:
            raw = journal.read()
            saved = None if raw is None else _PreparingAuthorization.parse(raw)
            if isinstance(saved, _DeviceAuthorizationFlow):
                if (
                    saved.request.client_id != vault.client_id
                    or saved.request.resource != vault.resource
                    or saved.request.scope != vault.scope
                    or saved.request.origin != vault.account_origin
                ):
                    raise E2eeError("device_authorization_corrupt")
                if (
                    saved.request.subject == subject
                    and record.environment is not None
                    and saved.response is not None
                    and record.environment.authorization_id == saved.response.request_id
                    and record.environment.subject == subject
                    and record.environment.scope == vault.scope
                    and isinstance(record.state, Ready)
                    and record.state.pair.scope == vault.scope
                    and record.state.pair.subject == subject
                    and record.state.pair.environment_authorization_id
                    == record.environment.authorization_id
                    and record.state.pair.environment_authorization_expires_at
                    == record.environment.expires_at
                    and record.login_intent is None
                ):
                    if saved.phase != _Phase.COMPLETE:
                        saved.phase = _Phase.COMPLETE
                        journal.replace(saved.serialize())
                    if (
                        record.environment.expires_at <= time.time()
                        or record.state.pair.refresh_expires_at <= time.time()
                    ):
                        saved = None
                elif saved.phase == _Phase.INFLIGHT:
                    raise E2eeError("authentication_login_uncertain")
                elif saved.phase == _Phase.REJECTED:
                    if record.login_intent == saved.intent:
                        record = replace(record, login_intent=None)
                        vault._save(credentials, record)
                    saved = None
                elif saved.phase == _Phase.COMPLETE:
                    saved = None
                elif (
                    isinstance(record.state, SignedOut) and record.login_intent is None
                ):
                    saved = None
                if (
                    isinstance(saved, _DeviceAuthorizationFlow)
                    and saved.request.subject != subject
                ):
                    raise E2eeError("device_authorization_in_progress")
            if isinstance(saved, _PreparingAuthorization) and saved.subject != subject:
                raise E2eeError("device_authorization_in_progress")
            if saved is None:
                if record.login_intent is not None:
                    raise E2eeError("authentication_superseded")
                saved = _PreparingAuthorization(
                    str(uuid.uuid4()),
                    subject,
                    authorization_expires_at,
                    secrets.token_urlsafe(32),
                )
                journal.replace(saved.serialize())
            if isinstance(saved, _PreparingAuthorization):
                if record.login_intent not in {None, saved.intent}:
                    raise E2eeError("authentication_superseded")
                vault._save(credentials, replace(record, login_intent=saved.intent))
                session = IdentitySession(
                    vault.store, origin=vault.account_origin, subject=saved.subject
                )
                try:
                    pairing = session.prepare_pairing(operation_id=saved.operation_id)
                finally:
                    session.lock()
                enrollment = identity.EnrollmentBody.FromString(pairing.body)
                request = OAuthDeviceAuthorizationRequest(
                    client_id=vault.client_id,
                    resource=vault.resource,
                    scope=vault.scope,
                    subject=saved.subject,
                    device=encode(enrollment.device.SerializeToString()),
                    pairing_request=b64encode(pairing.SerializeToString()).decode(
                        "ascii"
                    ),
                    authorization_expires_at=saved.authorization_expires_at,
                    operation_id=saved.operation_id,
                    origin=vault.account_origin,
                )
                flow = _DeviceAuthorizationFlow(
                    request, None, None, _Phase.REQUESTING, saved.intent, 0, 0
                )
                journal.replace(flow.serialize())
            else:
                flow = saved
                if flow.phase != _Phase.COMPLETE and record.login_intent != flow.intent:
                    raise E2eeError("authentication_superseded")
            if flow.phase == _Phase.REQUESTING or (
                flow.phase == _Phase.WAITING and flow.poll_expires_at <= time.time()
            ):
                _refresh_device_authorization(vault, flow, credentials, journal)
    authorization, binding = flow.response, flow.binding
    if authorization is None or binding is None:
        raise E2eeError("device_authorization_corrupt")
    if flow.phase == _Phase.COMPLETE:
        _verify_device_authorization(vault, binding)
        return binding
    on_verification(authorization)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(min(flow.interval, max(0, deadline - time.monotonic())))
        if time.monotonic() >= deadline:
            break
        with vault.store.credential(vault._storage_key) as credentials:
            current = vault._load(credentials)
            if current.login_intent != flow.intent:
                raise E2eeError("authentication_superseded")
            if isinstance(current.state, RevokePending):
                raise E2eeError("logout_incomplete")
            if isinstance(current.state, RefreshUncertain):
                raise E2eeError("authentication_refresh_uncertain")
            with vault.store.credential(flow_key) as journal:
                if journal.read() != flow.serialize():
                    raise E2eeError("authentication_superseded")
                if flow.poll_expires_at <= time.time():
                    _refresh_device_authorization(vault, flow, credentials, journal)
                device_code = _open_device_code(vault, flow, authorization)
                flow.phase = _Phase.INFLIGHT
                journal.replace(flow.serialize())
                if journal.read() != flow.serialize():
                    raise E2eeError("authentication_login_uncertain")
                try:
                    with httpx.Client(
                        timeout=30, follow_redirects=False, transport=vault._transport
                    ) as client:
                        response = client.post(
                            vault.account_origin + "/oauth/token",
                            data={
                                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                                "device_code": device_code,
                                "client_id": vault.client_id,
                                "resource": vault.resource,
                            },
                        )
                    payload = response.json()
                except (httpx.HTTPError, ValueError):
                    raise E2eeError("authentication_login_uncertain") from None
                if response.status_code == 400:
                    try:
                        rejection = OAuthErrorResponse.from_dict(payload)
                    except (ValueError, KeyError, TypeError):
                        raise E2eeError("authentication_login_uncertain") from None
                    if rejection.error in {
                        OAuthErrorResponseError.AUTHORIZATION_PENDING,
                        OAuthErrorResponseError.SLOW_DOWN,
                    }:
                        flow.phase = _Phase.WAITING
                        if rejection.error == OAuthErrorResponseError.SLOW_DOWN:
                            flow.interval += 5
                        journal.replace(flow.serialize())
                        continue
                    if rejection.error in {
                        OAuthErrorResponseError.ACCESS_DENIED,
                        OAuthErrorResponseError.EXPIRED_TOKEN,
                    }:
                        flow.phase = _Phase.REJECTED
                        journal.replace(flow.serialize())
                        vault._save(credentials, replace(current, login_intent=None))
                        raise E2eeError("device_authorization_" + rejection.error.value)
                if response.status_code != 200:
                    raise E2eeError("authentication_login_uncertain")
                pair = TokenPair.parse(payload)
                if (
                    pair.subject != binding.subject
                    or pair.scope != vault.scope
                    or pair.environment_authorization_id != binding.request_id
                    or pair.environment_authorization_expires_at != binding.expires_at
                ):
                    raise E2eeError("invalid_token_response")
                accepted = CredentialRecord(
                    secrets.token_urlsafe(32),
                    None,
                    Ready(pair),
                    EnvironmentAuthorization(
                        binding.request_id,
                        binding.subject,
                        pair.scope,
                        binding.expires_at,
                    ),
                )
                vault._save(credentials, accepted)
                flow.phase = _Phase.COMPLETE
                journal.replace(flow.serialize())
                break
    if flow.phase == _Phase.COMPLETE:
        _verify_device_authorization(vault, binding)
        return binding
    raise E2eeError("authentication_timeout")
