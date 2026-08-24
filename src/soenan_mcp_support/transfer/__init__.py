"""Synchronous plaintext transfers for Soenan MCP capabilities."""

from .descriptors import (
    DescriptorError,
    DownloadDescriptor,
    UploadDescriptor,
    parse_download_descriptor,
    parse_upload_descriptor,
)
from ._http import (
    DEFAULT_TIMEOUTS,
    TransferError,
    TransferHTTPError,
    TransferSizeMismatch,
    TransferTimeoutError,
    TransferTimeouts,
    download_file,
    upload_file,
)

__all__ = [
    "DEFAULT_TIMEOUTS",
    "DescriptorError",
    "DownloadDescriptor",
    "TransferError",
    "TransferHTTPError",
    "TransferSizeMismatch",
    "TransferTimeoutError",
    "TransferTimeouts",
    "UploadDescriptor",
    "download_file",
    "parse_download_descriptor",
    "parse_upload_descriptor",
    "upload_file",
]
