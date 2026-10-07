from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from soenan_arteligo_support.e2ee import E2eeCrypto, E2eeError
from soenan_arteligo_support.e2ee._crypto import decode, encode, wipe
from soenan_arteligo_support.transfer._crypto import CHUNK_SIZE, ChunkMetadata, EncryptionPlan


def test_shared_record_vector_roundtrip_and_tamper_rejection():
    vector = json.loads((Path(__file__).parent / "fixtures/record_binary_vector.json").read_text())
    crypto = E2eeCrypto()
    key, key_aad, aad = (decode(vector[field]) for field in ("key", "key_aad", "aad"))
    try:
        assert crypto.open_record(key, vector["ciphertext"], key_aad, aad, vector["kind"]) == vector["document"]
        ciphertext = crypto.seal_record(key, vector["document"], key_aad, aad, vector["kind"])
        assert decode(ciphertext)[0] == 2
        assert crypto.open_record(key, ciphertext, key_aad, aad, vector["kind"]) == vector["document"]
        corrupted = decode(ciphertext)
        corrupted[-1] ^= 1
        with pytest.raises(E2eeError, match="authentication_failed"):
            crypto.open_record(key, encode(corrupted), key_aad, aad, vector["kind"])
        with pytest.raises(E2eeError, match="authentication_failed"):
            crypto.open_record(key, ciphertext, key_aad, b"other context", vector["kind"])
    finally:
        for secret in (key, key_aad, aad):
            wipe(secret)


@pytest.mark.parametrize("count", [1, 2, 1024])
def test_compact_source_preserves_chunk_integrity_and_unknown_fields(count):
    crypto = E2eeCrypto()
    size = (count - 1) * CHUNK_SIZE + 37
    chunks = tuple(
        ChunkMetadata(index=index, ciphertext_offset=index * (CHUNK_SIZE + 16),
                      ciphertext_sha256=bytes([index % 256]) * 32,
                      ciphertext_size=(37 if index + 1 == count else CHUNK_SIZE) + 16,
                      final=index + 1 == count, plaintext_offset=index * CHUNK_SIZE,
                      plaintext_size=37 if index + 1 == count else CHUNK_SIZE)
        for index in range(count)
    )
    source = EncryptionPlan("project", "file", "object", 1, size, count, b"N" * 8,
                            b"K" * 32, b"W" * 12, b"C" * 48, chunks).manifest()
    document = {"source": source, "unknown": {"keep": "value"}}
    key = crypto.key()
    try:
        ciphertext = crypto.seal_record(key, document, b"key-aad", b"aad", "file")
        assert crypto.open_record(key, ciphertext, b"key-aad", b"aad", "file") == document
        assert len(decode(ciphertext)) < len(crypto.canonical(document))
        extended = deepcopy(document)
        extended["source"]["object"]["futureField"] = {"keep": True}
        ciphertext = crypto.seal_record(key, extended, b"key-aad", b"aad", "file")
        assert crypto.open_record(key, ciphertext, b"key-aad", b"aad", "file") == extended
    finally:
        wipe(key)
