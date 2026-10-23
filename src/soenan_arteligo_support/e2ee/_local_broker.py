from __future__ import annotations

import base64
import ctypes
import hmac
import json
import math
import os
import secrets
import signal
import socket
import stat
import struct
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import anyio

from ._crypto import E2eeError
from ._file_boundary import FileBoundary

if TYPE_CHECKING:
    from ._session import DeviceSession


@dataclass(frozen=True)
class LocalGrantHandle:
    socket_path: str
    grant_id: str
    broker_pid: int
    uid: int
    expires_at: float

    def encode(self) -> str:
        raw = json.dumps(self.__dict__, separators=(",", ":"), allow_nan=False).encode()
        return "alg1." + base64.urlsafe_b64encode(raw).decode().rstrip("=")

    @classmethod
    def parse(cls, value: str) -> LocalGrantHandle:
        try:
            if not value.startswith("alg1."):
                raise ValueError
            encoded = value[5:]
            raw = base64.b64decode(encoded + "=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
            data = _json(raw)
            if not isinstance(data, dict) or set(data) != {
                "socket_path", "grant_id", "broker_pid", "uid", "expires_at",
            }:
                raise ValueError
            if (
                not isinstance(data["socket_path"], str)
                or not os.path.isabs(data["socket_path"])
                or "\0" in data["socket_path"]
                or not isinstance(data["grant_id"], str) or len(data["grant_id"]) != 43
                or type(data["broker_pid"]) is not int or data["broker_pid"] <= 0
                or type(data["uid"]) is not int or data["uid"] < 0
                or type(data["expires_at"]) not in (int, float)
                or not math.isfinite(data["expires_at"])
            ):
                raise ValueError
            handle = cls(**data)
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, OverflowError):
            raise E2eeError("invalid_local_grant_handle") from None
        if handle.expires_at <= time.time():
            raise E2eeError("local_grant_expired")
        return handle


@dataclass
class MemoryGrant:
    projects: frozenset[str]
    access: Literal["read-only", "update"]
    expires_in: int
    expires_at: float = field(init=False)
    deadline: float = field(init=False)
    _revoked: threading.Event = field(default_factory=threading.Event, init=False)
    _reason: str = field(default="local_grant_revoked", init=False)

    def __post_init__(self) -> None:
        if (
            not self.projects or any(not isinstance(value, str) or not value for value in self.projects)
            or self.access not in {"read-only", "update"}
            or type(self.expires_in) is not int or not 0 < self.expires_in <= 86400
        ):
            raise E2eeError("invalid_local_grant")
        self.expires_at = time.time() + self.expires_in
        self.deadline = time.monotonic() + self.expires_in

    def require_active(self) -> None:
        if time.monotonic() >= self.deadline:
            raise E2eeError("local_grant_expired")
        if self._revoked.is_set():
            raise E2eeError(self._reason)

    def authorize(self, project: str, *, update: bool) -> None:
        self.require_active()
        if project not in self.projects:
            raise E2eeError("project_not_granted")
        if update and self.access != "update":
            raise E2eeError("update_not_granted")

    def revoke(self, reason: str = "local_grant_revoked") -> None:
        if not self._revoked.is_set():
            self._reason = reason
            self._revoked.set()


def _json(raw: bytes) -> Any:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    def invalid_constant(_):
        raise ValueError

    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid_constant)


def _receive(connection: socket.socket) -> Any:
    def exact(length: int) -> bytes:
        data = bytearray()
        while len(data) < length:
            part = connection.recv(min(length - len(data), 1024 * 1024))
            if not part:
                raise EOFError
            data.extend(part)
        return bytes(data)

    length = struct.unpack("!Q", exact(8))[0]
    if not 0 < length <= sys.maxsize:
        raise E2eeError("invalid_local_broker_request")
    try:
        return _json(exact(length))
    except (ValueError, UnicodeError, RecursionError):
        raise E2eeError("invalid_local_broker_request") from None


