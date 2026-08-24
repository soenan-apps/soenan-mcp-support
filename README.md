# Soenan MCP Support SDK for Python

`soenan-mcp-support` provides client-side managed encryption and direct Railway Bucket transfer orchestration for applications and agents that use Soenan MCP.

The package does not include an MCP client. Your existing client remains responsible for OAuth and MCP JSON-RPC. Pass its authenticated `call_tool` function to the transfer SDK.

## Requirements

- Python 3.10 or later
- An MCP client authorized for the Audaligo file tools
- Direct network access to the presigned Railway Bucket URLs returned by Audaligo

The SDK uses `cryptography==50.0.0` for AES-256-GCM interoperability with the Audaligo managed encryption contract.

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

Pass your MCP client's authenticated tool caller and a path or seekable binary stream to `upload_file`:

```python
from soenan_mcp_support.transfer import upload_file


def call_tool(name: str, arguments: dict[str, object]) -> dict[str, object]:
    return mcp_client.call_tool(name, arguments)


result = upload_file(
    call_tool,
    project_id=project_id,
    filename="recording.wav",
    source=source_path,
    operation_id=operation_id,
)
```

The SDK performs the following operations:

1. Calls `audaligo_begin_file_upload` to obtain upload state and the project key ring.
2. Generates a file data key and encrypts the plaintext locally with the Audaligo AES-256-GCM chunk contract.
3. Calls `audaligo_put_file_upload_manifest` with the ciphertext manifest.
4. Obtains one short-lived Railway Bucket write capability per chunk.
5. Sends each ciphertext chunk directly from the caller to Railway Bucket.
6. Confirms the uploaded chunks and commits the file through MCP control-plane tools.

The source must be seekable. The SDK reads the source twice: once to compute the encrypted manifest and once to upload the same deterministic ciphertext. It keeps at most one 8 MiB plaintext chunk and its ciphertext in memory. Neither plaintext nor ciphertext passes through the Soenan MCP server.

## Download a file

Pass a destination path to get atomic replacement in the destination directory:

```python
from soenan_mcp_support.transfer import download_file

written = download_file(
    call_tool,
    project_id=project_id,
    file_id=file_id,
    destination=destination_path,
)
```

The SDK obtains the encrypted manifest and project key ring through `audaligo_begin_file_download`. It obtains one short-lived Railway Bucket read capability per chunk, downloads ciphertext directly, validates its length and SHA-256 digest, authenticates and decrypts it locally, and writes plaintext to the destination.

For a destination path, the SDK writes a private temporary sibling, flushes the completed file, and atomically replaces the destination. It removes the temporary file after any failure and leaves an existing destination unchanged. For a seekable binary stream, it restores the original length after a failed download when the stream supports truncation.

## Timeouts

Every direct Bucket request uses finite socket-connect, socket-read, and total deadlines:

```python
from soenan_mcp_support.transfer import TransferTimeouts, upload_file

upload_file(
    call_tool,
    project_id=project_id,
    filename="recording.wav",
    source=source_path,
    operation_id=operation_id,
    timeouts=TransferTimeouts(connect=10, read=60, total=900),
)
```

The SDK does not retry a Bucket request after it starts. The caller can invoke the capability tool again after a failed or ambiguous request if Audaligo permits a replacement capability for the current upload state.

## Security invariants

- The caller performs encryption and decryption. Soenan MCP handles only control-plane tool calls and small key or manifest payloads.
- Plaintext and ciphertext file bodies travel directly between the caller and Railway Bucket.
- The SDK validates the project, file, object, epoch, chunk layout, ciphertext length, SHA-256 digest, and AES-GCM authentication tag before accepting a download.
- The SDK does not log project keys, data keys, presigned URLs, capability headers, manifests, filenames, or file content.
- The SDK rejects redirects and does not retry a request after transmission starts.
- A download path changes only after every chunk passes validation.
- Presigned URLs and headers are bearer authority. Do not serialize, log, trace, cache, or send them through an agent model.
