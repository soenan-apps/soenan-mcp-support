# Soenan MCP transfer CLI and Python support

`soenan-mcp-support` encrypts and decrypts Audaligo files locally. Ciphertext moves directly between the command and Railway Bucket. The Soenan MCP tool result contains a short-lived, one-time key claim URL instead of project keys or file data keys.

Use the `soenan-mcp-transfer` command for normal agent and operator workflows. The Python API remains available for applications that already own an authenticated MCP client.

## Requirements

- Python 3.10 or later
- A Soenan MCP OAuth access token with the Audaligo file scopes
- Direct network access to Soenan MCP, the Audaligo key claim URL, and the presigned Railway Bucket URLs

The package uses `cryptography==50.0.0` for AES-256-GCM interoperability with the Audaligo managed encryption contract.

## Installation

Before a package release, install the source by pinning its full 40-character commit instead of a branch or mutable tag:

```console
python -m pip install 'soenan-mcp-support @ git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>'
```

After publishing a package version, install that exact version:

```console
python -m pip install 'soenan-mcp-support==0.1.0'
```

## CLI configuration

Keep the OAuth access token out of command arguments and process listings:

```console
export SOENAN_MCP_URL=https://mcp.soenan.com/mcp
export SOENAN_MCP_ACCESS_TOKEN='...'
```

The command calls MCP itself. Key claim responses and Bucket capabilities do not pass through the agent model.

## Upload a file

```console
soenan-mcp-transfer upload \
  --project-id prj_... \
  --source ./recording.wav \
  --operation-id file_...
```

Use `--filename` to override the local basename or `--mix-version-id` to attach the committed file to a mix version.

The command:

1. Calls `audaligo_begin_file_upload` and receives an opaque one-time key claim URL.
2. Redeems the claim directly with Audaligo and receives one operation-bound file data key.
3. Encrypts the file locally and stores the Audaligo-issued wrapped key in the manifest.
4. Obtains one short-lived Railway Bucket write capability per chunk.
5. Sends each ciphertext chunk directly to Railway Bucket.
6. Confirms the chunks and commits the file through MCP.

The source is read twice: once to compute the encrypted manifest and once to upload the same deterministic ciphertext. The command keeps at most one 8 MiB plaintext chunk and its ciphertext in memory. Neither plaintext nor ciphertext passes through Soenan MCP.

## Download a file

```console
soenan-mcp-transfer download \
  --project-id prj_... \
  --file-id file_... \
  --destination ./recording.wav
```

The command obtains the encrypted manifest and an opaque one-time key claim URL through MCP. It redeems the claim directly with Audaligo, receives only the requested file data key, downloads ciphertext directly from Railway Bucket, validates every chunk, decrypts locally, and atomically replaces the destination.

## Python API

Applications that already own an authenticated MCP client can import `upload_file` and `download_file`. Pass the client’s `call_tool` function. The workflow redeems key claims itself; callers do not parse or receive key material.

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

- Soenan MCP handles only control-plane tool calls and opaque one-time key claim descriptors. Project keys and file data keys do not enter MCP tool results.
- Plaintext and ciphertext file bodies travel directly between the caller and Railway Bucket.
- Audaligo stores only a wrapped file data key in claim state. Claim redemption returns the operation-bound plaintext key directly to the command over TLS.
- The command validates the project, file, object, epoch, wrapped key, chunk layout, ciphertext length, SHA-256 digest, and AES-GCM authentication tag before accepting a download.
- The command does not log access tokens, key claims, data keys, presigned URLs, capability headers, manifests, filenames, or file content.
- The command rejects redirects and does not retry a request after transmission starts.
- A download path changes only after every chunk passes validation.
- Treat key claim URLs, presigned URLs, and capability headers as bearer authority. The MCP tool may return the opaque key claim URL, but clients must not log, persist, or reproduce it outside that single transfer.
