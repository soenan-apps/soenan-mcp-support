from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable, Mapping

from arteligo_public_api_client.models.owner_authority_response import OwnerAuthorityResponse
from arteligo_public_api_client.models.owner_custody_evidence import OwnerCustodyEvidence
from arteligo_public_api_client.models.owner_custody_response import OwnerCustodyResponse
from arteligo_public_api_client.models.owner_transfer_decision import OwnerTransferDecision

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_authority import SelectedOwnerHead
from ._owner_projection import CertificateProjectionReference, CertificateSignatureProjection
from ._owner_protocol import gate_descriptor, object_value, parse_model

if TYPE_CHECKING:
    from ._session import DeviceSession


@dataclass(frozen=True)
class OperationProofContext:
    events: tuple[dict[str, Any], ...]
    event_bytes: tuple[bytes, ...]
    digest: str
    context: dict[str, Any] | None
    receipt: dict[str, Any] | None
    rejection: dict[str, Any] | None
    subjects: Mapping[str, dict[str, Any]]
    organizations: Mapping[str, dict[str, Any]]
    targets: tuple[dict[str, Any], ...]
    references: tuple[dict[str, Any], ...]
    offers: tuple[dict[str, Any], ...]
    gates: tuple[dict[str, Any], ...]
    scope_authorizations: tuple[dict[str, Any], ...]
    gate_slots: tuple[dict[str, Any], ...]

    @classmethod
    def parse(cls, session: DeviceSession, events: Iterable[dict[str, Any]],
              raw_events: Iterable[bytes]) -> OperationProofContext:
        values, encoded = tuple(events), tuple(raw_events)
        if len(values) != len(encoded):
            raise E2eeError("invalid_key_operation_proof")
        digest = hashlib.sha256()
        subjects: dict[str, dict[str, Any]] = {}
        organizations: dict[str, dict[str, Any]] = {}
        targets, references, offers, gates, authorizations, slots = [], [], [], [], [], []
        context = receipt = rejection = complete = None
        for sequence, event in enumerate(values):
            if (complete is not None or event.get("sequence") != sequence or type(event.get("sequence")) is not int
                    or len(event) != 2):
                raise E2eeError("invalid_key_operation_proof")
            raw = encoded[sequence]
            if json.loads(raw) != event:
                raise E2eeError("invalid_key_operation_proof")
            kind = next(name for name in event if name != "sequence")
            value = object_value(event[kind])
            if kind == "complete":
                if value.get("part_count") != sequence or value.get("payload_digest") != encode(digest.digest()):
                    raise E2eeError("invalid_key_operation_proof")
                complete = value
                continue
            digest.update(len(raw).to_bytes(8, "big"))
            digest.update(raw)
            if kind == "context" and context is None:
                context = value
            elif kind == "receipt" and receipt is None:
                receipt = value
            elif kind == "rejection" and rejection is None:
                if value.get("reason") not in {"preparation_expired", "state_changed", "access_denied", "invalid_request", "conflict"}:
                    raise E2eeError("invalid_key_operation_proof")
                rejection = value
            elif kind in {"subject", "organization"}:
                collection, key = (subjects, "account_subject") if kind == "subject" else (organizations, "organization_id")
                identifier = value[key]
                if value.get("outcome") not in {"available", "missing", "denied"}:
                    raise E2eeError("invalid_key_operation_proof")
                previous = collection.get(identifier)
                if previous is not None:
                    lists = {"revoked_device_ids"} if kind == "subject" else {"memberships", "candidates", "pending_transfers"}
                    if any(previous.get(name) != item for name, item in value.items() if name not in lists):
                        raise E2eeError("invalid_key_operation_proof")
                    collection[identifier] = {**value, **{name: [*previous[name], *value[name]] for name in lists}}
                else:
                    collection[identifier] = value
            elif kind == "target":
                targets.append(value)
            elif kind == "reference":
                references.append(value)
            elif kind == "gate_offer":
                offers.append(value)
            elif kind == "gate":
                gates.append(value)
            elif kind == "scope_authorization":
                target = object_value(value.get("target"))
                if (set(target) != {"actor_subject", "organization_id", "scope_id", "basis", "operation_class"}
                        or target["basis"] not in {"product_entitlement", "project_sponsorship"}
                        or target["operation_class"] not in {"interactive_read", "interactive_mutation"}):
                    raise E2eeError("invalid_key_operation_proof")
                authorizations.append(value)
            elif kind == "gate_slot_result":
                slots.append(value)
            else:
                raise E2eeError("invalid_key_operation_proof")
        if complete is None or sum(value is not None for value in (context, receipt, rejection)) != 1:
            raise E2eeError("incomplete_key_operation_stream")
        for collection, key in ((targets, "target"), (references, "reference"),
                                (authorizations, "target"), (slots, "slot")):
            seen = set()
            for value in collection:
                raw = session.crypto.canonical(value[key])
                try:
                    identity = bytes(raw)
                finally:
                    wipe(raw)
                if identity in seen or value.get("outcome") not in {"available", "missing", "denied"}:
                    raise E2eeError("invalid_key_operation_proof")
                seen.add(identity)
        for offer in offers:
            if not any(value["slot"] == offer.get("slot") and value["outcome"] == "available" for value in slots):
                raise E2eeError("invalid_key_operation_proof")
        return cls(values, encoded, complete["payload_digest"], context, receipt, rejection, subjects, organizations,
                   tuple(targets), tuple(references), tuple(offers), tuple(gates), tuple(authorizations), tuple(slots))

    @classmethod
    def from_wire(cls, session: DeviceSession, wire: str) -> OperationProofContext:
        raw = decode(wire)
        try:
            wrappers = json.loads(raw)
            if not isinstance(wrappers, list):
                raise E2eeError("invalid_key_operation_proof")
            events, encoded = [], []
            for wrapper in wrappers:
                if not isinstance(wrapper, dict) or set(wrapper) != {"event", "event_bytes"}:
                    raise E2eeError("invalid_key_operation_proof")
                event_bytes = decode(wrapper["event_bytes"])
                try:
                    encoded.append(bytes(event_bytes))
                finally:
                    wipe(event_bytes)
                events.append(object_value(wrapper["event"]))
            return cls.parse(session, events, encoded)
        except (ValueError, KeyError, TypeError):
            raise E2eeError("invalid_key_operation_proof") from None
        finally:
            wipe(raw)

    def require_identity(self, session: DeviceSession, operation_id: str,
                         preparation: OperationProofContext | None = None,
                         *, request_digest: str | None = None) -> None:
        identity = self.context if request_digest is None else self.receipt or self.rejection
        if (identity is None or identity.get("operation_id") != operation_id
                or identity.get("actor_subject") != session.subject
                or request_digest is not None and identity.get("request_digest") != request_digest):
            raise E2eeError("invalid_key_operation_proof")
        if preparation is not None and identity.get("preparation_digest") != preparation.digest:
            raise E2eeError("invalid_key_operation_proof")

    @staticmethod
    def _available(value: Mapping[str, Any], missing: str) -> None:
        if value.get("outcome") == "missing":
            raise E2eeError(missing)
        if value.get("outcome") != "available":
            raise E2eeError("access_denied")

    def subject(self, subject: str) -> dict[str, Any]:
        value = self.subjects.get(subject)
        if value is None:
            raise E2eeError("root_replacement_dependency_missing")
        self._available(value, "owner_custody_evidence_missing")
        return value

    def authority(self, organization: str) -> SelectedOwnerHead:
        value = self.organizations.get(organization)
        if value is None:
            raise E2eeError("root_replacement_dependency_missing")
        self._available(value, "owner_authority_unavailable")
        response = parse_model(OwnerAuthorityResponse.from_dict, value["authority"])
        return SelectedOwnerHead.parse(response, organization)

    def reference_outcome(self, kind: str, subject: str, organization: str | None, digest: str) -> dict[str, Any]:
        values = [value for value in self.references if value["reference"]["kind"] == kind
                  and value["reference"]["digest"] == digest
                  and (not subject or value["reference"]["account_subject"] == subject)
                  and (organization is None or value["reference"]["organization_id"] == organization)]
        if not values:
            raise E2eeError("root_replacement_dependency_missing")
        first = {name: value for name, value in values[0].items() if name != "reference"}
        if any({name: item for name, item in value.items() if name != "reference"} != first for value in values):
            raise E2eeError("invalid_key_operation_proof")
        return values[0]

    def reference(self, kind: str, subject: str, organization: str | None, digest: str) -> dict[str, Any]:
        value = self.reference_outcome(kind, subject, organization, digest)
        self._available(value, {"selected_binding": "owner_binding_not_selected",
            "transfer_decision": "owner_receipt_missing",
            "certificate_projection": "owner_certificate_projection_missing"}.get(kind, "owner_custody_evidence_missing"))
        return value

    def scope_authorized(self, subject: str, organization: str, scope: str, basis: str, operation_class: str) -> bool:
        target = {"actor_subject": subject, "organization_id": organization, "scope_id": scope,
                  "basis": basis, "operation_class": operation_class}
        value = next((value for value in self.scope_authorizations if value["target"] == target), None)
        if value is None or value["outcome"] == "missing":
            raise E2eeError("root_replacement_dependency_missing")
        return value["outcome"] == "available"

    def require_scope(self, subject: str, captured: Mapping[str, Any], operation_class: str) -> None:
        scope = captured["scope"]
        if not self.scope_authorized(subject, scope["owner_org"], scope["project_id"],
                                     captured["authorization_basis"], operation_class):
            raise E2eeError("access_denied")

    def gate_offer(self, organization: str, subject: str, candidate_id: str, proposed: bool) -> dict[str, Any] | None:
        values = [value for value in self.gate_slots if value["slot"]["organization_id"] == organization
                  and value["slot"]["candidate_subject"] == subject
                  and value["slot"]["proposed_candidate"] is proposed
                  and (proposed or value["slot"]["candidate_id"] == candidate_id)]
        if len(values) != 1 or values[0]["outcome"] == "missing":
            raise E2eeError("root_replacement_dependency_missing")
        if values[0]["outcome"] == "denied":
            return None
        offers = [offer for offer in self.offers if offer["slot"] == values[0]["slot"]]
        if len(offers) != 1:
            raise E2eeError("root_replacement_dependency_missing")
        return offers[0]

    def selected(self, organization: str, digest: str) -> SelectedOwnerHead:
        if self.organizations.get(organization, {}).get("outcome") == "available":
            current = self.authority(organization)
            if current.head.binding_digest == digest:
                return current
        value = self.reference("selected_binding", "", organization, digest)
        response = parse_model(OwnerAuthorityResponse.from_dict, value["selected_binding"])
        result = SelectedOwnerHead.parse(response, organization)
        if result.head.binding_digest != digest:
            raise E2eeError("owner_binding_mismatch")
        return result

    def witness(self, subject: str, digest: str) -> OwnerCustodyEvidence:
        latest = self.subjects.get(subject, {}).get("latest_root_transition")
        if latest is not None and latest.get("evidence_digest") == digest:
            return parse_model(OwnerCustodyEvidence.from_dict, latest)
        if self.receipt is not None:
            for value in self.receipt["root_transition"]["custody_evidence"]:
                if value["account_subject"] == subject and value["evidence_digest"] == digest:
                    return parse_model(OwnerCustodyEvidence.from_dict, value)
        value = self.reference("custody_evidence", subject, None, digest)
        return parse_model(OwnerCustodyEvidence.from_dict, value["evidence"])

    def projection(self, reference: CertificateProjectionReference) -> CertificateSignatureProjection:
        value = self.reference("certificate_projection", reference.witness_subject, None, reference.certificate_digest)
        return CertificateSignatureProjection.parse(value["certificate_projection"], reference)

    def custody(self, organization: str, subject: str, *, proof_scope: str | None = None) -> OwnerCustodyResponse:
        state = self.subject(subject)
        candidates = [value for value in self.targets if value["target"]["account_subject"] == subject
                      and value["target"]["organization_id"] == organization
                      and (value["target"]["scope_id"] in {"", organization} if proof_scope is None
                           else value["target"]["scope_id"] == proof_scope)]
        live = [value for value in candidates if value["target"]["purpose"] in {"actor", "scope_recipient", "owner_candidate"}]
        if live:
            candidates = live
        if not candidates:
            raise E2eeError("root_replacement_dependency_missing")
        for value in candidates:
            self._available(value, "owner_custody_evidence_missing")
        flags = {(value["can_manage_organization_keys"], value["can_receive_organization_keys"]) for value in candidates}
        if len(flags) != 1:
            raise E2eeError("invalid_key_operation_proof")
        manage, receive = flags.pop()
        return parse_model(OwnerCustodyResponse.from_dict, {"organization_id": organization,
            "account_subject": subject, "custody_revision": state["custody_revision"],
            "revoked_device_ids": state["revoked_device_ids"], "owner_bindings_digest": state["owner_bindings_digest"],
            "head": self.authority(organization).head.to_dict(), "can_manage_organization_keys": manage,
            "can_receive_organization_keys": receive, "latest_root_transition": state.get("latest_root_transition")})

    def gate(self, organization: str, gate_id: str):
        value = next((value for value in self.gates if value["organization_id"] == organization
                      and value["gate_id"] == gate_id), None)
        if value is None:
            raise E2eeError("root_replacement_dependency_missing")
        return gate_descriptor(value)

    def decision(self, organization: str, operation_id: str) -> OwnerTransferDecision:
        state = self.organizations.get(organization)
        if state is None:
            raise E2eeError("root_replacement_dependency_missing")
        value = next((value for value in state["pending_transfers"] if value["operation_id"] == operation_id), None)
        if value is None:
            value = self.reference("transfer_decision", "", organization, operation_id)["transfer_decision"]
        return parse_model(OwnerTransferDecision.from_dict, value)
