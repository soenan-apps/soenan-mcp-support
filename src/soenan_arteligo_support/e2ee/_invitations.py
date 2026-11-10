from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from google.protobuf.message import DecodeError
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from ._crypto import E2eeError, decode, encode, wipe

if TYPE_CHECKING:
    from ._session import DeviceSession


def _invitation_token(
    origin: str, invitation: str, identifier: str | None
) -> app.InvitationLink:
    if not isinstance(invitation, str) or any(
        ord(value) < 32 or ord(value) == 127 for value in invitation
    ):
        raise E2eeError("invalid_invitation_link")
    if invitation.startswith("ainv2_"):
        token = invitation
    else:
        try:
            parsed = urlsplit(invitation)
        except ValueError:
            raise E2eeError("invalid_invitation_link") from None
        parts = parsed.path.split("/")
        if len(parts) != 3 or parts[:2] != ["", "invitations"]:
            raise E2eeError("invalid_invitation_link")
        if identifier is not None and identifier != parts[2]:
            raise E2eeError("invalid_invitation_link")
        identifier = parts[2]
        if not parsed.fragment.startswith("invite="):
            raise E2eeError("invalid_invitation_link")
        token = parsed.fragment[7:]
        if (
            invitation
            != f"{origin.rstrip('/')}/invitations/{identifier}#invite={token}"
        ):
            raise E2eeError("invalid_invitation_link")
    if re.fullmatch(r"ainv2_[A-Za-z0-9_-]+", token) is None:
        raise E2eeError("invalid_invitation_link")
    raw = decode(token[6:])
    try:
        link = app.InvitationLink.FromString(bytes(raw))
    except DecodeError:
        raise E2eeError("invalid_invitation_link") from None
    finally:
        wipe(raw)
    if (
        re.fullmatch(r"[A-Za-z0-9_-]{1,128}", link.invitation_id) is None
        or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", link.project_id) is None
        or (identifier is not None and identifier != link.invitation_id)
        or len(link.secret) != 32
        or len(link.inviter_root_digest) != 32
        or len(link.descriptor_digest) != 32
    ):
        link.Clear()
        raise E2eeError("invalid_invitation_link")
    return link


def _status(response, project_id, invitation_id):
    matches = [
        item for item in response.invitations if item.invitation_id == invitation_id
    ]
    if len(matches) != 1:
        raise E2eeError("invalid_response")
    status = matches[0]
    if (
        status.project_id != project_id
        or status.state != "live"
        or not status.current_owner_subject
    ):
        raise E2eeError("owner_confirmation_fresh_invitation_required")
    try:
        descriptor = app.InvitationDescriptor.FromString(status.descriptor.body)
    except DecodeError:
        raise E2eeError("invalid_response") from None
    if (
        descriptor.project_id != project_id
        or descriptor.invitation_id != invitation_id
        or descriptor.expires_at <= int(time.time())
    ):
        raise E2eeError("invitation_binding_mismatch")
    return status, descriptor


def _read_invitation(session, project_id, invitation_id):
    return session.service.read_crypto_invitations(
        app.InvitationReadRequest(
            project_id=project_id,
            invitation_id=invitation_id,
            device_id=session.device_id,
        )
    )


def _receiver_digest(session, bundle, subject):
    identities = [
        crypto.IdentityStatement.FromString(item.statement.body)
        for item in bundle.identity_statements
    ]
    own = [identity for identity in identities if identity.subject == subject]
    if not own:
        raise E2eeError("identity_missing")
    identity = max(own, key=lambda item: item.revision)
    certificates = [
        item
        for item in bundle.key_certificates
        if (body := crypto.KeyCertificateBody.FromString(item.body)).subject == subject
        and body.public_key == identity.receiver
    ]
    digests = {session.digest(item.body) for item in certificates}
    if len(digests) != 1:
        raise E2eeError("receiver_certificate_missing")
    return session.digest(identity.receiver.SerializeToString())