def _send(connection: socket.socket, value: Any) -> None:
    raw = json.dumps(value, separators=(",", ":"), allow_nan=False).encode()
    connection.sendall(struct.pack("!Q", len(raw)))
    connection.sendall(raw)


def _peer(connection: socket.socket) -> tuple[int, int | None]:
    if hasattr(socket, "SO_PEERCRED"):
        pid, uid, _ = struct.unpack(
            "iII", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("iII"))
        )
        return uid, pid
    libc = ctypes.CDLL(None, use_errno=True)
    getpeereid = getattr(libc, "getpeereid", None)
    if getpeereid is None:
        raise E2eeError("local_peer_identity_unavailable")
    uid, gid = ctypes.c_uint(), ctypes.c_uint()
    if getpeereid(connection.fileno(), ctypes.byref(uid), ctypes.byref(gid)) != 0:
        raise E2eeError("local_peer_identity_unavailable")
    return uid.value, None


class LocalBrokerClient:
    def __init__(self, handle: LocalGrantHandle):
        self.handle = handle
        self._lock = threading.Lock()
        self._closed = False
        self._sequence = 0
        self._connection: socket.socket | None = None
        if not hasattr(os, "getuid") or not hasattr(socket, "AF_UNIX") or handle.uid != os.getuid():
            raise E2eeError("local_broker_unavailable")
        try:
            path = Path(handle.socket_path)
            directory = path.parent.lstat()
            endpoint = path.lstat()
            if (
                not stat.S_ISDIR(directory.st_mode) or directory.st_uid != handle.uid
                or stat.S_IMODE(directory.st_mode) != 0o700
                or not stat.S_ISSOCK(endpoint.st_mode) or endpoint.st_uid != handle.uid
                or stat.S_IMODE(endpoint.st_mode) != 0o600
            ):
                raise E2eeError("unsafe_local_broker_endpoint")
            connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._connection = connection
            connection.settimeout(min(10.0, max(0.001, handle.expires_at - time.time())))
            connection.connect(handle.socket_path)
            uid, pid = _peer(connection)
            if uid != handle.uid or (pid is not None and pid != handle.broker_pid):
                raise E2eeError("invalid_local_broker_peer")
            _send(connection, {"version": 1, "grant_id": handle.grant_id})
            response = _receive(connection)
            if response != {"ready": True}:
                raise E2eeError("invalid_local_broker_handshake")
            connection.settimeout(None)
        except (EOFError, OSError):
            self.close()
            raise E2eeError("local_grant_connection_closed") from None
        except BaseException:
            self.close()
            raise

    def request(self, method: Literal["list_tools", "call_tool"], **parameters: Any) -> Any:
        with self._lock:
            if self._closed or self._connection is None:
                raise E2eeError("local_grant_connection_closed")
            if time.time() >= self.handle.expires_at:
                self.close()
                raise E2eeError("local_grant_expired")
            self._sequence += 1
            connection = self._connection
            try:
                _send(connection, {"id": self._sequence, "method": method, **parameters})
                response = _receive(connection)
                if not isinstance(response, dict) or response.get("id") != self._sequence:
                    raise E2eeError("invalid_local_broker_response")
                if set(response) == {"id", "error"} and isinstance(response["error"], str):
                    raise E2eeError(response["error"])
                if set(response) != {"id", "result"}:
                    raise E2eeError("invalid_local_broker_response")
                return response["result"]
            except (EOFError, OSError):
                self.close()
                code = "local_grant_expired" if time.time() >= self.handle.expires_at else "local_grant_connection_closed"
                raise E2eeError(code) from None

    def close(self) -> None:
        self._closed = True
        connection, self._connection = self._connection, None
        if connection is not None:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()


