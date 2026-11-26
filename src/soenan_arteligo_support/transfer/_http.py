from __future__ import annotations

import http.client
import math
import socket
import ssl
import threading
import time
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from urllib.parse import SplitResult, urlsplit


class TransferError(Exception):
    """A transfer failed without disclosing its bearer capability."""

    code = "transfer_failed"
    recoverable = False

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        recoverable: bool | None = None,
    ) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code
        if recoverable is not None:
            self.recoverable = recoverable

    def wire_value(self) -> dict[str, object]:
        return {
            "error": {
                "code": self.code,
                "message": str(self),
                "recoverable": self.recoverable,
            }
        }


class TransferSizeMismatch(TransferError):
    """A local or remote byte count differs from the authorized descriptor."""

    code = "size_mismatch"

    def __init__(
        self, message: str = "ciphertext byte count does not match capability"
    ) -> None:
        super().__init__(message)


class TransferHTTPError(TransferError):
    """A direct control or Bucket endpoint returned an unsuccessful response."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(
            f"remote endpoint returned HTTP {status}",
            code="authorization_expired" if status in {401, 403} else "remote_error",
            recoverable=status in {401, 403, 408, 429, 500, 502, 503, 504},
        )


class TransferTimeoutError(TransferError):
    """The configured direct transfer deadline elapsed."""

    code = "timeout"
    recoverable = True

    def __init__(self) -> None:
        super().__init__("direct transfer deadline elapsed")


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
_COPY_SIZE = 256 * 1024
_DEFAULT_DOWNLOAD_BYTES_PER_SECOND = 512 * 1024


def put_ciphertext(
    url: str,
    headers: Mapping[str, str],
    ciphertext: BinaryIO,
    length: int,
    *,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> None:
    with _bucket_response(
        "PUT", url, headers, timeouts, transport, upload=(ciphertext, length)
    ) as (response, deadline):
        if response.status not in (200, 204):
            raise TransferHTTPError(response.status)
        response.read(1)
        _remaining(deadline)


@contextmanager
def get_ciphertext(
    url: str,
    headers: Mapping[str, str],
    expected_length: int,
    *,
    timeouts: TransferTimeouts,
    transport: TransferTransport,
) -> Generator[Callable[[int], bytes], None, None]:
    total = timeouts.total
    if timeouts is DEFAULT_TIMEOUTS:
        total = max(
            total,
            timeouts.connect + expected_length / _DEFAULT_DOWNLOAD_BYTES_PER_SECOND,
        )
    with _bucket_response("GET", url, headers, timeouts, transport, total=total) as (
        response,
        deadline,
    ):
        if response.status != 200:
            raise TransferHTTPError(response.status)
        if (
            response.headers.get_all("Content-Length") != [str(expected_length)]
            or response.getheader("Content-Range") is not None
            or response.getheader("Transfer-Encoding") is not None
        ):
            raise TransferSizeMismatch()

        def read(length: int) -> bytes:
            data = response.read(length)
            _remaining(deadline)
            return data

        yield read
        if response.length != 0 or read(1):
            raise TransferSizeMismatch()


@contextmanager
def _bucket_response(
    method: str,
    url: str,
    headers: Mapping[str, str],
    timeouts: TransferTimeouts,
    transport: TransferTransport,
    *,
    upload: tuple[BinaryIO, int] | None = None,
    total: float | None = None,
) -> Generator[tuple[http.client.HTTPResponse, float], None, None]:
    parsed = _parse_url(url, transport)
    deadline = time.monotonic() + (timeouts.total if total is None else total)
    connection = _connection(parsed, timeouts, deadline, transport)
    watchdog = None
    try:
        connection.connect()
        watchdog = _deadline_watchdog(connection, deadline)
        _set_socket_timeout(connection, timeouts, deadline)
        connection.putrequest(
            method, _request_target(parsed), skip_host=True, skip_accept_encoding=True
        )
        connection.putheader("Host", _authority(parsed))
        for name, value in headers.items():
            connection.putheader(name, value)
        if upload is not None:
            ciphertext, length = upload
            connection.putheader("Content-Length", str(length))
        connection.endheaders()
        if upload is not None:
            remaining = length
            while remaining:
                block = ciphertext.read(min(remaining, _COPY_SIZE))
                if not block:
                    raise TransferSizeMismatch()
                _set_socket_timeout(connection, timeouts, deadline)
                connection.send(block)
                remaining -= len(block)
        _set_socket_timeout(connection, timeouts, deadline)
        with connection.getresponse() as response:
            _remaining(deadline)
            yield response, deadline
            _remaining(deadline)
    except TimeoutError:
        raise TransferTimeoutError() from None
    except (OSError, http.client.HTTPException):
        if time.monotonic() >= deadline:
            raise TransferTimeoutError() from None
        raise TransferError("direct Bucket transfer failed") from None
    finally:
        if watchdog is not None:
            watchdog.cancel()
            watchdog.join()
        connection.close()


def _parse_url(url: str, transport: TransferTransport) -> SplitResult:
    if not isinstance(url, str) or not url or "#" in url:
        raise TransferError("Bucket capability URL is invalid")
    try:
        parsed = urlsplit(url)
    except ValueError:
        raise TransferError("Bucket capability URL is invalid") from None
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise TransferError("Bucket capability URL is invalid")
    try:
        port = parsed.port
    except ValueError:
        raise TransferError("Bucket capability URL is invalid") from None
    if port is not None and not 1 <= port <= 65535:
        raise TransferError("Bucket capability URL is invalid")
    if parsed.scheme == "http" and (
        not _is_loopback(parsed.hostname)
        or (
            transport.connect_host is not None
            and not _is_loopback(transport.connect_host)
        )
    ):
        raise TransferError("Bucket capability URL must use HTTPS")
    if parsed.path == "" or any(character in url for character in ("\r", "\n", "\x00")):
        raise TransferError("Bucket capability URL is invalid")
    return parsed


def _is_loopback(host: str) -> bool:
    return host.lower() in {"localhost", "127.0.0.1", "::1"}


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


class _LogicalHTTPSConnection(http.client.HTTPConnection):
    def __init__(
        self,
        *,
        logical_host: str,
        connect_host: str,
        connect_port: int,
        timeout: float,
        context: ssl.SSLContext,
    ) -> None:
        super().__init__(logical_host, connect_port, timeout=timeout)
        self._connect_host = connect_host
        self._connect_port = connect_port
        self._tls_context = context

    def connect(self) -> None:
        raw_socket = socket.create_connection(
            (self._connect_host, self._connect_port), self.timeout
        )
        self.sock = self._tls_context.wrap_socket(raw_socket, server_hostname=self.host)


def _request_target(parsed: SplitResult) -> str:
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def _authority(parsed: SplitResult) -> str:
    hostname = parsed.hostname
    if hostname is None:
        raise TransferError("Bucket capability URL is invalid")
    default_port = 443 if parsed.scheme == "https" else 80
    authority_host = f"[{hostname}]" if ":" in hostname else hostname
    return (
        authority_host
        if parsed.port in (None, default_port)
        else f"{authority_host}:{parsed.port}"
    )


def _set_socket_timeout(
    connection: http.client.HTTPConnection,
    timeouts: TransferTimeouts,
    deadline: float,
) -> None:
    remaining = _remaining(deadline)
    if connection.sock is not None:
        connection.sock.settimeout(min(timeouts.read, remaining))


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TransferTimeoutError()
    return remaining


def _deadline_watchdog(
    connection: http.client.HTTPConnection, deadline: float
) -> threading.Timer:
    connected_socket = connection.sock

    def expire() -> None:
        if connected_socket is not None:
            try:
                connected_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    timer = threading.Timer(max(0.0, deadline - time.monotonic()), expire)
    timer.daemon = True
    timer.start()
    return timer
