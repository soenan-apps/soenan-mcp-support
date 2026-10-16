#!/usr/bin/env python3
"""Exercise the installed SDK converter with real WAV bytes and FFmpeg processes."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import struct
import subprocess
import sys
import threading
import wave

from soenan_arteligo_support.transfer._http import TransferError, TransferTimeoutError
from soenan_arteligo_support.transfer._opus import preflight_wav_preview, prepare_opus_preview


def convert(source: Path, timeout: float) -> dict[str, object]:
    with source.open("rb") as stream:
        preflight_wav_preview(stream, source.stat().st_size)
        with prepare_opus_preview(stream, source_size=source.stat().st_size, timeout=timeout) as preview:
            return {
                "size": preview.size,
                "duration": preview.duration_seconds,
                "channels": preview.channels,
                "source_sha256": preview.source_sha256.hex(),
                "encoded_sha256": hashlib.sha256(preview.path.read_bytes()).hexdigest(),
            }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--hold", type=Path)
    args = parser.parse_args()
    if args.hold is not None:
        with args.hold.open("rb") as stream:
            with prepare_opus_preview(stream, source_size=args.hold.stat().st_size, timeout=60) as preview:
                print(json.dumps({"ready": True, "path": str(preview.path)}), flush=True)
                signal.pause()
        return
    if args.output is None:
        parser.error("--output is required")
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.output / "source.wav"
    with wave.open(str(source), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(48000)
        output.writeframes(b"".join(struct.pack("<h", int(12000 * math.sin(index * 2 * math.pi * 440 / 48000))) for index in range(48000)))
    original = source.read_bytes()
    ancillary = b"JUNK" + struct.pack("<I", 1048578) + bytes(1048578)
    extended = args.output / "large-ancillary.wav"
    extended.write_bytes(b"RIFF" + struct.pack("<I", len(original) - 8 + len(ancillary)) + original[8:12] + ancillary + original[12:])
    digest = hashlib.sha256(extended.read_bytes()).hexdigest()
    result = convert(extended, 60)
    if result["source_sha256"] != digest:
        raise RuntimeError("converter did not authenticate the original WAV bytes")
    invalid = args.output / "invalid-ancillary.wav"
    invalid.write_bytes(extended.read_bytes()[:16] + struct.pack("<I", 0xFFFFFFFF) + extended.read_bytes()[20:])
    try:
        convert(invalid, 60)
    except TransferError:
        result["invalid_chunk_rejected"] = True
    else:
        raise RuntimeError("out-of-file ancillary chunk was accepted")
    try:
        convert(extended, 0.001)
    except TransferTimeoutError:
        result["child_deadline_reaped"] = not any(thread.name == "arteligo-opus-input" for thread in threading.enumerate())
    else:
        raise RuntimeError("converter deadline was not exercised")
    if not result["child_deadline_reaped"]:
        raise RuntimeError("converter input thread survived deadline")
    if os.name == "posix":
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--hold", str(extended)], stdout=subprocess.PIPE, text=True)
        try:
            assert child.stdout is not None
            held = json.loads(child.stdout.readline())
            if not held.get("ready") or not str(held["path"]).startswith("/dev/fd/"):
                raise RuntimeError("preview was not held in an anonymous file")
            descriptor = None
            if sys.platform == "linux":
                descriptor = Path(f"/proc/{child.pid}/fd/{Path(held['path']).name}")
                if descriptor.stat().st_nlink != 0:
                    raise RuntimeError("preview inode has a persistent directory link")
            child.kill()
            child.wait(timeout=10)
            result["forced_exit_anonymous_preview"] = child.returncode == -signal.SIGKILL
            if descriptor is not None:
                if descriptor.exists():
                    raise RuntimeError("preview descriptor survived forced process exit")
                result["unlinked_preview_inode_released"] = True
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
    if hashlib.sha256(extended.read_bytes()).hexdigest() != digest:
        raise RuntimeError("converter changed the original WAV")
    result["original_preserved"] = True
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
