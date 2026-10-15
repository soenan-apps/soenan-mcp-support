"""Generate signed input data for disposable real API and database journeys."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import time
from pathlib import Path

from soenan_arteligo_support.e2ee import E2eeCrypto
from soenan_arteligo_support.e2ee._crypto import decode, wipe


def seal_fixture(crypto, key, scope, record_id, value):
    context = {
        "v": 1, "scope_id": scope, "record_id": record_id,
        "kind": "file", "key_epoch": 1, "revision": 1,
    }
    key_aad = crypto.canonical({**context, "domain": "arteligo.record-key"})
    aad = crypto.canonical({**context, "domain": "arteligo.record"})
    try:
        ciphertext = crypto.seal_record(key, value, key_aad, aad, "file")
        if crypto.open_record(key, ciphertext, key_aad, aad, "file") != value:
            raise RuntimeError("metadata fixture could not be authenticated")
        return {
            "record_id": record_id, "kind": "file", "expected_revision": 0,
            "key_epoch": 1, "deleted": False, "ciphertext": ciphertext,
        }
    finally:
        wipe(key_aad)
        wipe(aad)


def generate(output: Path, *, batches: int, plaintext_bytes: int) -> dict:
    if not 1 <= batches <= 100 or not 128 <= plaintext_bytes <= 512:
        raise ValueError("batches must be 1..100 and plaintext bytes 128..512")
    crypto = E2eeCrypto()
    signer = crypto.keypair()
    device_id = "dev_" + secrets.token_hex(16)
    public = {
        "device_id": device_id,
        "account_subject": "00000000-0000-4000-8000-000000000001",
        "encryption_public_key": signer["encryption_public_key"],
        "signing_public_key": signer["signing_public_key"],
        "state": "approved",
    }
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
                        writes = []
                        for _ in range(size):
                            value = {"name": "fixture.bin", "padding": ""}
                            base = crypto.canonical(value)
                            missing = plaintext_bytes - len(base)
                            wipe(base)
                            value["padding"] = secrets.token_hex(missing)[:missing]
                            writes.append(seal_fixture(
                                crypto, key, scope, "fil_" + secrets.token_hex(16), value))
                        command = crypto.sign(signer["signing_secret_key"], "records_write", {
                            "scope_id": scope, "format_version": 2,
                            "expires_at": int(time.time()) + 86400,
                            "records": writes, "preconditions": [],
                        }, device_id)
                        crypto.verify(public["signing_public_key"], "records_write", command)
                        body = decode(command["body_bytes"])
                        try:
                            metrics = {
                                "batch_records": size, "batch": batch,
                                "plaintext_bytes_per_record": plaintext_bytes,
                                "body_bytes": len(body),
                                "ciphertext_text_bytes": sum(len(write["ciphertext"]) for write in writes),
                                "command_json_bytes": len(json.dumps(command, separators=(",", ":")).encode()),
                                "authenticated_roundtrip_records": size,
                            }
                        finally:
                            wipe(body)
                        stream.write(json.dumps({
                            "scope_id": scope, "operation": "records_write", "device": public,
                            "command": command, "metrics": metrics,
                        }, separators=(",", ":")) + "\n")
                        statistics.append(metrics)
                    finally:
                        wipe(key)
    finally:
        signer.clear()
    return {
        "output": str(output), "batches": len(statistics),
        "authenticated_records": sum(row["batch_records"] for row in statistics),
        "samples": statistics,
        "limitations": "Signed input data only. Native cryptography prepares metadata for real API and DB consumers; it does not prove device approval, authorization, persistence, or usable Bucket objects. No private keys are exported.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batches", type=int, default=3)
    parser.add_argument("--plaintext-bytes", type=int, default=512)
    args = parser.parse_args()
    print(json.dumps(generate(args.output, batches=args.batches, plaintext_bytes=args.plaintext_bytes)))


if __name__ == "__main__":
    main()
