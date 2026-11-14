"""Real-provider response loss observations for the cloud journey process."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qs

import httpx
from arteligo_public_api_client.models.crypto_proto_message import CryptoProtoMessage
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from soenan_arteligo_support.e2ee._crypto import decode
from soenan_arteligo_support.e2ee._oauth import (
    CredentialRecord,
    Ready,
    RefreshUncertain,
)


@dataclass(frozen=True)
class ProbeRequest:
    kind: Literal["arm_commit", "arm_refresh", "observe_commit", "evidence"]
    project: str = ""

    @classmethod
    def parse(cls, value: object) -> ProbeRequest:
        if not isinstance(value, dict):
            raise ValueError("invalid_response_loss_request")
        method = value["method"]
        if method not in {"arm_commit", "arm_refresh", "observe_commit", "evidence"}:
            raise ValueError("invalid_response_loss_kind")
        arguments = value["arguments"]
        if not isinstance(arguments, dict):
            raise ValueError("invalid_response_loss_arguments")
        project = arguments.get("project", "")
        if not isinstance(project, str) or (
            method in {"arm_commit", "observe_commit"} and not project
        ):
            raise ValueError("invalid_response_loss_project")
        return cls(method, project)


@dataclass(frozen=True)
class SavedEntry:
    name: str
    value: str


@dataclass(frozen=True)
class SavedEnvironment:
    entries: tuple[SavedEntry, ...]

    @classmethod
    def read(cls, path: Path) -> SavedEnvironment:
        envelope = json.loads(path.read_bytes())
        values = envelope["values"]
        if (
            envelope["version"] != 1
            or not isinstance(values, dict)
            or any(
                not isinstance(key, str) or not isinstance(value, str)
                for key, value in values.items()
            )
        ):
            raise ValueError("invalid_saved_environment")
        encoded = json.dumps(values, sort_keys=True, separators=(",", ":")).encode()
        if hashlib.sha256(encoded).hexdigest() != envelope["sha256"]:
            raise ValueError("invalid_saved_environment_digest")
        return cls(
            tuple(SavedEntry(key, value) for key, value in sorted(values.items()))
        )

    def entry(self, prefix: str) -> SavedEntry:
        matches = [entry for entry in self.entries if entry.name.startswith(prefix)]
        if len(matches) != 1:
            raise ValueError("saved_state_missing_or_ambiguous")
        return matches[0]


@dataclass(frozen=True)
class ProductDocument:
    name: str
    state: crypto.ProductState
    pending: tuple[tuple[str, str], ...]
    publications: str

    @classmethod
    def read(cls, saved: SavedEnvironment) -> ProductDocument:
        entry = saved.entry("device:core:")
        raw = json.loads(entry.value)
        return cls(
            entry.name,
            crypto.ProductState.FromString(bytes(decode(raw["state"]))),
            tuple(sorted(raw["pending"].items())),
            json.dumps(raw.get("invitation_publications"), sort_keys=True),
        )

    def command(self, project: str) -> crypto.PreparedOperation:
        operation = dict(self.pending)[project]
        return next(
            item
            for item in self.state.prepared_operations
            if item.operation_id == operation
        )


@dataclass(frozen=True)
class ReplyEvidence:
    matched_requests: int = 0
    completed_200_replies: int = 0
    dropped_replies: int = 0
    completed_body_bytes: int = 0
    forwarded_application_bytes: int = 0
    token_requests: int = 0
    authorization_requests: int = 0
    pending_present_before_send: bool = False
    request_matches_persisted_command: bool = False
    original_state_retained: bool = False
    only_matching_operation_released: bool = False
    unrelated_state_retained: bool = False
    refresh_uncertain_before_send: bool = False
    refresh_uncertain_retained: bool = False
    environment_retained: bool = False


class ResponseLossProbe:
    def __init__(
        self, *, directory: str, profile: str, account_origin: str, arteligo_origin: str
    ):
        self.path = (
            Path(directory)
            / hashlib.sha256(profile.encode()).hexdigest()
            / "state.json"
        )
        self.account_origin = account_origin
        self.arteligo_origin = arteligo_origin
        self.kind: Literal["disarmed", "commit", "refresh", "observe"] = "disarmed"
        self.project = ""
        self.drop = False
        self.before: SavedEnvironment | None = None
        self.product: ProductDocument | None = None
        self.refresh: tuple[SavedEntry, CredentialRecord] | None = None
        self.evidence = ReplyEvidence()
        self.original = httpx.HTTPTransport.handle_request

    def install(self) -> None:
        probe = self

        def handle(self: httpx.HTTPTransport, request: httpx.Request) -> httpx.Response:
            return probe.handle(self, request)

        httpx.HTTPTransport.handle_request = handle

    def close(self) -> None:
        httpx.HTTPTransport.handle_request = self.original

    def handle(
        self, transport: httpx.HTTPTransport, request: httpx.Request
    ) -> httpx.Response:
        url = str(request.url)
        if request.method == "POST" and url == self.account_origin + "/oauth/token":
            self.evidence = replace(
                self.evidence, token_requests=self.evidence.token_requests + 1
            )
        if (
            request.method == "POST"
            and url == self.account_origin + "/oauth/device_authorization"
        ):
            self.evidence = replace(
                self.evidence,
                authorization_requests=self.evidence.authorization_requests + 1,
            )
        matched = False
        if (
            request.method == "POST"
            and self.kind in {"commit", "observe"}
            and url == self.arteligo_origin + "/api/e2ee/crypto/commit"
        ):
            envelope = CryptoProtoMessage.from_dict(json.loads(request.content))
            wire = app.CommitCryptoRequest.FromString(
                base64.b64decode(envelope.bytes_, validate=True)
            )
            if wire.project_id == self.project:
                saved = SavedEnvironment.read(self.path)
                product = ProductDocument.read(saved)
                prepared = product.command(self.project)
                exact = wire.command == prepared.command
                if not exact:
                    raise ValueError("wire_command_differs_from_persisted_command")
                self.before, self.product = saved, product
                self.evidence = replace(
                    self.evidence,
                    pending_present_before_send=True,
                    request_matches_persisted_command=True,
                )
                matched = True
        elif (
            request.method == "POST"
            and self.kind == "refresh"
            and url == self.account_origin + "/oauth/token"
        ):
            form = parse_qs(request.content.decode())
            if form["grant_type"] == ["refresh_token"] and form["client_id"] == [
                "arteligo-native-cli"
            ]:
                if self.refresh is None:
                    raise ValueError("refresh_probe_not_armed")
                entry, original = self.refresh
                current = next(
                    item
                    for item in SavedEnvironment.read(self.path).entries
                    if item.name == entry.name
                )
                record = CredentialRecord.parse(json.loads(current.value))
                if (
                    not isinstance(original.state, Ready)
                    or not isinstance(record.state, RefreshUncertain)
                    or record.state.revoke_proof != original.state.pair.refresh_token
                ):
                    raise ValueError("refresh_proof_not_persisted_before_send")
                self.evidence = replace(
                    self.evidence, refresh_uncertain_before_send=True
                )
                matched = True
        if matched:
            self.evidence = replace(
                self.evidence, matched_requests=self.evidence.matched_requests + 1
            )
        response = self.original(transport, request)
        if matched and response.status_code == 200:
            body = response.read()
            response.close()
            self.evidence = replace(
                self.evidence,
                completed_200_replies=self.evidence.completed_200_replies + 1,
                completed_body_bytes=len(body),
                forwarded_application_bytes=0 if self.drop else len(body),
            )
            if self.drop:
                self.evidence = replace(
                    self.evidence, dropped_replies=self.evidence.dropped_replies + 1
                )
                self.drop = False
                raise httpx.ReadError(
                    "journey_response_lost_after_provider_completion", request=request
                )
        return response

    def dispatch(self, request: ProbeRequest) -> ReplyEvidence:
        if request.kind in {"arm_commit", "observe_commit", "arm_refresh"}:
            self.evidence = ReplyEvidence()
            self.project = request.project
            if request.kind == "arm_commit":
                self.kind = "commit"
            elif request.kind == "observe_commit":
                self.kind = "observe"
            else:
                self.kind = "refresh"
            self.drop = request.kind != "observe_commit"
            self.before = SavedEnvironment.read(self.path)
            self.product = None
            self.refresh = None
            if request.kind == "arm_refresh":
                matches = [
                    (entry, CredentialRecord.parse(json.loads(entry.value)))
                    for entry in self.before.entries
                    if entry.name.startswith("oauth:")
                ]
                self.refresh = next(
                    (entry, record)
                    for entry, record in matches
                    if isinstance(record.state, Ready)
                    and record.state.pair.scope == "arteligo:app"
                )
        if request.kind == "evidence" and self.before is not None:
            saved = SavedEnvironment.read(self.path)
            if self.product is not None:
                current = ProductDocument.read(saved)
                prepared = self.product.command(self.project)
                remaining = crypto.ProductState()
                remaining.CopyFrom(self.product.state)
                del remaining.prepared_operations[:]
                remaining.prepared_operations.extend(
                    item
                    for item in self.product.state.prepared_operations
                    if item.operation_id != prepared.operation_id
                )
                expected_pending = tuple(
                    item
                    for item in self.product.pending
                    if item != (self.project, prepared.operation_id)
                )
                self.evidence = replace(
                    self.evidence,
                    original_state_retained=saved == self.before,
                    only_matching_operation_released=(
                        current.pending == expected_pending
                        and current.state == remaining
                    ),
                    unrelated_state_retained=(
                        current.publications == self.product.publications
                        and tuple(
                            entry
                            for entry in saved.entries
                            if entry.name != current.name
                        )
                        == tuple(
                            entry
                            for entry in self.before.entries
                            if entry.name != current.name
                        )
                    ),
                )
            if self.refresh is not None:
                entry, original = self.refresh
                current = next(
                    item for item in saved.entries if item.name == entry.name
                )
                record = CredentialRecord.parse(json.loads(current.value))
                self.evidence = replace(
                    self.evidence,
                    refresh_uncertain_retained=isinstance(original.state, Ready)
                    and isinstance(record.state, RefreshUncertain)
                    and record.state.revoke_proof == original.state.pair.refresh_token,
                    environment_retained=original.environment is not None
                    and record.environment == original.environment
                    and record.identity == original.identity
                    and record.login_intent == original.login_intent,
                    unrelated_state_retained=tuple(
                        item for item in saved.entries if item.name != entry.name
                    )
                    == tuple(
                        item for item in self.before.entries if item.name != entry.name
                    ),
                )
        return self.evidence
