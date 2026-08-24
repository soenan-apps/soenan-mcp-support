from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from typing import Any, Mapping
from urllib.parse import SplitResult, urlsplit


_MAX_PLAINTEXT_BYTES = 8 * 1024 * 1024 * 4096


class DescriptorError(ValueError):
    """The MCP result does not contain a valid transfer descriptor."""


@dataclass(frozen=True, repr=False)
class UploadDescriptor:
    """A one-time upload capability returned by ``audaligo_begin_file_upload``."""

    url: str
    content_length: int
    expires_at: datetime
    content_type: str = "application/octet-stream"
    method: str = "PUT"

    def __post_init__(self) -> None:
        _validate_constructed(
            self.url,
            self.content_length,
            self.expires_at,
            self.content_type,
            self.method,
            expected_method="PUT",
        )


    def __repr__(self) -> str:
        return _safe_repr(type(self).__name__, self.method, self.content_length, self.expires_at)

    def safe_summary(self) -> str:
        return _safe_repr(type(self).__name__, self.method, self.content_length, self.expires_at)


@dataclass(frozen=True, repr=False)
class DownloadDescriptor:
    """A one-time download capability returned by ``audaligo_begin_file_download``."""

    url: str
    filename: str
    content_length: int
    expires_at: datetime
    content_type: str = "application/octet-stream"
    method: str = "GET"

    def __post_init__(self) -> None:
        _validate_constructed(
            self.url,
            self.content_length,
            self.expires_at,
            self.content_type,
            self.method,
            expected_method="GET",
        )
        if not isinstance(self.filename, str) or not self.filename:
            raise DescriptorError("transfer descriptor has an invalid filename")


    def __repr__(self) -> str:
        return _safe_repr(type(self).__name__, self.method, self.content_length, self.expires_at)

    def safe_summary(self) -> str:
        return _safe_repr(type(self).__name__, self.method, self.content_length, self.expires_at)


def parse_upload_descriptor(result: Mapping[str, Any]) -> UploadDescriptor:
    """Parse an upload descriptor from a tool result or its structured content."""
    value = _structured_content(result)
    method = _string(value, "method")
    if method != "PUT":
        raise DescriptorError("transfer descriptor has an invalid method")
    content_type = _string(value, "contentType")
    if content_type != "application/octet-stream":
        raise DescriptorError("transfer descriptor has an invalid content type")
    return UploadDescriptor(
        url=_url(value),
        content_length=_size(value),
        expires_at=_expiry(value),
        content_type=content_type,
        method=method,
    )


def parse_download_descriptor(result: Mapping[str, Any]) -> DownloadDescriptor:
    """Parse a download descriptor from a tool result or its structured content."""
    value = _structured_content(result)
    method = _string(value, "method")
    if method != "GET":
        raise DescriptorError("transfer descriptor has an invalid method")
    content_type = _string(value, "contentType")
    if content_type != "application/octet-stream":
        raise DescriptorError("transfer descriptor has an invalid content type")
    filename = _string(value, "filename")
    if not filename:
        raise DescriptorError("transfer descriptor has an invalid filename")
    return DownloadDescriptor(
        url=_url(value),
        filename=filename,
        content_length=_size(value),
        expires_at=_expiry(value),
        content_type=content_type,
        method=method,
    )


def _structured_content(result: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(result, Mapping):
        raise DescriptorError("MCP tool result must be an object")

    value: Mapping[str, Any] = result
    nested_result = value.get("result")
    if isinstance(nested_result, Mapping):
        value = nested_result

    if value.get("isError") is True:
        raise DescriptorError("MCP tool call did not return a transfer descriptor")
    result_type = value.get("resultType")
    if result_type is not None and result_type != "complete":
        raise DescriptorError("MCP tool call is not complete")

    structured = value.get("structuredContent")
    if structured is not None:
        if not isinstance(structured, Mapping):
            raise DescriptorError("MCP structured content must be an object")
        value = structured
    return value


def _string(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str):
        raise DescriptorError(f"transfer descriptor field {key!r} must be a string")
    return item


def _size(value: Mapping[str, Any]) -> int:
    item = value.get("contentLength")
    if isinstance(item, bool) or not isinstance(item, (int, float)):
        raise DescriptorError("transfer descriptor contentLength must be an integer")
    if isinstance(item, float) and (not math.isfinite(item) or not item.is_integer()):
        raise DescriptorError("transfer descriptor contentLength must be an integer")
    size = int(item)
    if not 1 <= size <= _MAX_PLAINTEXT_BYTES:
        raise DescriptorError("transfer descriptor contentLength is outside the supported range")
    return size


def _expiry(value: Mapping[str, Any]) -> datetime:
    text = _string(value, "expiresAt")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise DescriptorError(
            "transfer descriptor expiresAt must be an ISO 8601 timestamp"
        ) from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DescriptorError("transfer descriptor expiresAt must include a time zone")
    return parsed


def _url(value: Mapping[str, Any]) -> str:
    text = _string(value, "url")
    try:
        parsed = urlsplit(text)
        _validate_url(parsed)
    except ValueError:
        raise DescriptorError("transfer descriptor contains an invalid capability URL") from None
    return text


def _validate_url(value: SplitResult) -> None:
    if value.scheme not in {"http", "https"} or not value.hostname:
        raise ValueError("invalid endpoint")
    if value.username is not None or value.password is not None or value.fragment:
        raise ValueError("invalid endpoint")


def _validate_constructed(
    url: str,
    content_length: int,
    expires_at: datetime,
    content_type: str,
    method: str,
    *,
    expected_method: str,
) -> None:
    if method != expected_method:
        raise DescriptorError("transfer descriptor has an invalid method")
    if content_type != "application/octet-stream":
        raise DescriptorError("transfer descriptor has an invalid content type")
    if (
        isinstance(content_length, bool)
        or not isinstance(content_length, int)
        or not 1 <= content_length <= _MAX_PLAINTEXT_BYTES
    ):
        raise DescriptorError("transfer descriptor contentLength is outside the supported range")
    if (
        not isinstance(expires_at, datetime)
        or expires_at.tzinfo is None
        or expires_at.utcoffset() is None
    ):
        raise DescriptorError("transfer descriptor expiresAt must include a time zone")
    if not isinstance(url, str):
        raise DescriptorError("transfer descriptor contains an invalid capability URL")
    try:
        _validate_url(urlsplit(url))
    except ValueError:
        raise DescriptorError(
            "transfer descriptor contains an invalid capability URL"
        ) from None


def _safe_repr(name: str, method: str, size: int, expiry: datetime) -> str:
    return (
        f"{name}(method={method!r}, content_length={size!r}, "
        f"expires_at={expiry.isoformat()!r}, capability=<redacted>)"
    )
