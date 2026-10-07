"""Generate public, cryptographically checked metadata for disposable DB benchmarks."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import time
from pathlib import Path

from soenan_arteligo_support.e2ee import DeviceSession, E2eeCrypto, EncryptedRecords
from soenan_arteligo_support.e2ee._crypto import decode, wipe


class MemoryStore:
    def __init__(self):
        self.values = {}

    def read(self, name):
        return self.values.get(name)

    def write(self, name, value):
        self.values[name] = value

    def delete(self, name):
        self.values.pop(name, None)


class OfflineAPI:
    def call(self, *args, **kwargs):
        raise RuntimeError("metadata fixture must not make network calls")


def generate(output: Path, *, batches: int, plaintext_bytes: int) -> dict:
    if not 1 <= batches <= 100 or not 128 <= plaintext_bytes <= 512:
        raise ValueError("batches must be 1..100 and plaintext bytes 128..512")
    crypto = E2eeCrypto()
    session = DeviceSession(OfflineAPI(), crypto, MemoryStore(),
        origin="https://metadata-fixture.invalid", subject="00000000-0000-4000-8000-000000000001")
    session._device = {**crypto.keypair(), "device_id": "dev_" + secrets.token_hex(16)}
    session.state = "approved"
    public = session.public
    session._devices[session.device_id] = public
    session.trust.pin_device(public)
    records = EncryptedRecords(session)
    statistics = []
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w") as stream:
            for size in (1, 3, 64, 256):
                for batch in range(batches):
                    scope = "prj_" + secrets.token_hex(16)
                    key = crypto.key()
                    try:
                        session._remember(scope, 1, key)
                    finally:
                        wipe(key)
                    values, writes = [], []
                    for _ in range(size):
                        value = {"name": "fixture.bin", "padding": ""}
                        base = crypto.canonical(value)
                        missing = plaintext_bytes - len(base)
                        wipe(base)
                        value["padding"] = secrets.token_hex(missing)[:missing]
                        values.append(value)
                        writes.append(records.seal(scope, record_id="fil_" + secrets.token_hex(16),
                            kind="file", expected_revision=0, key_epoch=1, value=value))
                    command = session.sign("records_write", {"scope_id": scope,
                        "format_version": 2, "expires_at": int(time.time()) + 86400,
                        "records": writes, "preconditions": []})
                    crypto.verify(public["signing_public_key"], "records_write", command)
                    verified = {}
                    for ordinal, (write, value) in enumerate(zip(writes, values, strict=True)):
                        opened = records.open(scope, {**write, "revision": 1, "cursor": ordinal + 1,
                            "signed_command": command, "author_device_id": session.device_id}, verified=verified)
                        if opened["value"] != value:
                            raise RuntimeError("metadata fixture did not survive authenticated round trip")
                    body = decode(command["body_bytes"])
                    try:
                        metrics = {"batch_records": size, "batch": batch, "plaintext_bytes_per_record": plaintext_bytes,
                            "body_bytes": len(body), "ciphertext_text_bytes": sum(len(write["ciphertext"]) for write in writes),
                            "command_json_bytes": len(json.dumps(command, separators=(",", ":")).encode()),
                            "authenticated_roundtrip_records": size}
                    finally:
                        wipe(body)
                    stream.write(json.dumps({"scope_id": scope, "operation": "records_write",
                        "device": public, "command": command, "metrics": metrics}, separators=(",", ":")) + "\n")
                    statistics.append(metrics)
                    session._clear_keys()
    finally:
        session.lock()
    return {"output": str(output), "batches": len(statistics),
        "authenticated_records": sum(row["batch_records"] for row in statistics), "samples": statistics,
        "limitations": "Fixed-size minimal name/padding documents measure cryptographic and batch overhead; they are not full upload manifests or usable file objects. No private keys are exported."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batches", type=int, default=3)
    parser.add_argument("--plaintext-bytes", type=int, default=512)
    args = parser.parse_args()
    print(json.dumps(generate(args.output, batches=args.batches, plaintext_bytes=args.plaintext_bytes)))


if __name__ == "__main__":
    main()
