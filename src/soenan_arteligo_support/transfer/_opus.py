from __future__ import annotations

import io
import json
import math
import re
import shutil
import subprocess
import struct
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import BinaryIO, Iterator

from ._http import TransferError, TransferSizeMismatch, TransferTimeoutError

_PREVIEW_LIMIT = 512 * 1024 * 1024
_DISK_RESERVE = 256 * 1024 * 1024
_COPY_SIZE = 256 * 1024
_CHILD_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C"}
_LOUDNORM_RESULT = re.compile(rb"\{\s*\"input_i\"\s*:.*?\}", re.DOTALL)
_HEADER_SCAN_LIMIT = 1024 * 1024
_SURROUND_WEIGHT = 0.7071067811865476
_SURROUND_MASKS = frozenset({0x7, 0x33, 0x37, 0x607, 0x3F, 0x60F, 0x63F})
_WAVE_SUBFORMAT_TAIL = bytes.fromhex("00001000800000aa00389b71")


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TransferTimeoutError()
    return remaining


@dataclass(frozen=True)
class OpusPreview:
    path: Path
    size: int
    integrated_lufs_x100: int | None
    true_peak_dbtp_x100: int | None
    loudness_range_lu_x100: int | None
    duration_seconds: float
    channels: int
    bitrate: int
    source_sha256: bytes


@contextmanager
def prepare_opus_preview(
    source: BinaryIO, *, source_size: int, timeout: float
) -> Iterator[OpusPreview]:
    """Encode a seekable WAV stream locally without exposing its path to child processes."""
    with tempfile.TemporaryDirectory(prefix="arteligo-opus-") as temporary:
        output = Path(temporary) / "preview.webm"
        available = shutil.disk_usage(temporary).free - _DISK_RESERVE
        output_limit = min(_PREVIEW_LIMIT, available)
        if output_limit <= 0:
            raise TransferError("local preview disk space is insufficient")
        start = source.tell()
        end = source.seek(0, io.SEEK_END)
        source.seek(start)
        if end - start != source_size:
            raise TransferSizeMismatch(
                "WAV source size does not match the selected file"
            )
        deadline = time.monotonic() + timeout
        try:
            source_sha256 = _encode(
                source,
                source_size,
                output,
                _remaining(deadline),
                output_limit,
            )
            size = output.stat().st_size
            if not 0 < size <= output_limit:
                raise TransferError("encoded preview exceeds the local size limit")
            duration, channels = _verify_encoded_media(output, _remaining(deadline))
            bitrate = math.floor(size * 8 / duration + 0.5)
            if not 0 < bitrate <= 2_147_483_647:
                raise TransferError("encoded preview effective bitrate is unsupported")
            integrated, peak, loudness_range = _analyze(output, _remaining(deadline))
            source.seek(start)
            yield OpusPreview(
                output,
                size,
                integrated,
                peak,
                loudness_range,
                duration,
                channels,
                bitrate,
                source_sha256,
            )
        finally:
            source.seek(start)


