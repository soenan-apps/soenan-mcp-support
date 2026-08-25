from __future__ import annotations

import asyncio
import threading
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
from audaligo_public_api_client import AuthenticatedClient
from audaligo_public_api_client.api.encrypted_objects import (
    commit_encrypted_project_file,
    complete_encrypted_object_chunks,
    create_chunk_upload_capability,
    create_encrypted_object_upload,
    get_chunk_read_capability,
    get_encrypted_project_file_read_descriptor,
    put_encrypted_object_manifest,
)
from audaligo_public_api_client.models.commit_project_file_request import (
    CommitProjectFileRequest,
)
from audaligo_public_api_client.models.create_upload_request import CreateUploadRequest
from audaligo_public_api_client.models.put_manifest_request import PutManifestRequest
from audaligo_public_api_client.types import Response
from typing_extensions import Self

from ._http import TransferError, TransferTimeoutError, TransferTimeouts


class _AsyncRequest:
    __slots__ = (
        "_args",
        "_cancelled",
        "_kwargs",
        "_lock",
        "_operation",
        "_task",
        "completed",
    )

    def __init__(self, operation: Any, args: tuple[Any, ...], kwargs: dict[str, Any]):
        self._operation = operation
        self._args = args
        self._kwargs = kwargs
        self._lock = threading.Lock()
        self._task: asyncio.Task[Response[Any]] | None = None
        self._cancelled = False
        self.completed = threading.Event()

    def start(self) -> None:
        task = asyncio.create_task(self._invoke())
        with self._lock:
            self._task = task
            cancelled = self._cancelled
        task.add_done_callback(lambda _: self.completed.set())
        if cancelled:
            task.cancel()

    async def _invoke(self) -> Response[Any]:
        return await self._operation(*self._args, **self._kwargs)

    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True
            task = self._task
        if task is not None:
            task.cancel()

    def result(self) -> Response[Any]:
        with self._lock:
            task = self._task
        if task is None:
            raise RuntimeError("Audaligo API request did not start")
        return task.result()