def _verify_invitation(session, response, project_id, link, *, release_namespace=None):
    status, descriptor = _status(response, project_id, link.invitation_id)
    if (
        link.project_id != project_id
        or descriptor.inviter_root_digest != link.inviter_root_digest
    ):
        raise E2eeError("invitation_binding_mismatch")
    response.bundle.documents.add(
        signed=status.descriptor,
        expected_digest=link.descriptor_digest,
        expected_root_digest=link.inviter_root_digest,
    )
    response.bundle.commitments.add(
        plaintext=link.secret, expected_digest=descriptor.secret_digest
    )
    try:
        owners = [
            crypto.IdentityStatement.FromString(identity.statement.body)
            for identity in response.bundle.identity_statements
        ]
    except DecodeError:
        raise E2eeError("invalid_response") from None
    if not any(
        identity.subject == status.current_owner_subject
        and any(
            device.id == status.descriptor.signer_device_id and not device.revoked
            for device in identity.devices
        )
        for identity in owners
    ):
        raise E2eeError("owner_confirmation_fresh_invitation_required")
    session.verify_documents(
        response.bundle,
        release_namespaces=[release_namespace] if release_namespace is not None else (),
    )
    return status, descriptor


def confirm_project_owner(
    session: DeviceSession,
    project_id: str,
    invitation: str,
    *,
    invitation_id: str | None,
) -> dict[str, str]:
    session.require_approved()
    link = _invitation_token(session.origin, invitation, invitation_id)
    try:
        response = _read_invitation(session, project_id, link.invitation_id)
        status, _ = _verify_invitation(session, response, project_id, link)
        return {
            "project_id": project_id,
            "owner_subject": status.current_owner_subject,
            "owner_device_id": status.descriptor.signer_device_id,
        }
    finally:
        link.Clear()


def create_invitation(
    session: DeviceSession,
    project_id: str,
    invitation_id: str,
    *,
    role: str,
    expires_at: int,
) -> dict[str, str]:
    session.require_approved()
    if (
        role not in {"viewer", "editor"}
        or not int(time.time()) < expires_at <= int(time.time()) + 7 * 86400
    ):
        raise E2eeError("invalid_invitation")
    if re.fullmatch(r"[A-Za-z0-9_-]{1,128}", invitation_id) is None:
        raise E2eeError("invalid_invitation")
    namespace = "invitation:create:" + project_id + ":" + invitation_id
    pending = session.pending_documents(namespace)
    if pending is None:
        bundle = session.read_bundle(project_id, view="by_ids").bundle
        session.open_bundle(bundle)
        secret = session.random_bytes(32)
        descriptor = app.InvitationDescriptor(
            invitation_id=invitation_id,
            project_id=project_id,
            role=role,
            expires_at=expires_at,
            secret_digest=session.digest(secret),
            inviter_root_digest=session.trusted_root_digest(),
            proof_public_key=session.possession_proof(secret, b"").public_key,
        )
        link = app.InvitationLink(
            invitation_id=invitation_id,
            project_id=project_id,
            secret=secret,
            inviter_root_digest=descriptor.inviter_root_digest,
            descriptor_digest=session.digest(descriptor.SerializeToString()),
        )
        try:
            pending = session.prepare_documents(
                namespace,
                project_id,
                [descriptor.SerializeToString()],
                bundle,
                local=link.SerializeToString(),
            )
        finally:
            link.Clear()
    documents, local = pending
    link = app.InvitationLink.FromString(local)
    try:
        descriptor = app.InvitationDescriptor.FromString(documents[0].body)
        if descriptor.role != role or descriptor.expires_at != expires_at:
            raise E2eeError("invitation_publication_pending")
        response = session.service.create_crypto_invitation(
            app.InvitationRequest(
                project_id=project_id,
                invitation_id=invitation_id,
                descriptor=documents[0],
            )
        )
        _verify_invitation(
            session, response, project_id, link, release_namespace=namespace
        )
        return {
            "project_id": project_id,
            "invitation_id": invitation_id,
            "link": f"{session.origin.rstrip('/')}/invitations/{invitation_id}#invite=ainv2_{encode(link.SerializeToString())}",
        }
    finally:
        link.Clear()


