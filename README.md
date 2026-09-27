# Arteligo encrypted transfer support

`soenan-arteligo-support` consumes an authorized MCP `structuredContent` handoff, redeems its one-use file-key claim, and transfers ciphertext directly between the local process and Railway Bucket. Soenan MCP starts every transfer. The SDK does not start an Arteligo product operation and does not call Soenan MCP.

The MCP client obtains an Account-issued JWT for the single canonical MCP OAuth resource. MCP and Arteligo validate that JWT against Account JWKS. The SDK never forwards it to Arteligo. Account owns tokens and current product access; Arteligo owns project, file, key, claim, continuation, and Bucket-capability lifecycle.

## Requirements

- Python 3.10 or later
- An unmodified `structuredContent` result from an Arteligo begin-transfer MCP tool
- Direct network access to the handoff's Arteligo control origin and short-lived Railway Bucket URLs
- Local `ffmpeg` and `ffprobe` with `libopus` available on `PATH` for WAV uploads

The package uses `cryptography==50.0.0` for AES-256-GCM interoperability with Arteligo's managed encryption contracts.

WAV upload handoffs with `upload.previewProfile=opus-webm-v1` encode an audio-only 48 kHz, at-most-stereo WebM/Opus preview locally. FFmpeg targets 128 kbps with variable bitrate; `media.bitrate` reports the rounded effective rate of the serialized WebM (`plaintextSize × 8 ÷ durationSeconds`), not a guaranteed encoder setting. Before uploading the source, the SDK rejects WAV durations above 24 hours. It measures integrated LUFS, true peak dBTP, and loudness range from the **encoded preview**, not the WAV source. The child reads the source over standard input, inherits no caller environment, limits codec and filter thread settings to two each, and leaves no plaintext preview after the invocation. Actual encoded output is capped at 512 MiB and reserves 256 MiB of available local disk space; encoding, probing, and analysis share the configured total timeout. Non-WAV transfers do not require media tools.

For multichannel `WAVEFORMATEXTENSIBLE` input, the SDK accepts 3.0, quad, 5.0/5.1 back or side, and 7.1 speaker masks (`0x7`, `0x33`, `0x37`, `0x607`, `0x3f`, `0x60f`, `0x63f`). It folds center and surround channels into stereo with peak-safe normalization and omits LFE; unsupported or contradictory multichannel masks fail before encoding. Mono and stereo PCM/float WAV remain accepted.

The existing SDK source-object limit remains 4,096 chunks of 8 MiB each (32 GiB). WAVs above that limit are rejected before encryption or upload. A preview has at most 64 chunks of 8 MiB (512 MiB plaintext); quota accounts for the additional 16-byte authentication tag per chunk.

## Use the checked-out source

Install this source tree in an isolated environment while developing or verifying the transfer client:

```console
python3 -m pip install ./soenan-mcp-support
```

The MCP begin tool and Support SDK must implement the same handoff contract. This repository does not imply a package publication, release, or deployment.

## Use the CLI

Call the corresponding MCP begin tool first. Pass its complete `structuredContent` JSON object directly to standard input. Pass only the local source or destination path as an argument.

```console
# The MCP client writes structuredContent directly to this command's stdin.
soenan-arteligo-transfer upload --source ./recording.wav
soenan-arteligo-transfer download --destination ./recording.wav
soenan-arteligo-transfer download-preview --destination ./preview.m4a
```

Do not put the handoff, claim, continuation, capability, or presigned URL in command arguments, environment variables, logs, or durable files. The CLI reads one bounded JSON object from standard input and rejects duplicate or unexpected fields.

## Use the Python API

After the corresponding MCP begin call, pass the same unmodified `structuredContent` object directly in process.

