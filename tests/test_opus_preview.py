from __future__ import annotations

import io
import math
import shutil
import struct
import wave
from base64 import urlsafe_b64encode
from dataclasses import replace
from hashlib import sha256
from typing import Any

import pytest
from typing_extensions import Self

from soenan_arteligo_support.transfer import _workflow
from soenan_arteligo_support.transfer._claim import FileKeyClaim
from soenan_arteligo_support.transfer._crypto import (
    build_preview_encryption_plan,
    parse_preview_decryption_plan,
)
from soenan_arteligo_support.transfer._http import (
    TransferError, TransferSizeMismatch, TransferTimeoutError,
)
from soenan_arteligo_support.transfer._opus import (
    preflight_wav_preview, prepare_opus_preview,
)

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="local ffmpeg and ffprobe are required for preview encoding",
)


def _wav(*, silence: bool = False) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(48000)
        value = 0 if silence else 8000
        stream.writeframes(struct.pack("<h", value) * 48000)
    return output.getvalue()


def _extensible_wav(mask: int, channels: int) -> bytes:
    speakers = [bit for bit in range(32) if mask & (1 << bit)]
    speaker_bits = speakers[:channels]
    samples = (
        int(8000 * math.sin(2 * math.pi * 440 * index / 48000))
        for index in range(48000)
    )
    payload = b"".join(
        struct.pack(
            "<" + "h" * channels,
            *(sample if bit in (2, 4, 5, 9, 10) else 0 for bit in speaker_bits),
        )
        for sample in samples
    )
    fmt = struct.pack(
        "<HHIIHHHHI", 0xFFFE, channels, 48000, 48000 * channels * 2,
        channels * 2, 16, 22, 16, mask,
    ) + struct.pack("<I", 1) + bytes.fromhex("00001000800000aa00389b71")
    riff_size = 4 + 8 + len(fmt) + 8 + len(payload)
    return (
        struct.pack("<4sI4s", b"RIFF", riff_size, b"WAVE")
        + struct.pack("<4sI", b"fmt ", len(fmt)) + fmt
        + struct.pack("<4sI", b"data", len(payload)) + payload
    )


