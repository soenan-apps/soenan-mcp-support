from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ._crypto import E2eeError
from ._owner_envelopes import OWNER_KEY_PROOF
from ._owner_protocol import SignedEvidence
from ._project_identity import committed_creator, has_committed_creator
from ._trust import (
    _IdentityBoundEvidence, _RootIdentity, _ScopedEvidence, _TrustPathUnavailable, public_device,
)

if TYPE_CHECKING:
    from ._participants import ScopeParticipants


def organization_anchor(
    participants: ScopeParticipants,
    scope: str,
    subject: str,
    visiting: frozenset[str],
) -> _RootIdentity | None:
    from ._participants import _device, _fields

    session, trust = participants.session, participants.session.trust
    owner = session._scope_owner(scope)
    own_head = trust._confirmed_head(session.subject)
    if own_head is None:
        raise _TrustPathUnavailable()
    roots: dict[str, _RootIdentity] = {session.subject: own_head}
    own_lookup = session._current_device_lookup(None)

    def pin(root: _RootIdentity) -> None:
        session._check_scope(scope, owner)
        trust.pin_scope_recovery(scope, root.subject, root.document())

    def resolve(selected: str, active: frozenset[str]) -> _RootIdentity | None:
        if selected in roots:
            return roots[selected]
        visit = f"organization:{scope}:{selected}"
        if visit in active:
            return None
        active = active | {visit}
        for command in [*trust._endorsements, *session.owner_access.organization_anchors(scope)]:
            body = participants._body(command)
            if body.get("scope_id") != scope:
                continue
            _fields(body, {"scope_id", "trusted_device", "recovery_root"})
            device = _device(body["trusted_device"])
            if device["account_subject"] != selected:
                continue
            root = participants._root(body["recovery_root"], selected)
            issuer = trust._lookup_device(command["device_id"], own_lookup)
            if issuer["account_subject"] != session.subject:
                raise E2eeError("recovery_subject_mismatch")
            try:
                participants._historical_self_device(issuer, own_head)
            except _TrustPathUnavailable:
                continue
            session.crypto.verify(issuer["signing_public_key"], "peer_trust", command)
            pin(root)
            roots[selected] = root
            return root
        for proof in participants._load(scope, selected):
            if proof.get("kind") != "organization":
                continue
            evidence = participants._evidence(scope, proof)
            anchor = resolve(evidence.creator_root.subject, active)
            if anchor is None:
                continue
            try:
                admission = session.owner_access.current.historical_organization_admission(
                    scope, SignedEvidence.parse(proof["approval_command"]), evidence.approver, anchor,
                )
            except _TrustPathUnavailable:
                continue
            pin(admission.approver_root)
            pin(admission.root)
            roots[selected] = admission.root
            return admission.root
        return None

    root = resolve(subject, visiting)
    if root is None:
        return None
    session._check_scope(scope, owner)
    return root


