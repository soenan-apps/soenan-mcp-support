from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from ._http import (
    DEFAULT_TIMEOUTS,
    DEFAULT_TRANSPORT,
    TransferError,
    TransferTimeouts,
    TransferTransport,
    post_control_json,
)

_PROTOCOL_VERSION = "2026-07-28"
_ALLOWED_HEADERS = frozenset(
    {
        "authorization",
        "content-type",
        "accept",
        "mcp-protocol-version",
        "mcp-method",
        "mcp-name",
    }
)


@dataclass
class MCPHTTPToolCaller:
    """Synchronous stateless MCP tool caller used by the transfer CLI."""

    endpoint: str
    access_token: str = field(repr=False)
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS
    transport: TransferTransport = DEFAULT_TRANSPORT
    _request_id: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        parsed = urlsplit(self.endpoint)
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or not parsed.path.endswith("/mcp")
        ):
            raise ValueError("MCP endpoint must be an absolute /mcp URL")
        if (
            not self.access_token
            or len(self.access_token) > 8192
            or any(character in self.access_token for character in ("\r", "\n", "\x00"))
        ):
            raise ValueError("MCP access token is invalid")

    def __call__(
        self, name: str, arguments: Mapping[str, object]
    ) -> Mapping[str, Any]:
        if not name or len(name) > 128:
            raise TransferError("MCP tool name is invalid")
        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": _PROTOCOL_VERSION,
                    "io.modelcontextprotocol/clientCapabilities": {},
                },
                "name": name,
                "arguments": dict(arguments),
            },
        }
        encoded_request = json.dumps(
            request, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
        encoded_response = post_control_json(
            self.endpoint,
            {
                "authorization": f"Bearer {self.access_token}",
                "content-type": "application/json",
                "accept": "application/json, text/event-stream",
                "mcp-protocol-version": _PROTOCOL_VERSION,
                "mcp-method": "tools/call",
                "mcp-name": name,
            },
            body=encoded_request,
            allowed_headers=_ALLOWED_HEADERS,
            maximum_response_bytes=1_048_576,
            timeouts=self.timeouts,
            transport=self.transport,
        )
        try:
            response = json.loads(encoded_response, object_pairs_hook=_strict_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raise TransferError("MCP returned invalid JSON") from None
        if not isinstance(response, Mapping) or response.get("id") != self._request_id:
            raise TransferError("MCP returned an invalid response")
        if "error" in response:
            raise TransferError("MCP tool call failed")
        result = response.get("result")
        if not isinstance(result, Mapping):
            raise TransferError("MCP returned an invalid tool result")
        content = result.get("content")
        if (
            not isinstance(content, list)
            or len(content) != 1
            or not isinstance(content[0], Mapping)
            or content[0].get("type") != "text"
            or not isinstance(content[0].get("text"), str)
        ):
            raise TransferError("MCP returned an invalid tool result")
        try:
            value = json.loads(content[0]["text"], object_pairs_hook=_strict_object)
        except (json.JSONDecodeError, ValueError):
            raise TransferError("MCP returned invalid tool data") from None
        if not isinstance(value, Mapping):
            raise TransferError("MCP returned invalid tool data")
        return value


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value
