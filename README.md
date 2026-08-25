# Audaligo transfer CLI and Python support

`soenan-audaligo-support` encrypts and decrypts Audaligo files locally. It calls Audaligo's generated public API for transfer control and sends ciphertext directly to Railway Bucket. Product workflow details and key material do not pass through an agent model or Soenan MCP.

## Requirements

- Python 3.10 or later
- An OAuth access token whose resource is the Audaligo origin
- `audaligo:files:write` for uploads
- `audaligo:files:read` for downloads
- Direct network access to Audaligo and the presigned Railway Bucket URLs

The package uses `cryptography==50.0.0` for AES-256-GCM interoperability with Audaligo's managed encryption contract.

## Install from Git

Pin the full 40-character commit. Do not install from a branch or mutable tag.

```console
python -m pip install 'soenan-audaligo-support @ git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>'
```

## Configure the CLI

Keep the OAuth access token out of command arguments and process listings:

```console
export AUDALIGO_API_URL=https://audaligo.soenan.app
export AUDALIGO_ACCESS_TOKEN='...'
```

The token's OAuth resource must exactly match `AUDALIGO_API_URL`. An MCP-audience token is not accepted by Audaligo.

## Upload a file

```console
soenan-audaligo-transfer upload \
  --project-id prj_... \
  --source ./recording.wav \
  --operation-id 00000000-0000-4000-8000-000000000001
```

Use `--filename` to override the local basename or `--mix-version-id` to attach the committed file to a mix version.

The command:

1. Starts an upload through Audaligo's generated public API and receives an opaque, one-time key claim descriptor.
2. Redeems the claim directly with Audaligo and receives the operation-bound file data key.
3. Encrypts the file locally and submits the manifest containing Audaligo's wrapped key.
4. Obtains one short-lived Railway Bucket write capability per chunk.
5. Sends each ciphertext chunk directly to Railway Bucket.
6. Completes and commits the upload through Audaligo's public API.

The source is read twice: once to build the encrypted manifest and once to upload the same deterministic ciphertext. The command keeps at most one 8 MiB plaintext chunk and its ciphertext in memory.

## Download a file

```console
soenan-audaligo-transfer download \
  --project-id prj_... \
  --file-id file_... \
  --destination ./recording.wav
```

The command obtains the encrypted manifest and key claim descriptor from Audaligo, redeems the claim directly, downloads ciphertext from Railway Bucket, validates every chunk, decrypts locally, and atomically replaces the destination.

## Python API

```python
from soenan_audaligo_support.transfer import (
    DEFAULT_TIMEOUTS,
    AudaligoTransferAPI,
    TransferTimeouts,
    upload_file,
)

api = AudaligoTransferAPI(
    base_url="https://audaligo.soenan.app",
    access_token=access_token,
    timeouts=DEFAULT_TIMEOUTS,
)

result = upload_file(
    api,
    project_id=project_id,
    filename="recording.wav",
    source="./recording.wav",
    operation_id=operation_id,
    timeouts=TransferTimeouts(connect=10, read=60, total=900),
)
```

`download_file` uses the same `AudaligoTransferAPI`. Callers provide identifiers and paths; the workflow owns API response parsing, claim redemption, key handling, capability validation, and transfer sequencing.

## Security invariants

- Plaintext stays in the local process. Ciphertext bodies travel directly between the caller and Railway Bucket.
- Audaligo stores only a wrapped file data key in short-lived claim state. Claim redemption returns the exact operation-bound key over TLS.
- The command validates project, file, object, epoch, wrapped key, chunk layout, ciphertext length, SHA-256 digest, and AES-GCM authentication before accepting a download.
- The command does not log access tokens, key claims, data keys, presigned URLs, capability headers, manifests, filenames, or file content.
- The command rejects redirects and does not retry a Bucket request after transmission starts.
- A download path changes only after every chunk passes validation.
- Treat key claim descriptors, presigned URLs, and capability headers as bearer authority. Do not log, persist, or reproduce them outside the transfer.
