from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from ._crypto import E2eeError, decode, encode, wipe
from ._owner_envelopes import OWNER_KEY_PROOF
from ._owner_protocol import GENERATION_BLOCKERS, OwnerAuthorityHead, SignedEvidence, authority_head
from ._signed_commands import SavedCommand, UncertainCommand
from ._trust import _CurrentRecipientSet, _TrustPathUnavailable
from account_public_api_client.models.owner_custody_evidence import OwnerCustodyEvidence
from account_public_api_client.models.owner_custody_root_identity import OwnerCustodyRootIdentity

if TYPE_CHECKING:
    from ._owner_access import OwnerAccess




class OwnerOrganizationKeys:
    def qualify_recipients(self, organization: str, recipients: _CurrentRecipientSet, head: OwnerAuthorityHead) -> None:
        for target in recipients.roots:
            root = target.identity
            if root.subject == head.owner_subject:
                continue
            observed = self.owner.current.observe(organization, root.subject, head)
            if not observed.can_receive_organization_keys:
                raise E2eeError("organization_key_recipient_ineligible")
            latest = observed.latest_root_transition
            if isinstance(latest, OwnerCustodyEvidence):
                if (not isinstance(latest.target, OwnerCustodyRootIdentity)
                        or self.owner.verifier.root(latest.target.to_dict(), root.subject) != root):
                    raise E2eeError("owner_custody_changed")
        for device in recipients.devices:
            if device["account_subject"] == head.owner_subject:
                continue
            anchor = self.owner.current.independent_root(organization, device)
            qualified = self.owner.current.qualify(organization, device, anchor, head)
            if not qualified.custody.can_receive_organization_keys:
                raise E2eeError("organization_key_recipient_ineligible")

    def __init__(self, owner: OwnerAccess):
        self.owner, self.session = owner, owner.session

    def initialize(self, organization: str, head: OwnerAuthorityHead) -> None:
        pending = self.session.publications.pending("scope_initializations", organization, "organization_create")
        if pending is None:
            if head.owner_subject != self.session.subject:
                raise E2eeError("owner_required")
            key = self.session.crypto.key()
            try:
                envelope = self.owner.maintenance_issuer(head).wrap(organization, 1, key,
                    recipient=head.key_id, kind="owner", public_key=head.public_key,
                    owner_key_epoch=head.key_epoch, owner_binding_digest=head.binding_digest)
                body = {"scope_id": organization, "key_epoch": 1, "owner_authority": head.to_dict(),
                        "owner_key_proof": OWNER_KEY_PROOF, "envelopes": [envelope]}
                pending = SavedCommand("organization_create",
                    UncertainCommand(SignedEvidence.parse(self.session.sign("organization_create", body))),
                    key=encode(key), epoch=1)
                self.session.publications.save("scope_initializations", organization, pending)
            finally:
                wipe(key)
        if pending.command.body.get("owner_key_proof") != OWNER_KEY_PROOF or pending.key is None:
            raise E2eeError("unsupported_owner_key_proof")
        self.session.publications.submit("scope_initializations", organization, pending,
            lambda command: self.session.call("e2eeCreateOrganization", body=command))
        key = decode(pending.key)
        try:
            self.session._remember(organization, 1, key, owner=self.session._scope_owner(organization))
        finally:
            wipe(key)
        self.session.publications.finish("scope_initializations", organization, pending)
        self.session.scope_metadata(organization, refresh=True)

    def maintain(self, organization: str, head: OwnerAuthorityHead) -> None:
        metadata = self.session.scope_metadata(organization, refresh=True)
        if metadata["key_epoch"] == 0 and metadata["key_state"] == "uninitialized":
            self.initialize(organization, head)
            metadata = self.session.scope_metadata(organization, refresh=True)
        inventory = self.session.call("e2eeGetOwnerInventory", organization_id=organization)["organization"]
        epochs = inventory["epochs"]
        if (inventory["organization_id"] != organization or inventory["key_epoch"] != metadata["key_epoch"]
                or not isinstance(epochs, list) or any(type(epoch) is not int or epoch < 1 for epoch in epochs)
                or len(epochs) != len(set(epochs)) or metadata["key_epoch"] not in epochs):
            raise E2eeError("invalid_epoch_chain")
        for epoch in epochs:
            values = self.session.call("e2eeGetEnvelopes", scope_id=organization, epoch=epoch,
                                       recipient_id=head.key_id, recipient_kind="owner")["envelopes"]
            if values:
                self.owner.envelopes.sender(organization, epoch, values[0])
            else:
                self.owner.provision_envelope(organization, head, organization, epoch)
        try:
            self.owner.publications.require_generation(organization, metadata["key_epoch"])
        except E2eeError as error:
            if error.code not in GENERATION_BLOCKERS:
                raise
            self.session.rotate_scope(metadata)
        else:
            if metadata["key_state"] == "rekey_required":
                self.session.rotate_scope(metadata)


    def qualify_admin(self, organization: str, device: Mapping[str, Any], head: OwnerAuthorityHead) -> None:
        subject = device["account_subject"]
        if subject == head.owner_subject:
            raise E2eeError("owner_key_proof_required")
        permission = self.owner.account.custody(organization, subject, head.read_capability)
        if permission.head.to_dict() != head.to_dict() or permission.can_manage_organization_keys is not True:
            raise E2eeError("organization_key_authority_required")
        scope = None if subject == self.session.subject else organization
        material = self.session._device_material(scope, device["device_id"], refresh=True)
        lookup = self.session._current_device_lookup(scope)
        roots = lambda identifier: self.session._recovery_material(scope, identifier)
        try:
            if scope is not None and not self.session._participants.verify_device(organization, material, frozenset(), lookup, roots):
                raise E2eeError("organization_identity_verification_required")
            anchor = self.owner.current.independent_root(organization, material)
            qualified = self.owner.current.qualify(organization, material, anchor, head)
            if qualified.custody.can_manage_organization_keys is not True:
                raise E2eeError("organization_key_authority_required")
        except _TrustPathUnavailable:
            raise E2eeError("organization_identity_verification_required") from None
