# Audaligo encrypted transfer support

`soenan-audaligo-support` consumes an authorized MCP `structuredContent` handoff, redeems its one-use file-key claim, and transfers ciphertext directly between the local process and Railway Bucket. Soenan MCP starts every transfer. The SDK does not start an Audaligo product operation and does not call Soenan MCP.

The MCP client uses the single canonical MCP OAuth resource to obtain Account-owned delegation. That bearer authorizes MCP only; the SDK never forwards it to Audaligo. Account owns delegation and product access, while Audaligo owns project, file, key, claim, continuation, and Bucket-capability lifecycle.

## Requirements

- Python 3.10 or later
- An unmodified `structuredContent` result from an Audaligo begin-transfer MCP tool
- Direct network access to the handoff's Audaligo control origin and short-lived Railway Bucket URLs

The package uses `cryptography==50.0.0` for AES-256-GCM interoperability with Audaligo's managed encryption contracts.

## Use the pinned Git source

The only supported distribution form is source from the public Git repository pinned to a full commit. Do not use a branch, mutable tag, PyPI package, release binary, or container image. The verified implementation and revision are currently local; no public push, package publication, or deployment has occurred.

Use this exact `pipx` source template for the CLI:

```console
pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<FULL_COMMIT>' soenan-audaligo-transfer --help
```

Use the same direct-VCS source for the Python API:

```text
soenan-audaligo-support @ git+https://github.com/soenan-apps/soenan-mcp-support.git@<FULL_COMMIT>
```

Before installing or running, replace every `<FULL_COMMIT>` with the full 40-character commit published by the MCP begin tool description; do not use the angle-bracket placeholder literally. The revision identifies source; it is not evidence of PyPI, binary, container, Develop, or Production publication.

## Use the CLI

Call the corresponding MCP begin tool first. Pass its complete `structuredContent` JSON object directly to standard input. Pass only the local source or destination path as a command argument. Do not copy the handoff through an environment variable or durable intermediary.

Upload a source file:

```console
# The MCP client writes structuredContent directly to this command's stdin.
pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<FULL_COMMIT>' \
  soenan-audaligo-transfer upload --source ./recording.wav
```

Download a file:

```console
# The MCP client writes structuredContent directly to this command's stdin.
pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<FULL_COMMIT>' \
  soenan-audaligo-transfer download --destination ./recording.wav
```

Download an encrypted preview:

```console
# The MCP client writes structuredContent directly to this command's stdin.
pipx run --spec 'git+https://github.com/soenan-apps/soenan-mcp-support.git@<FULL_COMMIT>' \
  soenan-audaligo-transfer download-preview --destination ./preview.m4a
```

Do not put the handoff, claim, continuation, capability, or presigned URL in command arguments, environment variables, logs, or durable files. The CLI reads one bounded JSON object from standard input and rejects duplicate or unexpected fields.

## Use the Python API

After the corresponding MCP begin call, pass the same unmodified `structuredContent` object directly in process. Install the package from the direct-VCS source pinned above; do not resolve it through a package index.

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

The CLI parses arguments and standard input, then calls these public functions. Both modes use the same handoff parser and SDK-only claim redemption, continuation client, cryptography, Bucket capability validation, transfer engine, and error taxonomy. The MCP client and model do not redeem claims, handle key material, perform chunk cryptography, or use Bucket capabilities.

## Handoff contract

Every handoff uses `protocolVersion` `audaligo.encrypted-transfer.v1` and contains:

- `operation`: `upload`, `file_download`, or `preview_download`
- `projectId`, `objectId`, and `epoch`
- `keyClaim`: a one-time `audaligo.file-key-claim.v1` descriptor
- `continuation`: the opaque Audaligo transfer continuation
- `controlOrigin`: the direct Audaligo control origin
- `upload`, `file`, or `preview` metadata for the selected operation
- `manifest` for file and preview downloads

The handoff never contains a clear data key, wrapped data key, project key, presigned URL, or Bucket header. It carries opaque claim and continuation descriptors only through the direct standard-input or in-process handoff. Claim redemption is the only response that supplies operation-bound clear key material to the local SDK process.

Audaligo keys claim state by the SHA-256 digests of a 16-byte claim ID and a 32-byte claim secret. A claim expires after at most 600 seconds, can be consumed once, and does not mirror the durable wrapped key. Active continuation is bounded to 7,200 seconds. Every continuation control operation makes Audaligo resolve the Account delegation again and recheck current product, project, file, and resource authority.

The parser rejects an unsupported protocol, unknown field, missing field, expired claim, noncanonical integer, malformed URL, origin mismatch, operation mismatch, and metadata or manifest binding mismatch before transfer control starts.

## Recovery and errors

The SDK consumes a key claim once and never retries claim redemption. If the claim has expired or was already consumed, call the same MCP begin tool again with the same operation ID, then pass the new handoff to a new SDK invocation.

The SDK can reacquire a rejected download capability once because it buffers the complete GET response before decryption or destination writes. It does not retry an upload PUT after transmission starts. Audaligo control mutations remain idempotent under the continuation and operation binding.

`TransferError` exposes a stable `code`, a `recoverable` flag, and a secret-free `wire_value()`. The CLI writes the same error object to standard error. Errors never include claims, continuations, clear keys, capabilities, presigned URLs, headers, manifests, filenames, or content.

## Security invariants

- Soenan MCP begins every transfer before the SDK parses a handoff.
- Account owns delegation and product access. Audaligo owns project, file, key, claim, continuation, and Bucket-capability lifecycle.
- The SDK alone redeems the claim, handles clear key material, performs chunk cryptography, and controls Bucket I/O.
- Plaintext and clear data keys stay in the local process.
- Audaligo receives the opaque continuation header on control requests. The SDK sends and accepts no bearer credential.
- Browser file transfer is an independent product-session flow. Audaligo's public file API does not accept an Audaligo OAuth bearer.
- File downloads validate project, file, object, epoch, chunk layout, ciphertext length, SHA-256 digest, and AES-GCM authentication.
- Preview downloads authenticate the Audaligo preview fields with `audaligo:managed:file-preview:chunk-aead:v1` additional data.
- Uploads detect source size or content changes before commit.
- Transfers keep at most one bounded chunk and its ciphertext in memory.
- A download path changes only after every chunk passes validation and the temporary file is flushed.
