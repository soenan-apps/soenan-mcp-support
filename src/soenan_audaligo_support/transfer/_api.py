from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
from audaligo_public_api_client import Client
from audaligo_public_api_client.api.encrypted_objects import (
    commit_encrypted_project_file,
    complete_encrypted_object_chunks,
    create_chunk_upload_capability,
    get_chunk_read_capability,
    put_encrypted_object_manifest,
)
from audaligo_public_api_client.models.commit_project_file_request import (
    CommitProjectFileRequest,
)
from audaligo_public_api_client.models.put_manifest_request import PutManifestRequest
from audaligo_public_api_client.types import Response
from typing_extensions import Self

from ._http import TransferError, TransferTimeoutError, TransferTimeouts


class AudaligoTransferAPI:
    """Continuation-authorized access to Audaligo transfer control endpoints."""

    __slots__ = (
        "_client",
        "_continuation",
        "_operation_lock",
        "_origin",
        "_state_lock",
        "_terminal",
        "_total",
        "_transport_closing",
    )

    def __init__(
        self,
        *,
        control_origin: str,
        continuation: str,
        timeouts: TransferTimeouts,
        control_transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._origin = _validate_control_origin(control_origin)
        self._continuation = _validate_transfer_continuation(continuation)
        self._total = timeouts.total
        self._operation_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._terminal = False
        self._transport_closing = False
        self._client = Client(
            base_url=self._origin,
            timeout=httpx.Timeout(
                connect=min(timeouts.connect, timeouts.total),
                read=min(timeouts.read, timeouts.total),
                write=min(timeouts.read, timeouts.total),
                pool=min(timeouts.connect, timeouts.total),
            ),
            raise_on_unexpected_status=False,
            follow_redirects=False,
            httpx_args=(
                {} if control_transport is None else {"transport": control_transport}
            ),
        )

    def close(self) -> None:
        with self._state_lock:
            if self._terminal:
                return
            self._terminal = True
        done, errors = self._start_transport_close()
        if not done.wait(self._total):
            raise TransferTimeoutError() from None
        if errors:
            raise TransferError("Audaligo control client close failed") from None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object, **kwargs: Any) -> None:
        try:
            self.close()
        except TransferError:
            if not args or args[0] is None:
                raise

    def put_manifest(
        self,
        *,
        project_id: str,
        upload_id: str,
        manifest: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        response = self._request(
            put_encrypted_object_manifest.sync_detailed,
            project_id,
            upload_id,
            body=PutManifestRequest.from_dict({"manifest": dict(manifest)}),
            origin=self._origin,
            audaligo_transfer_continuation=self._continuation,
        )
        return self._body(response, HTTPStatus.OK, HTTPStatus.CREATED)

    def upload_capability(
        self,
        *,
        project_id: str,
        upload_id: str,
        chunk_index: int,
    ) -> Mapping[str, Any]:
        response = self._request(
            create_chunk_upload_capability.sync_detailed,
            project_id,
            upload_id,
            chunk_index,
            origin=self._origin,
            audaligo_transfer_continuation=self._continuation,
        )
        return self._capability(response)

    def complete_upload(
        self,
        *,
        project_id: str,
        upload_id: str,
    ) -> Mapping[str, Any]:
        response = self._request(
            complete_encrypted_object_chunks.sync_detailed,
            project_id,
            upload_id,
            origin=self._origin,
            audaligo_transfer_continuation=self._continuation,
        )
        return self._body(response, HTTPStatus.OK)

    def commit_file(
        self,
        *,
        project_id: str,
        file_id: str,
        upload_id: str,
        filename: str,
        plaintext_size: int,
    ) -> Mapping[str, Any]:
        value: dict[str, Any] = {
            "encryptedObjectId": upload_id,
            "fileKind": "project_file",
            "originalFilename": filename,
            "originalPlaintextSize": plaintext_size,
            "entryIntent": {
                "parentFolderId": None,
                "name": filename,
            },
        }
        response = self._request(
            commit_encrypted_project_file.sync_detailed,
            project_id,
            file_id,
            body=CommitProjectFileRequest.from_dict(value),
            origin=self._origin,
            audaligo_transfer_continuation=self._continuation,
        )
        return self._body(response, HTTPStatus.OK, HTTPStatus.CREATED)

    def read_capability(
        self,
        *,
        project_id: str,
        object_id: str,
        chunk_index: int,
    ) -> Mapping[str, Any]:
        response = self._request(
            get_chunk_read_capability.sync_detailed,
            project_id,
            object_id,
            chunk_index,
            audaligo_transfer_continuation=self._continuation,
        )
        return self._capability(response)

    def _request(
        self,
        operation: Callable[..., Response[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Response[Any]:
        deadline = time.monotonic() + self._total
        done = threading.Event()
        outcome: list[tuple[float, bool, object]] = []

        def run() -> None:
            try:
                with self._operation_lock:
                    with self._state_lock:
                        if self._terminal:
                            raise TransferError("Audaligo control client is closed")
                    value: object = operation(*args, client=self._client, **kwargs)
                success = True
            except Exception as error:  # noqa: BLE001
                # Generated clients do not share one response-decoding error hierarchy.
                value = error
                success = False
            outcome.append((time.monotonic(), success, value))
            done.set()

        threading.Thread(
            target=run,
            name="audaligo-transfer-control",
            daemon=True,
        ).start()
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not done.wait(remaining):
            self._expire()
            raise TransferTimeoutError() from None
        completed_at, success, value = outcome[0]
        if completed_at > deadline:
            self._expire()
            raise TransferTimeoutError() from None
        if success:
            return value  # type: ignore[return-value]
        self._raise_control_error(value)

    def _expire(self) -> None:
        with self._state_lock:
            self._terminal = True
        self._start_transport_close()

    def _start_transport_close(self) -> tuple[threading.Event, list[Exception]]:
        done = threading.Event()
        errors: list[Exception] = []
        with self._state_lock:
            if self._transport_closing:
                done.set()
                return done, errors
            self._transport_closing = True

        def close_transport() -> None:
            try:
                self._client.get_httpx_client().close()
            except Exception as error:  # noqa: BLE001
                # Custom transports do not share a narrower close-error hierarchy.
                errors.append(error)
            finally:
                done.set()

        threading.Thread(
            target=close_transport,
            name="audaligo-transfer-control-close",
            daemon=True,
        ).start()
        return done, errors

    @staticmethod
    def _raise_control_error(value: object) -> Any:
        if isinstance(value, httpx.TimeoutException):
            raise TransferTimeoutError() from None
        if isinstance(value, TransferError):
            raise value
        raise TransferError("Audaligo control request failed") from None

    @staticmethod
    def _body(response: Response[Any], *expected: HTTPStatus) -> Mapping[str, Any]:
        if response.status_code not in expected or response.parsed is None:
            raise TransferError(
                f"Audaligo control request returned HTTP {response.status_code}"
            )
        try:
            value = response.parsed.to_dict()
        except (AttributeError, TypeError, ValueError):
            raise TransferError("Audaligo control response is invalid") from None
        if not isinstance(value, Mapping):
            raise TransferError("Audaligo control response is invalid")
        return value

    @classmethod
    def _capability(cls, response: Response[Any]) -> Mapping[str, Any]:
        result = cls._body(response, HTTPStatus.OK).get("capability")
        if not isinstance(result, Mapping):
            raise TransferError("Audaligo control response is invalid")
        return result


_TRANSFER_CONTINUATION_PATTERN = re.compile(r"[A-Za-z0-9_-]{43}", re.ASCII)


def _validate_transfer_continuation(continuation: Any) -> str:
    if not isinstance(
        continuation, str
    ) or not _TRANSFER_CONTINUATION_PATTERN.fullmatch(continuation):
        raise TransferError("transfer continuation is invalid")
    return continuation


def _validate_control_origin(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise TransferError("control origin is invalid")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        raise TransferError("control origin is invalid") from None
    if (
        not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
        or (port is not None and not 1 <= port <= 65535)
    ):
        raise TransferError("control origin is invalid")
    if parsed.scheme != "https" and not (
        parsed.scheme == "http"
        and parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
    ):
        raise TransferError("control origin must use HTTPS")
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
