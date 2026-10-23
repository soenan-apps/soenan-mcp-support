from __future__ import annotations

import secrets
import ssl
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Mapping, TypeVar

import httpx
from account_public_api_client.api.organizations import (
    get_owner_authority, get_owner_certificate_signature_projection, get_owner_custody,
    get_owner_custody_evidence, get_owner_handoff_gate, get_owner_transfer_decision,
)
from account_public_api_client.client import Client
from account_public_api_client.models.owner_authority_response import OwnerAuthorityResponse
from account_public_api_client.models.owner_certificate_signature_projection_response import OwnerCertificateSignatureProjectionResponse
from account_public_api_client.models.owner_custody_evidence import OwnerCustodyEvidence
from account_public_api_client.models.owner_custody_evidence_response import OwnerCustodyEvidenceResponse
from account_public_api_client.models.owner_custody_response import OwnerCustodyResponse
from account_public_api_client.models.owner_handoff_gate_response import OwnerHandoffGateResponse
from account_public_api_client.models.owner_transfer_decision import OwnerTransferDecision
from account_public_api_client.models.owner_transfer_decision_response import OwnerTransferDecisionResponse
from account_public_api_client.types import Response

from ._crypto import E2eeError
from ._oauth import origin
from ._owner_protocol import OwnerAuthorityHead, OwnerHandoffGate, authority_head, gate_descriptor, bytes32
from ._owner_projection import CertificateProjectionReference, CertificateSignatureProjection

if TYPE_CHECKING:
    from ._session import DeviceSession

T = TypeVar("T", OwnerAuthorityResponse, OwnerCustodyResponse, OwnerCustodyEvidenceResponse,
            OwnerHandoffGateResponse, OwnerTransferDecisionResponse, OwnerCertificateSignatureProjectionResponse)


@dataclass(frozen=True)
class OwnerSourceSelection:
    operation_id: str
    successor_binding_digest: str
    source_manifest_id: str
    source_manifest_digest: str

    @classmethod
    def parse(cls, value: Any) -> OwnerSourceSelection:
        if (not isinstance(value, dict)
                or set(value) != {"operation_id", "successor_binding_digest", "source_manifest_id", "source_manifest_digest"}
                or any(not isinstance(item, str) or not item for item in value.values())):
            raise E2eeError("invalid_owner_authority")
        bytes32(value["successor_binding_digest"])
        bytes32(value["source_manifest_digest"])
        return cls(**value)


@dataclass(frozen=True)
class SelectedOwnerHead:
    head: OwnerAuthorityHead
    predecessor: OwnerAuthorityHead | None = None
    source_selection: OwnerSourceSelection | None = None

    @classmethod
    def parse(cls, response: OwnerAuthorityResponse, organization: str) -> SelectedOwnerHead:
        value = response.to_dict()
        if "source_selection" not in value:
            raise E2eeError("invalid_owner_authority")
        head = authority_head(value["head"], organization)
        predecessor = (authority_head(value["predecessor_head"], organization)
                       if value.get("predecessor_head") is not None else None)
        selection = (OwnerSourceSelection.parse(value["source_selection"])
                     if value["source_selection"] is not None else None)
        return cls(head, predecessor, selection)

    def matches(self, head: OwnerAuthorityHead) -> bool:
        return all(getattr(self.head, field) == getattr(head, field) for field in (
            "organization_id", "ownership_revision", "owner_subject", "key_id", "key_epoch",
            "public_key", "binding_digest",
        ))


