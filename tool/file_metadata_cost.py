"""Compare identical metadata using JSON v1 and binary v2 source codecs."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

from browser_metadata_fixture import file_record, node

from soenan_arteligo_support.e2ee._crypto import E2eeCrypto, decode, encode, wipe
from soenan_arteligo_support.e2ee._records import EncryptedRecords
from soenan_arteligo_support.transfer._workflow import _file_metadata_for_write, _completed_file_metadata


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
            files.append({**record, "value": _file_metadata_for_write(record["value"])})
            entries.append(entry)
        leaf, _ = node(entries)

        def size(value):
            value_bytes = crypto.canonical(value)
            try:
                return len(value_bytes)
            finally:
                wipe(value_bytes)

        def legacy_seal(value):
            data_key = crypto.key()
            plaintext = crypto.canonical(value["value"])
            key_aad = records._context("arteligo.record-key", scope, value["record_id"], value["kind"], 1, 1)
            aad = records._context("arteligo.record", scope, value["record_id"], value["kind"], 1, 1)
            try:
                packed = {
                    "wrapped_key": crypto.seal(key, data_key, key_aad),
                    "payload": crypto.seal(data_key, plaintext, aad),
                }
                return {
                    "record_id": value["record_id"], "kind": value["kind"],
                    "expected_revision": 0, "key_epoch": 1, "deleted": False,
                    "ciphertext": encode(json.dumps(packed, separators=(",", ":")).encode()),
                }
            finally:
                for secret in (data_key, plaintext, key_aad, aad):
                    wipe(secret)

        def measure(sealer):
            sealed = [sealer(value) for value in files]
            body = {
                "scope_id": scope, "records": [*sealed, sealer(leaf)],
                "format_version": 2, "expires_at": 1793836800, "preconditions": [],
            }
            signed = crypto.sign(signer["signing_secret_key"], "records_write", body, "cost-device")
            assert crypto.verify(signer["signing_public_key"], "records_write", signed) == body
            raw_body = decode(signed["body_bytes"])
            envelope = decode(sealed[0]["ciphertext"])
            representative = files[0]
            key_aad = records._context("arteligo.record-key", scope, representative["record_id"], "file", 1, 1)
            aad = records._context("arteligo.record", scope, representative["record_id"], "file", 1, 1)
            try:
                assert crypto.open_record(key, sealed[0]["ciphertext"], key_aad, aad, "file") == representative["value"]
                expanded_size = size(representative["value"])
                payload_plaintext = (
                    len(envelope) - 89 if envelope[0] == 2
                    else len(decode(json.loads(envelope)["payload"]["ciphertext"])) - 16
                )
                return {
                    "expanded_plaintext_json_bytes": expanded_size,
                    "stored_plaintext_json_bytes": payload_plaintext,
                    "source_manifest_json_bytes": size(representative["value"]["source"]) - expanded_size + payload_plaintext,
                    "decoded_ciphertext_packed_bytes": len(envelope),
                    "ciphertext_base64_bytes": len(sealed[0]["ciphertext"]),
                    "signed_record_json_bytes": size(sealed[0]),
                    "signed_body_bytes": len(raw_body),
                    "signed_command_json_bytes": size(signed),
                    "signed_body_bytes_per_file_including_leaf": len(raw_body) / 64,
                    "file_metadata_usage_bytes": len(envelope),
                }
            finally:
                for secret in (raw_body, envelope, key_aad, aad):
                    wipe(secret)

        profiles = []
        for count in (1, 16, 1024):
            value = deepcopy(files[0])
            object_value = value["value"]["source"]["object"]
            length = (count - 1) * 8 * 1024 * 1024 + 25
            object_value.update({"chunk_count": count, "plaintext_size": length,
                                 "ciphertext_size": length + 16 * count})
            checksum = object_value["chunks"][0]["ciphertext_sha256_b64u"]
            object_value["chunks"] = [
                {"chunk_index": index, "ciphertext_offset": index * (8 * 1024 * 1024 + 16),
                 "ciphertext_sha256_b64u": checksum,
                 "ciphertext_size": (25 if index + 1 == count else 8 * 1024 * 1024) + 16,
                 "final_chunk": index + 1 == count, "plaintext_offset": index * 8 * 1024 * 1024,
                 "plaintext_size": 25 if index + 1 == count else 8 * 1024 * 1024}
                for index in range(count)
            ]
            value["value"]["file"]["originalPlaintextSize"] = length
            old = legacy_seal(value)
            new = records.seal(scope, key_epoch=1, **value)
            key_aad = records._context("arteligo.record-key", scope, value["record_id"], "file", 1, 1)
            aad = records._context("arteligo.record", scope, value["record_id"], "file", 1, 1)
            try:
                assert crypto.open_record(key, new["ciphertext"], key_aad, aad, "file") == value["value"]
                profiles.append({"chunk_count": count, "json_v1_usage_bytes": len(decode(old["ciphertext"])),
                                 "binary_v2_usage_bytes": len(decode(new["ciphertext"])),
                                 "expanded_source_json_bytes": size(value["value"]["source"]),
                                 "synthetic_manifest_only_no_bucket_data": True})
            finally:
                wipe(key_aad)
                wipe(aad)

        before = measure(legacy_seal)
        after = measure(lambda value: records.seal(scope, key_epoch=1, **value))
        completed_records = [{**value, "value": _completed_file_metadata(value["value"], value["value"]["file"])} for value in files]
        locator_records = [{"record_id": "floc_" + value["record_id"], "kind": "directory", "expected_revision": 0,
            "value": {"format": 2, "type": "file_locator", "fileId": value["record_id"],
                "entryId": entry["id"], "name": entry["name"], "parentFolderId": entry["parentFolderId"], "entryRevision": 1}}
            for value, entry in zip(files, entries)]
        completed = [records.seal(scope, key_epoch=1, **value) for value in completed_records]
        locators = [records.seal(scope, key_epoch=1, **value) for value in locator_records]
        initial_body = {"scope_id": scope, "records": [*completed, *locators, records.seal(scope, key_epoch=1, **leaf)],
            "format_version": 2, "expires_at": 1793836800, "preconditions": []}
        initial_signed = crypto.sign(signer["signing_secret_key"], "records_write", initial_body, "cost-device")
        assert crypto.verify(signer["signing_public_key"], "records_write", initial_signed) == initial_body
        lifecycle = {
            "condition": "same 64 synthetic files; binary v2 both sides; common directory leaf included in initial signed body",
            "bucket_objects_created": 0, "database_records_created": 0,
            "before_file_metadata_usage_bytes": after["file_metadata_usage_bytes"],
            "after_content_usage_bytes": len(decode(completed[0]["ciphertext"])),
            "after_locator_usage_bytes": len(decode(locators[0]["ciphertext"])),
            "after_content_and_locator_usage_bytes": len(decode(completed[0]["ciphertext"])) + len(decode(locators[0]["ciphertext"])),
            "initial_signed_body_bytes_per_file_including_leaf_and_locator": len(decode(initial_signed["body_bytes"])) / 64,
            "rename_source_record_ciphertext_bytes_before": len(decode(records.seal(scope, key_epoch=1, **files[0])["ciphertext"])),
            "rename_locator_record_ciphertext_bytes_after": len(decode(locators[0]["ciphertext"])),
            "rename_directory_leaf_not_in_this_component_comparison": True,
            "rename_does_not_update_source_metadata": True,
        }
        return {
            "version": 2,
            "conditions": {
                "source": "synthetic small-file metadata using the SDK fixture builder",
                "crypto": "shared Rust AES-GCM, JCS and Ed25519 implementation",
                "file_count": 64,
                "directory_leaf_count": 1,
                "same_file_and_directory_values": True,
                "same_record_context_and_revision": True,
                "changed_fields": ["binary v2 envelope", "compact v2 source manifest"],
                "before": "JSON v1 envelope without directoryEntry copy",
                "after": "binary v2 envelope with compact source manifest",
                "bucket_objects_created": 0,
                "database_records_created": 0,
                "includes_database_heap_indexes_and_usage_ledgers": False,
                "plaintext_decryption_and_signature_verified": True,
                "comparison_to_legacy_9kb_average": False,
            },
            "source_chunk_profiles": profiles,
            "file_lifecycle": lifecycle,
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
