from __future__ import annotations

import json
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
from types import SimpleNamespace

import pytest
from test_e2ee import MemoryAPI, new_session

from soenan_arteligo_support.e2ee import E2eeCrypto, E2eeError, EncryptedRecords
from soenan_arteligo_support.e2ee._crypto import decode, encode
from soenan_arteligo_support.transfer import (
    _preview,
    _workflow,
    upload_file,
    upload_wav_preview,
)


class PreviewAPI(MemoryAPI):
    def __init__(self):
        super().__init__(E2eeCrypto())
        self.base_url = "https://bucket.test"
        self.uploads = {}
        self.puts = []

    def put(self, url, headers, ciphertext, **_kwargs):
        self.puts.append(url)
        self.uploads[url.removeprefix(self.base_url)] = ciphertext

    def call(self, operation, *, body=None, **parameters):
        value = (
            json.loads(decode(body["body_bytes"]))
            if body and "body_bytes" in body
            else None
        )
        if operation == "e2eeGetObject":
            existing = self.objects.get(parameters["object_id"])
            if existing is None or existing["state"] != "ready":
                raise E2eeError("not_found")
        if (
            operation == "e2eePutObjectCapability"
            and self.objects[value["object_id"]]["state"] != "uploading"
        ):
            raise E2eeError("revision_conflict")
        if operation == "e2eeFinalizeObject":
            for chunk in self.objects[value["object_id"]]["manifest"]["chunks"]:
                uploaded = self.uploads[f"/{value['object_id']}/{chunk['index']}"]
                assert len(uploaded) == chunk["ciphertext_size"]
                assert encode(sha256(uploaded).digest()) == chunk["checksum_sha256"]
        return super().call(operation, body=body, **parameters)


@pytest.fixture
def preview_workspace(tmp_path, monkeypatch):
    api = PreviewAPI()
    owner, _, _ = new_session(api, setup=True)
    scope = EncryptedRecords(owner).create_project(
        value={"title": "プレビュー再開"}, owner_org="org-test"
    )
    source = tmp_path / "source.wav"
    source.write_bytes(b"authenticated source bytes")
    monkeypatch.setattr(_workflow, "put_ciphertext", api.put)
    monkeypatch.setattr(_preview, "put_ciphertext", api.put)
    uploaded = upload_file(owner, project_id=scope, source=source)
    encoding = SimpleNamespace(calls=0, content=b"deterministic preview bytes")

    @contextmanager
    def encode_preview(stream, *, source_size, timeout):
        encoding.calls += 1
        source_bytes = stream.read()
        assert len(source_bytes) == source_size
        encoded = tmp_path / "encoded.webm"
        encoded.write_bytes(encoding.content)
        yield SimpleNamespace(
            path=encoded,
            size=len(encoding.content),
            integrated_lufs_x100=-1600,
            true_peak_dbtp_x100=-150,
            loudness_range_lu_x100=100,
            duration_seconds=1.0,
            channels=2,
            bitrate=len(encoding.content) * 8,
            source_sha256=sha256(source_bytes).digest(),
        )

    monkeypatch.setattr(_preview, "prepare_opus_preview", encode_preview)
    return api, owner, scope, uploaded["file_id"], source, encoding


def read_file(owner, scope, file_id):
    return EncryptedRecords(owner).read(scope, [file_id])[file_id]


def written_preview(owner, scope, body):
    values = json.loads(decode(body["body_bytes"]))["records"]
    record = values[0]
    opened = EncryptedRecords(owner).open(
        scope,
        {
            **record,
            "revision": record["expected_revision"] + 1,
            "author_device_id": owner.device_id,
            "signed_command": body,
        },
    )
    return opened["value"].get("preview", {})


@pytest.mark.parametrize(
    "failure",
    ["reservation_response", "finalize_response", "file_conflict", "file_response"],
)
def test_preview_resumes_same_object_after_commit_boundaries(
    preview_workspace, monkeypatch, failure
):
    api, owner, scope, file_id, source, encoding = preview_workspace
    original = api.call
    failed = False

    def interrupt(operation, *, body=None, **parameters):
        nonlocal failed
        preview = (
            written_preview(owner, scope, body)
            if operation == "e2eeWriteRecords"
            else {}
        )
        target = (
            (failure == "reservation_response" and preview.get("state") == "waiting")
            or (failure == "finalize_response" and operation == "e2eeFinalizeObject")
            or (
                failure in {"file_conflict", "file_response"}
                and preview.get("state") == "ready"
            )
        )
        if target and not failed:
            failed = True
            if failure == "file_conflict":
                current = read_file(owner, scope, file_id)
                EncryptedRecords(owner).write(
                    scope,
                    key_epoch=1,
                    records=[
                        {
                            "record_id": file_id,
                            "kind": "file",
                            "expected_revision": current["revision"],
                            "value": {
                                **current["value"],
                                "concurrent_note": "keep this edit",
                            },
                        }
                    ],
                )
            else:
                original(operation, body=body, **parameters)
                raise E2eeError("service_unavailable")
        return original(operation, body=body, **parameters)

    monkeypatch.setattr(api, "call", interrupt)
    with pytest.raises(E2eeError, match="revision_conflict|service_unavailable"):
        upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
    pending = read_file(owner, scope, file_id)["value"]["preview"]
    identifier = pending["previewId"]
    puts_before_retry = len(api.puts)
    encodings_before_retry = encoding.calls
    result = upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
    assert result == {"file_id": file_id, "preview_id": identifier, "state": "ready"}
    assert len(api.objects) == 2
    assert api.objects[identifier]["state"] == "ready"
    value = read_file(owner, scope, file_id)["value"]
    assert value["preview"] == {**pending, "state": "ready"}
    if failure == "file_conflict":
        assert value["concurrent_note"] == "keep this edit"
    if failure != "reservation_response":
        assert len(api.puts) == puts_before_retry
        assert encoding.calls == encodings_before_retry
    assert (
        upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
        == result
    )
    assert len(api.objects) == 2


