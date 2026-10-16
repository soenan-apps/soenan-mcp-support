"""Exercise genuine historical receipts and fresh markers on an owned normal stack."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import shlex
import tempfile
import secrets
import subprocess
import sys
import time
import threading

from profile_oauth_acceptance import (
    AccountActor, ActualTransport, IntegrationFailure, PrivateSecretService,
    WORKSPACE, emit, make_vault, provision_identity, require,
)
from soenan_arteligo_support.e2ee import DeviceSession, E2eeError, EncryptedRecords, open_session
from soenan_arteligo_support.e2ee._api import GeneratedAPI
from soenan_arteligo_support.e2ee._crypto import decode, encode, wipe
from soenan_arteligo_support.e2ee._directory import EncryptedDirectory
from soenan_arteligo_support.e2ee._directory_migration import migrate_directory, abort_directory_migration
from soenan_arteligo_support.e2ee._records import KINDS


def source_manifest():
    root = WORKSPACE / "soenan-mcp-support"
    files = [p for folder in ("src", "generated") for p in (root / folder).rglob("*.py")]
    files += [root / "tool/transfer_object_acceptance.py"]
    files += [Path(__file__), root / "tool/profile_oauth_acceptance.py"]
    arteligo = WORKSPACE / "arteligo"
    files += list((arteligo / "lib").rglob("*.dart"))
    files += list((arteligo / "contracts/encryption-vectors").rglob("*.json"))
    files += [arteligo / name for name in ("pubspec.yaml", "pubspec.lock",
        ".dart_tool/package_config.json", "tool/marker_contract_acceptance.dart",
        "integration_test/backend_read_acceptance_test.dart")]
    return {str(p.relative_to(WORKSPACE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def observe(stack, scope):
    from scripts.soenan_cli.integrations import docker

    require(scope.startswith("prj_") and all(c in "0123456789abcdef" for c in scope[4:]),
        "owned_scope_identity_required")
    sql = f"""BEGIN READ ONLY;
    SELECT json_build_object(
      'versions', (SELECT count(*) FROM e2ee_record_versions WHERE scope_id='{scope}'),
      'commands', (SELECT count(*) FROM e2ee_signed_commands WHERE scope_id='{scope}'),
      'receipts', (SELECT count(*) FROM e2ee_record_write_receipts WHERE scope_id='{scope}'),
      'heads', (SELECT coalesce(json_object_agg(record_id,json_build_object(
        'cursor',cursor,'charged',usage_charged,'immutable',immutable)), '{{}}'::json)
        FROM e2ee_record_heads WHERE scope_id='{scope}'),
      'resources', (SELECT coalesce(json_object_agg(resource_id,json_build_object(
        'state',state,'bytes',committed_bytes,'storage_revision',storage_revision)), '{{}}'::json)
        FROM artifact_usage_resources WHERE project_id='{scope}'),
      'deliveries', (SELECT coalesce(json_object_agg(q.id,json_build_object(
        'resource',q.resource_id,'kind',q.kind,'release',q.storage_release_kind)), '{{}}'::json)
        FROM quota_delivery_outbox q JOIN artifact_usage_resources r
        ON r.resource_id=q.resource_id WHERE r.project_id='{scope}'),
      'originals', (SELECT coalesce(json_object_agg(id::text,json_build_object(
        'body',encode(body,'base64'),'signature',encode(signature,'base64'))), '{{}}'::json)
        FROM e2ee_signed_commands WHERE scope_id='{scope}')
    ); COMMIT;"""
    postgres = stack.arteligo_postgres
    result = subprocess.run(docker.command("exec", "-i", postgres.container, "psql", "-X", "-qAt",
        "-U", postgres.user, "-d", postgres.database), input=sql.encode(), env=docker.environment(),
        capture_output=True, timeout=30)
    require(result.returncode == 0, "actual_marker_database_observation_failed")
    return json.loads(result.stdout)


def same_state(before, after):
    require(before == after, "unexpected_marker_database_mutation")


def reject(operation, code="invalid_request"):
    try:
        operation()
    except E2eeError as error:
        require(error.code == code, "marker_rejection_code_mismatch")
        return
    raise IntegrationFailure("invalid_marker_was_accepted")


def raw_sign(session, operation, body):
    message = bytearray(f"arteligo-e2ee-v1\n{operation}\n".encode()) + body
    try:
        signature = session.crypto.execute({"op": "sign_bytes",
            "secret_key": session._device["signing_secret_key"], "bytes": encode(message)})["signature"]
        return {"device_id": session.device_id, "body_bytes": encode(body), "signature": signature}
    finally:
        wipe(message)


def batch(scope, records, version=2):
    return {"scope_id": scope, "records": records, "format_version": version,
        "expires_at": int(time.time()) + 86400}


def send(session, scope, command):
    return session.call("e2eeWriteRecords", scope_id=scope, body=command)


def receipt_identity(response):
    return {key: value for key, value in response.items() if key != "server_time"}


def switch_image(stack, image, certificate, *, shared_runtime=False):
    import httpx
    from scripts.soenan_cli.integrations import docker

    require(image.startswith("sha256:") and len(image) == 71, "immutable_local_image_required")
    inspected = subprocess.run(docker.command("image", "inspect", "--format", "{{.Id}}", image),
        env=docker.environment(), capture_output=True, text=True, check=True)
    require(inspected.stdout.strip() == image, "selected_local_image_mismatch")
    name = stack.workspace.resource_name("soenan-local-arteligo-www")
    actual = subprocess.run(docker.command("inspect", "--format", "{{.Image}} {{.State.Running}}", name),
        env=docker.environment(), capture_output=True, text=True)
    if shared_runtime:
        require(actual.returncode == 0 and actual.stdout.strip() == image + " true",
            "shared_runtime_image_mismatch_no_topology_change")
    if actual.returncode != 0 or actual.stdout.strip() != image + " true":
        tag = "soenan/arteligo-www:mk-" + stack.workspace.workspace_id + "-" + image[7:19]
        subprocess.run(docker.command("image", "tag", image, tag),
            env=docker.environment(), capture_output=True, check=True)
        stack.image_tags["arteligo-www"] = tag
        stack._compose("up", "-d", "--no-deps", "--force-recreate", "arteligo-www")
    deadline = time.monotonic() + 90
    with httpx.Client(verify=str(certificate), trust_env=False, timeout=5) as client:
        while time.monotonic() < deadline:
            try:
                if client.get(stack.arteligo_origin + "/ready").status_code == 200:
                    break
            except httpx.TransportError:
                pass
            time.sleep(0.25)
        else:
            raise IntegrationFailure("owned_arteligo_image_not_ready")
    actual = subprocess.run(docker.command("inspect", "--format", "{{.Image}}", name),
        env=docker.environment(), capture_output=True, text=True, check=True)
    require(actual.stdout.strip() == image, "served_image_epoch_mismatch")


def live_root(session, records, organization):
    scope = "prj_" + secrets.token_hex(16)
    key = session.crypto.key()
    try:
        session._remember(scope, 1, key, owner=session._scope_owner(scope))
        envelopes = [session.wrap_key(scope, 1, key, recipient=identifier, kind=kind, public_key=public)
            for identifier, kind, public in (
                (session.device_id, "device", session.public["encryption_public_key"]),
                (session.recovery["recovery_id"], "recovery", session.recovery["encryption_public_key"]))]
        body = {"project_id": scope, "owner_org": organization, "participation_policy": "private",
            "envelopes": envelopes, "records": [records.deletion_marker(record_id=scope,
                kind="project", expected_revision=0, key_epoch=1)]}
        reject(lambda: session.command("e2eeCreateProject", "project_create", body))
        body["records"] = [records.seal(scope, record_id=scope, kind="project", expected_revision=0,
            key_epoch=1, value={"name": "MK live root", "id": scope})]
        signed = session.sign("project_create", body)
        created = session.call("e2eeCreateProject", body=signed)
        require(session.call("e2eeCreateProject", body=signed) == created, "creation_receipt_changed")
        require(records.read(scope, [scope])[scope]["deleted"] is False, "live_root_missing")
        emit("fresh_project_root", marker_rejected=True, live_content_accepted=True, exact_receipt_replayed=True)
        return scope
    finally:
        wipe(key)


def modern(session, records, stack, scope):
    for kind in sorted(KINDS):
        version = 3 if kind in {"chat", "comment"} else 2
        identifier = "mk_" + kind
        live = records.write(scope, key_epoch=1, records=[{"record_id": identifier, "kind": kind,
            "expected_revision": 0, "value": {"kind": kind, "retained": True}}])[0]
        require(live["payload_type"] == "content", "live_aead_readback_failed")
        marker = records.deletion_marker(record_id=identifier, kind=kind, expected_revision=1, key_epoch=1)
        before = observe(stack, scope)
        for extra in ({"padding": ""}, {"ciphertext": "AA"}, {"immutable": False}, {"value": {}}):
            signed = session.sign("records_write", batch(scope, [{**marker, **extra}], version))
            reject(lambda: send(session, scope, signed))
            same_state(before, observe(stack, scope))
        body = batch(scope, [marker], version)
        sibling = records.seal(scope, record_id="mk_sibling", kind=kind,
            expected_revision=0, key_epoch=1, value={"retained": True})
        invalid = [
            {**body, "padding": ""},
            {**body, "preconditions": [{"record_id": identifier, "expected_revision": 1,
                "require_live": True, "padding": ""}]},
            {**body, "records": [marker, {**sibling, "padding": ""}]},
            {**body, "records": [{key: value for key, value in marker.items() if key != "key_epoch"}]},
            {**body, "records": [{**marker, "deleted": False}]},
            {**body, "records": [{**marker, "deleted": 1}]},
            {**body, "records": [{**marker, "key_epoch": "1"}]},
        ]
        for malformed in invalid:
            reject(lambda: send(session, scope, session.sign("records_write", malformed)))
            same_state(before, observe(stack, scope))
        canonical = session.crypto.canonical(body)
        try:
            duplicate = bytes(canonical).replace(b'"deleted":true', b'"deleted":true,"deleted":true', 1)
            for raw in (json.dumps(body, indent=1).encode(), bytes(canonical) + b" ", duplicate):
                noncanonical = raw_sign(session, "records_write", raw)
                reject(lambda: send(session, scope, noncanonical))
                same_state(before, observe(stack, scope))
        finally:
            wipe(canonical)
        if version == 3:
            reject(lambda: send(session, scope, session.sign("records_write", batch(scope, [marker], 2))),
                "content_format_update_required")
            same_state(before, observe(stack, scope))
        signed = session.sign("records_write", body)
        result = send(session, scope, signed)
        after = observe(stack, scope)
        require(after["versions"] == before["versions"] + 1 and after["commands"] == before["commands"] + 1,
            "marker_version_count_incorrect")
        require(after["heads"][identifier]["charged"] is False, "marker_head_remains_charged")
        require(set(after["resources"]) == set(before["resources"]), "marker_created_resource")
        retired = [identifier for identifier, old in before["resources"].items()
            if old["state"] == "committed" and after["resources"][identifier]["state"] == "retired"]
        require(len(retired) == 1, "charged_head_not_retired_once")
        releases = [row for key, row in after["deliveries"].items() if key not in before["deliveries"]
            and row["resource"] == retired[0] and row["kind"] == "storage_release"
            and row["release"] == "retire_committed"]
        require(len(releases) == 1, "marker_release_delivery_not_exactly_once")
        require(receipt_identity(send(session, scope, signed)) == receipt_identity(result), "exact_marker_receipt_changed")
        same_state(after, observe(stack, scope))
        opened = records.read(scope, [identifier])[identifier]
        require(opened["payload_type"] == "deletion_marker" and "value" not in opened,
            "marker_exposed_plaintext_value")
        next_marker = {**marker, "expected_revision": 2}
        send(session, scope, session.sign("records_write", batch(scope, [next_marker], version)))
        repeated = observe(stack, scope)
        require(repeated["resources"] == after["resources"] and repeated["deliveries"] == after["deliveries"],
            "new_command_retired_marker_twice")
        require(records.read(scope, [identifier])[identifier]["revision"] == 3, "repeated_marker_not_visible")
        current = records.current(scope, kind=kind)
        require(any(row["record_id"] == identifier and row["payload_type"] == "deletion_marker"
            and row["revision"] == 3 for row in current["records"]), "current_marker_missing")
        history = records.page(scope)
        require(any(row["record_id"] == identifier and row["payload_type"] == "deletion_marker"
            for row in history["records"]), "historical_marker_missing")
        require(records.changes(scope)["cursor"] >= result["cursor"], "marker_change_cursor_missing")
        emit("fresh_marker", format=version, kind=kind, exact_five_fields=True,
            native_signature_and_aead=True, rejected_extras=4, malformed_commands=len(invalid),
            noncanonical_rejected=3, current_and_history=True,
            single_retirement=True, no_marker_resource=True, exact_receipt_no_write=True,
            new_command_no_duplicate_retirement=True, payload_free_readback=True)
    immutable = records.write(scope, key_epoch=1, records=[{"record_id": "mk_immutable", "kind": "schedule",
        "expected_revision": 0, "immutable": True, "value": {"retained": True}}])[0]
    before = observe(stack, scope)
    marker = records.deletion_marker(record_id="mk_immutable", kind="schedule", expected_revision=1, key_epoch=1)
    reject(lambda: send(session, scope, session.sign("records_write", batch(scope, [marker]))), "revision_conflict")
    same_state(before, observe(stack, scope))
    require(records.read(scope, ["mk_immutable"])["mk_immutable"] == immutable, "immutable_original_changed")
    page = records.immutable_kind(scope, "schedule")
    require(any(row["record_id"] == "mk_immutable" for row in page["records"]), "immutable_read_missing")
    emit("immutable_marker_rejected", unchanged_original=True, immutable_kind_read=True)


def deleted_root(session, records, stack, organization):
    scope = records.create_project(value={"name": "MK deleted root"}, owner_org=organization)
    live = records.read(scope, [scope])[scope]
    marker = records.write(scope, key_epoch=1, records=[{"record_id": scope,
        "kind": "project", "expected_revision": live["revision"], "deleted": True}])[0]
    require(marker["payload_type"] == "deletion_marker" and "value" not in marker,
        "deleted_project_root_not_a_marker")
    before = observe(stack, scope)
    reject(lambda: EncryptedDirectory(records, scope).page(), "not_found")
    reject(lambda: migrate_directory(records, scope), "not_found")
    same_state(before, observe(stack, scope))
    metadata = session.scope_metadata(scope, refresh=True)
    require(metadata["lifecycle"] == "active", "root_marker_changed_scope_lifecycle")
    emit("deleted_project_root", scope=scope, later_marker_allowed=True,
        lifecycle_unchanged=True, directory_not_found=True, migration_not_found=True,
        payload_free_readback=True, refused_consumers_no_write=True)


def migration_markers(session, records, stack, organization):
    scope = live_root(session, records, organization)
    partial = migrate_directory(records, scope, maximum_batches=1)
    require(not partial["complete"], "migration_fixture_must_be_in_progress")
    status = session.call("e2eeGetMigration", scope_id=scope)["migration"]
    checkpoint = status["checkpoint_record_id"]
    before = observe(stack, scope)
    require(abort_directory_migration(records, scope)["complete"], "normal_migration_abort_incomplete")
    opened = records.read(scope, [checkpoint])[checkpoint]
    require(opened["payload_type"] == "deletion_marker" and "value" not in opened,
        "aborted_checkpoint_retained_payload")
    after = observe(stack, scope)
    require(all(not row["charged"] for identifier, row in after["heads"].items()
        if identifier != scope), "aborted_staging_head_charged")
    require(after["resources"] == before["resources"], "aborted_staging_created_zero_resource")
    require(abort_directory_migration(records, scope)["complete"], "repeated_abort_incomplete")
    same_state(after, observe(stack, scope))
    require(not migrate_directory(records, scope, maximum_batches=1)["complete"],
        "restarted_migration_must_pause_before_resume")
    while not migrate_directory(records, scope)["complete"]:
        pass
    require(EncryptedDirectory(records, scope).page()["entries"] == [], "completed_directory_not_readable")
    emit("migration_marker_consumers", scope=scope, abort_checkpoint_marker=True,
        uncharged_staging=True, repeated_abort_no_write=True, checkpoint_resume=True,
        subsequent_migration_complete=True)


def migration_root_race(session, records, vault, actor, stack, args, *, change="delete"):
    scope = live_root(session, records, actor.organization)
    root = records.read(scope, [scope])[scope]

    class BeginGate(ActualTransport):
        def __init__(self):
            super().__init__(str(args.certificate))
            self.arrived = threading.Event()
            self.release = threading.Event()
            self.preconditions = None
            self.begin_requests = 0

        def handle_request(self, request):
            if request.method == "POST" and request.url.path == f"/api/e2ee/scopes/{scope}/records":
                command = json.loads(request.content)
                raw = decode(command["body_bytes"])
                try:
                    body = json.loads(raw)
                finally:
                    wipe(raw)
                if body.get("maintenance", {}).get("action") == "begin":
                    self.preconditions = body.get("preconditions")
                    self.begin_requests += 1
                    self.arrived.set()
                    require(self.release.wait(60), "actual_begin_transport_gate_not_released")
            return super().handle_request(request)

    gate = BeginGate()
    migrating = DeviceSession(GeneratedAPI(vault.bind(), transport=gate), session.crypto, vault.store,
        origin=stack.arteligo_origin, subject=session.subject)
    owner = owner_vault = worker = None
    outcome = {}
    cleanup = {}
    try:
        require(migrating.refresh() == "approved", "ordinary_migration_device_not_approved")
        profile = "mk-race-" + secrets.token_hex(16)
        owner_vault = make_vault({"account": stack.account_origin, "arteligo": stack.arteligo_origin},
            profile, ActualTransport(str(args.certificate)))
        owner_vault.login(open_browser=actor.authorize)
        actor.accept_product_terms(owner_vault.bind())
        owner = open_session(account_origin=stack.account_origin, arteligo_origin=stack.arteligo_origin,
            profile=profile)
        pairing = owner.enroll()
        owner.accept_approval(session.approve(pairing))
        pairing.clear()
        require(owner.state == "approved" and owner.device_id != session.device_id,
            "second_genuine_owner_device_required")

        def migrate():
            try:
                outcome["result"] = migrate_directory(EncryptedRecords(migrating), scope)
            except BaseException as error:
                outcome["error_type"] = type(error).__name__
                if isinstance(error, E2eeError):
                    outcome["error_code"] = error.code

        worker = threading.Thread(target=migrate)
        worker.start()
        require(gate.arrived.wait(60), "actual_live_root_read_did_not_reach_begin")
        try:
            concurrent = {"record_id": scope, "kind": "project", "expected_revision": root["revision"]}
            concurrent.update({"deleted": True} if change == "delete" else {
                "value": {**root["value"], "name": "Concurrent live root update"}})
            committed = EncryptedRecords(owner).write(scope, key_epoch=1, records=[concurrent])[0]
            require(committed["deleted"] == (change == "delete"), "racing_owner_change_not_committed")
            after_marker = observe(stack, scope)
        finally:
            gate.release.set()
        worker.join(120)
        require(not worker.is_alive(), "actual_migration_worker_did_not_join")
        status = session.call("e2eeGetMigration", scope_id=scope)["migration"]
        after_begin = observe(stack, scope)
        evidence = {"scope": scope, "migration_device_id": session.device_id,
            "marker_device_id": owner.device_id, "observed_live_revision": root["revision"],
            "begin_wire_preconditions": gate.preconditions, "begin_requests": gate.begin_requests,
            "concurrent_change": change, "outcome": outcome,
            "migration_state": status["state"] if status else None,
            "versions_after_marker": after_marker["versions"], "versions_after_begin": after_begin["versions"],
            "no_begin_write": after_marker == after_begin, "real_http_and_signatures": True}
        suffix = "" if change == "delete" else "-update"
        (args.evidence / f"migration-race{suffix}.json").write_text(json.dumps(evidence, indent=2))
        emit("migration_prebegin_race_observed", **evidence)
        require(status is None, "deleted_root_prebegin_race_left_migration_fence")
        same_state(after_marker, after_begin)
        expected = "not_found" if change == "delete" else "revision_conflict"
        require(outcome.get("error_code") == expected, "racing_root_conflict_classification_mismatch")
        require(gate.begin_requests == 1 and gate.preconditions == [{
            "record_id": scope, "expected_revision": root["revision"], "require_live": True}],
            "observed_live_root_precondition_or_once_only_begin_missing")
        emit("migration_prebegin_race", atomic_live_root_precondition=True, no_building_fence=True,
            no_begin_write=True, error_code=expected, second_genuine_owner=True, no_auto_replay=True)
    finally:
        gate.release.set()
        if worker is not None:
            worker.join(120)
            require(not worker.is_alive(), "owned_migration_worker_cleanup_not_joined")
        try:
            status = session.call("e2eeGetMigration", scope_id=scope)["migration"]
            if status and status["state"] in {"building", "aborting"}:
                cleanup["abort"] = abort_directory_migration(records, scope)
            cleanup["final_migration"] = session.call("e2eeGetMigration", scope_id=scope)["migration"]
        finally:
            migrating.lock()
            if owner is not None:
                owner.lock()
            if owner_vault is not None:
                owner_vault.logout()
            suffix = "" if change == "delete" else "-update"
            (args.evidence / f"migration-race-cleanup{suffix}.json").write_text(json.dumps(cleanup, indent=2))


def historical(session, records, stack, args, organization):
    scope = records.create_project(value={"name": "MK historical receipt"}, owner_org=organization)
    records.write(scope, key_epoch=1, records=[{"record_id": "mk_history", "kind": "schedule",
        "expected_revision": 0, "value": {"preserved": "live"}}])
    old_record = records.seal(scope, record_id="mk_history", kind="schedule", expected_revision=1,
        key_epoch=1, value={"preserved": "historical encrypted deletion"})
    old_record["deleted"] = True
    original_body = json.dumps(batch(scope, [old_record]), indent=1).encode()
    original = raw_sign(session, "records_write", original_body)
    original_path = args.evidence / "historical-original-command.json"
    descriptor = os.open(original_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as output:
        json.dump(original, output)
    original_file_digest = hashlib.sha256(original_path.read_bytes()).hexdigest()
    original = json.loads(original_path.read_text())
    receipt = send(session, scope, original)
    (args.evidence / "historical-original-response.json").write_text(json.dumps(receipt, indent=2))
    legacy = records.read(scope, ["mk_history"])["mk_history"]
    require(legacy["payload_type"] == "historical_encrypted_deletion"
        and legacy["value"] == {"preserved": "historical encrypted deletion"}, "old_service_aead_readback_failed")
    before = observe(stack, scope)
    emit("genuine_historical_receipt", accepted_by_image=args.historical_image,
        original_body_sha256=hashlib.sha256(original_body).hexdigest(),
        original_signature_sha256=hashlib.sha256(decode(original["signature"])).hexdigest(),
        historical_aead_opened=True, sql_fabrication=False)
    stack._compose("stop", "arteligo-www")
    canonical_receipt = WORKSPACE / ".local/sqlc-verification/arteligo-migration.json"
    require(not canonical_receipt.exists(), "previous_canonical_adoption_receipt_must_be_preserved")
    adoption_started = time.time()
    adopted = subprocess.run([str(WORKSPACE / "bin/soenan"), "sqlc", "adopt", "arteligo",
        "--workspace-config", str(args.arteligo_workspace_config)], cwd=WORKSPACE,
        capture_output=True, timeout=600)
    (args.evidence / "historical-adoption.stdout").write_bytes(adopted.stdout)
    (args.evidence / "historical-adoption.stderr").write_bytes(adopted.stderr)
    (args.evidence / "historical-adoption-process.json").write_text(json.dumps({
        "started_at_unix": adoption_started, "ended_at_unix": time.time(),
        "exit_code": adopted.returncode, "source_container": stack.arteligo_postgres.container,
    }, indent=2))
    require(adopted.returncode == 0, "normal_historical_adoption_failed")
    adoption_bytes = canonical_receipt.read_bytes()
    adoption = json.loads(adoption_bytes)
    require(adoption["source"]["container"] == stack.arteligo_postgres.container
        and adoption["source"]["database"] == stack.arteligo_postgres.database
        and adoption["local_adoption"] == "passed", "historical_adoption_receipt_identity_mismatch")
    descriptor = os.open(args.evidence / "historical-adoption-receipt.json",
        os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(adoption_bytes)
    emit("historical_adoption_bound", source_container=adoption["source"]["container"],
        receipt_sha256=hashlib.sha256(adoption_bytes).hexdigest())
    stack._compose("--profile", "tools", "run", "--rm", "--no-deps", "arteligo-migrate", "apply")
    switch_image(stack, args.current_image, args.certificate)
    same_state(before, observe(stack, scope))
    replayed = send(session, scope, original)
    (args.evidence / "historical-replayed-response.json").write_text(json.dumps(replayed, indent=2))
    require(receipt_identity(replayed) == receipt_identity(receipt),
        "genuine_historical_receipt_not_replayed")
    same_state(before, observe(stack, scope))
    require(records.read(scope, ["mk_history"])["mk_history"] == legacy, "historical_original_not_preserved")
    reject(lambda: send(session, scope, session.sign("records_write", batch(scope, [old_record]))))
    same_state(before, observe(stack, scope))
    require(any(row["record_id"] == "mk_history" for row in records.page(scope)["records"]),
        "historical_page_read_missing")
    require(records.changes(scope)["cursor"] >= receipt["cursor"], "history_cursor_lost")
    emit("historical_forward_cutover", served_image=args.current_image,
        normal_adoption_and_forward_migration=True, exact_receipt_before_fresh_validation=True,
        exact_originals_unchanged=True, historical_aead_read=True, fresh_encrypted_delete_rejected=True,
        original_response_server_time=receipt.get("server_time"),
        replayed_response_server_time=replayed.get("server_time"),
        response_comparison_excludes_only_current_server_time=True)
    require(hashlib.sha256(original_path.read_bytes()).hexdigest() == original_file_digest,
        "original_historical_input_file_changed")
    return {"scope_id": scope, "record_id": "mk_history", "command": original}


def compile_dart(root: Path, certificate: Path):
    product = WORKSPACE / "arteligo"
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    before = source_manifest()
    (root / "sources-before.json").write_text(json.dumps(before, indent=2))
    sdk = (product / ".fvm/flutter_sdk").resolve()
    engine = sdk / "bin/cache/artifacts/engine/linux-x64"
    from arteligo_e2ee_native import library_path
    native = Path(library_path()).resolve()
    kernel = root / "consumer.dill"
    mapping = root / "native-assets.json"
    mapping.write_text(json.dumps({"format-version": [1, 0, 0], "native-assets": {"linux_x64": {
        "package:arteligo/src/e2ee/crypto/e2ee_crypto_native.dart": ["absolute", str(native)]}}}))
    command = [str(sdk / "bin/cache/dart-sdk/bin/dartaotruntime"),
        str(engine / "frontend_server_aot.dart.snapshot"), "--sdk-root",
        str(sdk / "bin/cache/artifacts/engine/common/flutter_patched_sdk"),
        "--target=flutter", "--packages=" + str(product / ".dart_tool/package_config.json"),
        "--native-assets=" + str(mapping), "--depfile=" + str(root / "consumer.d"),
        "--output-dill=" + str(kernel), str(product / "tool/marker_contract_acceptance.dart")]
    (root / "compile-command.json").write_text(json.dumps(command))
    with (root / "compile.log").open("wb") as output:
        compiled = subprocess.run(command, cwd=product, input=b"", stdout=output,
            stderr=subprocess.STDOUT, timeout=180)
    require(compiled.returncode == 0 and kernel.is_file(), "normal_marker_consumer_compile_failed")
    dependencies = set(shlex.split((root / "consumer.d").read_text().split(": ", 1)[1]))
    selected = {name: value for name, value in before.items()
        if str(WORKSPACE / name) in dependencies or name.endswith((
            "pubspec.yaml", "pubspec.lock", "package_config.json", "marker_contract_acceptance.py"))}
    require(source_manifest() == before, "source_changed_during_marker_consumer_compile")
    paths = {"kernel": kernel, "native_codec": native, "engine": engine / "flutter_tester",
        "icu_data": engine / "icudtl.dat", "certificate": certificate.resolve(),
        "native_mapping": mapping, "packages": product / ".dart_tool/package_config.json"}
    artifacts = {name: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for name, path in paths.items()}
    (root / "compiled-sources.json").write_text(json.dumps(selected, indent=2))
    (root / "artifacts.json").write_text(json.dumps(artifacts, indent=2))
    return artifacts


def dart_consumers(session, records, vault, stack, organization, args, marker_scope, legacy):
    from soenan_arteligo_support.transfer import TransferTransport, download_file, upload_file
    from transfer_object_acceptance import cleanup_object

    require(args.dart_artifacts is not None, "compiled_normal_dart_marker_consumer_required")
    frozen_root = args.dart_artifacts.resolve()
    artifacts = json.loads((frozen_root / "artifacts.json").read_text())
    compiled_sources = json.loads((frozen_root / "compiled-sources.json").read_text())
    require(all(hashlib.sha256((WORKSPACE / path).read_bytes()).hexdigest() == value
        for path, value in compiled_sources.items()), "compiled_marker_consumer_source_epoch_mismatch")
    require(all(hashlib.sha256(Path(value["path"]).read_bytes()).hexdigest() == value["sha256"]
        for value in artifacts.values()), "compiled_marker_consumer_artifact_epoch_mismatch")
    scope = records.create_project(value={"title": "Owned marker whole consumers", "status": "active"},
        owner_org=organization)
    race_scope = live_root(session, records, organization)
    race_root = records.read(race_scope, [race_scope])[race_scope]
    race_state = {}
    migration_scope = None if args.dart_migration_race_only else live_root(session, records, organization)
    report = {}
    with tempfile.TemporaryDirectory(prefix="owned-mk-transfer-") as temporary:
        source = Path(temporary) / "owned-marker.bin"
        source.write_bytes(bytes(range(256)) * 16)
        transport = TransferTransport(ca_file=str(args.certificate))
        uploaded = upload_file(session, project_id=scope, source=source, transport=transport)
        report.update({"object_id": uploaded["object_id"], "declared_chunks": 1})
        report_path = args.evidence / "object-cleanup.json"
        try:
            pending = records.read(scope, ["upl_" + uploaded["object_id"]])["upl_" + uploaded["object_id"]]
            require(pending["payload_type"] == "deletion_marker" and "value" not in pending,
                "ordinary_upload_completion_not_a_closed_marker")
            before_resume = observe(stack, scope)
            require(upload_file(session, project_id=scope, source=source,
                upload_id=uploaded["object_id"], transport=transport) == uploaded,
                "ordinary_marker_upload_resume_changed_result")
            same_state(before_resume, observe(stack, scope))
            destination = Path(temporary) / "downloaded.bin"
            download_file(session, project_id=scope, file_id=uploaded["file_id"],
                destination=destination, transport=transport)
            require(destination.read_bytes() == source.read_bytes(), "actual_bucket_aead_readback_mismatch")
            result_path = args.evidence / "dart-result.json"
            command = [artifacts["engine"]["path"], "--disable-vm-service", "--enable-software-rendering",
                "--non-interactive", "--icu-data-file-path=" + artifacts["icu_data"]["path"],
                "--packages=" + artifacts["packages"]["path"], artifacts["kernel"]["path"]]
            (args.evidence / "dart-command.json").write_text(json.dumps(command))
            reader, writer = os.pipe()
            pairing_input = None
            process = None
            output = None
            try:
                process = subprocess.Popen(command, cwd=WORKSPACE / "arteligo", stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, pass_fds=(writer,),
                    env={**os.environ, "ARTELIGO_MARKER_CA": str(args.certificate),
                        "ARTELIGO_MARKER_RESULT": str(result_path), "ARTELIGO_MARKER_PAIRING_FD": str(writer)})
                os.close(writer)
                writer = None
                payload = bytearray((json.dumps({"origin": stack.arteligo_origin,
                    "account_origin": stack.account_origin, "subject": session.subject, "scope": scope,
                    "native_device_id": session.device_id, "file_id": uploaded["file_id"],
                    "marker_scope": marker_scope, "marker_ids": ["mk_" + kind for kind in sorted(KINDS)],
                    "legacy": legacy,
                    "migration_race_scope": race_scope, "migration_race_only": args.dart_migration_race_only,
                    "migration_race_change": args.migration_race_change,
                    "normal_migration_scope": migration_scope,
                    "access_token": vault.bind().access_token()}) + "\n").encode())
                try:
                    process.stdin.write(payload)
                    process.stdin.flush()
                finally:
                    wipe(payload)
                require(bool(select.select([reader], [], [], 120)[0]), "independent_dart_pairing_not_received")
                pairing_input = os.fdopen(reader, "rb", buffering=0)
                reader = None
                pairing_bytes = bytearray(pairing_input.readline())
                try:
                    pairing = json.loads(pairing_bytes)
                finally:
                    wipe(pairing_bytes)
                confirmation = bytearray((json.dumps(session.approve(pairing)) + "\n").encode())
                pairing.clear()
                try:
                    process.stdin.write(confirmation)
                    process.stdin.flush()
                finally:
                    wipe(confirmation)
                require(bool(select.select([pairing_input], [], [], 120)[0]), "dart_begin_gate_not_received")
                event = json.loads(pairing_input.readline())
                require(event.get("event") == "migration_begin" and event.get("scope") == race_scope,
                    "actual_dart_begin_scope_mismatch")
                concurrent = {"record_id": race_scope, "kind": "project",
                    "expected_revision": race_root["revision"]}
                concurrent.update({"deleted": True} if args.migration_race_change == "delete" else {
                    "value": {**race_root["value"], "name": "Concurrent native root update"}})
                changed = records.write(race_scope, key_epoch=1, records=[concurrent])[0]
                require(changed["deleted"] == (args.migration_race_change == "delete"),
                    "native_racing_dart_change_not_committed")
                after_marker = observe(stack, race_scope)
                process.stdin.write(b'{"release":true}\n')
                process.stdin.flush()
                require(bool(select.select([pairing_input], [], [], 120)[0]), "dart_migration_result_not_received")
                finished = json.loads(pairing_input.readline())
                require(finished.get("event") == "migration_finished" and finished.get("scope") == race_scope,
                    "actual_dart_finished_scope_mismatch")
                status = session.call("e2eeGetMigration", scope_id=race_scope)["migration"]
                after_begin = observe(stack, race_scope)
                race_state = {"scope": race_scope, "observed_live_revision": race_root["revision"],
                    "begin_wire_preconditions": event["preconditions"],
                    "concurrent_change": args.migration_race_change,
                    "migration_state": status["state"] if status else None,
                    "no_begin_write": after_marker == after_begin, "dart_outcome": finished,
                    "real_http_and_signatures": True}
                (args.evidence / "dart-migration-race.json").write_text(json.dumps(race_state, indent=2))
                emit("dart_migration_prebegin_race_observed", **race_state)
                abort = bool(status and status["state"] in {"building", "aborting"})
                output, _ = process.communicate(input=(json.dumps({"abort": abort}) + "\n").encode(), timeout=600)
                race_state["process_exit"] = process.returncode
                require(process.returncode == 0 and json.loads(result_path.read_text())["accepted"],
                    "real_dart_marker_consumer_failed")
                require(status is None, "dart_deleted_root_prebegin_race_left_migration_fence")
                same_state(after_marker, after_begin)
                require(event["preconditions"] == [{"record_id": race_scope,
                    "expected_revision": race_root["revision"], "require_live": True}],
                    "dart_observed_live_root_precondition_missing")
            finally:
                if pairing_input is not None:
                    pairing_input.close()
                if reader is not None:
                    os.close(reader)
                if writer is not None:
                    os.close(writer)
                if process is not None:
                    if process.poll() is None:
                        process.kill()
                    remaining, _ = process.communicate()
                    (args.evidence / "dart-run.log").write_bytes(output if output is not None else remaining)
                status = session.call("e2eeGetMigration", scope_id=race_scope)["migration"]
                require(not status or status["state"] not in {"building", "aborting"},
                    "dart_owned_migration_abort_not_completed_before_device_exit")
                race_state["final_migration"] = session.call("e2eeGetMigration", scope_id=race_scope)["migration"]
                (args.evidence / "dart-migration-race-cleanup.json").write_text(json.dumps(race_state, indent=2))
            require(all(hashlib.sha256(Path(value["path"]).read_bytes()).hexdigest() == value["sha256"]
                for value in artifacts.values()), "dart_artifacts_changed_during_real_marker_proof")
            if args.dart_migration_race_only:
                emit("dart_migration_race_only", whole_marker_acceptance=False)
                return
            root = records.read(scope, [scope])[scope]
            require(root["payload_type"] == "deletion_marker", "dart_root_marker_not_visible_to_native")
            reject(lambda: migrate_directory(records, scope), "not_found")
            reject(lambda: download_file(session, project_id=scope, file_id=uploaded["file_id"],
                destination=Path(temporary) / "deleted.bin", transport=transport), "not_found")
            require(records.read(scope, [uploaded["file_id"]])[uploaded["file_id"]]["payload_type"]
                == "deletion_marker", "dart_file_delete_not_visible_to_native")
            emit("whole_real_consumers", scope=scope, normal_sdk_upload=True, marker_resume_no_write=True,
                actual_bucket_aead=True, dart_independent_approval=True, calendar_truth_table=True,
                directory_and_chat=True, native_reads_dart_markers=True)
        finally:
            cleanup_object(stack, session, scope, report, report_path)


def run(args):
    from scripts.soenan_cli.core.workspace import read_configuration
    from scripts.soenan_cli.operations.local_dev import LocalDevelopmentStack
    from scripts.soenan_cli.operations.local_postgres import postgres_for_workspace

    workspace = read_configuration(args.workspace_config, expected_root=WORKSPACE)
    require(workspace.workspace_id == args.owned_workspace_id
        and (args.shared_runtime or workspace.workspace_id != "ws-859aef7290"),
        "explicit_owned_namespace_required")
    require(not args.shared_runtime or not args.historical_image,
        "shared_runtime_cannot_switch_to_historical_image")
    stack = LocalDevelopmentStack(root=WORKSPACE, workspace=workspace, workspace_config=args.workspace_config)
    require(not args.shared_runtime or args.csm_image is not None,
        "shared_fixture_requires_explicit_current_csm_image")
    if args.csm_image is not None:
        require(args.csm_image.startswith("sha256:") and len(args.csm_image) == 71,
            "immutable_csm_bootstrap_image_required")
        stack.image_tags["csm"] = args.csm_image
    require(bool(args.historical_image) == bool(args.arteligo_workspace_config),
        "historical_image_and_database_identity_required_together")
    if args.arteligo_workspace_config:
        historical_workspace = read_configuration(args.arteligo_workspace_config, expected_root=WORKSPACE)
        require(historical_workspace.workspace_id.startswith("ws-mkhist-"),
            "owned_fresh_historical_database_required")
        stack.arteligo_postgres = postgres_for_workspace("arteligo", historical_workspace)
        from scripts.soenan_cli.operations.sqlc_database import _assert_history, _metadata, _versions
        require(_versions(stack.arteligo_postgres.container, stack.arteligo_postgres.database) in (None, []),
            "unadopted_historical_database_required")
        _assert_history(stack.arteligo_postgres.container, stack.arteligo_postgres.database, _metadata("arteligo"))
    spec = importlib.util.find_spec("soenan_arteligo_support.e2ee._records")
    installed = Path(spec.origin).resolve().parent
    require(not installed.is_relative_to(WORKSPACE / "soenan-mcp-support"), "ordinary_installed_wheel_required")
    for folder in ("src", "generated"):
        for source in (WORKSPACE / "soenan-mcp-support" / folder).rglob("*.py"):
            packaged = installed.parent.parent / source.relative_to(WORKSPACE / "soenan-mcp-support" / folder)
            require(source.read_bytes() == packaged.read_bytes(), "installed_source_epoch_mismatch")
    frozen = source_manifest()
    args.evidence.mkdir(mode=0o700, parents=True, exist_ok=False)
    (args.evidence / "sources.json").write_text(json.dumps(frozen, indent=2))
    native = PrivateSecretService(args.secret_service_daemon, args.native_libraries)
    actor = session = vault = None
    original_failure = None
    forwarded = not args.historical_image
    try:
        switch_image(stack, args.historical_image or args.current_image, args.certificate,
            shared_runtime=args.shared_runtime)
        identity = provision_identity(stack, str(args.certificate))
        actor = AccountActor(stack, str(args.certificate), identity)
        os.environ["SSL_CERT_FILE"] = str(args.certificate)
        os.environ["NO_PROXY"] = "*"
        inputs = {"account": stack.account_origin, "arteligo": stack.arteligo_origin,
            "certificate": str(args.certificate)}
        profile = "mk-" + secrets.token_hex(16)
        vault = make_vault(inputs, profile, ActualTransport(str(args.certificate)))
        vault.login(open_browser=actor.authorize)
        actor.accept_product_terms(vault.bind())
        session = open_session(account_origin=inputs["account"], arteligo_origin=inputs["arteligo"], profile=profile)
        require(session.state == "needs_setup", "fresh_e2ee_identity_required")
        draft = session.prepare_setup()
        session.finish_setup(draft)
        draft.clear()
        records = EncryptedRecords(session)
        legacy = None
        if args.historical_image:
            legacy = historical(session, records, stack, args, actor.organization)
            forwarded = True
        if args.expect_prebegin_defects:
            require(not args.historical_image, "historical_acceptance_cannot_expect_current_defects")
            try:
                migration_root_race(session, records, vault, actor, stack, args)
            except IntegrationFailure as error:
                require(error.code == "deleted_root_prebegin_race_left_migration_fence",
                    "python_before_failed_for_unexpected_reason")
                observed = json.loads((args.evidence / "migration-race.json").read_text())
                require(observed["outcome"].get("error_type") == "KeyError"
                    and observed["migration_state"] == "building"
                    and not observed["no_begin_write"] and observed["begin_wire_preconditions"] == [],
                    "python_before_did_not_reproduce_the_reported_defect")
                emit("python_before_expected_failure", error=error.code, actual=observed)
            else:
                raise IntegrationFailure("python_before_defect_not_reproduced")
            args.dart_migration_race_only = True
            try:
                dart_consumers(session, records, vault, stack, actor.organization, args, None, None)
            except IntegrationFailure as error:
                require(error.code == "dart_deleted_root_prebegin_race_left_migration_fence",
                    "dart_before_failed_for_unexpected_reason")
                observed = json.loads((args.evidence / "dart-migration-race.json").read_text())
                require(observed["migration_state"] == "building" and not observed["no_begin_write"]
                    and observed["begin_wire_preconditions"] is None,
                    "dart_before_did_not_reproduce_the_reported_defect")
                emit("dart_before_expected_failure", error=error.code, actual=observed)
            else:
                raise IntegrationFailure("dart_before_defect_not_reproduced")
            require(source_manifest() == frozen, "consumer_source_changed_during_before_proof")
            emit("before_prebegin_defects", whole_marker_acceptance=False, fixed_behavior=False,
                python_fenced_key_error=True, dart_fenced_missing_error=True)
            return
        if not args.dart_migration_race_only:
            migration_root_race(session, records, vault, actor, stack, args)
            migration_root_race(session, records, vault, actor, stack, args, change="update")
        if args.migration_race_only:
            require(source_manifest() == frozen, "consumer_source_changed_during_race_proof")
            emit("migration_race_only", whole_marker_acceptance=False)
            return
        if args.dart_migration_race_only:
            dart_consumers(session, records, vault, stack, actor.organization, args, None, legacy)
            require(source_manifest() == frozen, "consumer_source_changed_during_dart_race_proof")
            return
        fresh = live_root(session, records, actor.organization)
        modern(session, records, stack, fresh)
        deleted_root(session, records, stack, actor.organization)
        migration_markers(session, records, stack, actor.organization)
        dart_consumers(session, records, vault, stack, actor.organization, args, fresh, legacy)
        require(source_manifest() == frozen, "consumer_source_changed_during_proof")
        emit("complete" if forwarded and args.historical_image else "modern_complete",
            source_manifest_sha256=hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest(),
            current_backend_image=args.current_image, historical_backend_image=args.historical_image,
            historical_receipt_exercised=bool(args.historical_image),
            calendar_ui_exercised=False, dart_consumer_exercised=True)
    except BaseException as error:
        original_failure = error
        emit("first_failure", error=error.code if isinstance(error, (E2eeError, IntegrationFailure)) else type(error).__name__)
        raise
    finally:
        try:
            if forwarded:
                switch_image(stack, args.current_image, args.certificate,
                    shared_runtime=args.shared_runtime)
            if session is not None:
                session.lock()
            if vault is not None:
                vault.logout()
            if actor is not None:
                actor.close_owned_identity()
        except Exception as error:
            emit("owned_cleanup_unresolved", error=error.code
                if isinstance(error, (E2eeError, IntegrationFailure)) else type(error).__name__)
            if original_failure is None:
                raise
        finally:
            if actor is not None:
                actor.close()
            native.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-config", type=Path, required=True)
    parser.add_argument("--owned-workspace-id", required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--secret-service-daemon", type=Path, required=True)
    parser.add_argument("--native-libraries", type=Path, required=True)
    parser.add_argument("--current-image", required=True)
    parser.add_argument("--csm-image")
    parser.add_argument("--shared-runtime", action="store_true")
    parser.add_argument("--historical-image")
    parser.add_argument("--arteligo-workspace-config", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--dart-artifacts", type=Path)
    parser.add_argument("--compile-consumer-only", action="store_true")
    parser.add_argument("--migration-race-only", action="store_true")
    parser.add_argument("--dart-migration-race-only", action="store_true")
    parser.add_argument("--migration-race-change", choices=("delete", "update"), default="delete")
    parser.add_argument("--expect-prebegin-defects", action="store_true")
    args = parser.parse_args()
    try:
        if args.compile_consumer_only:
            compile_dart(args.evidence, args.certificate)
        else:
            run(args)
    except Exception as error:
        emit("entry_failed", error=error.code
            if isinstance(error, (E2eeError, IntegrationFailure)) else type(error).__name__)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
