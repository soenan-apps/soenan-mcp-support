from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from ._crypto import E2eeError, decode, wipe
from ._trust import _ScopedEvidence, _TrustPathUnavailable, public_device

if TYPE_CHECKING:
    from ._session import DeviceSession


def _invitation_token(origin: str, invitation: str, identifier: str | None) -> tuple[str, str]:
    if not isinstance(invitation, str) or any(ord(value) < 32 or ord(value) == 127 for value in invitation):
        raise E2eeError("invalid_invitation_link")
    if invitation.startswith("ainv1_"):
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
        if invitation != f"{origin.rstrip('/')}/invitations/{identifier}#invite={token}":
            raise E2eeError("invalid_invitation_link")
    if (not isinstance(identifier, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", identifier) is None
            or re.fullmatch(r"ainv1_[A-Za-z0-9_-]{43}", token) is None):
        raise E2eeError("invalid_invitation_link")
    secret = decode(token[6:])
    try:
        if len(secret) != 32:
            raise E2eeError("invalid_invitation_link")
    finally:
        wipe(secret)
    return identifier, token[6:]


def confirm_project_owner(
    session: DeviceSession, project_id: str, invitation: str, *, invitation_id: str | None,
) -> dict[str, str]:
    session.require_approved()
    invitation_id, secret = _invitation_token(session.trust.origin, invitation, invitation_id)
    binding = session.crypto.execute({"op": "derive_invitation_signing_key", "secret": secret})
    try:
        info = session.call("e2eeGetInvitation", invitation_id=invitation_id)
        participants, trust = session._participants, session.trust
        body = participants._invitation(info["signed_command"], project_id, invitation_id)
        if binding["signing_public_key"] != body["binding_public_key"] or any(
            info.get(field) != body[field] for field in (
                "invitation_id", "project_id", "role", "expires_at",
                "binding_public_key", "binding_signature",
            )
        ):
            raise E2eeError("invitation_binding_mismatch")
        metadata = session.scope_metadata(project_id, refresh=True)
        if metadata.get("owner_org") == project_id:
            raise E2eeError("project_required")
        owner = session._scope_owner(project_id)
        creator = body["creator_device"]
        if public_device(info["creator_device"]) != creator:
            raise E2eeError("device_key_changed")
        root = participants._root(body["creator_recovery"], creator["account_subject"])
        lookup = session._current_device_lookup(project_id)
        try:
            material = trust._lookup_device(creator["device_id"], lookup)
            if public_device(material) != creator:
                raise E2eeError("device_key_changed")
            qualified = session.owner_access.qualify_current_creator(project_id, material, root, root)
            session.owner_access.assert_project_creator(project_id, root, device=creator, qualification=qualified)
            staged = _ScopedEvidence(project_id)
            staged.pin_root(root)
            trust.require_current_issuer(
                material, None if creator["account_subject"] == session.subject else project_id,
            )
            trust._verify_device(
                material, lookup, frozenset(),
                lambda identifier: session._recovery_material(project_id, identifier),
                project_id, staged,
            )
        except _TrustPathUnavailable:
            raise E2eeError("owner_confirmation_fresh_invitation_required") from None
        session._check_scope(project_id, owner)
        try:
            session._record_scope_owner(project_id, creator, body["creator_recovery"], qualified)
        except E2eeError as error:
            if error.code == "revision_conflict":
                raise E2eeError("owner_confirmation_fresh_invitation_required") from None
            raise
        session._check_scope(project_id, owner)
        return {
            "project_id": project_id, "owner_subject": root.subject,
            "owner_device_id": creator["device_id"], "recovery_id": root.identifier,
        }
    finally:
        binding.clear()
