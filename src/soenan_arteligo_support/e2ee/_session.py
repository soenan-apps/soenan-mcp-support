from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from collections.abc import Callable, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TypeVar, cast

from arteligo_public_api_client.models.crypto_proto_message import CryptoProtoMessage
from google.protobuf.message import DecodeError
from soenan.account.crypto.v1 import crypto_pb2 as shared
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from ._api import E2eeAPI, _ProviderRevisionConflict
from ._core import CryptoCore
from ._crypto import E2eeError, decode, encode
from ._service_generated import CryptoServiceClient, EnvelopeCall
from ._storage import ProfileStore


@dataclass(frozen=True)
class InvitationCreationPending:
    signed_document: bytes
    invitation_link: bytes


@dataclass(frozen=True)
class InvitationRequestPending:
    signed_document: bytes


@dataclass(frozen=True)
class InvitationRevocationPending:
    signed_document: bytes


InvitationPending = (
    InvitationCreationPending | InvitationRequestPending | InvitationRevocationPending
)
InvitationPendingT = TypeVar(
    "InvitationPendingT",
    InvitationCreationPending,
    InvitationRequestPending,
    InvitationRevocationPending,
)
_INVITATION_PENDING_TYPES = {
    "create": InvitationCreationPending,
    "request": InvitationRequestPending,
    "revoke": InvitationRevocationPending,
}