def _organization_history(
    participants: ScopeParticipants,
    scope: str,
    subject: str,
    lookup: Callable[[str], Mapping[str, Any]],
    recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    verify_target: Callable[[_ScopedEvidence, Mapping[str, Any]], None],
) -> bool:
    from ._participants import _device, _fields

    session, trust = participants.session, participants.session.trust
    metadata = session.scope_metadata(scope)
    organization = metadata.get("owner_org")
    if not isinstance(organization, str) or not organization or organization == scope:
        return False
    owner = session._scope_owner(scope)
    pages: dict[str, list[dict[str, Any]]] = {}
    context: dict[str, Any] | None = None

    def load(selected: str) -> list[dict[str, Any]]:
        nonlocal context
        if selected in pages:
            return pages[selected]
        proofs = []
        after = None
        while True:
            parameters = {
                "scope_id": scope, "source_scope_id": organization,
                "account_subject": selected, "limit": 256,
            }
            if after is not None:
                parameters["after_request_id"] = after
            page = session.call("e2eeGetScopeParticipantProofs", **parameters)
            session._check_scope(scope, owner)
            source = _fields(page.get("source"), {
                "scope_id", "links", "owner_statements", "project_command", "org_command",
            })
            if source["scope_id"] != organization:
                raise E2eeError("participant_scope_mismatch")
            if context is None:
                context = source
            elif context != source:
                raise E2eeError("participant_source_changed")
            values = page["proofs"]
            if not isinstance(values, list):
                raise E2eeError("invalid_participant_proof")
            previous = after
            for proof in values:
                if (not isinstance(proof, dict) or proof.get("scope_id") != organization
                        or proof.get("account_subject") != selected
                        or not isinstance(proof.get("request_id"), str)
                        or (previous is not None and proof["request_id"] <= previous)):
                    raise E2eeError("participant_scope_mismatch")
                previous = proof["request_id"]
            proofs.extend(values)
            after = page.get("next_after")
            if after is None:
                break
            if not values or after != previous:
                raise E2eeError("participant_cursor_mismatch")
        pages[selected] = proofs
        return proofs

    try:
        load(subject)
    except E2eeError as error:
        if error.code == "not_found":
            return False
        raise
    if context is None:
        raise E2eeError("invalid_participant_proof")
    source_context = context
    staged = _ScopedEvidence(scope)
    introducers: set[str] = set()
    members: set[str] = set()

    def seed(device: Mapping[str, Any], root: _RootIdentity) -> None:
        trust._pin_verified_device(scope, device, authority=staged)
        trust._pin_verified_recovery(scope, root.subject, root.document(), staged)


    def introduction_issuer(device: Mapping[str, Any]) -> bool:
        selected = device["account_subject"]
        if selected != session.subject and not participants._anchor_owner(
            scope, selected, frozenset(), lookup, recovery_lookup, allow_committed=False,
        ):
            return False
        if selected == session.subject:
            roots = [
                _RootIdentity.parse(trust.origin, selected, root)
                for root in trust._state["recovery"].values()
                if root["account_subject"] == selected
            ]
            head = trust._confirmed_head(selected)
            if head is not None:
                roots.append(head)
            material_lookup = session._current_device_lookup(None)
            root_lookup = lambda identifier: session._recovery_material(None, identifier)
        else:
            roots = [
                _RootIdentity.parse(trust.origin, selected, root)
                for (key_scope, _), root in trust._scope_roots.items()
                if key_scope == scope and root["account_subject"] == selected
            ]
            material_lookup, root_lookup = lookup, recovery_lookup
        for root in roots:
            trust._pin_verified_recovery(scope, selected, root.document(), staged)
        material = trust._lookup_device(device["device_id"], material_lookup)
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        trust._verify_device(
            material, material_lookup, frozenset(), root_lookup, scope, staged,
        )
        return True

    def verify_device(device: Mapping[str, Any]) -> None:
        material = trust._lookup_device(device["device_id"], lookup)
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        trust._verify_device(
            material, lookup, frozenset(), recovery_lookup, scope, staged,
        )

    def admit(selected: str) -> bool:
        admitted = False
        for proof in load(selected):
            if proof.get("kind") != "organization":
                continue
            evidence = participants._evidence(organization, proof)
            if evidence.creator_root.subject not in introducers:
                continue
            try:
                verify_device(evidence.approver)
            except _TrustPathUnavailable:
                continue
            seed(evidence.creator, evidence.creator_root)
            seed(evidence.device, evidence.root)
            members.add(selected)
            admitted = True
        return admitted

    def admit_initializer(selected: str) -> bool:
        if selected not in introducers:
            return False
        command = source_context["org_command"]
        body = _fields(participants._body(command), {"scope_id", "key_epoch", "envelopes"}
            | ({"owner_authority"} if "owner_authority" in participants._body(command) else set())
            | ({"owner_key_proof"} if "owner_key_proof" in participants._body(command) else set()))
        if (body["scope_id"] != organization or type(body["key_epoch"]) is not int
                or body["key_epoch"] != 1):
            raise E2eeError("participant_scope_mismatch")
        creator = trust._lookup_device(command["device_id"], lookup)
        if creator["account_subject"] != selected:
            return False
        verify_device(creator)
        session.crypto.verify(creator["signing_public_key"], "organization_create", command)
        members.add(selected)
        return True

    for command in [*trust._endorsements, *session.owner_access.organization_anchors(organization)]:
        body = participants._body(command)
        if body.get("scope_id") != organization:
            continue
        _fields(body, {"scope_id", "trusted_device", "recovery_root"})
        creator = _device(body["trusted_device"])
        root = participants._root(body["recovery_root"], creator["account_subject"])
        own_lookup = session._current_device_lookup(None)
        own_recovery = lambda identifier: session._recovery_material(None, identifier)
        issuer = trust._lookup_device(command["device_id"], own_lookup)
        if issuer["account_subject"] != session.subject:
            raise E2eeError("recovery_subject_mismatch")
        trust._verify_device(issuer, own_lookup, frozenset(), own_recovery, None)
        session.crypto.verify(issuer["signing_public_key"], "peer_trust", command)
        seed(creator, root)
        introducers.add(root.subject)
    for command in source_context["owner_statements"]:
        body = _fields(participants._body(command), {"scope_id", "trusted_device", "recovery_root"})
        if body["scope_id"] != organization:
            raise E2eeError("participant_scope_mismatch")
        issuer = trust._lookup_device(command["device_id"], lookup)
        try:
            if not introduction_issuer(issuer):
                continue
        except _TrustPathUnavailable:
            continue
        session.crypto.verify(issuer["signing_public_key"], "peer_trust", command)
        creator = _device(body["trusted_device"])
        root = participants._root(body["recovery_root"], creator["account_subject"])
        seed(creator, root)
        introducers.add(root.subject)
    if not introducers or (
        subject not in members and not admit(subject) and not admit_initializer(subject)
    ):
        return False
    session._check_scope(scope, owner)
    verify_target(staged, source_context)
    session._check_scope(scope, owner)
    return True