def _binary(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise TransferError("local media tools are unavailable")
    return executable


def _read_header(stream: BinaryIO, length: int) -> bytes:
    result = bytearray()
    while len(result) < length:
        part = stream.read(length - len(result))
        if not isinstance(part, bytes) or not part:
            raise TransferError("WAV header is incomplete")
        result.extend(part)
    return bytes(result)


def preflight_wav_preview(source: BinaryIO, source_size: int) -> None:
    """Reject impossible-duration previews before publishing the source object."""
    start = source.tell()
    try:
        riff = _read_header(source, 12)
        if riff[:4] not in (b"RIFF", b"RF64", b"BW64") or riff[8:] != b"WAVE":
            raise TransferError("preview source is not a WAV file")
        offset = 12
        byte_rate: int | None = None
        rf64_data_size: int | None = None
        block_align: int | None = None
        while offset + 8 <= min(source_size, _HEADER_SCAN_LIMIT):
            source.seek(start + offset)
            chunk_id, chunk_size = struct.unpack("<4sI", _read_header(source, 8))
            offset += 8
            if chunk_id == b"data":
                if chunk_size == 0xFFFFFFFF:
                    if rf64_data_size is None:
                        raise TransferError("RF64 data length is unavailable")
                    chunk_size = rf64_data_size
                if (
                    byte_rate is None
                    or block_align is None
                    or chunk_size > source_size - offset
                    or chunk_size % block_align
                ):
                    raise TransferError("WAV data size is invalid")
                duration = chunk_size / byte_rate
                if duration <= 0 or duration > 86400:
                    raise TransferError("WAV preview duration is unsupported")
                source.seek(start)
                _wav_pan_filter(source, source_size)
                return
            if (
                chunk_size > _HEADER_SCAN_LIMIT - offset
                or offset + chunk_size > source_size
            ):
                raise TransferError("WAV header exceeds the local scan limit")
            if chunk_id == b"ds64" and chunk_size >= 16:
                source.seek(start + offset + 8)
                rf64_data_size = struct.unpack("<Q", _read_header(source, 8))[0]
            if chunk_id == b"fmt ":
                if chunk_size < 16:
                    raise TransferError("WAV format header is incomplete")
                fmt = _read_header(source, 16)
                sample_rate, byte_rate, block_align = struct.unpack_from("<IIH", fmt, 4)
                if (
                    sample_rate == 0
                    or block_align == 0
                    or byte_rate != sample_rate * block_align
                ):
                    raise TransferError("WAV format rate is invalid")
            offset += chunk_size + (chunk_size & 1)
        raise TransferError("WAV audio data is missing")
    finally:
        source.seek(start)


def _wav_pan_filter(source: BinaryIO, source_size: int) -> str | None:
    start = source.tell()
    try:
        header = _read_header(source, 12)
        if header[:4] not in (b"RIFF", b"RF64", b"BW64") or header[8:] != b"WAVE":
            raise TransferError("preview source is not a WAV file")
        offset = 12
        while offset + 8 <= min(source_size, _HEADER_SCAN_LIMIT):
            source.seek(start + offset)
            chunk_id, chunk_size = struct.unpack("<4sI", _read_header(source, 8))
            offset += 8
            if chunk_id == b"data":
                break
            if (
                chunk_size > _HEADER_SCAN_LIMIT - offset
                or offset + chunk_size > source_size
            ):
                raise TransferError("WAV format header exceeds the local scan limit")
            if chunk_id == b"fmt ":
                if chunk_size < 16:
                    raise TransferError("WAV format header is incomplete")
                fmt = _read_header(source, min(chunk_size, 40))
                encoding, channels = struct.unpack_from("<HH", fmt)
                if not 1 <= channels <= 8:
                    raise TransferError("WAV channel count is unsupported")
                if encoding == 0xFFFE:
                    if (
                        chunk_size < 40
                        or struct.unpack_from("<H", fmt, 16)[0] < 22
                        or fmt[28:40] != _WAVE_SUBFORMAT_TAIL
                        or struct.unpack_from("<I", fmt, 24)[0] not in (1, 3)
                    ):
                        raise TransferError("WAV extensible format is unsupported")
                    mask = struct.unpack_from("<I", fmt, 20)[0]
                elif encoding in (1, 3):
                    mask = 0
                else:
                    raise TransferError("WAV encoding is unsupported")
                if channels == 1 and mask in (0, 0x1, 0x4):
                    return None
                if channels == 2 and mask in (0, 0x3):
                    return None
                if mask not in _SURROUND_MASKS or mask.bit_count() != channels:
                    raise TransferError("WAV channel layout is unsupported")
                speakers = [bit for bit in range(32) if mask & (1 << bit)]
                left = {
                    0: 1.0,
                    2: _SURROUND_WEIGHT,
                    4: _SURROUND_WEIGHT,
                    9: _SURROUND_WEIGHT,
                }
                right = {
                    1: 1.0,
                    2: _SURROUND_WEIGHT,
                    5: _SURROUND_WEIGHT,
                    10: _SURROUND_WEIGHT,
                }
                gain = 1.0 / max(
                    sum(left.get(bit, 0.0) for bit in speakers),
                    sum(right.get(bit, 0.0) for bit in speakers),
                )

                def row(weights: dict[int, float]) -> str:
                    return "+".join(
                        f"{weights[bit] * gain:.17g}*c{index}"
                        for index, bit in enumerate(speakers)
                        if bit in weights
                    )

                return f"pan=stereo|c0={row(left)}|c1={row(right)}"
            offset += chunk_size + (chunk_size & 1)
        raise TransferError("WAV format header is missing")
    finally:
        source.seek(start)


def _encode(
    source: BinaryIO,
    source_size: int,
    output: Path,
    timeout: float,
    output_limit: int,
) -> bytes:
    pan_filter = _wav_pan_filter(source, source_size)
    command = [
        _binary("ffmpeg"),
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-y",
        "-threads",
        "2",
        "-filter_threads",
        "2",
        "-i",
        "pipe:0",
        "-map",
        "0:a:0",
        "-vn",
        "-ar",
        "48000",
        *(["-af", pan_filter] if pan_filter is not None else ["-ac", "2"]),
        "-c:a",
        "libopus",
        "-threads",
        "2",
        "-b:a",
        "128k",
        "-vbr",
        "on",
        "-fflags",
        "+bitexact",
        "-flags:a",
        "+bitexact",
        "-fs",
        str(output_limit + 1),
        "-f",
        "webm",
        str(output),
    ]
    errors: list[Exception] = []
    source_digest = sha256()
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            env=_CHILD_ENV,
        )
    except OSError:
        raise TransferError("local ffmpeg is unavailable") from None

    def feed() -> None:
        remaining = source_size
        try:
            assert process.stdin is not None
            while remaining:
                data = source.read(min(remaining, _COPY_SIZE))
                if not isinstance(data, bytes) or not data or len(data) > remaining:
                    raise TransferSizeMismatch(
                        "WAV source changed during preview encoding"
                    )
                process.stdin.write(data)
                source_digest.update(data)
                remaining -= len(data)
            if source.read(1):
                raise TransferSizeMismatch("WAV source changed during preview encoding")
        except (OSError, ValueError, TransferSizeMismatch) as error:
            errors.append(error)
        finally:
            if process.stdin is not None:
                try:
                    process.stdin.close()
                except OSError:
                    pass

    feeder = threading.Thread(target=feed, name="arteligo-opus-input", daemon=True)
    feeder.start()
    try:
        process.wait(timeout=timeout)
        feeder.join(timeout=1)
        if feeder.is_alive():
            raise TransferTimeoutError()
        if errors:
            if isinstance(errors[0], TransferSizeMismatch):
                raise errors[0]
            raise TransferError("local WAV source could not be read") from None
        if process.returncode != 0:
            raise TransferError("local WAV-to-Opus encoding failed")
        return source_digest.digest()
    except (subprocess.TimeoutExpired, TransferTimeoutError):
        raise TransferTimeoutError() from None
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        feeder.join(timeout=1)


