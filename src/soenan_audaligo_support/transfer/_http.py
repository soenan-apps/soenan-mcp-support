from __future__ import annotations

import http.client
import math
import socket
import ssl
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import SplitResult, urlsplit


class TransferError(Exception):
    """A transfer failed without disclosing its bearer capability."""


class TransferSizeMismatch(TransferError):
    """A ciphertext byte count differs from the signed capability."""

    def __init__(self) -> None:
        super().__init__("ciphertext byte count does not match capability")


class TransferHTTPError(TransferError):
    """A direct control or Bucket endpoint returned an unsuccessful response."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"remote endpoint returned HTTP {status}")


class TransferTimeoutError(TransferError):
    """The configured direct Bucket transfer deadline elapsed."""

    def __init__(self) -> None:
        super().__init__("direct Bucket transfer deadline elapsed")


@dataclass(frozen=True)
class TransferTimeouts:
    """Finite connect, read, and total direct-transfer limits, in seconds."""

    connect: float = 10.0
    read: float = 30.0
    total: float = 300.0

    def __post_init__(self) -> None:
        for value in (self.connect, self.read, self.total):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError("transfer timeouts must be finite positive numbers")


@dataclass(frozen=True)
class TransferTransport:
    """Optional test/private-network connection override for a signed logical URL."""

    connect_host: str | None = None
    connect_port: int | None = None
    ca_file: str | Path | None = None

    def __post_init__(self) -> None:
        if (self.connect_host is None) != (self.connect_port is None):
            raise ValueError(
                "connect_host and connect_port must be configured together"
            )
        if self.connect_host is not None and not self.connect_host:
            raise ValueError("connect_host must be nonempty")
        if self.connect_port is not None and not 1 <= self.connect_port <= 65535:
            raise ValueError("connect_port must be between 1 and 65535")


DEFAULT_TIMEOUTS = TransferTimeouts()
DEFAULT_TRANSPORT = TransferTransport()
_ALLOWED_HEADERS = frozenset(
    {
        "content-type",
        "x-amz-checksum-sha256",
        "x-amz-content-sha256",
        "x-amz-server-side-encryption",
    }
)


def put_ciphertext(
    url: str,
    headers: Mapping[str, str],
    ciphertext: bytes,
    *,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> None:
    parsed = _parse_url(url)
    deadline = time.monotonic() + timeouts.total
    connection = _connection(parsed, timeouts, deadline, transport)
    watchdog = _deadline_watchdog(connection, deadline)
    try:
        connection.connect()
        _set_socket_timeout(connection, timeouts, deadline)
        connection.putrequest(
            "PUT", _request_target(parsed), skip_host=True, skip_accept_encoding=True
        )
        connection.putheader("Host", _authority(parsed))
        for name, value in _validated_headers(headers).items():
            connection.putheader(name, value)
        connection.putheader("Content-Length", str(len(ciphertext)))
        connection.endheaders()
        _set_socket_timeout(connection, timeouts, deadline)
        connection.send(ciphertext)
        _set_socket_timeout(connection, timeouts, deadline)
        response = connection.getresponse()
        try:
            if 300 <= response.status < 400:
                raise TransferHTTPError(response.status)
            if response.status not in (200, 204):
                raise TransferHTTPError(response.status)
            response.read(1)
        finally:
            response.close()
    except TransferError:
        raise
    except TimeoutError:
        raise TransferTimeoutError() from None
    except (OSError, http.client.HTTPException, ssl.SSLError):
        if time.monotonic() >= deadline:
            raise TransferTimeoutError() from None
        raise TransferError("direct Bucket upload failed") from None
    finally:
        watchdog.cancel()
        connection.close()


def get_ciphertext(
    url: str,
    headers: Mapping[str, str],
    expected_length: int,
    *,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> bytes:
    if expected_length <= 0:
        raise ValueError("expected_length must be positive")
    parsed = _parse_url(url)
    deadline = time.monotonic() + timeouts.total
    connection = _connection(parsed, timeouts, deadline, transport)
    watchdog = _deadline_watchdog(connection, deadline)
    try:
        connection.connect()
        _set_socket_timeout(connection, timeouts, deadline)
        connection.putrequest(
            "GET", _request_target(parsed), skip_host=True, skip_accept_encoding=True
        )
        connection.putheader("Host", _authority(parsed))
        for name, value in _validated_headers(headers).items():
            connection.putheader(name, value)
        connection.endheaders()
        _set_socket_timeout(connection, timeouts, deadline)
        response = connection.getresponse()
        try:
            if 300 <= response.status < 400:
                raise TransferHTTPError(response.status)
            if response.status != 200:
                raise TransferHTTPError(response.status)
            response_length = response.getheader("Content-Length")
            if (
                response_length is None
                or not response_length.isdecimal()
                or int(response_length) != expected_length
            ):
                raise TransferSizeMismatch()
            ciphertext = response.read(expected_length + 1)
            if len(ciphertext) != expected_length:
                raise TransferSizeMismatch()
            return ciphertext
        finally:
            response.close()
    except TransferError:
        raise
    except TimeoutError:
        raise TransferTimeoutError() from None
    except (OSError, http.client.HTTPException, ssl.SSLError):
        if time.monotonic() >= deadline:
            raise TransferTimeoutError() from None
        raise TransferError("direct Bucket download failed") from None
    finally:
        watchdog.cancel()
        connection.close()


def post_control_json(
    url: str,
    headers: Mapping[str, str],
    *,
    body: bytes = b"",
    allowed_headers: frozenset[str] = frozenset({"audaligo-key-claim"}),
    maximum_response_bytes: int,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> bytes:
    if len(body) > 1_048_576:
        raise TransferError("control-plane request exceeds its size limit")
    if not 1 <= maximum_response_bytes <= 1_048_576:
        raise ValueError("maximum_response_bytes is outside the control-plane limit")
    parsed = _parse_url(url)
    deadline = time.monotonic() + timeouts.total
    connection = _connection(parsed, timeouts, deadline, transport)
    watchdog = _deadline_watchdog(connection, deadline)
    try:
        connection.connect()
        _set_socket_timeout(connection, timeouts, deadline)
        connection.putrequest(
            "POST", _request_target(parsed), skip_host=True, skip_accept_encoding=True
        )
        connection.putheader("Host", _authority(parsed))
        for name, value in headers.items():
            if not isinstance(name, str) or not isinstance(value, str):
                raise TransferError("control-plane header is invalid")
            normalized_name = name.lower()
            if (
                normalized_name not in allowed_headers
                or not value
                or len(value) > 8_192
                or any(character in value for character in ("\r", "\n", "\x00"))
            ):
                raise TransferError("control-plane header is invalid")
            connection.putheader(name, value)
        connection.putheader("Content-Length", str(len(body)))
        connection.endheaders()
        if body:
            connection.send(body)
        response = connection.getresponse()
        try:
            if 300 <= response.status < 400:
                raise TransferHTTPError(response.status)
            if response.status != 200:
                raise TransferHTTPError(response.status)
            response_body = response.read(maximum_response_bytes + 1)
            if len(response_body) > maximum_response_bytes:
                raise TransferError("key claim response exceeds its size limit")
            return response_body
        finally:
            response.close()
    except TransferError:
        raise
    except TimeoutError:
        raise TransferTimeoutError() from None
    except (OSError, http.client.HTTPException, ssl.SSLError):
        if time.monotonic() >= deadline:
            raise TransferTimeoutError() from None
        raise TransferError("key claim redemption failed") from None
    finally:
        watchdog.cancel()
        connection.close()


def _parse_url(url: str) -> SplitResult:
    if not isinstance(url, str) or not url or len(url) > 8192 or "#" in url:
        raise TransferError("Bucket capability URL is invalid")
    parsed = urlsplit(url)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise TransferError("Bucket capability URL is invalid")
    try:
        _ = parsed.port
    except ValueError:
        raise TransferError("Bucket capability URL is invalid") from None
    if parsed.path == "" or any(character in url for character in ("\r", "\n", "\x00")):
        raise TransferError("Bucket capability URL is invalid")
    return parsed


def _validated_headers(headers: Mapping[str, str]) -> dict[str, str]:
    if not isinstance(headers, Mapping) or len(headers) > len(_ALLOWED_HEADERS):
        raise TransferError("Bucket capability headers are invalid")
    validated: dict[str, str] = {}
    for raw_name, raw_value in headers.items():
        if not isinstance(raw_name, str) or not isinstance(raw_value, str):
            raise TransferError("Bucket capability headers are invalid")
        name = raw_name.lower()
        if name not in _ALLOWED_HEADERS or name in validated:
            raise TransferError("Bucket capability headers are invalid")
        if (
            not raw_value
            or len(raw_value) > 1024
            or any(character in raw_value for character in ("\r", "\n", "\x00"))
        ):
            raise TransferError("Bucket capability headers are invalid")
        validated[name] = raw_value
    return validated


def _connection(
    parsed: SplitResult,
    timeouts: TransferTimeouts,
    deadline: float,
    transport: TransferTransport,
) -> http.client.HTTPConnection:
    logical_host = parsed.hostname
    if logical_host is None:
        raise TransferError("Bucket capability URL is invalid")
    logical_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    connect_host = transport.connect_host or logical_host
    connect_port = transport.connect_port or logical_port
    timeout = min(timeouts.connect, _remaining(deadline))
    if parsed.scheme == "https":
        context = ssl.create_default_context(
            cafile=str(transport.ca_file) if transport.ca_file else None
        )
        return _LogicalHTTPSConnection(
            logical_host=logical_host,
            connect_host=connect_host,
            connect_port=connect_port,
            timeout=timeout,
            context=context,
        )
    return http.client.HTTPConnection(connect_host, connect_port, timeout=timeout)


class _LogicalHTTPSConnection(http.client.HTTPSConnection):
    def __init__(
        self,
        *,
        logical_host: str,
        connect_host: str,
        connect_port: int,
        timeout: float,
        context: ssl.SSLContext,
    ) -> None:
        super().__init__(logical_host, connect_port, timeout=timeout, context=context)
        self._connect_host = connect_host
        self._connect_port = connect_port

    def connect(self) -> None:
        raw_socket = socket.create_connection(
            (self._connect_host, self._connect_port), self.timeout, self.source_address
        )
        if self._tunnel_host:
            self.sock = raw_socket
            self._tunnel()
        self.sock = self._context.wrap_socket(raw_socket, server_hostname=self.host)


def _request_target(parsed: SplitResult) -> str:
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def _authority(parsed: SplitResult) -> str:
    hostname = parsed.hostname
    if hostname is None:
        raise TransferError("Bucket capability URL is invalid")
    default_port = 443 if parsed.scheme == "https" else 80
    return (
        hostname if parsed.port in (None, default_port) else f"{hostname}:{parsed.port}"
    )


def _set_socket_timeout(
    connection: http.client.HTTPConnection,
    timeouts: TransferTimeouts,
    deadline: float,
) -> None:
    if connection.sock is not None:
        connection.sock.settimeout(min(timeouts.read, _remaining(deadline)))


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TransferTimeoutError()
    return remaining


def _deadline_watchdog(
    connection: http.client.HTTPConnection, deadline: float
) -> threading.Timer:
    def expire() -> None:
        connection.close()

    timer = threading.Timer(max(0.0, deadline - time.monotonic()), expire)
    timer.daemon = True
    timer.start()
    return timer
