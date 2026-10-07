"""Compare the same disposable file metadata with and without its entry copy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from browser_metadata_fixture import file_record, node

from soenan_arteligo_support.e2ee._crypto import E2eeCrypto, decode, wipe
from soenan_arteligo_support.e2ee._records import EncryptedRecords
from soenan_arteligo_support.transfer._workflow import _file_metadata_for_write


class CostSession:
    def __init__(self, crypto: E2eeCrypto, key: bytearray):
        self.crypto = crypto
        self.subject = "00000000-0000-0000-0000-000000000000"
        self.key = key

    def scope_key(self, _scope, _epoch):
        return bytearray(self.key)


def compare():
    crypto = E2eeCrypto()
    key = crypto.key()
    signer = crypto.keypair()
    session = CostSession(crypto, key)
    records = EncryptedRecords(session)
    scope = "prj_" + "0" * 32
    timestamp = "2026-10-06T00:00:00.000000Z"
    files, entries = [], []
    try:
        for index in range(64):
            record, entry = file_record(
                session, scope, index, "0" * 24, timestamp, key
            )
            files.append(
                {
                    **record,
                    "value": {**record["value"], "directoryEntry": entry},
                }
            )
            entries.append(entry)
        leaf, _ = node(entries)
        sealed_leaf = records.seal(scope, key_epoch=1, **leaf)

        def size(value):
            value_bytes = crypto.canonical(value)
            try:
                return len(value_bytes)
            finally:
                wipe(value_bytes)

        def measure(values):
            sealed = [
                records.seal(scope, key_epoch=1, **value) for value in values
            ]
            body = {
                "scope_id": scope,
                "records": [*sealed, sealed_leaf],
                "format_version": 2,
                "expires_at": 1793836800,
                "preconditions": [],
            }
            signed = crypto.sign(
                signer["signing_secret_key"], "records_write", body, "cost-device"
            )
            assert crypto.verify(
                signer["signing_public_key"], "records_write", signed
            ) == body
            raw_body = decode(signed["body_bytes"])
            envelope = decode(sealed[0]["ciphertext"])
            try:
                packed = json.loads(envelope)
                representative = values[0]
                data_key = crypto.open(
                    key,
                    packed["wrapped_key"],
                    records._context(
                        "arteligo.record-key",
                        scope,
                        representative["record_id"],
                        "file",
                        1,
                        1,
                    ),
                )
                plaintext = bytearray()
                try:
                    plaintext = crypto.open(
                        data_key,
                        packed["payload"],
                        records._context(
                            "arteligo.record",
                            scope,
                            representative["record_id"],
                            "file",
                            1,
                            1,
                        ),
                    )
                    assert json.loads(plaintext) == representative["value"]
                finally:
                    wipe(data_key)
                    wipe(plaintext)
                return {
                    "plaintext_json_bytes": size(representative["value"]),
                    "decoded_ciphertext_packed_bytes": len(envelope),
                    "ciphertext_base64_bytes": len(sealed[0]["ciphertext"]),
                    "signed_record_json_bytes": size(sealed[0]),
                    "signed_body_bytes": len(raw_body),
                    "signed_command_json_bytes": size(signed),
                    "signed_body_bytes_per_file_including_leaf": len(raw_body) / 64,
                    "file_metadata_usage_bytes": len(envelope),
                }
            finally:
                wipe(raw_body)
                wipe(envelope)

        before = measure(files)
        after = measure(
            [
                {**file, "value": _file_metadata_for_write(file["value"])}
                for file in files
            ]
        )
        return {
            "version": 1,
            "conditions": {
                "source": "synthetic small-file metadata using the SDK fixture builder",
                "crypto": "shared Rust AES-GCM, JCS and Ed25519 implementation",
                "file_count": 64,
                "directory_leaf_count": 1,
                "same_file_and_directory_values": True,
                "same_record_context_and_revision": True,
                "changed_field": "file payload directoryEntry copy only",
                "bucket_objects_created": 0,
                "database_records_created": 0,
                "includes_database_heap_indexes_and_usage_ledgers": False,
                "plaintext_decryption_and_signature_verified": True,
                "comparison_to_legacy_9kb_average": False,
            },
            "before": before,
            "after": after,
            "reduction_bytes": {
                name: before[name] - after[name] for name in before
            },
        }
    finally:
        wipe(key)
        signer.clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = compare()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    args.output.chmod(0o600)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