class AudaligoTransferAPI:
    """Typed control-plane access generated from Audaligo's public OpenAPI contract."""

    __slots__ = (
        "_client",
        "_close_complete",
        "_closed",
        "_lifecycle_lock",
        "_loop",
        "_origin",
        "_thread",
        "_total_timeout",
    )

    def __init__(
        self,
        *,
        base_url: str,
        access_token: str,
        timeouts: TransferTimeouts,
        control_transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        parsed = urlsplit(base_url)
        try:
            port = parsed.port
        except ValueError:
            raise ValueError("Audaligo API URL is invalid") from None
        if (
            not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
            or (port is not None and not 1 <= port <= 65535)
        ):
            raise ValueError("Audaligo API URL is invalid")
        if parsed.scheme != "https" and not (
            parsed.scheme == "http"
            and parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
        ):
            raise ValueError("Audaligo API URL must use HTTPS")
        if len(access_token.encode("utf-8")) != 43:
            raise ValueError("Audaligo access token is invalid")
        self._origin = urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
        self._total_timeout = timeouts.total
        self._closed = False
        self._close_complete = threading.Event()
        self._lifecycle_lock = threading.Lock()
        self._client = AuthenticatedClient(
            base_url=self._origin,
            token=access_token,
            prefix="Bearer",
            timeout=httpx.Timeout(
                connect=timeouts.connect,
                read=timeouts.read,
                write=timeouts.read,
                pool=timeouts.connect,
            ),
            raise_on_unexpected_status=False,
            follow_redirects=False,
            httpx_args=(
                {} if control_transport is None else {"transport": control_transport}
            ),
        )
        self._loop = asyncio.new_event_loop()
        ready = threading.Event()

        def run_loop() -> None:
            asyncio.set_event_loop(self._loop)
            ready.set()
            self._loop.run_forever()

        self._thread = threading.Thread(
            target=run_loop,
            name="audaligo-transfer-control",
        )
        self._thread.start()
        ready.wait()

    def close(self) -> None:
        with self._lifecycle_lock:
            if self._closed:
                wait_for_close = True
            else:
                self._closed = True
                wait_for_close = False
        if wait_for_close:
            self._close_complete.wait()
            return
        close_error: BaseException | None = None
        try:
            future = asyncio.run_coroutine_threadsafe(self._close_async(), self._loop)
            future.result()
        # Third-party transports have no narrower close exception contract.
        except Exception as error:  # noqa: BLE001
            close_error = error
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()
            self._loop.close()
            self._close_complete.set()
        if close_error is not None:
            raise TransferError("Audaligo API close failed") from None

    async def _close_async(self) -> None:
        current = asyncio.current_task()
        active = [
            task
            for task in asyncio.all_tasks()
            if task is not current and not task.done()
        ]
        for task in active:
            task.cancel()
        if active:
            await asyncio.gather(*active, return_exceptions=True)
        await self._client.get_async_httpx_client().aclose()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object, **kwargs: Any) -> None:
        self.close()

    def begin_upload(
        self,
        *,
        project_id: str,
        operation_id: str,
        mix_version_id: str | None,
        filename: str,
        plaintext_size: int,
    ) -> Mapping[str, Any]:
        preview_intent: dict[str, Any] | None = None
        if mix_version_id is not None:
            preview_intent = {
                "v": 1,
                "profile": "aac-lc-128k-m4a-v1",
                "filename": filename,
                "mediaType": "audio/wav",
                "plaintextSize": plaintext_size,
                "mixVersionId": mix_version_id,
            }
        body = CreateUploadRequest.from_dict(
            {} if preview_intent is None else {"previewIntent": preview_intent}
        )
        response = self._request(
            create_encrypted_object_upload.asyncio_detailed,
            project_id,
            body=body,
            origin=self._origin,
            idempotency_key=operation_id,
        )
        return self._body(response, HTTPStatus.CREATED)

    def put_manifest(
        self, *, project_id: str, upload_id: str, manifest: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        response = self._request(
            put_encrypted_object_manifest.asyncio_detailed,
            project_id,
            upload_id,
            body=PutManifestRequest.from_dict({"manifest": dict(manifest)}),
            origin=self._origin,
        )
        return self._body(response, HTTPStatus.OK, HTTPStatus.CREATED)

    def upload_capability(
        self, *, project_id: str, upload_id: str, chunk_index: int
    ) -> Mapping[str, Any]:
        response = self._request(
            create_chunk_upload_capability.asyncio_detailed,
            project_id,
            upload_id,
            chunk_index,
            origin=self._origin,
        )
        return self._capability(response)

    def complete_upload(self, *, project_id: str, upload_id: str) -> Mapping[str, Any]:
        response = self._request(
            complete_encrypted_object_chunks.asyncio_detailed,
            project_id,
            upload_id,
            origin=self._origin,
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
        mix_version_id: str | None,
    ) -> Mapping[str, Any]:
        value: dict[str, Any] = {
            "encryptedObjectId": upload_id,
            "fileKind": "project_file",
            "originalFilename": filename,
            "originalPlaintextSize": plaintext_size,
        }
        if mix_version_id is not None:
            value["mixVersionId"] = mix_version_id
        response = self._request(
            commit_encrypted_project_file.asyncio_detailed,
            project_id,
            file_id,
            body=CommitProjectFileRequest.from_dict(value),
            origin=self._origin,
        )
        return self._body(response, HTTPStatus.OK, HTTPStatus.CREATED)

    def read_descriptor(self, *, project_id: str, file_id: str) -> Mapping[str, Any]:
        response = self._request(
            get_encrypted_project_file_read_descriptor.asyncio_detailed,
            project_id,
            file_id,
        )
        body = self._body(response, HTTPStatus.OK)
        descriptor = _mapping(body, "descriptor")
        project_file = dict(_mapping(descriptor, "projectFile"))
        obj = _mapping(descriptor, "object")
        project_file["projectId"] = _string(obj, "projectId")
        return {
            "file": project_file,
            "manifest": _manifest_from_descriptor(descriptor),
            "keyClaim": _mapping(body, "keyClaim"),
        }

    def read_capability(
        self,
        *,
        project_id: str,
        object_id: str,
        chunk_index: int,
    ) -> Mapping[str, Any]:
        response = self._request(
            get_chunk_read_capability.asyncio_detailed,
            project_id,
            object_id,
            chunk_index,
        )
        return self._capability(response)

    def _request(
        self,
        operation: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Response[Any]:
        request = _AsyncRequest(
            operation,
            args,
            {"client": self._client, **kwargs},
        )
        with self._lifecycle_lock:
            if self._closed:
                raise TransferError("Audaligo API is closed")
            self._loop.call_soon_threadsafe(request.start)
        if not request.completed.wait(self._total_timeout):
            self._loop.call_soon_threadsafe(request.cancel)
            request.completed.wait()
            raise TransferTimeoutError()
        try:
            return request.result()
        except TransferError:
            raise
        except asyncio.CancelledError:
            raise TransferError("Audaligo API request failed") from None
        except (
            AttributeError,
            httpx.HTTPError,
            KeyError,
            RuntimeError,
            TypeError,
            ValueError,
        ):
            raise TransferError("Audaligo API request failed") from None

    @staticmethod
    def _body(response: Response[Any], *expected: HTTPStatus) -> Mapping[str, Any]:
        if response.status_code not in expected or response.parsed is None:
            raise TransferError("Audaligo API request failed")
        value = response.parsed.to_dict()
        if not isinstance(value, Mapping):
            raise TransferError("Audaligo API returned an invalid response")
        return value

    @classmethod
    def _capability(cls, response: Response[Any]) -> Mapping[str, Any]:
        return _mapping(cls._body(response, HTTPStatus.OK), "capability")


def _manifest_from_descriptor(descriptor: Mapping[str, Any]) -> Mapping[str, Any]:
    obj = _mapping(descriptor, "object")
    if obj.get("securityScope") not in {"managed_encryption", "managed_processing"}:
        raise TransferError("Audaligo read descriptor is not locally decryptable")
    wrapped = _mapping(descriptor, "wrappedDataKey")
    chunks = []
    raw_chunks = obj.get("chunks")
    if not isinstance(raw_chunks, list):
        raise TransferError("Audaligo read descriptor is invalid")
    for raw in raw_chunks:
        chunk = _mapping_value(raw)
        chunks.append(
            {
                "chunk_index": chunk.get("chunkIndex"),
                "ciphertext_offset": chunk.get("ciphertextOffset"),
                "ciphertext_sha256_b64u": chunk.get("ciphertextSha256B64u"),
                "ciphertext_size": chunk.get("ciphertextSize"),
                "final_chunk": chunk.get("finalChunk"),
                "plaintext_offset": chunk.get("plaintextOffset"),
                "plaintext_size": chunk.get("plaintextSize"),
            }
        )
    return {
        "v": obj.get("manifestVersion"),
        "type": obj.get("manifestType"),
        "suite_id": obj.get("suiteId"),
        "encryption": {
            "mode": "managed-project-key",
            "content_key_alg": obj.get("contentKeyAlg"),
            "wrap_alg": obj.get("wrapAlg"),
            "wrapped_data_key": {
                "nonceB64u": wrapped.get("nonceB64u"),
                "ciphertextB64u": wrapped.get("ciphertextB64u"),
            },
        },
        "object": {
            "project_id": obj.get("projectId"),
            "share_id": obj.get("shareId"),
            "file_id": obj.get("fileId"),
            "epoch": obj.get("epoch"),
            "object_id": obj.get("objectId"),
            "plaintext_size": obj.get("plaintextSize"),
            "ciphertext_size": obj.get("ciphertextSize"),
            "chunk_size": obj.get("chunkSize"),
            "chunk_count": obj.get("chunkCount"),
            "nonce_base_b64u": obj.get("nonceBaseB64u"),
            "chunks": chunks,
        },
    }


def _mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    return _mapping_value(value.get(key))


def _mapping_value(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TransferError("Audaligo API returned an invalid response")
    return value


def _string(value: Mapping[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise TransferError("Audaligo API returned an invalid response")
    return result
