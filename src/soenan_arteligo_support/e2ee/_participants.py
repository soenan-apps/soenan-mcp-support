from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_protocol import authority_head
from ._owner_verifier import FrozenProjectOrigin
from ._trust import (
    _ProofAuthority, _RootIdentity, _ScopedEvidence,
    _TrustPathUnavailable, public_device,
)

if TYPE_CHECKING:
    from ._session import DeviceSession
    from ._owner_access import CurrentCreatorQualification


@dataclass(frozen=True)
class _Participation:
    scope: str
    subject: str
    creator: dict[str, Any]
    creator_root: _RootIdentity
    device: dict[str, Any]
    root: _RootIdentity
    approver: dict[str, Any]



@dataclass(frozen=True)
class _ProjectOwnerInviterIntroduction:
    scope: str
    root: _RootIdentity


def _fields(value: Any, expected: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise E2eeError("invalid_participant_proof")
    return value


def _bytes(value: Any, count: int) -> None:
    decoded = decode(value)
    try:
        if len(decoded) != count:
            raise E2eeError("invalid_participant_proof")
    finally:
        wipe(decoded)


def _device(value: Any) -> dict[str, Any]:
    document = _fields(value, {
        "device_id", "account_subject", "encryption_public_key", "signing_public_key", "state",
    })
    if document["state"] != "approved":
        raise E2eeError("invalid_participant_proof")
    immutable = public_device(document)
    _bytes(immutable["encryption_public_key"], 32)
    _bytes(immutable["signing_public_key"], 32)
    return immutable


class ScopeParticipants:
    def __init__(self, session: DeviceSession):
        self.session = session
        self._proofs: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def clear(self) -> None:
        self._proofs.clear()

    def forget_scope(self, scope: str) -> None:
        for key in list(self._proofs):
            if key[0] == scope:
                self._proofs.pop(key)

    def _root(self, value: Any, subject: str) -> _RootIdentity:
        document = _fields(value, {
            "recovery_id", "generation", "encryption_public_key", "signing_public_key",
        })
        return _RootIdentity.parse(self.session.trust.origin, subject, document)

    def _body(self, command: Any) -> dict[str, Any]:
        signed = _fields(command, {"device_id", "body_bytes", "signature"})
        if not isinstance(signed["device_id"], str) or not signed["device_id"]:
            raise E2eeError("invalid_participant_proof")
        _bytes(signed["signature"], 64)
        decoded = decode(signed["body_bytes"])
        try:
            body = json.loads(decoded)
        except (ValueError, TypeError):
            raise E2eeError("invalid_participant_proof") from None
        finally:
            wipe(decoded)
        if not isinstance(body, dict):
            raise E2eeError("invalid_participant_proof")
        return body

    def _binding(self, key: str, signature: str, fields: list[str]) -> None:
        self.session.crypto.execute({
            "op": "verify_bytes", "public_key": key,
            "bytes": encode("\n".join(fields).encode()), "signature": signature,
        })

    def _invitation(self, command: Any, scope: str, identifier: str) -> dict[str, Any]:
        body = _fields(self._body(command), {
            "invitation_id", "project_id", "role", "expires_at", "binding_public_key",
            "binding_signature", "creator_device", "creator_recovery",
        })
        creator = _device(body["creator_device"])
        self._root(body["creator_recovery"], creator["account_subject"])
        if (body["project_id"] != scope or body["invitation_id"] != identifier
                or command["device_id"] != creator["device_id"]
                or body["role"] not in {"editor", "viewer"}
                or type(body["expires_at"]) is not int or body["expires_at"] <= 0):
            raise E2eeError("participant_scope_mismatch")
        _bytes(body["binding_public_key"], 32)
        self.session.crypto.verify(creator["signing_public_key"], "invitation_create", command)
        self._binding(body["binding_public_key"], body["binding_signature"], [
            "arteligo-e2ee-invitation-owner-v1", identifier, creator["account_subject"],
            creator["device_id"], creator["encryption_public_key"], creator["signing_public_key"],
        ])
        return body

    def _organization_envelope_command(
        self, scope: str, organization: str, envelope: dict[str, Any],
    ) -> tuple[dict[str, Any], str]:
        fields = {
            "scope_id", "key_epoch", "recipient_id", "recipient_kind", "organization_epoch",
            "sender_device_id", "encapsulated_key", "ciphertext",
        }
        _fields(envelope, fields | {"signed_command"} | (
            {"operation"} if "operation" in envelope else set()
        ))
        if any(
            type(envelope[field]) is not int or not 1 <= envelope[field] <= 2**63 - 1
            for field in ("key_epoch", "organization_epoch")
        ):
            raise E2eeError("invalid_envelope")
        if (envelope["scope_id"] != scope or envelope["recipient_kind"] != "organization"
                or envelope["recipient_id"] != organization
                or self.session.scope_metadata(scope).get("owner_org") != organization):
            raise E2eeError("participant_scope_mismatch")
        command = envelope["signed_command"]
        body = self._body(command)
        if "project_id" in body:
            _fields(body, {
                "project_id", "owner_org", "participation_policy", "envelopes", "records",
            } | ({"owner_authority"} if "owner_authority" in body else set())
              | ({"owner_key_proof"} if "owner_key_proof" in body else set()))
            if (body["project_id"] != scope or body["owner_org"] != organization
                    or body["participation_policy"] != "organization" or envelope["key_epoch"] != 1):
                raise E2eeError("participant_scope_mismatch")
            operation = "project_create"
        elif "expected_epoch" in body:
            _fields(body, {"scope_id", "expected_epoch", "envelopes"} | (
                {"previous_key_ciphertext"} if "previous_key_ciphertext" in body else set()
            ) | ({"owner_authority"} if "owner_authority" in body else set()) | (
                {"owner_key_proof"} if "owner_key_proof" in body else set()
            ))
            if (body["scope_id"] != scope or type(body["expected_epoch"]) is not int
                    or body["expected_epoch"] + 1 != envelope["key_epoch"]):
                raise E2eeError("participant_scope_mismatch")
            operation = "rotate_scope"
        else:
            _fields(body, {"scope_id", "key_epoch", "envelopes"} | (
                {"owner_authority"} if "owner_authority" in body else set()
            ) | ({"owner_key_proof"} if "owner_key_proof" in body else set()))
            if (body["scope_id"] != scope or type(body["key_epoch"]) is not int
                    or body["key_epoch"] != envelope["key_epoch"]):
                raise E2eeError("participant_scope_mismatch")
            operation = "envelopes_save"
        if (command["device_id"] != envelope["sender_device_id"]
                or not isinstance(body["envelopes"], list)
                or sum(
                    isinstance(value, dict) and set(value) == fields
                    and type(value["key_epoch"]) is int
                    and type(value["organization_epoch"]) is int
                    and all(value[field] == envelope[field] for field in fields)
                    for value in body["envelopes"]
                ) != 1):
            raise E2eeError("participant_envelope_mismatch")
        selected_operation = envelope.get("operation", operation)
        if selected_operation in {"owner_envelopes_save", "owner_rotate_scope"}:
            if selected_operation != "owner_" + operation:
                raise E2eeError("invalid_owner_key_command")
            self.session.owner_access.envelopes.verify(
                scope, envelope["key_epoch"], command, selected_operation,
            )
            operation = selected_operation
        elif selected_operation != operation:
            raise E2eeError("invalid_envelope")
        return command, operation

    def organization_envelope_sender(
        self, scope: str, organization: str, envelope: dict[str, Any],
    ) -> dict[str, Any]:
        command, operation = self._organization_envelope_command(scope, organization, envelope)
        material = self.session._device_material(scope, command["device_id"])
        self.session.crypto.verify(material["signing_public_key"], operation, command)
        sender = self.session.device(
            scope, command["device_id"], key_epoch=envelope["key_epoch"], envelope=envelope,
        )
        if public_device(material) != sender:
            raise E2eeError("device_key_changed")
        return sender

    def _evidence(self, scope: str, proof: dict[str, Any]) -> _Participation:
        if proof.get("kind") == "organization":
            return self._organization(scope, proof)
        if proof.get("kind") != "invitation":
            raise E2eeError("invalid_participant_proof")
        _fields(proof, {
            "kind", "scope_id", "request_id", "account_subject", "invitation_command",
            "request_command", "approval_command", "approver_device",
        })
        request_command = proof["request_command"]
        request = _fields(self._body(request_command), {
            "request_id", "invitation_id", "project_id", "invitation_command",
            "account_subject", "device", "recovery", "binding_signature",
        })
        invitation_command = proof["invitation_command"]
        invitation = self._invitation(invitation_command, scope, request["invitation_id"])
        device = _device(request["device"])
        root = self._root(request["recovery"], request["account_subject"])
        if (proof["scope_id"] != scope or request["project_id"] != scope
                or not isinstance(request["request_id"], str) or not request["request_id"]
                or proof["request_id"] != request["request_id"]
                or proof["account_subject"] != request["account_subject"]
                or device["account_subject"] != request["account_subject"]
                or request_command["device_id"] != device["device_id"]
                or request["invitation_command"] != invitation_command):
            raise E2eeError("participant_request_mismatch")
        self.session.crypto.verify(device["signing_public_key"], "invitation_request", request_command)
        self._binding(invitation["binding_public_key"], request["binding_signature"], [
            "arteligo-e2ee-invitation-binding-v1", request["invitation_id"],
            request["account_subject"], device["device_id"], device["encryption_public_key"],
            device["signing_public_key"], root.identifier, root.encryption_key, root.signing_key,
        ])
        approval_command = proof["approval_command"]
        approval_body = self._body(approval_command)
        approval = _fields(approval_body, {
            "request_id", "request_command", "key_epoch", "envelopes",
        } | ({"owner_authority"} if "owner_authority" in approval_body else set())
          | ({"owner_key_proof"} if "owner_key_proof" in approval_body else set()))
        creator = _device(invitation["creator_device"])
        approver = proof["approver_device"]
        if (not isinstance(approver, dict)
                or not set(approver) <= {
                    "device_id", "account_subject", "encryption_public_key", "signing_public_key",
                    "state", "certificates",
                }):
            raise E2eeError("invalid_participant_proof")
        approver_identity = _device(public_device(approver))
        epoch = approval["key_epoch"]
        if (approval["request_id"] != request["request_id"]
                or approval["request_command"] != request_command
                or approval_command["device_id"] != approver_identity["device_id"]
                or approver_identity["account_subject"] != creator["account_subject"]
                or type(epoch) is not int or epoch <= 0
                or not isinstance(approval["envelopes"], list)):
            raise E2eeError("participant_approval_mismatch")
        self._envelopes(scope, approval, device, root, approver_identity)
        self.session.crypto.verify(
            approver_identity["signing_public_key"], "invitation_approve", approval_command,
        )
        return _Participation(
            scope, request["account_subject"], creator,
            self._root(invitation["creator_recovery"], creator["account_subject"]),
            device, root, approver,
        )

    def _envelopes(
        self, scope: str, approval: dict[str, Any], device: dict[str, Any],
        root: _RootIdentity, approver: dict[str, Any],
    ) -> None:
        recipients: set[str] = set()
        organization = self.session.scope_metadata(scope).get("owner_org")
        declared = authority_head(approval["owner_authority"], organization) if "owner_authority" in approval else None
        if any(isinstance(value, dict) and value.get("recipient_kind") == "owner" for value in approval["envelopes"]):
            if not organization or len(approval["envelopes"]) != 1:
                raise E2eeError("participant_envelope_mismatch")
            envelope = _fields(approval["envelopes"][0], {
                "scope_id", "key_epoch", "recipient_id", "recipient_kind", "sender_device_id",
                "owner_key_epoch", "owner_binding_digest", "encapsulated_key", "ciphertext",
            })
            _bytes(envelope["owner_binding_digest"], 32)
            selected = self.session.owner_access.account.selected(organization, envelope["owner_binding_digest"])
            head = selected.head
            if (head.owner_subject != device["account_subject"]
                    or (declared is not None and not selected.matches(declared))
                    or any(envelope[name] != value for name, value in {
                        "scope_id": scope, "key_epoch": approval["key_epoch"], "recipient_id": head.key_id,
                        "recipient_kind": "owner", "owner_key_epoch": head.key_epoch,
                        "owner_binding_digest": head.binding_digest, "sender_device_id": approver["device_id"],
                    }.items())):
                raise E2eeError("participant_envelope_mismatch")
            _bytes(envelope["encapsulated_key"], 32)
            _bytes(envelope["ciphertext"], 48)
            return
        if declared is not None and declared.owner_subject == device["account_subject"]:
            raise E2eeError("participant_envelope_mismatch")
        for value in approval["envelopes"]:
            envelope = _fields(value, {
                "scope_id", "key_epoch", "recipient_id", "recipient_kind", "sender_device_id",
                "encapsulated_key", "ciphertext",
            })
            kind, recipient = envelope["recipient_kind"], envelope["recipient_id"]
            if (envelope["scope_id"] != scope or envelope["key_epoch"] != approval["key_epoch"]
                    or envelope["sender_device_id"] != approver["device_id"]
                    or not isinstance(kind, str) or not isinstance(recipient, str)
                    or (kind, recipient) not in {
                        ("device", device["device_id"]), ("recovery", root.identifier),
                    } or kind in recipients):
                raise E2eeError("participant_envelope_mismatch")
            recipients.add(kind)
            _bytes(envelope["encapsulated_key"], 32)
            _bytes(envelope["ciphertext"], 48)
        if recipients != {"device", "recovery"}:
            raise E2eeError("participant_envelope_mismatch")

    def _organization(self, scope: str, proof: dict[str, Any]) -> _Participation:
        _fields(proof, {
            "kind", "scope_id", "request_id", "account_subject", "request_command",
            "approval_command", "approver_device",
        })
        request_command = proof["request_command"]
        request = _fields(self._body(request_command), {
            "scope_id", "request_id", "account_subject", "device", "recovery", "challenge",
        })
        device = _device(request["device"])
        root = self._root(request["recovery"], device["account_subject"])
        _bytes(request["challenge"], 32)
        if (request["scope_id"] != scope or proof["scope_id"] != scope
                or not isinstance(request["request_id"], str) or not request["request_id"]
                or proof["request_id"] != request["request_id"]
                or proof["account_subject"] != request["account_subject"]
                or request["account_subject"] != device["account_subject"]
                or request_command["device_id"] != device["device_id"]):
            raise E2eeError("participant_request_mismatch")
        self.session.crypto.verify(
            device["signing_public_key"], "organization_share_request", request_command,
        )
        approval_command = proof["approval_command"]
        approval_body = self._body(approval_command)
        approval = _fields(approval_body, {
            "scope_id", "key_epoch", "envelopes", "participation",
        } | ({"owner_authority"} if "owner_authority" in approval_body else set())
          | ({"owner_key_proof"} if "owner_key_proof" in approval_body else set())
          | ({"issuer_admission"} if "issuer_admission" in approval_body else set()))
        participation = _fields(approval["participation"], {"request_command", "approver_recovery"})
        approver = proof["approver_device"]
        if not isinstance(approver, dict):
            raise E2eeError("invalid_participant_proof")
        issuer = _device(public_device(approver))
        issuer_root = self._root(participation["approver_recovery"], issuer["account_subject"])
        if (approval["scope_id"] != scope
                or participation["request_command"] != request_command
                or approval_command["device_id"] != issuer["device_id"]
                or type(approval["key_epoch"]) is not int or approval["key_epoch"] <= 0
                or not isinstance(approval["envelopes"], list)):
            raise E2eeError("participant_approval_mismatch")
        self._envelopes(scope, approval, device, root, issuer)
        self.session.crypto.verify(issuer["signing_public_key"], "envelopes_save", approval_command)
        return _Participation(
            scope, request["account_subject"], issuer, issuer_root, device, root, approver,
        )

    def _load(self, scope: str, subject: str) -> list[dict[str, Any]]:
        key = (scope, subject)
        if key in self._proofs:
            return self._proofs[key]
        owner = self.session._scope_owner(scope)
        proofs = []
        after = None
        while True:
            parameters = {"scope_id": scope, "account_subject": subject, "limit": 256}
            if after is not None:
                parameters["after_request_id"] = after
            page = self.session.call("e2eeGetScopeParticipantProofs", **parameters)
            self.session._check_scope(scope, owner)
            values = page["proofs"]
            if not isinstance(values, list):
                raise E2eeError("invalid_participant_proof")
            previous = after
            for value in values:
                if (not isinstance(value, dict) or value.get("scope_id") != scope
                        or value.get("account_subject") != subject
                        or not isinstance(value.get("request_id"), str)
                        or (previous is not None and value["request_id"] <= previous)):
                    raise E2eeError("participant_scope_mismatch")
                previous = value["request_id"]
            proofs.extend(values)
            after = page.get("next_after")
            if after is None:
                break
            if not values or after != previous:
                raise E2eeError("participant_cursor_mismatch")
        if proofs:
            self._proofs[key] = proofs
        return proofs

    def project_owner_inviter_introductions(
        self,
        organization: str,
        scope: str,
    ) -> tuple[_ProjectOwnerInviterIntroduction, ...]:
        candidates = [
            self._evidence(scope, proof)
            for proof in self._load(scope, self.session.subject)
            if proof.get("kind") == "invitation"
        ]
        if not candidates:
            return ()
        identities = self.session.owner_access.current.current_root_identity_device_ids(
            organization,
            scope,
            tuple(evidence.device for evidence in candidates),
        )
        introductions = []
        roots = set()
        for evidence in candidates:
            if evidence.device["device_id"] not in identities:
                continue
            if (evidence.creator_root.subject != evidence.creator["account_subject"]
                    or evidence.creator_root.origin != self.session.trust.origin):
                raise E2eeError("participant_scope_mismatch")
            if evidence.creator_root not in roots:
                roots.add(evidence.creator_root)
                introductions.append(_ProjectOwnerInviterIntroduction(scope, evidence.creator_root))
        return tuple(introductions)

    def _owner_signer(
        self, scope: str, device: Mapping[str, Any], visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        *, authority: _ProofAuthority | _ScopedEvidence = _ProofAuthority.SCOPE_OWNER,
    ) -> None:
        trust = self.session.trust
        material = trust._lookup_device(device["device_id"], lookup)
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        trust._verify_device(
            material, lookup, frozenset(), recovery_lookup, scope, authority,
        )

    def _pin_creator(self, scope: str, device: Mapping[str, Any], root: _RootIdentity,
                     qualification: CurrentCreatorQualification | None = None) -> None:
        self.session.owner_access.assert_project_creator(scope, root, device=device, qualification=qualification)
        trust = self.session.trust
        trust.pin_scope_device(scope, device)
        trust.pin_scope_recovery(scope, root.subject, root.document())
        if qualification is not None:
            trust._confirm_head(root, scope, current_device=qualification.current.device)

    def _anchor_owner(
        self, scope: str, subject: str, visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        *, allow_committed: bool = True,
    ) -> bool:
        session, trust = self.session, self.session.trust
        original = session.owner_access.project_origin_constraint(scope)
        if isinstance(original, FrozenProjectOrigin) and original.creator["account_subject"] != subject:
            return False

        inherited = session.owner_access.project_owner_anchor(scope, subject)
        if inherited is not None:
            creator, root = inherited
            if creator["account_subject"] != subject:
                return False
            qualified = session.owner_access.assert_creator_evidence(scope, root, creator, independent=root)
            self._pin_creator(scope, creator, root, qualified)
            return True
        own_material = session._current_device_lookup(None)

        def own_recovery(identifier: str) -> Mapping[str, Any] | None:
            return session._recovery_material(None, identifier)

        for command in trust._endorsements:
            body = self._body(command)
            if body.get("scope_id") != scope:
                continue
            _fields(body, {"scope_id", "trusted_device", "recovery_root"})
            creator = _device(body["trusted_device"])
            if creator["account_subject"] != subject:
                continue
            root = self._root(body["recovery_root"], subject)
            issuer = trust._lookup_device(command["device_id"], own_material)
            if issuer["account_subject"] != session.subject:
                raise E2eeError("recovery_subject_mismatch")
            try:
                trust._verify_device(issuer, own_material, visiting, own_recovery, None)
            except _TrustPathUnavailable:
                continue
            session.crypto.verify(issuer["signing_public_key"], "peer_trust", command)
            qualified = session.owner_access.assert_creator_evidence(scope, root, creator, independent=root)
            self._pin_creator(scope, creator, root, qualified)
            return True
        for proof in self._load(scope, session.subject):
            if proof.get("kind") != "invitation":
                continue
            own = self._evidence(scope, proof)
            if own.creator["account_subject"] != subject:
                continue
            device = trust._lookup_device(own.device["device_id"], own_material)
            if public_device(device) != own.device:
                raise E2eeError("device_key_changed")
            try:
                trust._verify_device(device, own_material, visiting, own_recovery, None)
                qualified = session.owner_access.assert_creator_evidence(scope, own.creator_root, own.creator, independent=own.creator_root)
                staged = _ScopedEvidence(scope)
                trust._pin_verified_device(scope, own.creator, authority=staged)
                trust._pin_verified_recovery(scope, subject, own.creator_root.document(), staged)
                self._owner_signer(
                    scope, own.approver, visiting, lookup, recovery_lookup, authority=staged,
                )
            except _TrustPathUnavailable:
                continue
            session._check_current()
            self._pin_creator(scope, own.creator, own.creator_root, qualified)
            return True
        if allow_committed:
            from ._participant_sources import committed_owner

            anchor = committed_owner(self, scope, subject, lookup, recovery_lookup)
            if anchor is not None:
                self._pin_creator(scope, anchor.device, anchor.root)
                return True
        return False

    def _authority(
        self, evidence: _Participation, visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> bool:
        session, scope = self.session, evidence.scope
        trust = session.trust
        subject = evidence.creator["account_subject"]
        original = session.owner_access.project_origin_constraint(scope)
        if isinstance(original, FrozenProjectOrigin):
            session.owner_access._assert_creator_identity(original, evidence.creator_root, evidence.creator)
        if not self._anchor_owner(scope, subject, visiting, lookup, recovery_lookup):
            return False
        anchor = trust._confirmed_head(subject, scope) or session.owner_access.current.independent_root(scope, evidence.creator)
        qualified = session.owner_access.assert_creator_evidence(scope, evidence.creator_root, evidence.creator, independent=anchor)
        self._owner_signer(scope, evidence.creator, visiting, lookup, recovery_lookup)
        staged = _ScopedEvidence(scope)
        trust._pin_verified_device(scope, evidence.creator, authority=staged)
        trust._pin_verified_recovery(scope, subject, evidence.creator_root.document(), staged)
        self._owner_signer(
            scope, evidence.approver, visiting, lookup, recovery_lookup, authority=staged,
        )
        session._check_current()
        self._pin_creator(scope, evidence.creator, evidence.creator_root, qualified)
        return True

    def verify_device(
        self, scope: str, device: Mapping[str, Any], visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
        *,
        key_epoch: int | None = None,
        envelope: Mapping[str, Any] | None = None,
    ) -> bool:
        for proof in self._load(scope, device["account_subject"]):
            evidence = self._evidence(scope, proof)
            if evidence.device["device_id"] != device["device_id"]:
                continue
            if evidence.device != public_device(device):
                raise E2eeError("device_key_changed")
            try:
                if not self._authority(evidence, visiting, lookup, recovery_lookup):
                    continue
            except _TrustPathUnavailable:
                continue
            self.session.trust.pin_scope_device(scope, device)
            self.session.trust.pin_scope_recovery(scope, evidence.subject, evidence.root.document())
            return True
        if self._anchor_owner(scope, device["account_subject"], visiting, lookup, recovery_lookup):
            try:
                self._owner_signer(scope, device, visiting, lookup, recovery_lookup)
                return True
            except _TrustPathUnavailable:
                pass
        from ._participant_sources import verify_source

        fresh = self.session._current_device_lookup(scope)

        def verify_target(staged: _ScopedEvidence, context: Mapping[str, Any]) -> None:
            self.session.trust._verify_device(
                device, fresh, frozenset(), recovery_lookup, scope, staged,
            )

        return verify_source(
            self, scope, device["account_subject"], fresh, recovery_lookup, verify_target,
            key_epoch=key_epoch, envelope=envelope,
        )

    def verify_recovery(
        self, scope: str, recovery: Mapping[str, Any], visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> bool:
        identity = _RootIdentity.parse(
            self.session.trust.origin, recovery["account_subject"], recovery,
        )
        for proof in self._load(scope, identity.subject):
            evidence = self._evidence(scope, proof)
            if evidence.root.identifier != identity.identifier:
                continue
            if evidence.root != identity:
                raise E2eeError("recovery_key_changed")
            try:
                if not self._authority(evidence, visiting, lookup, recovery_lookup):
                    continue
            except _TrustPathUnavailable:
                continue
            self.session.trust.pin_scope_device(scope, evidence.device)
            self.session.trust.pin_scope_recovery(scope, identity.subject, recovery)
            return True
        if self._anchor_owner(scope, identity.subject, visiting, lookup, recovery_lookup):
            try:
                self.session.trust._verify_recovery(
                    identity.subject, recovery, lookup, frozenset(), recovery_lookup,
                    scope, _ProofAuthority.SCOPE_OWNER,
                )
                return True
            except _TrustPathUnavailable:
                pass
        return False

    def _historical_self_device(
        self, device: Mapping[str, Any], own_head: _RootIdentity,
    ) -> None:
        session, trust = self.session, self.session.trust
        evidence = _ScopedEvidence(None)
        evidence.pin_root(own_head)
        lookup = session._current_device_lookup(None)
        material = trust._lookup_device(device["device_id"], lookup)
        if public_device(material) != public_device(device):
            raise E2eeError("device_key_changed")
        trust._verify_device(
            material, lookup, frozenset(),
            lambda identifier: session._recovery_material(None, identifier), None, evidence,
        )

    def _historical_participant_approval(
        self, participation: _Participation, anchor: _RootIdentity,
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> CurrentCreatorQualification | None:
        scope = participation.scope
        qualified = self.session.owner_access.assert_creator_evidence(
            scope, participation.creator_root, participation.creator, independent=anchor,
        )
        evidence = _ScopedEvidence(scope)
        evidence.pin_root(anchor)
        self._owner_signer(
            scope, participation.creator, frozenset(), lookup, recovery_lookup, authority=evidence,
        )
        evidence.pin_root(participation.creator_root)
        self._owner_signer(
            scope, participation.approver, frozenset(), lookup, recovery_lookup, authority=evidence,
        )
        return qualified

    def _qualify_current_creator(self, scope: str, initial: _RootIdentity,
                                 qualification: CurrentCreatorQualification | None = None) -> CurrentCreatorQualification | None:
        session, trust = self.session, self.session.trust
        session.owner_access.assert_project_creator(scope, initial, qualification=qualification)
        subject = initial.subject
        owner = session._scope_owner(scope)
        anchor = trust._confirmed_head(subject, scope) or trust._confirmed_head(subject) or initial
        audience = session.call("e2eeGetRecipients", scope_id=scope)
        if audience.get("purpose") != "distribution":
            raise E2eeError("invalid_recipient_purpose")
        roots = [value for value in audience["recoveries"] if value["account_subject"] == subject]
        if len(roots) != 1:
            return None
        offered = roots[0]
        current = _RootIdentity.parse(trust.origin, subject, offered)
        trust._assert_head(current, anchor.document())
        for device in audience["devices"]:
            if device.get("account_subject") != subject or device.get("state") != "approved":
                continue
            try:
                qualified = session.owner_access.qualify_current_creator(scope, device, anchor, current)
            except E2eeError as error:
                if error.code not in {"owner_device_requalification_required", "device_revoked"}:
                    raise
                continue
            session._check_scope(scope, owner)
            trust._confirm_head(qualified.current.root, scope, current_device=qualified.current.device)
            return qualified
        return None

    def _current_owner_anchor(
        self, scope: str, subject: str, visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> _RootIdentity | None:
        session, trust = self.session, self.session.trust
        original = session.owner_access.project_origin_constraint(scope)
        if isinstance(original, FrozenProjectOrigin) and original.creator["account_subject"] != subject:
            return None
        own_head = trust._confirmed_head(session.subject)
        if own_head is None:
            raise _TrustPathUnavailable()
        for command in trust._endorsements:
            body = self._body(command)
            if body.get("scope_id") != scope:
                continue
            _fields(body, {"scope_id", "trusted_device", "recovery_root"})
            creator = _device(body["trusted_device"])
            if creator["account_subject"] != subject:
                continue
            initial = self._root(body["recovery_root"], subject)
            try:
                issuer = trust._lookup_device(
                    command["device_id"], lambda value: session._device_material(None, value)
                )
                if issuer["account_subject"] != session.subject:
                    raise E2eeError("recovery_subject_mismatch")
                self._historical_self_device(issuer, own_head)
                session.crypto.verify(issuer["signing_public_key"], "peer_trust", command)
                qualified = session.owner_access.assert_creator_evidence(scope, initial, creator, independent=initial)
                current = self._qualify_current_creator(scope, initial, qualified)
            except _TrustPathUnavailable:
                continue
            if current is not None:
                return current.current.root
        for proof in self._load(scope, session.subject):
            if proof.get("kind") != "invitation":
                continue
            own = self._evidence(scope, proof)
            if own.creator_root.subject != subject:
                continue
            try:
                self._historical_self_device(own.device, own_head)
                qualified = self._historical_participant_approval(
                    own, own.creator_root, lookup, recovery_lookup,
                )
                current = self._qualify_current_creator(scope, own.creator_root, qualified)
            except _TrustPathUnavailable:
                continue
            if current is not None:
                return current.current.root
        from ._participant_sources import committed_owner

        committed = committed_owner(self, scope, subject, lookup, recovery_lookup)
        if committed is not None:
            session.owner_access.assert_project_creator(scope, committed.root, device=committed.device)
            qualified = self._qualify_current_creator(scope, committed.root)
            return qualified.current.root if qualified is not None else None
        return None

    def current_anchor(
        self, scope: str, subject: str, visiting: frozenset[str],
        lookup: Callable[[str], Mapping[str, Any]],
        recovery_lookup: Callable[[str], Mapping[str, Any] | None] | None,
    ) -> _RootIdentity | None:
        if self.session.scope_metadata(scope).get("owner_org") == scope:
            from ._participant_sources import organization_anchor

            return organization_anchor(self, scope, subject, visiting)
        trust = self.session.trust
        for proof in self._load(scope, subject):
            evidence = self._evidence(scope, proof)
            initial = self._current_owner_anchor(
                scope, evidence.creator_root.subject, visiting, lookup, recovery_lookup,
            )
            if initial is None:
                continue
            anchor = trust._confirmed_head(initial.subject, scope) or initial
            try:
                self._historical_participant_approval(evidence, anchor, lookup, recovery_lookup)
            except _TrustPathUnavailable:
                continue
            self.session._check_current()
            return evidence.root
        return self._current_owner_anchor(scope, subject, visiting, lookup, recovery_lookup)
