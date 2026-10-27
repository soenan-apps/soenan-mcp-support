from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from arteligo_public_api_client.models.e2_ee_organization_admission import E2EeOrganizationAdmission
from arteligo_public_api_client.models.e2_ee_organization_share_request import E2EeOrganizationShareRequest

from ._crypto import E2eeCrypto, E2eeError, decode, wipe
from ._owner_protocol import ROOT_FIELDS, SignedEvidence, object_value, parse_model
from ._owner_projection import CertificateSignatureProjection
from ._trust import _RootIdentity, public_device


@dataclass(frozen=True)
class OrganizationAdmission:
    organization: str
    device: dict[str, Any]
    root: _RootIdentity
    approver_root: _RootIdentity
    approval: SignedEvidence | CertificateSignatureProjection
    request: SignedEvidence

    @classmethod
    def parse(cls, crypto: E2eeCrypto, origin: str, approval: SignedEvidence | CertificateSignatureProjection,
              approver: Mapping[str, Any]) -> OrganizationAdmission:
        body = approval.body
        original = parse_model(E2EeOrganizationAdmission.from_dict, body) if isinstance(approval, SignedEvidence) else None
        participation = object_value(body["participation"])
        request = SignedEvidence.parse(participation["request_command"])
        consent = parse_model(E2EeOrganizationShareRequest.from_dict, request.body)
        device = public_device(consent.device.to_dict())
        issuer = public_device(approver)
        root = _RootIdentity.parse(origin, device["account_subject"], consent.recovery.to_dict())
        approver_root = _RootIdentity.parse(origin, issuer["account_subject"], participation["approver_recovery"])
        if (body["scope_id"] != consent.scope_id or consent.account_subject != device["account_subject"]
                or request.device_id != device["device_id"] or approval.device_id != issuer["device_id"]
                or type(body["key_epoch"]) is not int or body["key_epoch"] < 1 or not consent.request_id):
            raise E2eeError("participant_approval_mismatch")
        challenge = decode(consent.challenge)
        try:
            if len(challenge) != 32:
                raise E2eeError("participant_request_mismatch")
        finally:
            wipe(challenge)
        request.verify(crypto, device["signing_public_key"], "organization_share_request")
        approval.verify(crypto, issuer["signing_public_key"], "envelopes_save")
        for envelope in original.envelopes if original is not None else ():
            if (envelope.scope_id != body["scope_id"] or envelope.key_epoch != body["key_epoch"]
                    or envelope.sender_device_id != issuer["device_id"]):
                raise E2eeError("participant_envelope_mismatch")
        return cls(body["scope_id"], device, root, approver_root, approval, request)

    def target(self) -> dict[str, Any]:
        return {"organization_id": self.organization, "recovery_root": {
            "account_subject": self.root.subject, **{name: self.root.document()[name] for name in ROOT_FIELDS}}}