class OwnerAccountReads:
    def __init__(self, session: DeviceSession):
        self.session = session
        self._selected: dict[tuple[str, str], SelectedOwnerHead] = {}
        self._capabilities: dict[str, str] = {}
        self._snapshots: dict[str, SelectedOwnerHead] = {}
        self._projections: dict[CertificateProjectionReference, CertificateSignatureProjection] = {}
        self._tls = ssl.create_default_context()

    def _read(self, request: Callable[[Client, str], Response[Any]], response_type: type[T],
              *, missing: str = "owner_authority_unavailable") -> T:
        self.session._check_current()
        challenge = secrets.token_urlsafe(32)
        try:
            with Client(
                base_url=origin(self.session._credentials.account_origin),
                headers={"Cache-Control": "no-store", "Accept": "application/json"},
                timeout=httpx.Timeout(30), follow_redirects=False,
                verify_ssl=self._tls,
                raise_on_unexpected_status=False, httpx_args={"trust_env": False},
            ) as client:
                response = request(client, challenge)
            if int(response.status_code) == 404:
                raise E2eeError(missing)
            if int(response.status_code) != 200:
                raise E2eeError("owner_authority_unavailable")
            value = response.parsed
            if (not isinstance(value, response_type) or value.challenge != challenge
                    or "no-store" not in response.headers.get("cache-control", "").lower()):
                raise E2eeError("invalid_owner_authority")
            self.session._check_current()
            return value
        except (httpx.HTTPError, ValueError, TypeError, KeyError, AttributeError):
            raise E2eeError("owner_authority_unavailable") from None

    def capability(self, organization: str) -> str:
        if organization not in self._capabilities:
            state = self.session.owner_access.store.find(organization)
            retained = next((item["binding_digest"] for item in (self.session.recovery or {}).get("owner_access_history", [])
                             if item["organization_id"] == organization), None)
            if retained is None and state is not None:
                retained = next((key.binding_digest for key in state.keys
                                 if key.binding.body.device.account_subject == self.session.subject), None)
            proof = (self.session.call("e2eeGetOwnerBinding", organization_id=organization, binding_digest=retained)
                     if retained is not None else self.session.call("e2eeGetOwnerAuthority", organization_id=organization))
            self._capabilities[organization] = authority_head(proof.get("owner_authority"), organization).read_capability
        return self._capabilities[organization]

    def authority_snapshot(self, organization: str, capability: str) -> SelectedOwnerHead:
        response = self._read(lambda client, challenge: get_owner_authority.sync_detailed(
            organization_id=organization, client=client, challenge=challenge,
            x_owner_read_capability=capability,
        ), OwnerAuthorityResponse)
        snapshot = SelectedOwnerHead.parse(response, organization)
        self._snapshots[organization] = snapshot
        self._capabilities[organization] = capability
        return snapshot

    def authority(self, organization: str, capability: str) -> OwnerAuthorityHead:
        return self.authority_snapshot(organization, capability).head

    def selected(self, organization: str, digest: str, *, capability: str | None = None) -> SelectedOwnerHead:
        self.session._check_current()
        if capability is not None:
            self._capabilities[organization] = capability
        identity = (organization, digest)
        if identity not in self._selected:
            response = self._read(lambda client, challenge: get_owner_authority.sync_detailed(
                organization_id=organization, client=client, challenge=challenge,
                x_owner_read_capability=self.capability(organization), binding_digest=digest,
            ), OwnerAuthorityResponse, missing="owner_binding_not_selected")
            snapshot = SelectedOwnerHead.parse(response, organization)
            if snapshot.head.binding_digest != digest:
                raise E2eeError("owner_binding_mismatch")
            self._selected[identity] = snapshot
        return self._selected[identity]

    def gate(self, organization: str, gate_id: str) -> OwnerHandoffGate:
        response = self._read(lambda client, challenge: get_owner_handoff_gate.sync_detailed(
            gate_id=gate_id, client=client, challenge=challenge, x_owner_read_capability=self.capability(organization),
        ), OwnerHandoffGateResponse)
        return gate_descriptor(response.gate.to_dict())

    def decision(self, organization: str, operation_id: str) -> OwnerTransferDecision:
        response = self._read(lambda client, challenge: get_owner_transfer_decision.sync_detailed(
            operation_id=operation_id, client=client, challenge=challenge,
            x_owner_read_capability=self.capability(organization),
        ), OwnerTransferDecisionResponse)
        if response.decision.operation_id != operation_id:
            raise E2eeError("owner_receipt_mismatch")
        return response.decision

    def witness(self, subject: str, digest: str) -> OwnerCustodyEvidence:
        bytes32(digest)
        response = self._read(lambda client, challenge: get_owner_custody_evidence.sync_detailed(
            account_subject=subject, evidence_digest=digest, client=client, challenge=challenge,
        ), OwnerCustodyEvidenceResponse, missing="owner_custody_evidence_missing")
        if response.evidence.account_subject != subject or response.evidence.evidence_digest != digest:
            raise E2eeError("owner_custody_evidence_mismatch")
        return response.evidence

    def projection(self, certificate: Mapping[str, Any]) -> CertificateSignatureProjection:
        reference = CertificateProjectionReference.parse(certificate)
        self.session._check_current()
        if reference not in self._projections:
            response = self._read(lambda client, challenge: get_owner_certificate_signature_projection.sync_detailed(
                account_subject=reference.witness_subject, certificate_digest=reference.certificate_digest,
                client=client, challenge=challenge,
            ), OwnerCertificateSignatureProjectionResponse, missing="owner_certificate_projection_missing")
            self._projections[reference] = CertificateSignatureProjection.parse(response.projection.to_dict(), reference)
        return self._projections[reference]

    def custody(self, organization: str, subject: str, capability: str) -> OwnerCustodyResponse:
        response = self._read(lambda client, challenge: get_owner_custody.sync_detailed(
            organization_id=organization, account_subject=subject, client=client,
            challenge=challenge, x_owner_read_capability=capability,
        ), OwnerCustodyResponse)
        if (response.organization_id != organization or response.account_subject != subject
                or type(response.custody_revision) is not int or response.custody_revision < 0
                or type(response.can_manage_organization_keys) is not bool
                or type(response.can_receive_organization_keys) is not bool
                or not isinstance(response.revoked_device_ids, list)
                or any(not isinstance(identifier, str) or not identifier for identifier in response.revoked_device_ids)
                or len(response.revoked_device_ids) != len(set(response.revoked_device_ids))):
            raise E2eeError("owner_invalidation_unconfirmed")
        bytes32(response.owner_bindings_digest)
        return response