def _b64(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def test_encoded_preview_is_webm_opus_and_ciphertext_authenticates() -> None:
    source_data = _wav()
    source = io.BytesIO(source_data)
    with prepare_opus_preview(source, source_size=len(source_data), timeout=30) as preview:
        assert source.tell() == 0
        assert 0 < preview.size < len(source_data)
        assert preview.channels == 2
        assert 0 < preview.duration_seconds < 2
        assert preview.bitrate == round(preview.size * 8 / preview.duration_seconds)
        assert 0 < preview.bitrate <= 2_147_483_647
        assert preview.integrated_lufs_x100 is not None
        assert preview.true_peak_dbtp_x100 is not None
        assert preview.loudness_range_lu_x100 is not None
        assert preview.source_sha256 == sha256(source_data).digest()
        assert _workflow._preview_loudness(
            replace(preview, integrated_lufs_x100=110)
        )["integratedLufsX100"] == 110
        with preview.path.open("rb") as encoded:
            plan = build_preview_encryption_plan(
                encoded,
                project_id="project_1", source_object_id="source_1",
                processing_id="processing_1", preview_id="preview_1",
                job_id="job_1", epoch=7, data_key=b"k" * 32,
                nonce_base=b"n" * 8, plaintext_size=preview.size,
            )
            manifest = {
                "contract": "audaligo.preview.read.v1",
                "sourceObjectId": "source_1", "processingId": "processing_1",
                "jobId": "job_1", "nonceBase64url": _b64(plan.nonce_base),
                "plaintextSize": preview.size,
                "ciphertextSize": sum(chunk.ciphertext_size for chunk in plan.chunks),
                "chunkSize": 8 * 1024 * 1024,
                "chunks": [
                    {
                        "chunkIndex": chunk.index,
                        "plaintextOffset": chunk.plaintext_offset,
                        "plaintextSize": chunk.plaintext_size,
                        "ciphertextOffset": chunk.ciphertext_offset,
                        "ciphertextSize": chunk.ciphertext_size,
                        "ciphertextSha256Base64url": _b64(chunk.ciphertext_sha256),
                        "finalChunk": chunk.final,
                    }
                    for chunk in plan.chunks
                ],
            }
            reader = parse_preview_decryption_plan(
                manifest, project_id="project_1", preview_id="preview_1",
                epoch=7, data_key=b"k" * 32,
            )
            for chunk in plan.chunks:
                plaintext = encoded.read(chunk.plaintext_size)
                ciphertext = plan.seal_chunk(plaintext, chunk.index)
                assert sha256(ciphertext).digest() == chunk.ciphertext_sha256
                assert reader.open_chunk(ciphertext, chunk.index) == plaintext
        temporary_path = preview.path
    assert not temporary_path.exists()


def test_silence_has_no_invented_loudness_measurement() -> None:
    data = _wav(silence=True)
    with prepare_opus_preview(io.BytesIO(data), source_size=len(data), timeout=30) as preview:
        assert preview.integrated_lufs_x100 is None
        assert preview.true_peak_dbtp_x100 is None


@pytest.mark.parametrize(
    ("mask", "channels"),
    [(0x7, 3), (0x33, 4), (0x37, 5), (0x607, 5),
     (0x3F, 6), (0x60F, 6), (0x63F, 8)],
)
def test_extensible_surround_preview_keeps_center_and_surround(
    mask: int, channels: int,
) -> None:
    data = _extensible_wav(mask, channels)
    with prepare_opus_preview(io.BytesIO(data), source_size=len(data), timeout=30) as preview:
        assert preview.channels == 2
        assert preview.integrated_lufs_x100 is not None
        assert preview.true_peak_dbtp_x100 is not None


@pytest.mark.parametrize(
    ("mask", "channels"), [(0x107, 4), (0x3F, 5)],
)
def test_extensible_unknown_or_contradictory_mask_is_rejected(
    mask: int, channels: int,
) -> None:
    data = _extensible_wav(mask, channels)
    with pytest.raises(TransferError, match="channel layout"):
        with prepare_opus_preview(io.BytesIO(data), source_size=len(data), timeout=30):
            pytest.fail("unsupported mask must not produce a preview")


def test_source_size_change_and_invalid_wave_fail_without_publishing() -> None:
    data = _wav()
    with pytest.raises(TransferSizeMismatch):
        with prepare_opus_preview(io.BytesIO(data[:-1]), source_size=len(data), timeout=30):
            pytest.fail("invalid preview must not be yielded")
    with pytest.raises(TransferError):
        with prepare_opus_preview(io.BytesIO(b"not a WAV"), source_size=9, timeout=30):
            pytest.fail("invalid preview must not be yielded")


def test_variable_bitrate_preview_is_not_rejected_by_target_size_estimate() -> None:
    data_size = 10 * 3600 * 48000 * 2
    header = (
        struct.pack("<4sI4s", b"RIFF", data_size + 36, b"WAVE")
        + struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 48000, 96000, 2, 16)
        + struct.pack("<4sI", b"data", data_size)
    )
    preflight_wav_preview(io.BytesIO(header), len(header) + data_size)
    over_duration_size = 25 * 3600 * 8000
    over_duration = (
        struct.pack("<4sI4s", b"RIFF", over_duration_size + 36, b"WAVE")
        + struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, 8000, 8000, 1, 8)
        + struct.pack("<4sI", b"data", over_duration_size)
    )
    with pytest.raises(TransferError, match="duration is unsupported"):
        preflight_wav_preview(io.BytesIO(over_duration), len(over_duration) + over_duration_size)


def test_insufficient_local_disk_stops_before_media_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace
    from soenan_arteligo_support.transfer import _opus

    data = _wav()
    monkeypatch.setattr(_opus.shutil, "disk_usage", lambda path: SimpleNamespace(free=0))
    monkeypatch.setattr(
        _opus, "_encode",
        lambda *args, **kwargs: pytest.fail("encoder must not run without disk space"),
    )
    with pytest.raises(TransferError, match="disk space"):
        with prepare_opus_preview(io.BytesIO(data), source_size=len(data), timeout=30):
            pytest.fail("preview must not be yielded")


def _handoff(size: int) -> dict[str, Any]:
    return {
        "operation": "upload", "projectId": "project_1", "objectId": "source_1",
        "epoch": "7", "continuation": "c" * 43,
        "controlOrigin": "https://arteligo.example",
        "protocolVersion": "arteligo.encrypted-transfer.v1",
        "keyClaim": {
            "url": f"https://arteligo.example/key-claims/source#{'a' * 43}",
            "expiresAtUnixMilliseconds": "4102444800000",
            "protocol": "arteligo.file-key-claim.v1",
        },
        "upload": {
            "filename": "recording.wav", "plaintextSize": str(size),
            "operationId": "00000000-0000-4000-8000-000000000001",
            "previewProfile": "opus-webm-v1",
        },
        "previewId": "preview_1", "processingId": "processing_1", "jobId": "job_1",
    }


