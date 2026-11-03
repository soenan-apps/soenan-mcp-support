from __future__ import annotations

import base64
import hashlib
import json
import threading
import uuid
from contextlib import contextmanager

from google.protobuf.message import DecodeError, Message
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from ._api import E2eeAPI
from ._core import CryptoCore
from ._crypto import E2eeError, decode, encode
from ._storage import ProfileSecureStore


class DeviceSession:
    def __init__(self, api: E2eeAPI, store: ProfileSecureStore, *, origin: str, subject: str):
        self._api, self.store, self.subject = api, store, subject
        self.origin = origin
        self._credentials = api.credentials
        self.core = CryptoCore()
        namespace = hashlib.sha256((origin + "\n" + subject).encode()).hexdigest()
        self._storage_key = "device:core:" + namespace
        self._lock = threading.RLock()
        self._locked = False

    @contextmanager
    def _document(self):
        self._credentials.check_current()
        if self._locked:
            raise E2eeError("device_locked")
        with self._lock, self.store.credential(self._storage_key) as item:
            raw = item.read()
            if raw is None:
                document = {"state": encode(crypto.CoreState(subject=self.subject).SerializeToString()), "pending": {}}
            else:
                try:
                    document = json.loads(raw)
                    if crypto.CoreState.FromString(bytes(decode(document["state"]))).subject != self.subject:
                        raise ValueError()
                except (ValueError, KeyError, TypeError, DecodeError):
                    raise E2eeError("secure_store_corrupt") from None
            yield document
            self._credentials.check_current()
            item.replace(json.dumps(document, separators=(",", ":")))

    @staticmethod
    def _state(document):
        return crypto.CoreState.FromString(bytes(decode(document["state"])))

    @property
    def device_id(self):
        with self._document() as document:
            return self._state(document).device_id

    @property
    def state(self):
        with self._document() as document:
            status = self._state(document).device_status
        return {crypto.UNREGISTERED: "needs_setup", crypto.PENDING: "pending_approval",
            crypto.APPROVED: "approved", crypto.REVOKED: "revoked"}[status]

    def require_approved(self):
        status = self.state
        if status == "revoked":
            raise E2eeError("device_revoked")
        if status != "approved":
            raise E2eeError("device_approval_required")

    def call(self, operation: str, *, body=None, **parameters):
        self._credentials.check_current()
        if self._locked:
            raise E2eeError("device_locked")
        return self._api.call(operation, body=body, **parameters)

    def request(self, operation: str, message: Message, response_type):
        response = self.call(operation, body={"bytes": base64.b64encode(message.SerializeToString()).decode("ascii")})
        try:
            return response_type.FromString(base64.b64decode(response["bytes"], validate=True))
        except (KeyError, ValueError, TypeError, DecodeError):
            raise E2eeError("invalid_response") from None

    def read_bundle(self, project_id="", **query):
        return self.request("readCrypto", app.ReadCryptoRequest(project_id=project_id, device_id=self.device_id, **query), app.ReadCryptoResponse)

    def open_result(self, bundle, *, release_namespaces=()):
        with self._document() as document:
            operations = [document["domain_documents"][namespace]["operation_id"] for namespace in release_namespaces]
            opened = self.core.execute(crypto.CoreRequest(open=crypto.OpenInput(
                state=self._state(document), bundle=bundle, release_operation_ids=operations))).opened
            document["state"] = encode(opened.state.SerializeToString())
            for namespace in release_namespaces:
                del document["domain_documents"][namespace]
            return opened

    def prepare(self, project_id, *, values=(), deliveries=(), create_keys=(), binding=b"", operation_id=None, bundle=None):
        self.require_approved()
        if bundle is None:
            bundle = self.read_bundle(project_id).bundle
        with self._document() as document:
            if project_id in document["pending"]:
                raise E2eeError("record_publication_pending")
            mutation = crypto.CryptoMutationInput(state=self._state(document), bundle=bundle,
                operation_id=operation_id or str(uuid.uuid4()), values=values, deliveries=deliveries,
                create_protection_keys=create_keys, namespace_id=project_id, application_binding=binding)
            prepared = self.core.execute(crypto.CoreRequest(prepare=mutation)).prepared
            document["state"] = encode(prepared.state.SerializeToString())
            document["pending"][project_id] = mutation.operation_id
        return prepared.command

    def open_bundle(self, bundle, *, release_namespaces=()):
        return list(self.open_result(bundle, release_namespaces=release_namespaces).values)

    def verify_documents(self, bundle, *, release_namespaces=()):
        return list(self.open_result(bundle, release_namespaces=release_namespaces).verified_documents)

    def commit(self, project_id, *, operation="commitCrypto", request=None):
        with self._document() as document:
            pending = document["pending"].get(project_id)
            if pending is None:
                raise E2eeError("record_publication_not_pending")
            command = self._prepared(self._state(document), pending).command
        message = request or app.CommitCryptoRequest(project_id=project_id, command=command)
        mutation = message if isinstance(message, app.CommitCryptoRequest) else message.mutation
        mutation.signer_public_key = self.signing_public_key
        response = self.request(operation, message, app.CommitCryptoResponse)
        with self._document() as document:
            opened = self.core.execute(crypto.CoreRequest(open=crypto.OpenInput(
                state=self._state(document), bundle=response.bundle, release_operation_ids=[pending]))).opened
            document["state"] = encode(opened.state.SerializeToString())
            if document["pending"].get(project_id) == pending:
                del document["pending"][project_id]
        return response, opened

    def enroll(self, *, action=crypto.APPROVE_DEVICE, pairing_request=None, addition_code=b"", account_assertion="", now_seconds=0, sealed_bootstrap=b""):
        bundle = self.settings().bundle
        with self._document() as document:
            enrollment = crypto.DeviceEnrollment(state=self._state(document), bundle=bundle,
                operation_id=str(uuid.uuid4()), action=action, addition_code=addition_code,
                account_assertion=account_assertion, now_seconds=now_seconds, sealed_bootstrap=sealed_bootstrap)
            if pairing_request is not None:
                enrollment.pairing_request.CopyFrom(pairing_request)
            change = self.core.execute(crypto.CoreRequest(enroll=enrollment)).identity_change
            document["state"] = encode(change.state.SerializeToString())
        return change

    def publish_identity(self, change, *, rotate=False):
        operation = "rotateCrypto" if rotate else "enrollCrypto"
        signer = self.signing_public_key
        if not rotate:
            body = crypto.EnrollmentBody.FromString(change.command.body)
            if body.action == crypto.OPEN_CODE:
                signer = body.code_public_key
        request = app.IdentityChangeRequest(command=change.command, identity=change.identity, bootstrap=change.bootstrap,
            key_certificates=change.key_certificates, deliveries=change.deliveries, signer_public_key=signer)
        with self._document() as document:
            saved = document.get("identity_publication")
            raw = encode(request.SerializeToString())
            if saved is not None and (saved["operation"] != operation or saved["request"] != raw):
                raise E2eeError("identity_operation_pending")
            document["identity_publication"] = {"operation": operation, "request": raw}
        return self.resume_identity()

    def rotate(self, *, revoke_device_ids=()):
        with self._document() as document:
            pending = document.get("identity_publication")
        if pending is not None:
            if pending["operation"] != "rotateCrypto":
                raise E2eeError("identity_operation_pending")
            request = app.IdentityChangeRequest.FromString(bytes(decode(pending["request"])))
            previous = crypto.RotationBody.FromString(request.command.body)
            if list(previous.revoked_device_ids) != list(revoke_device_ids) or previous.replace_addition_key:
                raise E2eeError("identity_operation_pending")
            return self.resume_identity()
        bundle = self.read_bundle().bundle
        with self._document() as document:
            change = self.core.execute(crypto.CoreRequest(rotate=crypto.IdentityRotation(
                state=self._state(document), bundle=bundle, operation_id=str(uuid.uuid4()), revoke_device_ids=revoke_device_ids))).identity_change
            document["state"] = encode(change.state.SerializeToString())
        return self.publish_identity(change, rotate=True)

    def lock(self):
        with self._lock:
            self._locked = True

    def pending_command(self, project_id):
        with self._document() as document:
            pending = document["pending"].get(project_id)
            return self._prepared(self._state(document), pending).command if pending is not None else None

    def configure(self, configuration):
        with self._document() as document:
            state = self._state(document)
            state.account_jwks = configuration.account_jwks
            state.account_issuer = configuration.account_issuer
            state.account_audience = configuration.account_audience
            document["state"] = encode(state.SerializeToString())

    def settings(self):
        response = self.request("getCryptoSettings", app.CryptoSettingsRequest(), app.CryptoSettingsResponse)
        self.configure(response)
        return response

    def catalog_response(self, *, cursor="", limit=256):
        self.require_approved()
        response = self.request("listCryptoProjects", app.ProjectCatalogRequest(device_id=self.device_id, cursor=cursor, limit=limit), app.ProjectCatalogResponse)
        self.open_bundle(response.bundle)
        return response

    def catalog(self, *, cursor="", limit=256):
        from google.protobuf.json_format import MessageToDict
        response = self.catalog_response(cursor=cursor, limit=limit)
        return {"projects": [{"project_id": p.project_id, "scope_id": p.project_id, "group_id": p.group_id, "role": p.role,
            "shared": p.shared, "key_epoch": p.protection_key.generation} for p in response.projects],
            "cursor": response.cursor, "has_more": response.has_more,
            "groups": [MessageToDict(group, preserving_proto_field_name=True) for group in response.groups]}

    def project(self, project_id):
        cursor = ""
        while True:
            response = self.catalog_response(cursor=cursor)
            for project in response.projects:
                if project.project_id == project_id:
                    return project
            if not response.has_more:
                raise E2eeError("project_access_denied")
            cursor = response.cursor

    def audience(self, group_id, project_id):
        response = self.request("getCryptoProjectAudience", app.ProjectAudienceRequest(
            device_id=self.device_id, group_id=group_id, project_id=project_id), app.ProjectAudienceResponse)
        self.open_bundle(response.bundle)
        return response

    def prepare_owner_delivery(self, project_id, subject):
        project = self.project(project_id)
        audience = self.audience(project.group_id, project_id)
        recipients = [m.receiver for m in audience.members if m.subject == subject]
        if not recipients:
            raise E2eeError("owner_candidate_invalidated")
        command = self.pending_command(project_id)
        if command is not None:
            previous = crypto.MutationBody.FromString(command.body)
            binding = app.RecordMutationBinding.FromString(previous.application_binding)
            if (previous.values or binding.membership.subject != subject
                    or binding.project_policy.group_id != project.group_id
                    or not binding.project_policy.prepare_owner_deliveries):
                raise E2eeError("record_publication_pending")
        else:
            binding = app.RecordMutationBinding(project_policy=app.ProjectPolicyBinding(
                project_id=project_id, group_id=project.group_id, shared=project.shared,
                current_protection_key=project.protection_key,
                expected_distribution_revision=project.distribution_revision, prepare_owner_deliveries=True),
                membership=app.MembershipBinding(subject=subject))
            command = self.prepare(project_id, deliveries=[crypto.DeliveryMutation(
                target=project.protection_key, recipient=receiver) for receiver in recipients],
                binding=binding.SerializeToString(), bundle=audience.bundle)
        self.commit(project_id, operation="prepareCryptoOwnerDelivery",
            request=app.OwnerDeliveryRequest(project_id=project_id, subject=subject,
                mutation=app.CommitCryptoRequest(project_id=project_id, command=command)))
        return {"project_id": project_id, "subject": subject, "state": "prepared"}

    def _save_identity_draft(self, change, kind):
        operation_kind = crypto.ENROLLMENT if kind == "genesis" else crypto.ROOT_ROTATION
        with self._document() as document:
            operation = next((operation for operation in self._state(document).identity_operations
                if operation.kind == operation_kind and operation.command == change.command
                and operation.binding_bytes == change.binding_bytes), None)
            if operation is None:
                raise E2eeError("identity_operation_not_pending")
            token = operation.operation_id
            document.setdefault("identity_drafts", {})[token] = {"kind": kind, "operation_id": token}
        return {"draft_id": token, "code": encode(operation.addition_code)}

    def _identity_draft(self, draft, kind):
        with self._document() as document:
            saved = document.get("identity_drafts", {}).get(draft.get("draft_id"))
            if saved is None or saved["kind"] != kind:
                raise E2eeError("identity_operation_not_pending")
            return self._identity_operation(self._state(document), saved["operation_id"])

    def prepare_setup(self):
        pending = self._pending_identity_draft("genesis")
        if pending is not None:
            return pending
        change = self.enroll(action=crypto.PREPARE_GENESIS)
        return self._save_identity_draft(change, "genesis")

    def setup(self, draft):
        import time
        change = self._identity_draft(draft, "genesis")
        if not change.HasField("identity"):
            attestation = self.request("attestCrypto", app.NonceAttestationRequest(
                nonce=change.binding_nonce, binding_bytes=change.binding_bytes), app.NonceAttestationResponse)
            with self._document() as document:
                state = self._state(document)
                state.account_jwks = attestation.configuration.account_jwks
                state.account_issuer = attestation.configuration.account_issuer
                state.account_audience = attestation.configuration.account_audience
                operation_id = str(uuid.uuid4())
                change = self.core.execute(crypto.CoreRequest(enroll=crypto.DeviceEnrollment(
                    state=state, action=crypto.COMMIT_GENESIS, account_assertion=attestation.assertion,
                    now_seconds=int(time.time()), operation_id=operation_id))).identity_change
                document["identity_drafts"][draft["draft_id"]]["operation_id"] = operation_id
                document["state"] = encode(change.state.SerializeToString())
        binding = crypto.GenesisPublicBinding.FromString(change.binding_bytes)
        response = self.request("genesisCrypto", app.GenesisRequest(binding=binding,
            binding_bytes=change.binding_bytes, identity=change.identity,
            account_assertion=crypto.IdentityStatement.FromString(change.identity.statement.body).account_attestation.decode(),
            bootstrap=change.bootstrap, key_certificates=change.key_certificates), app.CommitCryptoResponse)
        with self._document() as document:
            state = self._state(document)
            release = self._identity_release_ids(state, change.command, binding_bytes=change.binding_bytes)
            opened = self.core.execute(crypto.CoreRequest(open=crypto.OpenInput(
                state=state, bundle=response.bundle, release_operation_ids=release))).opened
            document["state"] = encode(opened.state.SerializeToString())
            del document["identity_drafts"][draft["draft_id"]]
        return {"state": "approved", "device_id": self.device_id}

    def prepare_addition_key(self):
        pending = self._pending_identity_draft("addition")
        if pending is not None:
            return pending
        bundle = self.read_bundle().bundle
        with self._document() as document:
            change = self.core.execute(crypto.CoreRequest(rotate=crypto.IdentityRotation(
                state=self._state(document), bundle=bundle, operation_id=str(uuid.uuid4()),
                replace_addition_key=True))).identity_change
            document["state"] = encode(change.state.SerializeToString())
        return self._save_identity_draft(change, "addition")

    def replace_addition_key(self, draft):
        change = self._identity_draft(draft, "addition")
        self.publish_identity(change, rotate=True)
        return {"state": "approved", "device_id": self.device_id}

    def add_by_key(self, code):
        with self._document() as document:
            pending = document.get("identity_publication")
        if pending is not None:
            request = app.IdentityChangeRequest.FromString(bytes(decode(pending["request"])))
            body = crypto.EnrollmentBody.FromString(request.command.body)
            if pending["operation"] != "enrollCrypto" or body.action != crypto.OPEN_CODE:
                raise E2eeError("identity_operation_pending")
            self.resume_identity()
        else:
            settings = self.settings()
            change = self.enroll(action=crypto.OPEN_CODE, addition_code=bytes(decode(code)),
                sealed_bootstrap=settings.sealed_bootstrap)
            self.publish_identity(change)
        return {"state": "approved", "device_id": self.device_id}

    def addition_code(self):
        change = self.enroll(action=crypto.EXPORT_CODE)
        return encode(change.addition_code)

    def pending_documents(self, namespace):
        with self._document() as document:
            saved = document.get("domain_documents", {}).get(namespace)
            if saved is None:
                return None
            prepared = self._prepared(self._state(document), saved["operation_id"])
            return list(prepared.signed_documents), bytes(decode(saved["local"]))

    def prepare_documents(self, namespace, project_id, documents, bundle, *, local=b""):
        with self._document() as document:
            saved = document.setdefault("domain_documents", {}).get(namespace)
            if saved is not None:
                prepared = self._prepared(self._state(document), saved["operation_id"])
                return list(prepared.signed_documents), bytes(decode(saved["local"]))
            operation_id = str(uuid.uuid4())
            prepared = self.core.execute(crypto.CoreRequest(prepare=crypto.CryptoMutationInput(
                state=self._state(document), bundle=bundle, namespace_id=project_id,
                operation_id=operation_id, documents=documents))).prepared
            document["state"] = encode(prepared.state.SerializeToString())
            document["domain_documents"][namespace] = {
                "operation_id": operation_id,
                "local": encode(local)}
            return list(prepared.signed_documents), local

    @staticmethod
    def _prepared(state, operation_id):
        for prepared in state.prepared_operations:
            if prepared.operation_id == operation_id:
                return prepared
        raise E2eeError("prepared_operation_missing")

    def digest(self, value):
        return hashlib.sha256(value).digest()

    def random_bytes(self, length):
        return self.core.execute_utility(crypto.CoreUtilityRequest(random=crypto.RandomInput(length=length))).random_bytes

    def trusted_root_digest(self):
        with self._document() as document:
            for anchor in self._state(document).trust_anchors:
                if anchor.subject == self.subject:
                    return bytes(anchor.root_digest)
        raise E2eeError("untrusted_identity")

    def pairing_request(self):
        from google.protobuf.json_format import MessageToDict
        change = self.enroll(action=crypto.PREPARE_DEVICE)
        return MessageToDict(change.command, preserving_proto_field_name=True)

    def approve(self, pairing):
        from google.protobuf.json_format import MessageToDict, ParseDict
        pairing_request = ParseDict(pairing, crypto.SignedBytes())
        device = crypto.EnrollmentBody.FromString(pairing_request.body).device
        with self._document() as document:
            pending = document.get("identity_publication")
        if pending is not None:
            request = app.IdentityChangeRequest.FromString(bytes(decode(pending["request"])))
            body = crypto.EnrollmentBody.FromString(request.command.body)
            if pending["operation"] != "enrollCrypto" or body.action != crypto.APPROVE_DEVICE or body.device != device:
                raise E2eeError("identity_operation_pending")
            response = self.resume_identity()
        else:
            change = self.enroll(action=crypto.APPROVE_DEVICE, pairing_request=pairing_request)
            response = self.publish_identity(change)
        return MessageToDict(response, preserving_proto_field_name=True)

    def accept_approval(self, approval):
        from google.protobuf.json_format import ParseDict
        response = ParseDict(approval, app.CommitCryptoResponse())
        self.open_bundle(response.bundle)
        self.require_approved()
        return {"state": "approved", "device_id": self.device_id}

    def reanchor(self):
        self.rotate()
        return {"state": "approved", "device_id": self.device_id}

    def _pending_identity_draft(self, kind):
        with self._document() as document:
            for token, saved in document.get("identity_drafts", {}).items():
                if saved["kind"] == kind:
                    change = self._identity_operation(self._state(document), saved["operation_id"])
                    return {"draft_id": token, "code": encode(change.addition_code)}
        return None

    def resume_identity(self):
        with self._document() as document:
            pending = document.get("identity_publication")
            if pending is None:
                raise E2eeError("identity_operation_not_pending")
            request = app.IdentityChangeRequest.FromString(bytes(decode(pending["request"])))
        response = self.request(pending["operation"], request, app.CommitCryptoResponse)
        with self._document() as document:
            state = self._state(document)
            release = self._identity_release_ids(state, request.command)
            opened = self.core.execute(crypto.CoreRequest(open=crypto.OpenInput(
                state=state, bundle=response.bundle, release_operation_ids=release))).opened
            document["state"] = encode(opened.state.SerializeToString())
            for token, saved in list(document.get("identity_drafts", {}).items()):
                if saved["operation_id"] in release:
                    del document["identity_drafts"][token]
            if document.get("identity_publication") == pending:
                del document["identity_publication"]
        return response

    @staticmethod
    def _identity_release_ids(state, command, *, binding_bytes=b""):
        return [operation.operation_id for operation in state.identity_operations
            if operation.command == command or (binding_bytes and operation.binding_bytes == binding_bytes)]

    @staticmethod
    def _identity_operation(state, operation_id):
        for operation in state.identity_operations:
            if operation.operation_id == operation_id:
                return operation
        raise E2eeError("identity_operation_not_pending")

    def possession_proof(self, secret, challenge):
        return self.core.execute_utility(crypto.CoreUtilityRequest(
            prove=crypto.ProofInput(secret=secret, challenge=challenge))).proof

    @property
    def signing_public_key(self):
        with self._document() as document:
            return bytes(self._state(document).device_signing_public)

    def prepare_group_member(self, group_id, subject):
        audience = self.audience(group_id, "")
        recipients = [member for member in audience.members if member.subject == subject]
        if not recipients:
            raise E2eeError("organization_member_not_found")
        mutations = []
        operation_ids = {}
        for project in audience.projects:
            command = self.pending_command(project.project_id)
            if command is not None:
                previous = crypto.MutationBody.FromString(command.body)
                previous_binding = app.RecordMutationBinding.FromString(previous.application_binding)
                if (previous.values or previous_binding.membership.subject != subject
                        or previous_binding.project_policy.group_id != group_id
                        or not previous_binding.project_policy.prepare_owner_deliveries):
                    raise E2eeError("record_publication_pending")
            if command is None:
                bundle = crypto.CryptoReadBundle()
                bundle.CopyFrom(audience.bundle)
                bundle.distribution_revision = project.distribution_revision
                binding = app.RecordMutationBinding(project_policy=app.ProjectPolicyBinding(
                    project_id=project.project_id, group_id=group_id, shared=project.shared,
                    current_protection_key=project.protection_key,
                    expected_distribution_revision=project.distribution_revision, prepare_owner_deliveries=True),
                    membership=app.MembershipBinding(subject=subject, expected_revision=recipients[0].revision,
                        role=recipients[0].role, owner_candidate=recipients[0].owner_candidate))
                command = self.prepare(project.project_id,
                    deliveries=[crypto.DeliveryMutation(target=project.protection_key, recipient=m.receiver) for m in recipients],
                    binding=binding.SerializeToString(), bundle=bundle)
            mutations.append(app.CommitCryptoRequest(project_id=project.project_id, command=command,
                signer_public_key=self.signing_public_key))
            with self._document() as document:
                operation_ids[project.project_id] = document["pending"][project.project_id]
        response = self.request("prepareCryptoGroupMember", app.GroupMemberPreparationRequest(
            group_id=group_id, subject=subject, mutations=mutations,
            expected_group_revision=audience.group_revision, catalog_digest=audience.catalog_digest,
            device_id=self.device_id), app.GroupMemberPreparationResponse)
        if len(response.results) != len(mutations):
            raise E2eeError("invalid_commit_receipt")
        with self._document() as document:
            state = self._state(document)
            for index, result in enumerate(response.results):
                release = list(operation_ids.values()) if index == len(response.results) - 1 else []
                state = self.core.execute(crypto.CoreRequest(open=crypto.OpenInput(
                    state=state, bundle=result.bundle, release_operation_ids=release))).opened.state
            document["state"] = encode(state.SerializeToString())
            for project_id, operation_id in operation_ids.items():
                if document["pending"].get(project_id) == operation_id:
                    del document["pending"][project_id]
        return {"group_id": group_id, "subject": subject, "state": "prepared", "project_count": len(mutations)}

    def revoke_device(self, device_id):
        self.rotate(revoke_device_ids=[device_id])
        return {"state": "revoked", "device_id": device_id}

    def remove_project_member(self, project_id, subject):
        project = self.project(project_id)
        audience = self.audience(project.group_id, project_id)
        target = next((m for m in audience.members if m.subject == subject), None)
        if target is None:
            raise E2eeError("project_member_not_found")
        command = self.pending_command(project_id)
        if command is not None:
            previous = crypto.MutationBody.FromString(command.body)
            binding = app.RecordMutationBinding.FromString(previous.application_binding)
            if (previous.values or binding.membership.subject != subject
                    or not binding.membership.revoked):
                raise E2eeError("record_publication_pending")
        else:
            key = crypto.KeyRef(id=project.protection_key.id, generation=project.protection_key.generation + 1)
            binding = app.RecordMutationBinding(project_policy=app.ProjectPolicyBinding(
                project_id=project_id, group_id=project.group_id, shared=project.shared,
                current_protection_key=key, expected_distribution_revision=project.distribution_revision,
                prepare_owner_deliveries=True), membership=app.MembershipBinding(
                    subject=subject, expected_revision=target.revision, role=target.role, revoked=True))
            recipients = [m for m in audience.members if m.subject != subject or m.owner_candidate]
            command = self.prepare(project_id, create_keys=[key],
                deliveries=[crypto.DeliveryMutation(target=key, recipient=m.receiver) for m in recipients],
                binding=binding.SerializeToString(), bundle=audience.bundle)
        self.commit(project_id)
        return {"project_id": project_id, "subject": subject, "state": "removed"}
