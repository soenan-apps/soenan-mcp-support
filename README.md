# Audaligo encrypted transfer support

`soenan-audaligo-support` consumes an authorized MCP `structuredContent` handoff, redeems its one-time file-key claim, and transfers ciphertext directly between the local process and Railway Bucket. The package does not start an Audaligo product operation and does not call Soenan MCP.

## Requirements

- Python 3.10 or later
- An unmodified `structuredContent` result from one of the Audaligo begin-transfer MCP tools
- Direct network access to the handoff's Audaligo control origin and short-lived Railway Bucket URLs

The package uses `cryptography==50.0.0` for AES-256-GCM interoperability with Audaligo's managed encryption contracts.

## Install from a Git commit

Use the public Git repository and pin its full 40-character commit. Do not use a branch, mutable tag, package index, release binary, or container image.

Run one transfer in an isolated environment:

```console
pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>' soenan-audaligo-transfer --help
```

Install the same source as a direct Python dependency:

```text
soenan-audaligo-support @ git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>
```

The commit must match the commit in the MCP begin tool description.

## Use the CLI

Call the corresponding MCP begin tool first. Pass its complete `structuredContent` JSON object to standard input. Pass only the local source or destination path as a command argument.

Upload a source file:

```console
# The MCP client writes structuredContent directly to this command's stdin.
  pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>' \
  soenan-audaligo-transfer upload --source ./recording.wav
```

Download a file:

```console
# The MCP client writes structuredContent directly to this command's stdin.
  pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>' \
  soenan-audaligo-transfer download --destination ./recording.wav
```

Download an encrypted preview:

```console
# The MCP client writes structuredContent directly to this command's stdin.
  pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<40-character-commit>' \
  soenan-audaligo-transfer download-preview --destination ./preview.m4a
```

Do not put the handoff, claim, continuation, capability, or presigned URL in command arguments, environment variables, logs, or durable files. The CLI reads one bounded JSON object from standard input and rejects duplicate or unexpected fields.

## Use the Python API

Pass the same unmodified MCP `structuredContent` object in process:

```python
from soenan_audaligo_support.transfer import (
    TransferTimeouts,
    download_file,
    download_preview,
    upload_file,
)

upload_result = upload_file(
    upload_structured_content,
    source="./recording.wav",
    timeouts=TransferTimeouts(connect=10, read=60, total=900),
)

written = download_file(
    file_download_structured_content,
    destination="./recording.wav",
)

preview_written = download_preview(
    preview_download_structured_content,
    destination="./preview.m4a",
)
```

The CLI parses arguments and standard input, then calls these public functions. Both modes use the same handoff parser, claim redemption, continuation client, cryptography, capability validation, transfer engine, and error taxonomy.

## Handoff contract

Every handoff uses `protocolVersion` `audaligo.encrypted-transfer.v1` and contains:

- `operation`: `upload`, `file_download`, or `preview_download`
- `projectId`, `objectId`, and `epoch`
- `keyClaim`: a one-time `audaligo.file-key-claim.v1` descriptor
- `continuation`: the opaque Audaligo transfer continuation
- `controlOrigin`: the direct Audaligo control origin
- `upload`, `file`, or `preview` metadata for the selected operation
- `manifest` for file and preview downloads

The handoff never contains a clear data key, wrapped data key, project key, presigned URL, or Bucket header. Claim redemption is the only response that supplies operation-bound key material to the local SDK process.

The parser rejects an unsupported protocol, unknown field, missing field, expired claim, noncanonical integer, malformed URL, origin mismatch, operation mismatch, and metadata or manifest binding mismatch before transfer control starts.

## Recovery and errors

The SDK consumes a key claim once and never retries claim redemption. If the claim has expired or was already consumed, call the same MCP begin tool again with the same operation ID, then pass the new handoff to a new SDK invocation.

The SDK can reacquire a rejected download capability once because it buffers the complete GET response before decryption or destination writes. It does not retry an upload PUT after transmission starts. Audaligo control mutations remain idempotent under the continuation and operation binding.

`TransferError` exposes a stable `code`, a `recoverable` flag, and a secret-free `wire_value()`. The CLI writes the same error object to standard error. Errors never include claims, continuations, clear keys, capabilities, presigned URLs, headers, manifests, filenames, or content.

## Security invariants

- The SDK starts only after it parses an MCP begin handoff.
- Plaintext and clear data keys stay in the local process.
- Audaligo receives the continuation header on control requests. The SDK sends no bearer header.
- The claim URL and control origin must use HTTPS and must have the same origin. Exact loopback hosts can use HTTP for local acceptance.
- File downloads validate project, file, object, epoch, chunk layout, ciphertext length, SHA-256 digest, and AES-GCM authentication.
- Preview downloads authenticate the Audaligo preview fields with `audaligo:managed:file-preview:chunk-aead:v1` additional data.
- Uploads detect source size or content changes before commit.
- Transfers keep at most one bounded chunk and its ciphertext in memory.
- A download path changes only after every chunk passes validation and the temporary file is flushed.