@pytest.mark.parametrize("preview_timeout_once", [False, True])
def test_source_commit_precedes_scoped_preview_publication(
    monkeypatch: pytest.MonkeyPatch, preview_timeout_once: bool,
) -> None:
    source = _wav()
    calls: list[str] = []
    encrypted: dict[str, bytes] = {}
    manifests: dict[str, dict[str, Any]] = {}
    fail_preview = preview_timeout_once
    reset_count = 0
    preview_state = "reserved"

    class API:
        def __init__(self, **kwargs: object) -> None:
            assert kwargs["continuation"] == "c" * 43

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def put_manifest(self, **kwargs: Any) -> dict[str, Any]:
            if "source" in manifests:
                assert manifests["source"] == kwargs["manifest"]
                calls.append("source_manifest_ready")
                return {"state": "ready"}
            manifests["source"] = kwargs["manifest"]
            calls.append("source_manifest")
            return {"state": "uploading"}

        def upload_capability(self, **kwargs: Any) -> dict[str, Any]:
            return _capability("source_1", kwargs["chunk_index"], manifests["source"]["object"]["chunks"])

        def complete_upload(self, **kwargs: object) -> dict[str, Any]:
            calls.append("source_complete")
            return {"state": "ready"}

        def commit_file(self, **kwargs: object) -> dict[str, Any]:
            calls.append("source_commit")
            return {"fileId": kwargs["file_id"]}

        def begin_preview_upload(self, **kwargs: object) -> dict[str, Any]:
            calls.append("preview_begin")
            index = reset_count + 1
            return {
                "previewId": f"preview_{index}", "sourceObjectId": "source_1",
                "processingId": f"processing_{index}", "jobId": f"job_{index}",
                "epoch": "7", "state": preview_state,
                "nonceBaseB64u": _b64(bytes([108 + index]) * 8),
                "keyClaim": {
                    "url": f"https://arteligo.example/key-claims/preview#{'b' * 43}",
                    "expiresAtUnixMilliseconds": "4102444800000",
                    "protocol": "arteligo.file-key-claim.v1",
                },
            }

        def reset_preview_upload(self, **kwargs: object) -> dict[str, Any]:
            nonlocal reset_count, preview_state
            assert kwargs["expected_preview_id"] == f"preview_{reset_count + 1}"
            calls.append("preview_reset")
            reset_count += 1
            preview_state = "reserved"
            index = reset_count + 1
            return {
                "previewId": f"preview_{index}", "sourceObjectId": "source_1",
                "processingId": f"processing_{index}", "jobId": f"job_{index}",
                "epoch": "7", "state": "reserved",
                "nonceBaseB64u": _b64(bytes([108 + index]) * 8),
                "keyClaim": {
                    "url": f"https://arteligo.example/key-claims/preview#{'b' * 43}",
                    "expiresAtUnixMilliseconds": "4102444800000",
                    "protocol": "arteligo.file-key-claim.v1",
                },
            }

        def put_preview_manifest(self, **kwargs: Any) -> dict[str, Any]:
            manifests["preview"] = kwargs["manifest"]
            calls.append("preview_manifest")
            return {"objectId": f"preview_{reset_count + 1}", "state": "waiting"}

        def preview_upload_capability(self, **kwargs: Any) -> dict[str, Any]:
            nonlocal fail_preview
            if fail_preview:
                fail_preview = False
                raise TransferTimeoutError()
            return _capability(
                f"preview_{reset_count + 1}", kwargs["chunk_index"],
                manifests["preview"]["chunks"],
            )

        def complete_preview_upload(self, **kwargs: object) -> dict[str, Any]:
            nonlocal preview_state
            preview_state = "ready"
            calls.append("preview_complete")
            return {"objectId": f"preview_{reset_count + 1}", "state": "ready"}

    def key_claim(*args: Any, **kwargs: Any) -> FileKeyClaim:
        object_id = kwargs["expected_object_id"]
        assert object_id == "source_1" or object_id.startswith("preview_")
        return FileKeyClaim(
            direction="upload", project_id="project_1", object_id=object_id,
            epoch=7, data_key=(b"s" if object_id == "source_1" else bytes([111 + reset_count])) * 32,
            wrapped_nonce=b"w" * 12, wrapped_data_key=b"d" * 48,
        )

    monkeypatch.setattr(_workflow, "ArteligoTransferAPI", API)
    monkeypatch.setattr(_workflow, "redeem_file_key_claim", key_claim)
    monkeypatch.setattr(
        _workflow, "put_ciphertext",
        lambda url, headers, ciphertext, **kwargs: encrypted.__setitem__(url, ciphertext),
    )
    if preview_timeout_once:
        with pytest.raises(TransferError) as failure:
            _workflow.upload_file(_handoff(len(source)), source=io.BytesIO(source))
        assert failure.value.code == "preview_pending"
        assert failure.value.recoverable
        assert "source_commit" in calls and "preview_complete" not in calls
        assert "https://bucket.example/source_1:0" in encrypted
    refreshed_handoff = _handoff(len(source))
    if preview_timeout_once:
        refreshed_handoff.update({
            "previewId": "preview_2", "processingId": "processing_2", "jobId": "job_2",
        })
    result = _workflow.upload_file(refreshed_handoff, source=io.BytesIO(source))
    assert result["fileId"] == "00000000-0000-4000-8000-000000000001"
    assert calls == (
        ["source_manifest", "source_complete", "source_commit", "preview_begin",
         "preview_reset", "preview_begin", "preview_manifest",
         "source_manifest_ready", "source_commit", "preview_begin",
         "preview_reset", "preview_begin", "preview_manifest", "preview_complete"]
        if preview_timeout_once
        else ["source_manifest", "source_complete", "source_commit", "preview_begin",
              "preview_reset", "preview_begin", "preview_manifest", "preview_complete"]
    )
    preview_manifest = manifests["preview"]
    assert preview_manifest["media"]["mimeType"] == "audio/webm"
    assert preview_manifest["media"]["codecs"] == "opus"
    assert preview_manifest["media"]["playbackLoudness"]["kind"] == "measured"
    assert preview_manifest["media"]["bitrate"] == round(
        preview_manifest["plaintextSize"] * 8
        / preview_manifest["media"]["durationSeconds"]
    )
    assert preview_manifest["nonceBaseB64u"] == _b64(bytes([108 + reset_count + 1]) * 8)
    assert f"https://bucket.example/preview_{reset_count + 1}:0" in encrypted
    assert "https://bucket.example/source_1:0" in encrypted


