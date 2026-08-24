from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
from pathlib import Path
import tempfile
import threading
import time
import unittest

from soenan_mcp_support.transfer import (
    DescriptorError,
    TransferHTTPError,
    TransferSizeMismatch,
    TransferTimeoutError,
    TransferTimeouts,
    DownloadDescriptor,
    UploadDescriptor,
    download_file,
    parse_download_descriptor,
    parse_upload_descriptor,
    upload_file,
)


_SECRET = "capability-do-not-disclose"
_EXPIRY = "2030-01-02T03:04:05Z"


def _upload_result(url: str, length: int) -> dict[str, object]:
    return {
        "resultType": "complete",
        "content": [{"type": "text", "text": "Tool call completed."}],
        "structuredContent": {
            "method": "PUT",
            "url": url,
            "contentType": "application/octet-stream",
            "contentLength": length,
            "expiresAt": _EXPIRY,
        },
    }


def _download_result(url: str, length: int) -> dict[str, object]:
    return {
        "result": {
            "resultType": "complete",
            "structuredContent": {
                "method": "GET",
                "url": url,
                "filename": "private-name.bin",
                "contentType": "application/octet-stream",
                "contentLength": length,
                "expiresAt": _EXPIRY,
            },
        }
    }


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, handler: type[BaseHTTPRequestHandler]) -> None:
        super().__init__(("127.0.0.1", 0), handler)
        self.requests: list[tuple[str, str]] = []
        self.request_headers: list[dict[str, str]] = []
        self.received = b""
    def handle_error(
        self, request: object, client_address: tuple[str, int]
    ) -> None:
        pass


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    upload_status = 204
    download_status = 200
    download_body = b"downloaded plaintext"
    declared_download_length: int | None = None
    redirect_location: str | None = None

    def do_PUT(self) -> None:
        self.server.requests.append(("PUT", self.path))  # type: ignore[attr-defined]
        self.server.request_headers.append(dict(self.headers.items()))  # type: ignore[attr-defined]
        length = int(self.headers["Content-Length"])
        self.server.received = self.rfile.read(length)  # type: ignore[attr-defined]
        if self.redirect_location:
            self.send_response(307)
            self.send_header("Location", self.redirect_location)
        else:
            self.send_response(self.upload_status)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def do_GET(self) -> None:
        self.server.requests.append(("GET", self.path))  # type: ignore[attr-defined]
        self.server.request_headers.append(dict(self.headers.items()))  # type: ignore[attr-defined]
        if self.redirect_location:
            self.send_response(307)
            self.send_header("Location", self.redirect_location)
            body = b""
        else:
            self.send_response(self.download_status)
            body = self.download_body if self.download_status == 200 else b""
            if self.download_status == 200:
                self.send_header("Content-Type", "application/octet-stream")
        length = self.declared_download_length
        self.send_header("Content-Length", str(len(body) if length is None else length))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def _server(handler: type[_Handler] = _Handler):
    server = _Server(handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield server, f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


class _SmallReads(io.BytesIO):
    def __init__(self, value: bytes) -> None:
        super().__init__(value)
        self.largest_request = 0

    def read(self, size: int = -1) -> bytes:
        self.largest_request = max(self.largest_request, size)
        return super().read(size)


class _NonSeekable:
    def __init__(self, value: bytes) -> None:
        self._stream = io.BytesIO(value)

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def seekable(self) -> bool:
        return False


class _UnreadableSource(io.BytesIO):
    def readable(self) -> bool:
        return False


class _UnwritableDestination(io.BytesIO):
    def writable(self) -> bool:
        return False

class _UntruncatableDestination(io.BytesIO):
    def truncate(self, size: int | None = None) -> int:
        raise io.UnsupportedOperation("truncate")

class DescriptorTests(unittest.TestCase):
    def test_parses_actual_wrapped_tool_result_shapes(self) -> None:
        upload = parse_upload_descriptor(_upload_result(f"https://mcp.example/{_SECRET}", 7))
        download = parse_download_descriptor(
            _download_result(f"https://mcp.example/{_SECRET}", 9)
        )

        self.assertEqual(upload.method, "PUT")
        self.assertEqual(upload.content_length, 7)
        self.assertEqual(download.method, "GET")
        self.assertEqual(download.filename, "private-name.bin")

    def test_repr_summary_and_parse_error_redact_capability(self) -> None:
        descriptor = parse_upload_descriptor(
            _upload_result(f"https://mcp.example/{_SECRET}", 7)
        )
        self.assertNotIn(_SECRET, repr(descriptor))
        self.assertNotIn(_SECRET, descriptor.safe_summary())

        result = _upload_result(f"https://mcp.example/{_SECRET}", 7)
        result["structuredContent"]["method"] = "POST"  # type: ignore[index]
        with self.assertRaises(DescriptorError) as raised:
            parse_upload_descriptor(result)
        self.assertNotIn(_SECRET, str(raised.exception))
        self.assertNotIn(_SECRET, repr(raised.exception))

    def test_rejects_invalid_capability_ports(self) -> None:
        for port in ("invalid", "70000", "0"):
            with self.subTest(port=port), self.assertRaises(DescriptorError):
                parse_upload_descriptor(
                    _upload_result(f"http://mcp.example:{port}/{_SECRET}", 7)
                )


class UploadTests(unittest.TestCase):
    def test_upload_streams_plaintext_with_exact_headers(self) -> None:
        payload = b"plaintext" * 20_000
        source = _SmallReads(payload)
        with _server() as (server, origin):
            descriptor = parse_upload_descriptor(
                _upload_result(f"{origin}/transfers/upload/{_SECRET}", len(payload))
            )
            count = upload_file(descriptor, source)

        self.assertEqual(count, len(payload))
        self.assertEqual(server.received, payload)
        self.assertEqual(server.requests, [("PUT", f"/transfers/upload/{_SECRET}")])
        self.assertLessEqual(source.largest_request, 64 * 1024)
        headers = server.request_headers[0]
        self.assertEqual(headers["Content-Type"], "application/octet-stream")
        self.assertEqual(headers["Content-Length"], str(len(payload)))
        self.assertNotIn("Authorization", headers)
        self.assertNotIn("Cookie", headers)

    def test_path_size_mismatch_does_not_start_one_time_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory, _server() as (server, origin):
            source = Path(directory, "source.bin")
            source.write_bytes(b"short")
            descriptor = parse_upload_descriptor(
                _upload_result(f"{origin}/transfers/upload/{_SECRET}", 99)
            )
            with self.assertRaises(TransferSizeMismatch):
                upload_file(descriptor, source)

        self.assertEqual(server.requests, [])

    def test_non_seekable_stream_is_rejected_before_one_time_request(self) -> None:
        with _server() as (server, origin):
            descriptor = parse_upload_descriptor(
                _upload_result(f"{origin}/transfers/upload/{_SECRET}", 4)
            )
            with self.assertRaises(TypeError):
                upload_file(descriptor, _NonSeekable(b"data"))

        self.assertEqual(server.requests, [])

    def test_unreadable_stream_is_rejected_before_one_time_request(self) -> None:
        with _server() as (server, origin):
            descriptor = parse_upload_descriptor(
                _upload_result(f"{origin}/transfers/upload/{_SECRET}", 4)
            )
            with self.assertRaises(TypeError):
                upload_file(descriptor, _UnreadableSource(b"data"))

        self.assertEqual(server.requests, [])

    def test_redirect_is_rejected_without_second_request(self) -> None:
        class Redirect(_Handler):
            redirect_location = "/must-not-follow"

        with _server(Redirect) as (server, origin):
            descriptor = parse_upload_descriptor(
                _upload_result(f"{origin}/transfers/upload/{_SECRET}", 4)
            )
            with self.assertRaises(TransferHTTPError) as raised:
                upload_file(descriptor, io.BytesIO(b"data"))

        self.assertEqual(raised.exception.status, 307)
        self.assertEqual(server.requests, [("PUT", f"/transfers/upload/{_SECRET}")])

    def test_error_response_is_not_retried_and_does_not_leak_capability(self) -> None:
        class Unavailable(_Handler):
            upload_status = 503

        with _server(Unavailable) as (server, origin):
            descriptor = parse_upload_descriptor(
                _upload_result(f"{origin}/transfers/upload/{_SECRET}", 4)
            )
            with self.assertRaises(TransferHTTPError) as raised:
                upload_file(descriptor, io.BytesIO(b"data"))

        self.assertEqual(server.requests, [("PUT", f"/transfers/upload/{_SECRET}")])
        self.assertNotIn(_SECRET, str(raised.exception))
        self.assertNotIn(_SECRET, repr(raised.exception))


class DownloadTests(unittest.TestCase):
    def test_download_atomically_replaces_path_with_plaintext(self) -> None:
        with tempfile.TemporaryDirectory() as directory, _server() as (server, origin):
            destination = Path(directory, "download.bin")
            destination.write_bytes(b"old")
            body = _Handler.download_body
            descriptor = parse_download_descriptor(
                _download_result(f"{origin}/transfers/download/{_SECRET}", len(body))
            )
            count = download_file(descriptor, destination)

            self.assertEqual(count, len(body))
            self.assertEqual(destination.read_bytes(), body)
            self.assertEqual(list(Path(directory).glob("*.part")), [])
        self.assertEqual(server.requests, [("GET", f"/transfers/download/{_SECRET}")])
        headers = server.request_headers[0]
        self.assertEqual(headers["Accept"], "application/octet-stream")
        self.assertNotIn("Authorization", headers)
        self.assertNotIn("Cookie", headers)

    def test_size_mismatch_preserves_destination_and_removes_partial_file(self) -> None:
        class Truncated(_Handler):
            download_body = b"short"
            declared_download_length = 10

        with tempfile.TemporaryDirectory() as directory, _server(Truncated) as (server, origin):
            destination = Path(directory, "download.bin")
            destination.write_bytes(b"keep me")
            descriptor = parse_download_descriptor(
                _download_result(f"{origin}/transfers/download/{_SECRET}", 10)
            )
            with self.assertRaises(TransferSizeMismatch):
                download_file(descriptor, destination)

            self.assertEqual(destination.read_bytes(), b"keep me")
            self.assertEqual(list(Path(directory).glob("*.part")), [])
        self.assertEqual(len(server.requests), 1)

    def test_redirect_is_rejected_and_stream_is_rolled_back(self) -> None:
        class Redirect(_Handler):
            redirect_location = "/must-not-follow"

        destination = io.BytesIO(b"prefix")
        destination.seek(0, io.SEEK_END)
        with _server(Redirect) as (server, origin):
            descriptor = DownloadDescriptor(
                url=f"{origin}/transfers/download/{_SECRET}",
                filename="private.bin",
                content_length=4,
                expires_at=datetime.now(timezone.utc),
            )
            with self.assertRaises(TransferHTTPError):
                download_file(descriptor, destination)

        self.assertEqual(destination.getvalue(), b"prefix")
        self.assertEqual(server.requests, [("GET", f"/transfers/download/{_SECRET}")])

    def test_unwritable_stream_is_rejected_before_one_time_request(self) -> None:
        with _server() as (server, origin):
            descriptor = parse_download_descriptor(
                _download_result(f"{origin}/transfers/download/{_SECRET}", 4)
            )
            with self.assertRaises(TypeError):
                download_file(descriptor, _UnwritableDestination())

        self.assertEqual(server.requests, [])

    def test_non_eof_stream_is_rejected_without_losing_existing_data(self) -> None:
        destination = io.BytesIO(b"existing")
        destination.seek(2)
        with _server() as (server, origin):
            descriptor = parse_download_descriptor(
                _download_result(f"{origin}/transfers/download/{_SECRET}", 4)
            )
            with self.assertRaises(ValueError):
                download_file(descriptor, destination)

        self.assertEqual(destination.getvalue(), b"existing")
        self.assertEqual(server.requests, [])

    def test_untruncatable_stream_is_rejected_before_one_time_request(self) -> None:
        destination = _UntruncatableDestination()
        with _server() as (server, origin):
            descriptor = parse_download_descriptor(
                _download_result(f"{origin}/transfers/download/{_SECRET}", 4)
            )
            with self.assertRaises(TypeError):
                download_file(descriptor, destination)

        self.assertEqual(server.requests, [])

    def test_total_deadline_interrupts_slow_response_headers(self) -> None:
        class SlowHeaders(_Handler):
            def do_GET(self) -> None:
                time.sleep(0.2)
                super().do_GET()

        with _server(SlowHeaders) as (server, origin):
            descriptor = parse_download_descriptor(
                _download_result(f"{origin}/transfers/download/{_SECRET}", 4)
            )
            with self.assertRaises(TransferTimeoutError):
                download_file(
                    descriptor,
                    io.BytesIO(),
                    timeouts=TransferTimeouts(connect=1, read=1, total=0.05),
                )

        self.assertEqual(server.requests, [("GET", f"/transfers/download/{_SECRET}")])


if __name__ == "__main__":
    unittest.main()