def verify_source(
    participants: ScopeParticipants,
    scope: str,
    subject: str,
    lookup: Callable[[str], Mapping[str, Any]],
    recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    verify_target: Callable[[_ScopedEvidence, Mapping[str, Any]], None],
    *,
    key_epoch: int | None = None,
    envelope: Mapping[str, Any] | None = None,
) -> bool:
    from ._participants import _fields

    session, trust = participants.session, participants.session.trust

    def verify(staged: _ScopedEvidence, context: Mapping[str, Any]) -> None:
        organization = context["scope_id"]
        creation = context["project_command"]
        body = _fields(participants._body(creation), {
            "project_id", "owner_org", "participation_policy", "envelopes", "records",
        } | ({"owner_authority"} if "owner_authority" in participants._body(creation) else set())
          | ({"owner_key_proof"} if "owner_key_proof" in participants._body(creation) else set()))
        if (body["project_id"] != scope or body["owner_org"] != organization
                or body["participation_policy"] not in {"private", "organization"}
                or not isinstance(body["envelopes"], list)
                or not isinstance(context["links"], list)):
            raise _TrustPathUnavailable()
        creator = trust._lookup_device(creation["device_id"], lookup)
        creator_subject = creator["account_subject"]
        if not participants._anchor_owner(
            scope, creator_subject, frozenset(), lookup, recovery_lookup,
        ):
            raise _TrustPathUnavailable()
        participants._owner_signer(scope, creator, frozenset(), lookup, recovery_lookup)
        session.crypto.verify(creator["signing_public_key"], "project_create", creation)
        epoch = key_epoch if key_epoch is not None else (
            envelope["key_epoch"] if envelope is not None
            else session.scope_metadata(scope)["key_epoch"]
        )
        if type(epoch) is not int or epoch <= 0:
            raise E2eeError("invalid_envelope")
        owner_shared = False
        sharing = [
            {**value, "signed_command": creation} for value in body["envelopes"]
            if isinstance(value, dict) and value.get("recipient_kind") == "organization"
            and value.get("recipient_id") == organization
        ] + context["links"]
        for link in sharing:
            signed, operation = participants._organization_envelope_command(scope, organization, link)
            if link["key_epoch"] > epoch:
                continue
            issuer = trust._lookup_device(signed["device_id"], lookup)
            if issuer["account_subject"] != creator_subject:
                continue
            try:
                participants._owner_signer(scope, issuer, frozenset(), lookup, recovery_lookup)
            except _TrustPathUnavailable:
                continue
            session.crypto.verify(issuer["signing_public_key"], operation, signed)
            owner_shared = True
            break
        if not owner_shared:
            raise _TrustPathUnavailable()
        if envelope is not None and envelope.get("recipient_kind") == "organization":
            selected = dict(envelope)
        else:
            values = session.call(
                "e2eeGetEnvelopes", scope_id=scope, epoch=epoch,
                recipient_id=organization, recipient_kind="organization",
            )["envelopes"]
            if len(values) != 1:
                raise _TrustPathUnavailable()
            selected = values[0]
        if selected.get("key_epoch") != epoch:
            raise E2eeError("participant_envelope_mismatch")
        signed, operation = participants._organization_envelope_command(
            scope, organization, selected,
        )
        sender = trust._lookup_device(signed["device_id"], lookup)
        session.crypto.verify(sender["signing_public_key"], operation, signed)
        if operation in {"owner_envelopes_save", "owner_rotate_scope"} or participants._body(signed).get("owner_key_proof") == OWNER_KEY_PROOF:
            session.owner_access.envelopes.verify(scope, epoch, signed, operation)
            verify_target(staged, context)
            return

        def verify_sender(evidence: _ScopedEvidence, source: Mapping[str, Any]) -> None:
            if source != context:
                raise E2eeError("participant_source_changed")
            trust._verify_device(sender, lookup, frozenset(), recovery_lookup, scope, evidence)

        try:
            trust._verify_device(sender, lookup, frozenset(), recovery_lookup, scope, staged)
        except _TrustPathUnavailable:
            try:
                organization_sender = _organization_history(
                    participants, scope, sender["account_subject"], lookup, recovery_lookup, verify_sender,
                )
            except _TrustPathUnavailable:
                organization_sender = False
            if not organization_sender:
                invited = False
                for proof in participants._load(scope, sender["account_subject"]):
                    if proof.get("kind") != "invitation":
                        continue
                    participation = participants._evidence(scope, proof)
                    try:
                        if not participants._authority(participation, frozenset(), lookup, recovery_lookup):
                            continue
                    except _TrustPathUnavailable:
                        continue
                    invitation = _ScopedEvidence(scope)
                    invitation.pin_device(participation.device)
                    invitation.pin_root(participation.root)
                    try:
                        trust._verify_device(
                            sender, lookup, frozenset(), recovery_lookup, scope, invitation,
                        )
                    except _TrustPathUnavailable:
                        continue
                    invited = True
                    break
                if not invited:
                    raise _TrustPathUnavailable()
        verify_target(staged, context)

    return _organization_history(
        participants, scope, subject, lookup, recovery_lookup, verify,
    )