```python
from soenan_arteligo_support.transfer import (
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

Every handoff uses `protocolVersion` `arteligo.encrypted-transfer.v1` and contains:

- `operation`: `upload`, `file_download`, or `preview_download`
- `projectId`, `objectId`, and `epoch`
- `keyClaim`: a one-time `arteligo.file-key-claim.v1` descriptor
- `continuation`: the opaque Arteligo transfer continuation
- `controlOrigin`: the direct Arteligo control origin
- `upload`, `file`, or `preview` metadata for the selected operation
- `manifest` for file and preview downloads

The handoff never contains a clear data key, wrapped data key, project key, presigned URL, or Bucket header. It carries opaque claim and continuation descriptors only through the direct standard-input or in-process handoff. Claim redemption is the only response that supplies operation-bound clear key material to the local SDK process.

Arteligo keys claim state by the SHA-256 digests of a 16-byte claim ID and a 32-byte claim secret. A claim expires after at most 600 seconds, can be consumed once, and does not mirror the durable wrapped key. Active continuation is bounded to 7,200 seconds. Each continuation control operation checks the saved Account principal and current product, project, file, and resource authority; the SDK sends no OAuth bearer.

The parser rejects an unsupported protocol, unknown field, missing field, expired claim, noncanonical integer, malformed URL, origin mismatch, operation mismatch, metadata or manifest binding mismatch before transfer control starts. A preview manifest uses the canonical `audaligo.preview.read.v1` contract and accepts audio (`audio/mp4`, `mp4a.40.2` or `audio/webm`, `opus`) or video (`video/mp4`, H.264 with optional AAC) output tuples. Bitrate is not part of this download descriptor.

Existing encrypted objects retain the versioned `audaligo.managed-encrypted-object-manifest`, `aes-256-gcm-audaligo-v1`, `audaligo.preview.read.v1`, and `audaligo:managed:*:v1` identifiers. The SDK must authenticate and decrypt that stored format without changing its AES-GCM additional authenticated data or key derivation. A future format rename requires an explicit data-preserving decrypt/re-encrypt migration coordinated with Arteligo; renaming these wire literals alone would make existing objects unreadable. The MCP handoff and key-claim protocols are short-lived and use the new `arteligo.*` names.

## Recovery and errors

The SDK consumes a key claim once and never retries claim redemption. If the claim has expired or was already consumed, call the same MCP begin tool again with the same operation ID, then pass the new handoff to a new SDK invocation.

For a WAV upload, the SDK uploads and commits the source first. Under the original source continuation it begins the source-bound sidecar. A ready sidecar needs no new encoding. Otherwise the SDK resets the previous attempt **before** starting a fresh encoder, so the new WebM can never be encrypted under a previous preview DEK and nonce. It checks the WAV against the committed source bytes, encodes and measures the WebM, refreshes the one-use preview claim under the same reset identity, and publishes the encrypted manifest and direct Bucket chunks. The backend verifies ciphertext size and checksum before completing publication and derives playback gain from the client-reported measurement; silence is unmeasurable.

If the sidecar fails after source commit, `upload_file` returns `preview_pending` rather than source-upload success. Call the same MCP begin tool again with the same operation ID and local WAV, then retry the SDK. Arteligo reissues the source continuation and key claim, and the SDK reuses the committed source, fencing the incomplete preview attempt before re-encoding. A ready preview is never reset. No claim, key, plaintext media, or presigned URL passes through MCP or model output.

The SDK can reacquire a rejected download capability once because it buffers the complete GET response before decryption or destination writes. It does not retry an upload PUT after transmission starts. Arteligo control mutations remain idempotent under the continuation and operation binding.

`TransferError` exposes a stable `code`, a `recoverable` flag, and a secret-free `wire_value()`. The CLI writes the same error object to standard error. Errors never include claims, continuations, clear keys, capabilities, presigned URLs, headers, manifests, filenames, or content.

## Security invariants

- Soenan MCP begins every transfer before the SDK parses a handoff.
- Account owns JWT issuance and current product access. Arteligo owns project, file, key, claim, continuation, and Bucket-capability lifecycle.
- The SDK alone redeems the claim, handles clear key material, performs chunk cryptography, and controls Bucket I/O.
- Plaintext and clear data keys stay in the local process.
- Arteligo receives the opaque continuation header on control requests. The SDK sends and accepts no bearer credential.
- Browser file transfer uses Arteligo's HttpOnly cookie; native control APIs use an Arteligo-audience Bearer JWT. The SDK uses only the MCP-authorized handoff and continuation, never either credential.
- File downloads validate project, file, object, epoch, chunk layout, ciphertext length, SHA-256 digest, and AES-GCM authentication.
- Audio and video preview downloads authenticate the Arteligo preview IDs, sizes, offsets, and final-chunk state with `audaligo:managed:file-preview:chunk-aead:v1` additional data.
- Uploads detect source size or content changes before commit.
- Transfers keep at most one bounded chunk and its ciphertext in memory.
- A download path changes only after every chunk passes validation and the temporary file is flushed.

## Regenerate the Python API client

The [Arteligo product repository](https://github.com/soenan-apps/arteligo) owns `../arteligo/contracts/openapi/arteligo-public.yaml`. After changing that source, regenerate the complete Python client with the pinned generator (do not hand-edit generated models):

```console
cd soenan-mcp-support
uvx --from openapi-python-client==0.28.0 --with ruff==0.16.9 openapi-python-client generate --path ../arteligo/contracts/openapi/arteligo-public.yaml --meta none --output-path generated/arteligo_public_api_client --overwrite
```
