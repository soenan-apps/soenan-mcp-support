from __future__ import annotations

from dataclasses import dataclass
import http.client
import math
import os
from pathlib import Path
import socket
import tempfile
import time
from typing import BinaryIO, TypeAlias
from urllib.parse import urlsplit

from .descriptors import DownloadDescriptor, UploadDescriptor


PathSource: TypeAlias = str | os.PathLike[str]
UploadSource: TypeAlias = PathSource | BinaryIO
DownloadDestination: TypeAlias = PathSource | BinaryIO


class TransferError(Exception):
    """A transfer failed without disclosing its capability URL."""


class TransferSizeMismatch(TransferError):
    """The transferred plaintext byte count differs from the descriptor."""

    def __init__(self) -> None:
        super().__init__("transfer byte count does not match descriptor")


class TransferHTTPError(TransferError):
    """The transfer endpoint returned an unsuccessful response."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"transfer endpoint returned HTTP {status}")


class TransferTimeoutError(TransferError):
    """The configured transfer deadline elapsed."""

    def __init__(self) -> None:
        super().__init__("transfer deadline elapsed")


@dataclass(frozen=True)
class TransferTimeouts:
    """Finite network and whole-transfer time limits, in seconds."""

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


DEFAULT_TIMEOUTS = TransferTimeouts()
_CHUNK_SIZE = 64 * 1024


def upload_file(
    descriptor: UploadDescriptor,
    source: UploadSource,
    *,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
) -> int:
    """Stream plaintext from a path or binary stream to a one-time upload capability."""
    stream: BinaryIO
    close_stream = False
    if isinstance(source, (str, os.PathLike)):
        path = Path(source)
        if path.stat().st_size != descriptor.content_length:
            raise TransferSizeMismatch()
        stream = path.open("rb")
        close_stream = True
    else:
        stream = source
        _require_reader(stream)
        remaining_size = _remaining_stream_size(stream)
        if remaining_size is None:
            raise TypeError("source binary stream must be seekable")
        if remaining_size != descriptor.content_length:
            raise TransferSizeMismatch()

    deadline = time.monotonic() + timeouts.total
    connection = _connection(descriptor.url, timeouts, deadline)
    try:
        connection.connect()
        _set_socket_timeout(connection, timeouts, deadline)
        target = _request_target(descriptor.url)
        connection.putrequest("PUT", target, skip_accept_encoding=True)
        connection.putheader("Content-Type", descriptor.content_type)
        connection.putheader("Content-Length", str(descriptor.content_length))
        connection.putheader("Cache-Control", "no-store")
        connection.endheaders()

        sent = 0
        while sent < descriptor.content_length:
            _set_socket_timeout(connection, timeouts, deadline)
            chunk = stream.read(min(_CHUNK_SIZE, descriptor.content_length - sent))
            data = _binary_chunk(chunk)
            if not data or len(data) > descriptor.content_length - sent:
                raise TransferSizeMismatch()
            connection.send(data)
            sent += len(data)


        _set_socket_timeout(connection, timeouts, deadline)
        response = connection.getresponse()
        try:
            if 300 <= response.status < 400:
                raise TransferHTTPError(response.status)
            if response.status != 204:
                raise TransferHTTPError(response.status)
        finally:
            response.close()
        return sent
    except TransferError:
        raise
    except (TimeoutError, socket.timeout):
        raise TransferTimeoutError() from None
    except (OSError, http.client.HTTPException):
        raise TransferError("transfer endpoint communication failed") from None
    finally:
        connection.close()
        if close_stream:
            stream.close()


def download_file(
    descriptor: DownloadDescriptor,
    destination: DownloadDestination,
    *,
    timeouts: TransferTimeouts = DEFAULT_TIMEOUTS,
) -> int:
    """Stream plaintext to a path atomically or to a writable binary stream."""
    if isinstance(destination, (str, os.PathLike)):
        return _download_to_path(descriptor, Path(destination), timeouts)

    _require_writer(destination)
    rollback = _rollback_position(destination)
    try:
        return _download_to_stream(descriptor, destination, timeouts)
    except BaseException:
        _rollback_stream(destination, rollback)
        raise


def _download_to_path(
    descriptor: DownloadDescriptor, destination: Path, timeouts: TransferTimeouts
) -> int:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".part", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as stream:
            count = _download_to_stream(descriptor, stream, timeouts)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        return count
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def _download_to_stream(
    descriptor: DownloadDescriptor, destination: BinaryIO, timeouts: TransferTimeouts
) -> int:
    deadline = time.monotonic() + timeouts.total
    connection = _connection(descriptor.url, timeouts, deadline)
    try:
        connection.connect()
        _set_socket_timeout(connection, timeouts, deadline)
        connection.putrequest("GET", _request_target(descriptor.url), skip_accept_encoding=True)
        connection.putheader("Accept", descriptor.content_type)
        connection.putheader("Cache-Control", "no-store")
        connection.endheaders()
        _set_socket_timeout(connection, timeouts, deadline)
        response = connection.getresponse()
        try:
            if 300 <= response.status < 400:
                raise TransferHTTPError(response.status)
            if response.status != 200:
                raise TransferHTTPError(response.status)
            if response.getheader("Content-Type", "").lower() != descriptor.content_type:
                raise TransferError("transfer endpoint returned an invalid content type")
            if _response_length(response) != descriptor.content_length:
                raise TransferSizeMismatch()

            received = 0
            while True:
                _set_socket_timeout(connection, timeouts, deadline)
                try:
                    chunk = response.read(
                        min(_CHUNK_SIZE, descriptor.content_length - received + 1)
                    )
                except http.client.IncompleteRead:
                    raise TransferSizeMismatch() from None
                if not chunk:
                    break
                received += len(chunk)
                if received > descriptor.content_length:
                    raise TransferSizeMismatch()
                _write_all(destination, chunk)
            if received != descriptor.content_length:
                raise TransferSizeMismatch()
            return received
        finally:
            response.close()
    except TransferError:
        raise
    except (TimeoutError, socket.timeout):
        raise TransferTimeoutError() from None
    except (OSError, http.client.HTTPException):
        raise TransferError("transfer endpoint communication failed") from None
    finally:
        connection.close()


def _connection(
    url: str, timeouts: TransferTimeouts, deadline: float
) -> http.client.HTTPConnection:
    parsed = urlsplit(url)
    timeout = min(timeouts.connect, _remaining(deadline))
    if parsed.scheme == "https":
        return http.client.HTTPSConnection(parsed.hostname, parsed.port, timeout=timeout)
    return http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=timeout)


def _request_target(url: str) -> str:
    parsed = urlsplit(url)
    target = parsed.path or "/"
    if parsed.query:
        target += f"?{parsed.query}"
    return target


def _set_socket_timeout(
    connection: http.client.HTTPConnection, timeouts: TransferTimeouts, deadline: float
) -> None:
    remaining = _remaining(deadline)
    if connection.sock is not None:
        connection.sock.settimeout(min(timeouts.read, remaining))


def _remaining(deadline: float) -> float:
    value = deadline - time.monotonic()
    if value <= 0:
        raise TransferTimeoutError()
    return value




def _response_length(response: http.client.HTTPResponse) -> int:
    value = response.getheader("Content-Length")
    try:
        length = int(value) if value is not None else -1
    except ValueError:
        length = -1
    if length < 0:
        raise TransferSizeMismatch()
    return length


def _binary_chunk(value: object) -> bytes | bytearray | memoryview:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError("binary stream read() must return bytes")
    return value


def _write_all(stream: BinaryIO, data: bytes) -> None:
    remaining = memoryview(data)
    while remaining:
        written = stream.write(remaining)
        if not isinstance(written, int) or written <= 0:
            raise OSError("binary stream did not accept transfer bytes")
        remaining = remaining[written:]


def _require_reader(stream: object) -> None:
    if not callable(getattr(stream, "read", None)):
        raise TypeError("source must be a path or readable binary stream")


def _require_writer(stream: object) -> None:
    if not callable(getattr(stream, "write", None)):
        raise TypeError("destination must be a path or writable binary stream")


def _rollback_position(stream: BinaryIO) -> int | None:
    try:
        return stream.tell() if stream.seekable() else None
    except (AttributeError, OSError):
        return None


def _rollback_stream(stream: BinaryIO, position: int | None) -> None:
    if position is None:
        return
    try:
        stream.seek(position)
        stream.truncate()
    except (AttributeError, OSError):
        pass


def _remaining_stream_size(stream: BinaryIO) -> int | None:
    try:
        if not stream.seekable():
            return None
        position = stream.tell()
        end = stream.seek(0, os.SEEK_END)
        stream.seek(position)
        return end - position
    except (AttributeError, OSError):
        return None
