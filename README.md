# Soenan MCP Support SDK for Python

`soenan-mcp-support` provides focused support utilities for applications and agents that use Soenan MCP. Its first module, `soenan_mcp_support.transfer`, streams files through the one-time descriptors returned by `audaligo_begin_file_upload` and `audaligo_begin_file_download`.

The package does not include an MCP client. Your existing client remains responsible for OAuth and MCP requests. The transfer module does not implement OAuth, MCP JSON-RPC, or encryption.

## Requirements

- Python 3.10 or later
- A completed begin-upload or begin-download MCP tool result
- An HTTPS connection to the production Soenan MCP transfer endpoint

The runtime has no third-party dependencies.

## Installation

Before a package release, install the source by pinning its full 40-character commit instead of a branch or mutable tag:

```console
python -m pip install 'soenan-mcp-support @ git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>'
```

After publishing a package version, install that exact version:

```console
python -m pip install 'soenan-mcp-support==0.1.0'
```

## Upload a file

Pass either the complete MCP tool result or its `structuredContent` object to `parse_upload_descriptor`. Then pass a path or a readable binary stream to `upload_file`.

```python
from soenan_mcp_support.transfer import parse_upload_descriptor, upload_file

# Obtain this result with the MCP client and authentication stack you already use.
begin_result = mcp_client.call_tool(
    "audaligo_begin_file_upload",
    {
        "projectId": project_id,
        "filename": "recording.wav",
        "plaintextSize": source_path.stat().st_size,
        "operationId": operation_id,
    },
)

descriptor = parse_upload_descriptor(begin_result)
upload_file(descriptor, source_path)
```

For a binary stream, the descriptor's `contentLength` is authoritative:

```python
with source_path.open("rb") as source:
    upload_file(descriptor, source)
```

The SDK sends `PUT`, `Content-Type: application/octet-stream`, and the exact `Content-Length` from the descriptor. It reads and sends at most 64 KiB at a time. Paths and seekable streams with the wrong remaining size fail before the SDK contacts the one-time endpoint. Upload streams must be seekable so the SDK can validate the complete remaining size before consuming the capability.

## Download a file

Pass a destination path to get atomic replacement in the destination directory:

```python
from soenan_mcp_support.transfer import download_file, parse_download_descriptor

begin_result = mcp_client.call_tool(
    "audaligo_begin_file_download",
    {"projectId": project_id, "fileId": file_id},
)

descriptor = parse_download_descriptor(begin_result)
download_file(descriptor, destination_path)
```

The SDK writes a private temporary sibling, validates the response status, media type, declared size, and received size, flushes the completed file, and atomically replaces the destination. It removes the temporary file after any failure and leaves an existing destination unchanged.

You can also pass a writable binary stream. If the stream supports seeking and truncation, the SDK restores its original length after a failed download. A non-seekable stream can retain bytes written before a network failure, so use a path when failure cleanup is required.

## Agent sample

An agent can keep protocol work and transfer work separate:

```python
from soenan_mcp_support.transfer import download_file, parse_download_descriptor


def save_tool_download(tool_result: dict[str, object], output_path: str) -> None:
    descriptor = parse_download_descriptor(tool_result)
    download_file(descriptor, output_path)


# The host agent obtains tool_result through its existing MCP client.
save_tool_download(tool_result, "/private/output/project-file.bin")
```

Do not put the descriptor or its `url` in an agent message, tool summary, trace, or log.

## Timeouts

Every request uses finite connect, socket-read, and whole-transfer limits. Override them explicitly for a large transfer:

```python
from soenan_mcp_support.transfer import TransferTimeouts, upload_file

upload_file(
    descriptor,
    source_path,
    timeouts=TransferTimeouts(connect=10, read=60, total=900),
)
```

The SDK never retries. A transfer capability is one-time authority, and an endpoint can consume it as soon as a request starts. Obtain a new descriptor through the corresponding MCP begin tool after any failed or ambiguous attempt.

## Managed-encryption semantics

The SDK reads and writes **plaintext**. The Soenan MCP transfer gateway applies or removes managed encryption while processing the transfer. The SDK never receives project keys, creates ciphertext, decrypts downloaded data, or implements a parallel encryption format.

For upload, `plaintextSize` and the upload descriptor's `contentLength` are plaintext byte counts. For download, `contentLength` is also the expected plaintext byte count.

## Security invariants

- Treat `descriptor.url` as a bearer capability. Anyone who obtains it can attempt the one-time transfer before it expires.
- Do not serialize, log, trace, cache, or send the capability URL through an agent model.
- Descriptor `repr()`, exceptions, and `safe_summary()` redact the capability URL. The SDK emits no logs.
- The SDK sends no `Authorization` or `Cookie` header to a transfer endpoint.
- The SDK rejects every redirect. It never forwards a capability to another origin or path.
- The SDK validates exact plaintext sizes and does not retry after a request starts.
- Production descriptors use HTTPS. Plain HTTP remains accepted so callers can exercise local test servers.
- A download path is replaced only after the complete response passes validation.

The descriptor's `filename` can also contain private information. The safe representation and summary omit it. Use it only when your application has explicitly chosen how to handle server-provided filenames; `download_file` never selects a destination from it.
