from __future__ import annotations

import json
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Protocol

import httpx
from arteligo_public_api_client.models.crypto_proto_message import CryptoProtoMessage

from ._crypto import E2eeError
from ._oauth import BoundCredentials
from ._service_generated import EnvelopeCall

if TYPE_CHECKING:
    from arteligo_public_api_client.models.session_authorization import (
        SessionAuthorization,
    )


class _ProviderRevisionConflict(E2eeError):
    def __init__(self):
        super().__init__("revision_conflict")


def sse_documents(response: httpx.Response) -> Iterator[dict[str, Any]]:
    if response.headers.get("content-type", "").split(";", 1)[0] != "text/event-stream":
        raise E2eeError("invalid_response")
    data: list[str] = []
    for line in response.iter_lines():
        if line == "":
            if data:
                value = json.loads("\n".join(data))
                if not isinstance(value, dict):
                    raise E2eeError("invalid_response")
                yield value
                data.clear()
        elif line.startswith("data:"):
            data.append(line[5:].removeprefix(" "))
        elif line and not line.startswith((":", "event:", "id:", "retry:")):
            raise E2eeError("invalid_response")
    if data:
        raise E2eeError("incomplete_key_operation_stream")


class E2eeAPI(Protocol):
    credentials: BoundCredentials

    def initialize_authorization(
        self,
        organization_ids: list[str],
        *,
        project_ids: list[str],
    ) -> SessionAuthorization: ...
    def execute(self, call: EnvelopeCall) -> CryptoProtoMessage: ...


def initialize_session_authorization(
    arteligo_origin: str,
    token: str,
    transport: httpx.BaseTransport | None,
    *,
    organization_ids: list[str],
    project_ids: list[str],
) -> SessionAuthorization:
    from arteligo_public_api_client.api.session import (
        initialize_session_authorization as endpoint,
    )
    from arteligo_public_api_client.client import AuthenticatedClient
    from arteligo_public_api_client.models.initialize_session_authorization_request import (
        InitializeSessionAuthorizationRequest,
    )
    from arteligo_public_api_client.models.session_authorization import (
        SessionAuthorization,
    )
    from arteligo_public_api_client.models.session_authorization_outcome import (
        SessionAuthorizationOutcome,
    )

    try:
        body = InitializeSessionAuthorizationRequest(
            organization_ids=organization_ids,
            project_ids=project_ids,
        )
        with AuthenticatedClient(
            base_url=arteligo_origin,
            token=token,
            timeout=httpx.Timeout(30),
            follow_redirects=False,
            raise_on_unexpected_status=False,
            httpx_args={"transport": transport},
        ) as client:
            response = endpoint.sync_detailed(
                client=client,
                body=body,
            )
        if int(response.status_code) == 401:
            raise E2eeError("authorization_expired")
        if int(response.status_code) == 403:
            raise E2eeError("authorization_denied")
        if int(response.status_code) != 200:
            raise E2eeError("authorization_unavailable")
        value = response.parsed
        if not isinstance(value, SessionAuthorization):
            raise E2eeError("invalid_authorization_response")
        match value.outcome:
            case SessionAuthorizationOutcome.READY:
                return value
            case SessionAuthorizationOutcome.PENDING:
                raise E2eeError("authorization_pending")
            case SessionAuthorizationOutcome.EXPIRED:
                raise E2eeError("authorization_expired")
            case _:
                raise E2eeError("invalid_authorization_response")
    except E2eeError:
        raise
    except (
        httpx.HTTPError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        ImportError,
    ):
        raise E2eeError("authorization_unavailable") from None


class GeneratedAPI:
    """Transport adapter over the product-owned, generated public API client."""

    def __init__(
        self,
        credentials: BoundCredentials,
        *,
        transport: httpx.BaseTransport | None = None,
    ):
        self.credentials = credentials
        self.transport = transport

    def initialize_authorization(
        self,
        organization_ids: list[str],
        *,
        project_ids: list[str],
    ) -> SessionAuthorization:
        authorization = initialize_session_authorization(
            self.credentials.arteligo_origin,
            self.credentials.access_token(),
            self.transport,
            organization_ids=organization_ids,
            project_ids=project_ids,
        )
        self.credentials.check_current()
        return authorization

    def execute(self, call: EnvelopeCall) -> CryptoProtoMessage:
        from arteligo_public_api_client.client import AuthenticatedClient
        from arteligo_public_api_client.models.error_code import ErrorCode
        from arteligo_public_api_client.models.error_envelope import ErrorEnvelope

        try:
            client = AuthenticatedClient(
                base_url=self.credentials.arteligo_origin,
                token=self.credentials.access_token(),
                timeout=httpx.Timeout(30),
                follow_redirects=False,
                raise_on_unexpected_status=False,
                httpx_args={"transport": self.transport},
            )
            with client:
                response = call(client)
            status = int(response.status_code)
            if not 200 <= status < 300:
                if (
                    status == 409
                    and isinstance(response.parsed, ErrorEnvelope)
                    and response.parsed.error.code == ErrorCode.REVISION_CONFLICT
                ):
                    raise _ProviderRevisionConflict()
                codes = {
                    400: "invalid_request",
                    401: "authentication_required",
                    403: "access_denied",
                    404: "not_found",
                    409: "revision_conflict",
                    429: "rate_limited",
                }
                code = codes.get(status, "service_unavailable")
                if isinstance(response.parsed, ErrorEnvelope):
                    detail = response.parsed.error.code.value
                    if detail in {
                        "limit_exceeded",
                        "quota_exceeded",
                        "rekey_required",
                        "device_revoked",
                        "project_access_denied",
                        "content_format_update_required",
                        "owner_rotation_required",
                        "owner_handoff_fenced",
                        "owner_key_generation_stale",
                        "owner_candidate_invalidated",
                        "owner_candidate_key_consumed",
                        "owner_custody_changed",
                        "owner_coverage_incomplete",
                        "owner_authority_changed",
                        "ambiguous_owner_authority",
                        "owner_key_proof_required",
                        "authorization_pending",
                        "authorization_unavailable",
                        "authorization_expired",
                        "authorization_denied",
                    } and (detail != "project_access_denied" or status == 403):
                        code = detail
                raise E2eeError(code)
            if not isinstance(response.parsed, CryptoProtoMessage):
                raise E2eeError("invalid_response")
            return response.parsed
        except E2eeError:
            raise
        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            ImportError,
        ):
            raise E2eeError("service_unavailable") from None
