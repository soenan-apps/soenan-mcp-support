#!/usr/bin/env python3
"""Exercise the installed SDK against an owned normal stack and real Bucket bytes."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import subprocess
from datetime import datetime, timezone
import sys
import tempfile
import time

from profile_oauth_acceptance import (
    AccountActor, ActualTransport, PrivateSecretService, WORKSPACE,
    make_vault, provision_identity, require,
)
from soenan_arteligo_support.e2ee import DeviceSession, E2eeCrypto, EncryptedRecords, SystemSecureStore
from soenan_arteligo_support.e2ee._api import GeneratedAPI
from soenan_arteligo_support.transfer import download_file, upload_file, TransferTimeouts, TransferTransport
from soenan_arteligo_support.transfer._workflow import _capability, _object


def save(path: Path, value: dict) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as output:
        json.dump(value, output, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def session_for(inputs: dict, transport: ActualTransport):
    vault = make_vault(inputs, inputs["profile"], transport)
    session = DeviceSession(GeneratedAPI(vault.bind(), transport=transport), E2eeCrypto(),
        SystemSecureStore(inputs["profile"]), origin=inputs["arteligo"], subject=inputs["subject"])
    session.refresh()
    return vault, session


def download_worker(path: Path) -> None:
    inputs = json.loads(path.read_text())
    class ObservedTransport(ActualTransport):
        def handle_request(self, request):
            if request.url.path.endswith("/chunks/1"):
                print(json.dumps({"partial_plaintext_bytes_at_least": 8 * 1024 * 1024}), flush=True)
            return super().handle_request(request)
    _, session = session_for(inputs, ObservedTransport(inputs["certificate"]))
    try:
        download_file(session, project_id=inputs["scope_id"], file_id=inputs["file_id"],
            destination=inputs["partial_destination"],
            transport=TransferTransport(ca_file=inputs["certificate"]))
    finally:
        session.lock()


def runtime_image(stack) -> str:
    from scripts.soenan_cli.integrations import docker
    return subprocess.check_output(docker.command("inspect", "--format", "{{.Image}}",
        stack.workspace.resource_name("soenan-local-arteligo-www")), env=docker.environment(), text=True).strip()


def query(stack, statement: str, *, product: str = "arteligo"):
    from scripts.soenan_cli.integrations import docker
    database = getattr(stack, product + "_postgres")
    output = subprocess.check_output(docker.command("exec", "-i", database.container,
        "psql", "-X", "-qAt", "--set=ON_ERROR_STOP=1", "-U", database.user, "-d", database.database),
        input=("BEGIN READ ONLY;\n" + statement + "\nCOMMIT;").encode(), env=docker.environment())
    return json.loads(output)


def observe_object(stack, identifier: str):
    import uuid
    require(str(uuid.UUID(identifier)) == identifier, "canonical_owned_object_id_required")
    return query(stack, f"""SELECT (
      SELECT json_build_object('state', state, 'cleanup_pass', cleanup_pass,
        'cleanup_at', extract(epoch from cleanup_at),
        'remaining_chunks', (SELECT count(*) FROM e2ee_object_chunks WHERE object_id='{identifier}' AND NOT deleted),
        'total_chunks', (SELECT count(*) FROM e2ee_object_chunks WHERE object_id='{identifier}'))
      FROM e2ee_objects WHERE id='{identifier}');""")


def account_usage(stack, identifier: str) -> dict:
    import uuid
    require(str(uuid.UUID(identifier)) == identifier, "canonical_owned_object_id_required")
    resource = "e2ee-object/" + identifier
    return query(stack, f"""SELECT json_build_object(
      'resources', (SELECT coalesce(json_agg(x), '[]'::json) FROM (
        SELECT resource_id, state, reserved_bytes, committed_bytes, product_revision
        FROM account_storage_usage_resources
        WHERE product_id='arteligo' AND resource_id='{resource}') x),
      'receipts', (SELECT coalesce(json_agg(x), '[]'::json) FROM (
        SELECT resource_id, operation, release_kind, result, count(*) AS receipts
        FROM account_storage_usage_receipts
        WHERE product_id='arteligo' AND resource_id='{resource}'
        GROUP BY resource_id, operation, release_kind, result
        ORDER BY resource_id, operation, release_kind, result) x));""", product="account")


def physical_chunks_absent(stack, scope: str, identifier: str, count: int) -> dict:
    protected = stack._read_secrets()
    credentials = {"host": "rustfs:9000", "port": stack.bucket_port,
        "access_key": protected["bucket_access_key"], "secret_key": protected["bucket_secret_key"]}
    protected.clear()
    try:
        for index in range(count):
            path = f"/arteligo-local/projects/{scope}/encrypted-objects/{identifier}/chunks/{index}.bin"
            status, _ = stack._s3_request("HEAD", path, **credentials)
            require(status == 404, "owned_physical_chunk_not_absent")
        return {"checked_chunks": count, "all_head_status": 404}
    finally:
        credentials.clear()


def cleanup_object(stack, session, scope: str, report: dict, report_path: Path) -> None:
    identifier = report.get("object_id")
    if identifier is None:
        return
    observed = observe_object(stack, identifier)
    report["cleanup_observation"] = observed
    if observed is None:
        report["object_cleanup"] = "declaration_not_persisted"
        save(report_path, report)
        return
    if observed["state"] not in {"delete_pending", "deleted"}:
        report["signed_delete"] = "dispatching"
        save(report_path, report)
        _object(session, scope, identifier, "delete")
        report["signed_delete"] = "acknowledged"
        save(report_path, report)
    deadline = time.monotonic() + 900
    while True:
        observed = observe_object(stack, identifier)
        report["cleanup_observation"] = observed
        save(report_path, report)
        if observed is not None and observed["state"] == "deleted" and observed["remaining_chunks"] == 0:
            break
        require(time.monotonic() < deadline, "owned_object_cleanup_deadline")
        time.sleep(2)
    require(observed["cleanup_pass"] == 1, "owned_second_cleanup_pass_missing")
    report["physical_cleanup"] = physical_chunks_absent(stack, scope, identifier, report["declared_chunks"])
    deadline = time.monotonic() + 120
    while True:
        usage = account_usage(stack, identifier)
        report["account_usage_after_cleanup"] = usage
        save(report_path, report)
        applied = sum(row["receipts"] for row in usage["receipts"]
            if row["operation"] == "release" and row["result"] == "applied")
        if applied == 1:
            break
        require(applied == 0 and time.monotonic() < deadline, "account_release_not_exactly_once")
        time.sleep(2)
    require(len(usage["resources"]) == 1 and all(row["reserved_bytes"] == 0
        and row["committed_bytes"] == 0 and row["state"] in {"retired", "released"}
        for row in usage["resources"]), "account_usage_not_settled")
    _object(session, scope, identifier, "delete")
    repeated = account_usage(stack, identifier)
    require(repeated == usage, "repeated_delete_changed_account_usage")
    report.update(account_usage_after_repeat=repeated, object_cleanup="complete")
    save(report_path, report)


def run(args) -> None:
    from scripts.soenan_cli.core.workspace import read_configuration
    from scripts.soenan_cli.operations.local_dev import LocalDevelopmentStack
    from scripts.soenan_cli.operations.develop_capacity_sdk import inspect_artifact
    source = args.source.resolve()
    size = source.stat().st_size
    require(size > 8 * 1024**3, "actual_aggregate_boundary_bytes_required")
    require(source.stat().st_blocks * 512 >= size, "fully_written_original_required")
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    temporary = Path.home() / ".cache" / "soenan" / ("f49n-" + secrets.token_hex(4))
    temporary.mkdir(mode=0o700, parents=True, exist_ok=False)
    os.environ.update(TMPDIR=str(temporary), SSL_CERT_FILE=str(args.certificate), NO_PROXY="*")
    tempfile.tempdir = str(temporary)
    spec = importlib.util.find_spec("soenan_arteligo_support.transfer._workflow")
    require(spec is not None and not Path(spec.origin).resolve().is_relative_to(WORKSPACE / "soenan-mcp-support"),
        "ordinary_installed_sdk_required")
    artifact = inspect_artifact()
    workspace = read_configuration(args.workspace_config, expected_root=WORKSPACE)
    stack = LocalDevelopmentStack(workspace=workspace, workspace_config=args.workspace_config,
        product_roots={"account": WORKSPACE / "soenan-account", "csm": WORKSPACE / "soenan-csm",
            "arteligo": WORKSPACE / "arteligo", "mcp-support": WORKSPACE / "soenan-mcp-support"})
    require(runtime_image(stack) == args.expected_image, "normal_runtime_image_mismatch")
    report = {"state": "starting", "source": str(source), "plaintext_size": size,
        "image": args.expected_image,
        "owned_output": str(args.output), "cleanup_authority": "Only the new identity, scope, object and files recorded here are owned."}
    report["driver_sha256"] = digest(Path(__file__).resolve())
    report["installed_artifact"] = artifact
    report["owned_temporary_root"] = str(temporary)
    report_path = args.output / "result.json"
    save(report_path, report)
    native = PrivateSecretService(args.secret_service_daemon, args.native_libraries)
    actor = vault = session = None
    original_failure = None
    try:
        identity = provision_identity(stack, str(args.certificate), manual_term_seconds=24 * 3600)
        report.update(protected_identity_path=identity["protected_identity_path"],
            subject=identity["subject"], organization=identity["organization"], billing=identity["billing"])
        save(report_path, report)
        actor = AccountActor(stack, str(args.certificate), identity)
        inputs = {"account": stack.account_origin, "arteligo": stack.arteligo_origin,
            "certificate": str(args.certificate), "profile": "f49-" + secrets.token_hex(16),
            "subject": actor.subject}
        report["profile"] = inputs["profile"]
        scope = "prj_" + secrets.token_hex(16)
        report["scope_id"] = scope
        save(report_path, report)
        class ObservedTransport(ActualTransport):
            def handle_request(self, request):
                if request.method == "POST" and request.url.path.endswith("/objects"):
                    signed = json.loads(request.content)
                    body = signed.get("body_bytes", "")
                    body = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
                    report["object_id"] = body["object_id"]
                    report["declared_chunks"] = len(body["chunks"])
                    save(report_path, report)
                return super().handle_request(request)
        transport = ObservedTransport(str(args.certificate))
        vault = make_vault(inputs, inputs["profile"], transport)
        vault.login(open_browser=actor.authorize)
        actor.accept_product_terms(vault.bind())
        session = DeviceSession(GeneratedAPI(vault.bind(), transport=transport), E2eeCrypto(),
            SystemSecureStore(inputs["profile"]), origin=stack.arteligo_origin, subject=actor.subject)
        require(session.refresh() == "needs_setup", "fresh_owned_device_required")
        draft = session.prepare_setup()
        try:
            session.finish_setup(draft)
        finally:
            draft.clear()
        records = EncryptedRecords(session)
        timestamp = datetime.now(timezone.utc).isoformat()
        records.create_project(project_id=scope, owner_org=actor.organization, value={
            "title": "F49 actual transfer", "participationPolicy": "private", "status": "active",
            "progress": 0.0, "responsibility": {"revision": 0, "waitingOn": None},
            "createdAt": timestamp, "updatedAt": timestamp, "deadlineDate": None, "brief": {}, "members": []})
        if args.prepare_barrier:
            report.update(state="prepared", preparation_image=args.expected_image)
            save(report_path, report)
            print(json.dumps({"scenario": "F49_PREPARED", "receipt": str(report_path)}), flush=True)
            args.expected_image = json.loads(sys.stdin.readline())["image"]
            require(runtime_image(stack) == args.expected_image, "released_runtime_image_mismatch")
            report["image"] = args.expected_image
        report["source_sha256"] = digest(source)
        report["state"] = "uploading"
        save(report_path, report)
        uploaded = upload_file(session, project_id=scope, source=source,
            timeouts=TransferTimeouts(total=300), transport=TransferTransport(ca_file=args.certificate))
        report.update(uploaded=uploaded, state="uploaded")
        save(report_path, report)
        record = records.read(scope, [uploaded["file_id"]])[uploaded["file_id"]]
        manifest = record["value"]["source"]["object"]
        expected_chunks = (size + 8 * 1024 * 1024 - 1) // (8 * 1024 * 1024)
        require(manifest["chunk_count"] == expected_chunks and manifest["plaintext_size"] == size,
            "actual_large_manifest_readback_mismatch")
        report["manifest_chunk_count"] = manifest["chunk_count"]
        report["ciphertext_size"] = sum(chunk["ciphertext_size"] for chunk in manifest["chunks"])
        report["last_chunk_ciphertext_size"] = manifest["chunks"][-1]["ciphertext_size"]
        require(report["ciphertext_size"] == size + 16 * expected_chunks,
            "authenticated_ciphertext_size_mismatch")
        report["ready_object"] = observe_object(stack, uploaded["object_id"])
        require(report["ready_object"]["state"] == "ready"
            and report["ready_object"]["total_chunks"] == expected_chunks
            and report["ready_object"]["remaining_chunks"] == expected_chunks,
            "actual_uploaded_chunks_missing")
        worker_inputs = {**inputs, "scope_id": scope, "file_id": uploaded["file_id"],
            "partial_destination": str(args.output / "cancelled-readback.bin")}
        worker_path = args.output / "worker.json"
        save(worker_path, worker_inputs)
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--download-worker", str(worker_path)],
            stdout=subprocess.PIPE, text=True)
        try:
            require(child.stdout is not None, "download_worker_pipe_missing")
            partial = json.loads(child.stdout.readline())
            require(partial.get("partial_plaintext_bytes_at_least", 0) >= 8 * 1024 * 1024,
                "actual_partial_download_not_observed")
            child.kill()
            child.wait(timeout=15)
            require(not Path(worker_inputs["partial_destination"]).exists(), "cancelled_destination_published")
            require(not list(args.output.glob(".arteligo-*")), "cancelled_plaintext_partial_leaked")
            report["forced_download_exit"] = {"returncode": child.returncode, **partial, "no_named_partial": True}
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
        destination = args.output / "readback.bin"
        report["downloaded_bytes"] = download_file(session, project_id=scope, file_id=uploaded["file_id"],
            destination=destination, transport=TransferTransport(ca_file=args.certificate))
        report["readback_sha256"] = digest(destination)
        require(report["readback_sha256"] == report["source_sha256"], "actual_decrypted_bytes_mismatch")
        try:
            download_file(session, project_id=scope, file_id=uploaded["file_id"], destination=destination,
                transport=TransferTransport(ca_file=args.certificate))
        except Exception as error:
            require(getattr(error, "code", None) == "destination_exists", "existing_destination_wrong_error")
        else:
            raise RuntimeError("existing committed destination replaced")
        require(digest(destination) == report["source_sha256"], "committed_destination_changed")
        report.update(state="readback_verified", committed_destination_preserved=True)
        save(report_path, report)
        if args.capability_handoff is not None:
            index = manifest["chunk_count"] - 1
            capability = session.call("e2eeGetObjectCapability", scope_id=scope,
                object_id=uploaded["object_id"], index=index)
            length = manifest["chunks"][index]["ciphertext_size"]
            url, headers = _capability(capability, "GET", length)
            descriptor = {
                "contract": "arteligo.railway-bucket-capability", "version": 2,
                "operation": capability["method"], "objectId": uploaded["object_id"],
                "chunkIndex": index,
                "expiresAt": datetime.fromtimestamp(capability["expires_at"], timezone.utc).isoformat(),
                "contentLength": length, "url": url, "headers": headers,
            }
            require(descriptor["operation"] == "GET" and descriptor["contentLength"] > 0,
                "derived_get_capability_mismatch")
            require(args.capability_handoff.parent == args.output and not args.capability_handoff.exists(),
                "fresh_owned_capability_path_required")
            save(args.capability_handoff, descriptor)
            report["read_capability_receipt"] = str(args.capability_handoff)
            save(report_path, report)
            print(json.dumps({"scenario": "F49_CAPABILITY_READY", "receipt": str(args.capability_handoff)}), flush=True)
            require(sys.stdin.readline().strip() == "continue", "owned_capability_consumer_handoff_not_completed")
            require(not args.capability_handoff.exists(), "owned_capability_receipt_not_consumed")
            report["native_get_handoff"] = "consumer_acknowledged_and_receipt_unlinked"
        report["state"] = "cleanup_pending"
        save(report_path, report)
        cleanup_object(stack, session, scope, report, report_path)
        require(runtime_image(stack) == args.expected_image, "runtime_changed_during_transfer")
        require(digest(source) == report["source_sha256"], "original_changed")
        final_artifact = inspect_artifact()
        require(final_artifact["source_sha256"] == artifact["source_sha256"]
            and final_artifact["native_library_sha256"] == artifact["native_library_sha256"],
            "sdk_source_changed_during_transfer")
        require(digest(Path(__file__).resolve()) == report["driver_sha256"],
            "driver_changed_during_transfer")
        report["state"] = "complete"
    except BaseException as error:
        original_failure = error
        report.update(state="failed", failure=getattr(error, "code", type(error).__name__))
        raise
    finally:
        authority_retained = False
        try:
            if session is not None and report.get("object_id") is not None and report.get("object_cleanup") not in {
                "complete", "declaration_not_persisted"
            }:
                while True:
                    try:
                        cleanup_object(stack, session, scope, report, report_path)
                        break
                    except BaseException as error:
                        report.update(state="recovery_authority_retained",
                            object_cleanup_failure=getattr(error, "code", type(error).__name__),
                            native_recovery_root=str(native.root))
                        save(report_path, report)
                        print(json.dumps({"scenario": "F49_RECOVERY_AUTHORITY_RETAINED",
                            "receipt": str(report_path), "http_in_flight": False}), flush=True)
                        while sys.stdin.readline().strip() != "retry-cleanup":
                            time.sleep(1)
            if session is not None:
                session.lock()
            if vault is not None:
                vault.logout()
            if actor is not None:
                actor.close_owned_identity()
                report["identity_cleanup"] = "complete"
        except BaseException as error:
            authority_retained = True
            report["identity_cleanup"] = getattr(error, "code", type(error).__name__)
            report["state"] = "recovery_authority_retained" if authority_retained else "cleanup_failed"
            if original_failure is None:
                raise
        finally:
            if not authority_retained:
                if actor is not None:
                    actor.close()
                native.close()
            save(report_path, report)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-worker", type=Path)
    parser.add_argument("--workspace-config", type=Path)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--secret-service-daemon", type=Path)
    parser.add_argument("--native-libraries", type=Path)
    parser.add_argument("--expected-image")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--capability-handoff", type=Path)
    parser.add_argument("--prepare-barrier", action="store_true")
    args = parser.parse_args()
    if args.download_worker is not None:
        download_worker(args.download_worker)
    else:
        for name in ("workspace_config", "certificate", "secret_service_daemon", "native_libraries", "expected_image", "source", "output"):
            if getattr(args, name) is None:
                parser.error("missing --" + name.replace("_", "-"))
        run(args)


if __name__ == "__main__":
    main()