def test_ready_preview_retry_does_not_reset_or_encode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _wav()
    calls: list[str] = []

    class API:
        def __init__(self, **kwargs: object) -> None:
            pass

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def put_manifest(self, **kwargs: object) -> dict[str, Any]:
            return {"state": "ready"}

        def commit_file(self, **kwargs: object) -> dict[str, Any]:
            return {"fileId": kwargs["file_id"]}

        def begin_preview_upload(self, **kwargs: object) -> dict[str, Any]:
            calls.append("begin")
            return {
                "previewId": "preview_2", "sourceObjectId": "source_1",
                "processingId": "processing_2", "jobId": "job_2",
                "epoch": "7", "nonceBaseB64u": _b64(b"m" * 8),
                "state": "ready",
            }

        def reset_preview_upload(self, **kwargs: object) -> None:
            pytest.fail("ready preview must not be reset")

    def claim(*args: Any, **kwargs: Any) -> FileKeyClaim:
        assert kwargs["expected_object_id"] == "source_1"
        return FileKeyClaim(
            direction="upload", project_id="project_1", object_id="source_1",
            epoch=7, data_key=b"s" * 32,
            wrapped_nonce=b"w" * 12, wrapped_data_key=b"d" * 48,
        )

    monkeypatch.setattr(_workflow, "ArteligoTransferAPI", API)
    monkeypatch.setattr(_workflow, "redeem_file_key_claim", claim)
    monkeypatch.setattr(
        _workflow, "prepare_opus_preview",
        lambda *args, **kwargs: pytest.fail("ready preview must not be re-encoded"),
    )
    refreshed_handoff = _handoff(len(source))
    refreshed_handoff.update({
        "previewId": "preview_2", "processingId": "processing_2", "jobId": "job_2",
    })
    result = _workflow.upload_file(refreshed_handoff, source=io.BytesIO(source))
    assert result["fileId"] == "00000000-0000-4000-8000-000000000001"
    assert calls == ["begin"]


def _capability(object_id: str, index: int, chunks: list[dict[str, Any]]) -> dict[str, Any]:
    chunk = chunks[index]
    return {
        "operation": "PUT", "objectId": object_id, "chunkIndex": index,
        "contentLength": chunk.get("ciphertextSize", chunk.get("ciphertext_size")),
        "url": f"https://bucket.example/{object_id}:{index}", "headers": {},
    }