def _verify_encoded_media(output: Path, timeout: float) -> tuple[float, int]:
    try:
        result = subprocess.run(
            [
                _binary("ffprobe"),
                "-v",
                "error",
                "-show_entries",
                "format=format_name,duration:stream=codec_type,codec_name,sample_rate,channels",
                "-of",
                "json",
                str(output),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
            close_fds=True,
            env=_CHILD_ENV,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise TransferError("encoded preview could not be verified") from None
    try:
        if result.returncode or len(result.stdout) > 4096:
            raise ValueError
        metadata = json.loads(result.stdout)
        streams = metadata["streams"]
        if (
            "webm" not in metadata["format"]["format_name"].split(",")
            or len(streams) != 1
            or streams[0]["codec_type"] != "audio"
            or streams[0]["codec_name"] != "opus"
            or streams[0]["sample_rate"] != "48000"
            or streams[0]["channels"] not in (1, 2)
        ):
            raise ValueError
        duration = float(metadata["format"]["duration"])
        if not math.isfinite(duration) or not 0 < duration <= 86400:
            raise ValueError
        return duration, streams[0]["channels"]
    except (KeyError, TypeError, ValueError):
        raise TransferError("encoded preview is not WebM/Opus audio") from None


def _analyze(output: Path, timeout: float) -> tuple[int | None, int | None, int | None]:
    command = [
        _binary("ffmpeg"),
        "-hide_banner",
        "-nostdin",
        "-threads",
        "2",
        "-filter_threads",
        "2",
        "-i",
        str(output),
        "-map",
        "0:a:0",
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f",
        "null",
        "-",
    ]
    with tempfile.TemporaryFile(mode="w+b") as diagnostics:
        try:
            result = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=diagnostics,
                timeout=timeout,
                check=False,
                close_fds=True,
                env=_CHILD_ENV,
            )
        except subprocess.TimeoutExpired:
            raise TransferTimeoutError() from None
        except OSError:
            raise TransferError("local ffmpeg analysis is unavailable") from None
        if result.returncode:
            raise TransferError("encoded preview loudness analysis failed")
        if diagnostics.tell() > 65536:
            raise TransferError("encoded preview loudness analysis is invalid")
        diagnostics.seek(0)
        found = _LOUDNORM_RESULT.search(diagnostics.read())
    if found is None:
        raise TransferError("encoded preview loudness analysis is invalid")
    try:
        values = json.loads(found.group())
        return (
            _hundredths(values["input_i"]),
            _hundredths(values["input_tp"]),
            _hundredths(values["input_lra"]),
        )
    except (KeyError, ValueError, TypeError):
        raise TransferError("encoded preview loudness analysis is invalid") from None


def _hundredths(value: object) -> int | None:
    if not isinstance(value, str):
        raise ValueError("invalid loudness")
    number = float(value)
    if math.isnan(number) or number == math.inf:
        raise ValueError("invalid loudness")
    if number == -math.inf:
        return None
    return round(number * 100)