def request_invitation(
    session: DeviceSession,
    project_id: str,
    invitation: str,
    *,
    invitation_id: str | None,
) -> dict[str, str]:
    session.require_approved()
    link = _invitation_token(session.origin, invitation, invitation_id)
    try:
        response = _read_invitation(session, project_id, link.invitation_id)
        _verify_invitation(session, response, project_id, link)
        namespace = "invitation:request:" + project_id + ":" + link.invitation_id
        pending = session.pending_documents(namespace)
        if pending is None:
            receiver_digest = _receiver_digest(
                session, response.bundle, session.subject
            )
            challenge = app.InvitationJoinChallenge(
                invitation_id=link.invitation_id,
                subject=session.subject,
                descriptor_digest=link.descriptor_digest,
                receiver_digest=receiver_digest,
            ).SerializeToString()
            binding = app.InvitationJoinBinding(
                invitation_id=link.invitation_id,
                subject=session.subject,
                descriptor_digest=link.descriptor_digest,
                receiver_digest=receiver_digest,
                challenge_bytes=challenge,
                proof=session.possession_proof(link.secret, challenge),
            )
            pending = session.prepare_documents(
                namespace, project_id, [binding.SerializeToString()], response.bundle
            )
        documents, _ = pending
        result = session.service.request_crypto_invitation(
            app.InvitationJoinRequest(
                project_id=project_id,
                invitation_id=link.invitation_id,
                request=documents[0],
            )
        )
        matching = [
            item
            for item in result.invitations
            if item.project_id == project_id
            and item.invitation_id == link.invitation_id
        ]
        if len(matching) != 1 or documents[0] not in matching[0].requests:
            raise E2eeError("invalid_response")
        result.bundle.documents.add(signed=documents[0])
        session.verify_documents(result.bundle, release_namespaces=[namespace])
        return {
            "project_id": project_id,
            "invitation_id": link.invitation_id,
            "state": "pending",
        }
    finally:
        link.Clear()


