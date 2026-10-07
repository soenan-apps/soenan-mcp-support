from __future__ import annotations

import importlib
import json
import re
from enum import Enum
from typing import Any, Protocol, get_args, get_type_hints

import httpx

from ._crypto import E2eeError
from ._oauth import OAuthSession


class E2eeAPI(Protocol):
    def call(
        self, operation: str, *, body: dict[str, Any] | None = None, **parameters: Any
    ) -> dict[str, Any]: ...


class GeneratedAPI:
    """Transport adapter over the product-owned, generated public API client."""

    def __init__(
        self, oauth: OAuthSession, *, transport: httpx.BaseTransport | None = None
    ):
        self.oauth = oauth
        self.transport = transport

    def call(
        self, operation: str, *, body: dict[str, Any] | None = None, **parameters: Any
    ) -> dict[str, Any]:
        from arteligo_public_api_client.client import AuthenticatedClient

        if operation == "getProductSession":
            module_name = "session.get_product_session"
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
                base_url=self.oauth.arteligo_origin,
                token=self.oauth.access_token(),
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
                        "service_terms_acceptance_required",
                        "content_format_update_required",
                    }:
                        code = detail
                except (ValueError, AttributeError):
                    pass
                raise E2eeError(code)
            if len(response.content) > 16 * 1024 * 1024:
                raise E2eeError("limit_exceeded")
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
