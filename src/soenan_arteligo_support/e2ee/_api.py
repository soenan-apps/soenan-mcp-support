from __future__ import annotations

import importlib
import json
import re
from enum import Enum
from typing import Any, Iterator, Protocol, get_args, get_type_hints

import httpx

from ._crypto import E2eeError
from ._oauth import BoundCredentials


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
    def call(
        self, operation: str, *, body: dict[str, Any] | None = None, **parameters: Any
    ) -> dict[str, Any]: ...
    def stream(self, operation: str, *, body: dict[str, Any]) -> Iterator[dict[str, Any]]: ...


def await_session_authorization(arteligo_origin: str, token: str,
                                transport: httpx.BaseTransport | None) -> dict[str, Any]:
    from arteligo_public_api_client.api.session import await_session_authorization as endpoint
    from arteligo_public_api_client.client import AuthenticatedClient

    try:
        with AuthenticatedClient(
            base_url=arteligo_origin, token=token, timeout=httpx.Timeout(30),
            follow_redirects=False, raise_on_unexpected_status=False,
            httpx_args={"transport": transport},
        ) as client:
            response = endpoint.sync_detailed(client=client)
        if int(response.status_code) == 401:
            raise E2eeError("authorization_expired")
        if int(response.status_code) == 403:
            raise E2eeError("authorization_denied")
        if int(response.status_code) != 200 or response.parsed is None:
            raise E2eeError("authorization_unavailable")
        value = response.parsed.to_dict()
        if (value.get("outcome") not in {"ready", "delivery_pending", "expired", "source_behind", "denied"}
                or not isinstance(value.get("denied_organization_ids"), list)
                or any(not isinstance(item, str) or not item for item in value["denied_organization_ids"])
                or type(value.get("expires_at_unix_seconds")) is not int
                or not isinstance(value.get("access_token_id"), str) or not value["access_token_id"]):
            raise E2eeError("invalid_authorization_response")
        error = {"delivery_pending": "authorization_delivery_pending", "expired": "authorization_expired",
                 "source_behind": "authorization_source_behind", "denied": "authorization_denied"}.get(value["outcome"])
        if error is not None:
            raise E2eeError(error)
        return value
    except E2eeError:
        raise
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError, ImportError):
        raise E2eeError("authorization_unavailable") from None


class GeneratedAPI:
    """Transport adapter over the product-owned, generated public API client."""

    def __init__(
        self, credentials: BoundCredentials, *, transport: httpx.BaseTransport | None = None
    ):
        self.credentials = credentials
        self.transport = transport

    def stream(self, operation: str, *, body: dict[str, Any]) -> Iterator[dict[str, Any]]:
        if operation != "e2eePrepareRootReplacement":
            raise E2eeError("unsupported_operation")
        from arteligo_public_api_client.client import AuthenticatedClient
        from ._root_wire import root_events, root_input

        try:
            content = root_input(body["operation_id"], body, prepare=True)
            client = AuthenticatedClient(
                base_url=self.credentials.arteligo_origin,
                token=self.credentials.access_token(), timeout=httpx.Timeout(30),
                follow_redirects=False, raise_on_unexpected_status=False,
                httpx_args={"transport": self.transport},
            )
            with client, client.get_httpx_client().stream(
                "POST", "/api/e2ee/root-replacements/prepare", content=content,
                headers={"Content-Type": "application/x-ndjson", "Accept": "text/event-stream"},
            ) as response:
                if response.status_code != 200:
                    raise E2eeError("root_replacement_preparation_failed")
                yield from root_events(sse_documents(response))
        except E2eeError:
            raise
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError, ImportError):
            raise E2eeError("service_unavailable") from None

    def _apply_root(self, operation_id: str, body: dict[str, Any]) -> dict[str, Any]:
        from arteligo_public_api_client.client import AuthenticatedClient
        from ._root_wire import root_input

        if re.fullmatch(r"[A-Za-z0-9_-]{1,128}", operation_id) is None:
            raise E2eeError("invalid_recovery_replacement")
        try:
            client = AuthenticatedClient(
                base_url=self.credentials.arteligo_origin, token=self.credentials.access_token(),
                timeout=httpx.Timeout(30), follow_redirects=False, raise_on_unexpected_status=False,
                httpx_args={"transport": self.transport},
            )
            with client:
                response = client.get_httpx_client().post(
                    f"/api/e2ee/root-replacements/{operation_id}/apply",
                    content=root_input(operation_id, body, prepare=False),
                    headers={"Content-Type": "application/x-ndjson", "Accept": "application/json"},
                )
            if response.status_code != 200:
                raise E2eeError("recovery_replacement_pending")
            value = response.json()
            if not isinstance(value, dict):
                raise E2eeError("invalid_response")
            return value
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
            raise E2eeError("recovery_replacement_pending") from None

    def call(
        self, operation: str, *, body: dict[str, Any] | None = None, **parameters: Any
    ) -> dict[str, Any]:
        from arteligo_public_api_client.client import AuthenticatedClient
        if operation == "e2eeApplyRootReplacement" and body is not None:
            return self._apply_root(parameters["operation_id"], body)

        if operation == "getProductSession":
            module_name = "session.get_product_session"
        elif operation == "awaitSessionAuthorization":
            module_name = "session.await_session_authorization"
        elif operation.startswith("e2ee") and operation.isalnum():
            module_name = (
                "e2ee.e_2_ee" + re.sub(r"(?=[A-Z])", "_", operation[4:]).lower()
            )
        else:
            raise E2eeError("unsupported_operation")
        try:
            endpoint = importlib.import_module(
                "arteligo_public_api_client.api." + module_name
            )
            hints = get_type_hints(endpoint.sync_detailed)
            for name, value in parameters.items():
                hint = hints.get(name)
                candidates = get_args(hint) or (hint,)
                enum = next(
                    (
                        candidate
                        for candidate in candidates
                        if isinstance(candidate, type) and issubclass(candidate, Enum)
                    ),
                    None,
                )
                if enum is not None:
                    parameters[name] = enum(value)
            if body is not None:
                model = hints["body"]
                parameters["body"] = model.from_dict(body)
            client = AuthenticatedClient(
                base_url=self.credentials.arteligo_origin,
                token=self.credentials.access_token(),
                timeout=httpx.Timeout(30),
                follow_redirects=False,
                raise_on_unexpected_status=False,
                httpx_args={"transport": self.transport},
            )
            with client:
                response = endpoint.sync_detailed(client=client, **parameters)
            status = int(response.status_code)
            if not 200 <= status < 300:
                codes = {
                    400: "invalid_request",
                    401: "authentication_required",
                    403: "access_denied",
                    404: "not_found",
                    409: "revision_conflict",
                    429: "rate_limited",
                }
                code = codes.get(status, "service_unavailable")
                try:
                    failure = json.loads(response.content).get("error")
                    detail = (
                        failure.get("code") if isinstance(failure, dict) else failure
                    )
                    if detail in {
                        "limit_exceeded",
                        "quota_exceeded",
                        "rekey_required",
                        "device_revoked",
                        "project_access_denied",
                        "service_terms_acceptance_required",
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
                        "authorization_delivery_pending",
                        "authorization_unavailable",
                        "authorization_expired",
                        "authorization_source_behind",
                        "authorization_denied",
                        "authorization_reconciliation_required",
                    } and (detail != "project_access_denied" or status == 403):
                        code = detail
                except (ValueError, AttributeError):
                    pass
                raise E2eeError(code)
            if response.parsed is None:
                if status in {201, 204}:
                    return {}
                raise E2eeError("invalid_response")
            return response.parsed.to_dict()
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