@pytest.mark.parametrize("changed", [False, True])
def test_preview_partial_upload_retains_nonce_and_rejects_changed_encoded_bytes(
    preview_workspace, monkeypatch, changed
):
    api, owner, scope, file_id, source, encoding = preview_workspace
    original_put = api.put

    def interrupted_put(*args, **kwargs):
        original_put(*args, **kwargs)
        raise E2eeError("service_unavailable")

    monkeypatch.setattr(_preview, "put_ciphertext", interrupted_put)
    with pytest.raises(E2eeError, match="service_unavailable"):
        upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
    pending = read_file(owner, scope, file_id)["value"]["preview"]
    assert pending["state"] == "waiting"
    assert api.objects[pending["previewId"]]["state"] == "uploading"
    before = deepcopy(api.uploads)
    monkeypatch.setattr(_preview, "put_ciphertext", original_put)
    if changed:
        encoding.content = b"encoder produced different preview bytes"
        with pytest.raises(E2eeError, match="preview_encoding_changed"):
            upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
        assert api.uploads == before
        assert read_file(owner, scope, file_id)["value"]["preview"] == pending
    else:
        result = upload_wav_preview(
            owner, project_id=scope, file_id=file_id, source=source
        )
        assert result["preview_id"] == pending["previewId"]
        assert api.uploads == before
        assert read_file(owner, scope, file_id)["value"]["preview"] == {
            **pending,
            "state": "ready",
        }
    assert len(api.objects) == 2


@pytest.mark.parametrize("published", [False, True])
def test_ready_preview_rejects_a_changed_source_without_bucket_writes(
    preview_workspace, monkeypatch, published
):
    api, owner, scope, file_id, source, _ = preview_workspace
    if not published:
        original = api.call

        def lost_finalize(operation, **parameters):
            result = original(operation, **parameters)
            if operation == "e2eeFinalizeObject":
                raise E2eeError("service_unavailable")
            return result

        monkeypatch.setattr(api, "call", lost_finalize)
        with pytest.raises(E2eeError, match="service_unavailable"):
            upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
        monkeypatch.setattr(api, "call", original)
    else:
        upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
    before = deepcopy(api.uploads)
    pending = read_file(owner, scope, file_id)["value"]["preview"]
    source.write_bytes(source.read_bytes()[:-1] + b"!")
    with pytest.raises(E2eeError, match="source_changed"):
        upload_wav_preview(owner, project_id=scope, file_id=file_id, source=source)
    assert api.uploads == before
    assert len(api.objects) == 2
    assert read_file(owner, scope, file_id)["value"]["preview"] == pending


def test_approval_skips_only_organizations_without_a_key(monkeypatch):
    api = MemoryAPI(E2eeCrypto())
    owner, _, _ = new_session(api, setup=True)
    scope = EncryptedRecords(owner).create_project(
        value={"title": "承認時にも共有する鍵"}, owner_org="org-test"
    )
    api.projects[scope]["lifecycle"] = "rekey_required"
    added, _, _ = new_session(api)
    pairing = added.enroll()
    original = api.call

    def organizations(operation, **parameters):
        if operation == "e2eeListOrganizations":
            return {
                "projects": [
                    {
                        "project_id": "org-unused",
                        "owner_org": "org-unused",
                        "participation_policy": "organization",
                        "role": "owner",
                        "key_epoch": 0,
                        "lifecycle": "uninitialized",
                    }
                ]
            }
        if operation == "e2eeGetEnvelopes" and parameters["scope_id"] == "org-unused":
            raise E2eeError("not_found")
        return original(operation, **parameters)

    monkeypatch.setattr(api, "call", organizations)
    receipt = owner.approve(pairing)
    added.accept_approval(receipt)
    assert added.state == "approved"
    assert added.scope_key(scope, 1) == owner.scope_key(scope, 1)
    assert all(envelope["scope_id"] != "org-unused" for envelope in api.envelopes)