def serve_local_grant(
    session: DeviceSession,
    grant: MemoryGrant,
    files: FileBoundary,
    announce: Callable[[LocalGrantHandle], None],
) -> None:
    from ._mcp import _broker_operations

    if not hasattr(os, "getuid") or not hasattr(socket, "AF_UNIX"):
        raise E2eeError("local_broker_unavailable")
    operations = _broker_operations(session, grant, files)
    active: list[socket.socket] = []
    previous_signals = {}
    with tempfile.TemporaryDirectory(prefix="arteligo-grant-") as directory:
        os.chmod(directory, 0o700)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
            path = str(Path(directory) / "broker.sock")
            listener.bind(path)
            os.chmod(path, 0o600)
            listener.listen(1)
            listener.settimeout(max(0.001, grant.deadline - time.monotonic()))
            handle = LocalGrantHandle(path, secrets.token_urlsafe(32), os.getpid(), os.getuid(), grant.expires_at)

            def stop(reason="local_grant_revoked"):
                grant.revoke(reason)
                try:
                    listener.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                listener.close()
                for connection in active:
                    try:
                        connection.shutdown(socket.SHUT_RD)
                    except OSError:
                        pass

            if threading.current_thread() is threading.main_thread():
                signals = [signal.SIGINT, signal.SIGTERM]
                if hasattr(signal, "SIGHUP"):
                    signals.append(signal.SIGHUP)
                for signum in signals:
                    previous_signals[signum] = signal.signal(signum, lambda *_: stop())
            timer = threading.Timer(max(0, grant.deadline - time.monotonic()), stop, args=("local_grant_expired",))
            timer.daemon = True
            timer.start()
            def serve_connection() -> None:
                try:
                    connection, _ = listener.accept()
                except (OSError, TimeoutError):
                    grant.require_active()
                    return
                with connection:
                    active.append(connection)
                    uid, _ = _peer(connection)
                    if uid != handle.uid:
                        raise E2eeError("invalid_local_broker_peer")
                    connection.settimeout(min(10.0, max(0.001, grant.deadline - time.monotonic())))
                    hello = _receive(connection)
                    if (
                        not isinstance(hello, dict) or set(hello) != {"version", "grant_id"}
                        or type(hello["version"]) is not int or hello["version"] != 1
                        or not isinstance(hello["grant_id"], str)
                        or not hmac.compare_digest(hello["grant_id"], handle.grant_id)
                    ):
                        raise E2eeError("invalid_local_broker_handshake")
                    grant.require_active()
                    _send(connection, {"ready": True})
                    listener.close()
                    connection.settimeout(None)
                    while True:
                        grant.require_active()
                        try:
                            request = _receive(connection)
                        except (EOFError, OSError):
                            break
                        identifier = request.get("id") if isinstance(request, dict) else None
                        try:
                            grant.require_active()
                            if type(identifier) is not int or identifier <= 0:
                                raise E2eeError("invalid_local_broker_request")
                            if request.get("method") == "list_tools" and set(request) == {"id", "method"}:
                                result = operations.describe()
                            elif request.get("method") == "call_tool" and set(request) == {"id", "method", "name", "arguments"}:
                                result = operations.invoke(request["name"], request["arguments"])
                            else:
                                raise E2eeError("invalid_local_broker_request")
                            response = {"id": identifier, "result": result}
                        except E2eeError as error:
                            response = {"id": identifier, "error": error.code}
                        try:
                            connection.settimeout(30.0)
                            _send(connection, response)
                            connection.settimeout(None)
                        except (OSError, EOFError):
                            break

            try:
                announce(handle)
                anyio.run(anyio.to_thread.run_sync, serve_connection)
            except (EOFError, OSError):
                pass
            except E2eeError as error:
                if error.code not in {"local_grant_expired", "local_grant_revoked"}:
                    raise
            finally:
                timer.cancel()
                stop("local_grant_connection_closed")
                active.clear()
                for signum, handler in previous_signals.items():
                    signal.signal(signum, handler)