@dataclass(frozen=True)
class _CommittedCreator:
    device: dict[str, Any]
    root: _RootIdentity
    command: SignedEvidence

def committed_owner(
    participants: ScopeParticipants,
    scope: str,
    subject: str,
    lookup: Callable[[str], Mapping[str, Any]],
    recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
) -> _CommittedCreator | None:
    from ._participants import _fields
    if not has_committed_creator(scope):
        return None

    session, trust = participants.session, participants.session.trust
    anchor = None

    def verify(staged: _ScopedEvidence, context: Mapping[str, Any]) -> None:
        nonlocal anchor
        command = context["project_command"]
        body = _fields(participants._body(command), {
            "project_id", "owner_org", "participation_policy", "envelopes", "records",
        } | ({"owner_authority"} if "owner_authority" in participants._body(command) else set())
          | ({"owner_key_proof"} if "owner_key_proof" in participants._body(command) else set()))
        if (body["project_id"] != scope or body["owner_org"] != context["scope_id"]
                or body["participation_policy"] not in {"private", "organization"}):
            raise E2eeError("participant_scope_mismatch")
        creator = trust._lookup_device(command["device_id"], lookup)
        if creator["account_subject"] != subject or not committed_creator(
            scope, creator["signing_public_key"],
        ):
            return
        original = SignedEvidence.parse(command)
        root = session.owner_access.verifier.creation_root(context["scope_id"], original, creator)
        if staged.roots.get(root.identifier) != root.document():
            recovery = recovery_lookup(root.identifier) if recovery_lookup is not None else None
            if recovery is None:
                raise _TrustPathUnavailable()
            trust._verify_recovery(subject, recovery, lookup, frozenset(), recovery_lookup, scope, staged)
        session.owner_access.assert_project_creator(scope, root, device=creator)
        identity = _IdentityBoundEvidence(scope)
        identity.pin_root(root)
        try:
            trust._verify_device(creator, lookup, frozenset(), recovery_lookup, scope, identity)
        except _TrustPathUnavailable:
            return
        session.crypto.verify(creator["signing_public_key"], "project_create", command)
        anchor = _CommittedCreator(public_device(creator), root, original)

    if not _organization_history(participants, scope, subject, lookup, recovery_lookup, verify):
        return None
    return anchor