class DeviceSession:
    def __init__(
        self,
        api: E2eeAPI,
        store: ProfileStore,
        *,
        origin: str,
        subject: str,
        identity,
    ):
        self._api, self.store, self.subject = api, store, subject
        self.identity = identity
        self.origin = origin
        self._credentials = api.credentials
        self.service = CryptoServiceClient(self.exchange)
        self.core = CryptoCore()
        namespace = hashlib.sha256((origin + "\n" + subject).encode()).hexdigest()
        self._storage_key = "device:core:" + namespace
        self._lock = threading.RLock()
        self._locked = False
        self._initialized_organizations = set()
        self._initialized_projects = set()

    @contextmanager
    def _document(self):
        self._credentials.check_current()
        if self._locked:
            raise E2eeError("device_locked")
        with (
            self._lock,
            self.identity._lock,
            self.store.credential(self._storage_key) as item,
        ):
            with self.identity.document() as identity_document:
                raw = item.read()
                if raw is None:
                    document = {
                        "state": encode(crypto.ProductState().SerializeToString()),
                        "pending": {},
                    }
                else:
                    try:
                        document = json.loads(raw)
                        crypto.ProductState.FromString(bytes(decode(document["state"])))
                    except (ValueError, KeyError, TypeError, DecodeError):
                        raise E2eeError("secure_store_corrupt") from None
                document["_identity"] = identity_document
                yield document
                self._credentials.check_current()
                del document["_identity"]
            item.replace(json.dumps(document, separators=(",", ":")))

    def _state(self, document) -> crypto.CoreState:
        return crypto.CoreState(
            identity=self.identity._state(document["_identity"]),
            product=crypto.ProductState.FromString(bytes(decode(document["state"]))),
        )

    def _save_state(self, document, state):
        document["state"] = encode(state.product.SerializeToString())
        document["_identity"]["state"] = encode(state.identity.SerializeToString())

    @property
    def device_id(self) -> str:
        return self.identity.device_id

    @property
    def state(self) -> str:
        return self.identity.state

    def require_approved(self) -> None:
        self.identity.require_approved()

    def exchange(self, call: EnvelopeCall) -> CryptoProtoMessage:
        self._credentials.check_current()
        if self._locked:
            raise E2eeError("device_locked")
        return self._api.execute(call)

    def initialize_organization(self, organization_id: str) -> None:
        self._credentials.check_current()
        if self._locked:
            raise E2eeError("device_locked")
        if organization_id in self._initialized_organizations:
            return
        authorization = self._api.initialize_authorization(
            [organization_id], project_ids=[]
        )
        if authorization.subject != self.subject:
            raise E2eeError("authentication_superseded")
        self._initialized_organizations.add(organization_id)

    def initialize_project(self, project_id: str) -> None:
        self._credentials.check_current()
        if self._locked:
            raise E2eeError("device_locked")
        if project_id in self._initialized_projects:
            return
        authorization = self._api.initialize_authorization([], project_ids=[project_id])
        if authorization.subject != self.subject:
            raise E2eeError("authentication_superseded")
        self._initialized_projects.add(project_id)

    def read_bundle(
        self, project_id: str, *, view: str, **query
    ) -> app.ReadCryptoResponse:
        self.initialize_project(project_id)
        return self.service.read_crypto(
            app.ReadCryptoRequest(
                project_id=project_id, device_id=self.device_id, view=view, **query
            )
        )

    def open_result(
        self, bundle: crypto.CryptoReadBundle, *, release_namespaces: Sequence[str] = ()
    ) -> crypto.OpenedValues:
        self.identity.observe_receiver_generation(bundle)
        with self._document() as document:
            for namespace in release_namespaces:
                if namespace not in document.get("invitation_publications", {}):
                    raise E2eeError("invitation_publication_not_pending")
            opened = self.core.execute(
                crypto.CoreRequest(
                    open=crypto.OpenInput(
                        state=self._state(document),
                        bundle=bundle,
                    )
                )
            ).opened
            self._save_state(document, opened.state)
            for namespace in release_namespaces:
                del document["invitation_publications"][namespace]
            return opened

    def prepare(
        self,
        project_id,
        *,
        values=(),
        deletions=(),
        deliveries=(),
        create_keys=(),
        binding=b"",
        operation_id=None,
        bundle=None,
    ):
        self.require_approved()
        if bundle is None:
            bundle = self.read_bundle(
                project_id,
                view="by_ids",
                value_ids=[value.id for value in (*values, *deletions)],
            ).bundle
        self.identity.observe_receiver_generation(bundle)
        with self._document() as document:
            if project_id in document["pending"]:
                raise E2eeError("record_publication_pending")
            mutation = crypto.CryptoMutationInput(
                state=self._state(document),
                bundle=bundle,
                operation_id=operation_id or str(uuid.uuid4()),
                values=values,
                deletions=deletions,
                accept_until=int(time.time()) + 30 * 24 * 60 * 60,
                deliveries=deliveries,
                create_protection_keys=create_keys,
                namespace_id=project_id,
                application_binding=binding,
            )
            prepared = self.core.execute(crypto.CoreRequest(prepare=mutation)).prepared
            self._save_state(document, prepared.state)
            document["pending"][project_id] = mutation.operation_id
        return prepared.command

    def open_bundle(
        self, bundle: crypto.CryptoReadBundle, *, release_namespaces: Sequence[str] = ()
    ) -> list[crypto.OpenedValue]:
        return list(
            self.open_result(bundle, release_namespaces=release_namespaces).values
        )

    def verify_documents(
        self, bundle: crypto.CryptoReadBundle, *, release_namespaces: Sequence[str] = ()
    ) -> list[shared.SignedBytes]:
        return list(
            self.open_result(
                bundle, release_namespaces=release_namespaces
            ).verified_documents
        )

    def commit(
        self,
        project_id: str,
        *,
        mutation: app.CommitCryptoRequest,
        send: Callable[[], app.CommitCryptoResponse],
        initialize: bool = True,
    ) -> tuple[app.CommitCryptoResponse, crypto.OpenedValues]:
        with self._document() as document:
            pending = document["pending"].get(project_id)
            if pending is None:
                raise E2eeError("record_publication_not_pending")
            command = self._prepared(self._state(document), pending).command
        if initialize:
            self.initialize_project(project_id)
        mutation.signer_public_key = self.signing_public_key
        try:
            response = send()
        except _ProviderRevisionConflict:
            if mutation.command == command:
                with self._document() as document:
                    if document["pending"].get(project_id) == pending:
                        state = self._state(document)
                        if any(
                            prepared.operation_id == pending
                            and prepared.command == command
                            for prepared in state.product.prepared_operations
                        ):
                            rejection = crypto.RejectPreparedOperationInput(
                                state=state,
                                command=command,
                            )
                            rejected = self.core.execute(
                                crypto.CoreRequest(reject_prepared_operation=rejection)
                            ).rejected_prepared_operation
                            if rejected.removed:
                                self._save_state(document, rejected.state)
                                del document["pending"][project_id]
            raise
        if response.receipt.operation_id != pending:
            raise E2eeError("receipt_conflict")
        bundle = crypto.CryptoReadBundle()
        bundle.CopyFrom(response.bundle)
        bundle.commit_receipts.add().CopyFrom(response.receipt)
        bundle.documents.add(signed=command)
        bundle.commitments.add(
            plaintext=command.body, expected_digest=response.receipt.mutation_digest
        )
        self.identity.observe_receiver_generation(bundle)
        with self._document() as document:
            opened = self.core.execute(
                crypto.CoreRequest(
                    open=crypto.OpenInput(
                        state=self._state(document),
                        bundle=bundle,
                        release_operation_ids=[pending],
                    )
                )
            ).opened
            self._save_state(document, opened.state)
            if document["pending"].get(project_id) == pending:
                del document["pending"][project_id]
        return response, opened

    def lock(self) -> None:
        with self._lock:
            self._locked = True
            self.identity.lock()

    def pending_command(self, project_id):
        with self._document() as document:
            pending = document["pending"].get(project_id)
            return (
                self._prepared(self._state(document), pending).command
                if pending is not None
                else None
            )

    def catalog_response(
        self, *, cursor: str = "", limit: int = 256
    ) -> app.ProjectCatalogResponse:
        self.require_approved()
        response = self.service.list_crypto_projects(
            app.ProjectCatalogRequest(
                device_id=self.device_id, cursor=cursor, limit=limit
            )
        )
        self.open_bundle(response.bundle)
        return response

    def project(self, project_id):
        self.require_approved()
        initialized = self.read_bundle(project_id, view="by_ids")
        self.open_bundle(initialized.bundle)
        return initialized.project

    def audience(self, group_id: str, project_id: str) -> app.ProjectAudienceResponse:
        if project_id and group_id not in self._initialized_organizations:
            self.initialize_project(project_id)
        else:
            self.initialize_organization(group_id)
        response = self.service.get_crypto_project_audience(
            app.ProjectAudienceRequest(
                device_id=self.device_id, group_id=group_id, project_id=project_id
            )
        )
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
            if (
                previous.values
                or binding.membership.subject != subject
                or binding.project_policy.group_id != project.group_id
                or not binding.project_policy.prepare_owner_deliveries
            ):
                raise E2eeError("record_publication_pending")
        else:
            binding = app.RecordMutationBinding(
                project_policy=app.ProjectPolicyBinding(
                    project_id=project_id,
                    group_id=project.group_id,
                    shared=project.shared,
                    current_protection_key=project.protection_key,
                    expected_distribution_revision=project.distribution_revision,
                    prepare_owner_deliveries=True,
                ),
                membership=app.MembershipBinding(subject=subject),
            )
            command = self.prepare(
                project_id,
                deliveries=[
                    crypto.DeliveryMutation(
                        target=project.protection_key, recipient=receiver
                    )
                    for receiver in recipients
                ],
                binding=binding.SerializeToString(),
                bundle=audience.bundle,
            )
        request = app.OwnerDeliveryRequest(
            project_id=project_id,
            subject=subject,
            mutation=app.CommitCryptoRequest(project_id=project_id, command=command),
        )
        self.commit(
            project_id,
            mutation=request.mutation,
            send=lambda: self.service.prepare_crypto_owner_delivery(request),
        )
        return {"project_id": project_id, "subject": subject, "state": "prepared"}

    def pending_documents(
        self, namespace: str, pending_type: type[InvitationPendingT]
    ) -> InvitationPendingT | None:
        with self._document() as document:
            saved = document.get("invitation_publications", {}).get(namespace)
            if saved is None:
                return None
            try:
                stored_type = _INVITATION_PENDING_TYPES[saved["kind"]]
                if stored_type is not pending_type:
                    raise E2eeError("invitation_publication_pending")
                signed_document = bytes(decode(saved["signed_document"]))
                shared.SignedBytes.FromString(signed_document)
                if stored_type is InvitationCreationPending:
                    invitation_link = bytes(decode(saved["invitation_link"]))
                    app.InvitationLink.FromString(invitation_link)
                    pending: InvitationPending = stored_type(
                        signed_document, invitation_link
                    )
                else:
                    pending = stored_type(signed_document)
                return cast(InvitationPendingT, pending)
            except (KeyError, TypeError, ValueError, DecodeError):
                raise E2eeError("secure_store_corrupt") from None

    def prepare_documents(
        self,
        namespace: str,
        body: bytes,
        bundle: crypto.CryptoReadBundle,
        make_pending: Callable[[bytes], InvitationPendingT],
    ) -> InvitationPendingT:
        self.identity.observe_receiver_generation(bundle)
        with self._document() as document:
            publications = document.setdefault("invitation_publications", {})
            if namespace in publications:
                raise E2eeError("invitation_publication_pending")
            signed = self.core.execute(
                crypto.CoreRequest(
                    sign_documents=crypto.SignDocumentsInput(
                        state=self._state(document),
                        bundle=bundle,
                        documents=[body],
                    )
                )
            ).signed_documents
            self._save_state(document, signed.state)
            pending = make_pending(signed.documents[0].SerializeToString())
            kind = next(
                kind
                for kind, pending_type in _INVITATION_PENDING_TYPES.items()
                if type(pending) is pending_type
            )
            saved = {
                "kind": kind,
                "signed_document": encode(pending.signed_document),
            }
            if isinstance(pending, InvitationCreationPending):
                saved["invitation_link"] = encode(pending.invitation_link)
            publications[namespace] = saved
            return pending

    @staticmethod
    def _prepared(state, operation_id):
        for prepared in state.product.prepared_operations:
            if prepared.operation_id == operation_id:
                return prepared
        raise E2eeError("prepared_operation_missing")

    def digest(self, value):
        return hashlib.sha256(value).digest()

    def random_bytes(self, length):
        return self.identity.core.execute_utility(
            shared.CoreUtilityRequest(random=shared.RandomInput(length=length))
        ).random_bytes

    def possession_proof(self, secret, challenge):
        return self.identity.core.execute_utility(
            shared.CoreUtilityRequest(
                prove=shared.ProofInput(secret=secret, challenge=challenge)
            )
        ).proof

    @property
    def signing_public_key(self):
        return self.identity.signing_public_key

    def prepare_group_member(self, group_id, subject):
        self.initialize_organization(group_id)
        audience = self.audience(group_id, "")
        recipients = [
            member for member in audience.members if member.subject == subject
        ]
        if not recipients:
            raise E2eeError("organization_member_not_found")
        mutations = []
        operation_ids = {}
        for project in audience.projects:
            command = self.pending_command(project.project_id)
            if command is not None:
                previous = crypto.MutationBody.FromString(command.body)
                previous_binding = app.RecordMutationBinding.FromString(
                    previous.application_binding
                )
                if (
                    previous.values
                    or previous_binding.membership.subject != subject
                    or previous_binding.project_policy.group_id != group_id
                    or not previous_binding.project_policy.prepare_owner_deliveries
                ):
                    raise E2eeError("record_publication_pending")
            if command is None:
                bundle = crypto.CryptoReadBundle()
                bundle.CopyFrom(audience.bundle)
                bundle.distribution_revision = project.distribution_revision
                binding = app.RecordMutationBinding(
                    project_policy=app.ProjectPolicyBinding(
                        project_id=project.project_id,
                        group_id=group_id,
                        shared=project.shared,
                        current_protection_key=project.protection_key,
                        expected_distribution_revision=project.distribution_revision,
                        prepare_owner_deliveries=True,
                    ),
                    membership=app.MembershipBinding(
                        subject=subject,
                        expected_revision=recipients[0].revision,
                        role=recipients[0].role,
                        owner_candidate=recipients[0].owner_candidate,
                    ),
                )
                command = self.prepare(
                    project.project_id,
                    deliveries=[
                        crypto.DeliveryMutation(
                            target=project.protection_key, recipient=m.receiver
                        )
                        for m in recipients
                    ],
                    binding=binding.SerializeToString(),
                    bundle=bundle,
                )
            mutations.append(
                app.CommitCryptoRequest(
                    project_id=project.project_id,
                    command=command,
                    signer_public_key=self.signing_public_key,
                )
            )
            with self._document() as document:
                operation_ids[project.project_id] = document["pending"][
                    project.project_id
                ]
        response = self.service.prepare_crypto_group_member(
            app.GroupMemberPreparationRequest(
                group_id=group_id,
                subject=subject,
                mutations=mutations,
                expected_group_revision=audience.group_revision,
                catalog_digest=audience.catalog_digest,
                device_id=self.device_id,
            )
        )
        if len(response.results) != len(mutations):
            raise E2eeError("invalid_commit_receipt")
        with self._document() as document:
            state = self._state(document)
            for result, mutation in zip(response.results, mutations, strict=False):
                state = self.core.execute(
                    crypto.CoreRequest(
                        open=crypto.OpenInput(
                            state=state,
                            bundle=result.bundle,
                            release_operation_ids=[operation_ids[mutation.project_id]],
                        )
                    )
                ).opened.state
            self._save_state(document, state)
            for project_id, operation_id in operation_ids.items():
                if document["pending"].get(project_id) == operation_id:
                    del document["pending"][project_id]
        return {
            "group_id": group_id,
            "subject": subject,
            "state": "prepared",
            "project_count": len(mutations),
        }

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
            if (
                previous.values
                or binding.membership.subject != subject
                or not binding.membership.revoked
            ):
                raise E2eeError("record_publication_pending")
        else:
            key = shared.KeyRef(
                id=project.protection_key.id,
                generation=project.protection_key.generation + 1,
            )
            binding = app.RecordMutationBinding(
                project_policy=app.ProjectPolicyBinding(
                    project_id=project_id,
                    group_id=project.group_id,
                    shared=project.shared,
                    current_protection_key=key,
                    expected_distribution_revision=project.distribution_revision,
                    prepare_owner_deliveries=True,
                ),
                membership=app.MembershipBinding(
                    subject=subject,
                    expected_revision=target.revision,
                    role=target.role,
                    revoked=True,
                ),
            )
            recipients = [
                m for m in audience.members if m.subject != subject or m.owner_candidate
            ]
            command = self.prepare(
                project_id,
                create_keys=[key],
                deliveries=[
                    crypto.DeliveryMutation(target=key, recipient=m.receiver)
                    for m in recipients
                ],
                binding=binding.SerializeToString(),
                bundle=audience.bundle,
            )
        request = app.CommitCryptoRequest(project_id=project_id, command=command)
        self.commit(
            project_id,
            mutation=request,
            send=lambda: self.service.commit_crypto(request),
        )
        return {"project_id": project_id, "subject": subject, "state": "removed"}