def approve_invitation(
    session: DeviceSession, project_id: str, invitation_id: str, subject: str
) -> dict[str, str]:
    session.require_approved()
    pending = session.pending_command(project_id)
    if pending is not None:
        body = crypto.MutationBody.FromString(pending.body)
        binding = app.RecordMutationBinding.FromString(body.application_binding)
        if (
            binding.invitation.invitation_id != invitation_id
            or binding.membership.subject != subject
        ):
            raise E2eeError("record_publication_pending")
    else:
        response = _read_invitation(session, project_id, invitation_id)
        status, descriptor = _status(response, project_id, invitation_id)
        if status.current_owner_subject != session.subject:
            raise E2eeError("owner_required")
        root = session.trusted_root_digest()
        response.bundle.documents.add(
            signed=status.descriptor, expected_root_digest=root
        )
        descriptor_digest = session.digest(status.descriptor.body)
        selected = []
        for request in status.requests:
            try:
                join = app.InvitationJoinBinding.FromString(request.body)
            except DecodeError:
                raise E2eeError("invalid_response") from None
            if join.subject != subject:
                continue
            challenge = app.InvitationJoinChallenge(
                invitation_id=invitation_id,
                subject=subject,
                descriptor_digest=descriptor_digest,
                receiver_digest=join.receiver_digest,
            ).SerializeToString()
            if (
                join.invitation_id != invitation_id
                or join.descriptor_digest != descriptor_digest
                or join.challenge_bytes != challenge
                or join.proof.challenge != challenge
                or join.proof.public_key != descriptor.proof_public_key
            ):
                raise E2eeError("invitation_binding_mismatch")
            response.bundle.documents.add(signed=request)
            response.bundle.proofs.add().CopyFrom(join.proof)
            selected.append(request)
        if len(selected) != 1:
            raise E2eeError("invitation_request_missing")
        session.verify_documents(response.bundle)
        join = app.InvitationJoinBinding.FromString(selected[0].body)
        if join.receiver_digest != _receiver_digest(session, response.bundle, subject):
            raise E2eeError("invitation_receiver_changed")
        identities = [
            crypto.IdentityStatement.FromString(identity.statement.body)
            for identity in response.bundle.identity_statements
        ]
        if not any(
            identity.subject == subject
            and any(
                device.id == selected[0].signer_device_id and not device.revoked
                for device in identity.devices
            )
            for identity in identities
        ):
            raise E2eeError("invitation_binding_mismatch")
        project = session.project(project_id)
        recipients = [
            member for member in status.applicants if member.subject == subject
        ]
        if len(recipients) != 1:
            raise E2eeError("invitation_recipient_missing")
        recipient = recipients[0]
        binding = app.RecordMutationBinding(
            project_policy=app.ProjectPolicyBinding(
                project_id=project_id,
                group_id=project.group_id,
                shared=project.shared,
                current_protection_key=project.protection_key,
                expected_distribution_revision=project.distribution_revision,
            ),
            invitation=app.InvitationBinding(
                invitation_id=invitation_id,
                expires_at=descriptor.expires_at,
                secret_digest=descriptor.secret_digest,
                inviter_root_digest=descriptor.inviter_root_digest,
                descriptor_digest=descriptor_digest,
            ),
            membership=app.MembershipBinding(
                subject=subject,
                expected_revision=recipient.revision,
                role=descriptor.role,
            ),
        )
        pending = session.prepare(
            project_id,
            deliveries=[
                crypto.DeliveryMutation(
                    target=project.protection_key, recipient=recipient.receiver
                )
            ],
            binding=binding.SerializeToString(),
            bundle=response.bundle,
        )
    request = app.InvitationApproval(
        project_id=project_id,
        invitation_id=invitation_id,
        subject=subject,
        mutation=app.CommitCryptoRequest(project_id=project_id, command=pending),
    )
    session.commit(
        project_id,
        mutation=request.mutation,
        send=lambda: session.service.approve_crypto_invitation(request),
    )
    return {
        "project_id": project_id,
        "invitation_id": invitation_id,
        "subject": subject,
        "state": "joined",
    }


def revoke_invitation(
    session: DeviceSession, project_id: str, invitation_id: str
) -> dict[str, str]:
    session.require_approved()
    namespace = "invitation:revoke:" + project_id + ":" + invitation_id
    pending = session.pending_documents(namespace)
    if pending is None:
        current = _read_invitation(session, project_id, invitation_id)
        status, _ = _status(current, project_id, invitation_id)
        if status.current_owner_subject != session.subject:
            raise E2eeError("owner_required")
        current.bundle.documents.add(
            signed=status.descriptor, expected_root_digest=session.trusted_root_digest()
        )
        session.verify_documents(current.bundle)
        pending = session.prepare_documents(
            namespace, project_id, [status.descriptor.body], current.bundle
        )
    documents, _ = pending
    response = session.service.revoke_crypto_invitation(
        app.InvitationRequest(
            project_id=project_id, invitation_id=invitation_id, descriptor=documents[0]
        )
    )
    if not any(
        item.project_id == project_id
        and item.invitation_id == invitation_id
        and item.state == "revoked"
        for item in response.invitations
    ):
        raise E2eeError("invalid_response")
    session.open_bundle(response.bundle, release_namespaces=[namespace])
    return {
        "project_id": project_id,
        "invitation_id": invitation_id,
        "state": "revoked",
    }
