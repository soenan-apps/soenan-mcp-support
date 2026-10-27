from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_invitation_participant_proof import (
        E2EeInvitationParticipantProof,
    )
    from ..models.e2_ee_organization_participant_proof import (
        E2EeOrganizationParticipantProof,
    )
    from ..models.e2_ee_participant_source import E2EeParticipantSource


T = TypeVar("T", bound="E2EeScopeParticipantProofs")


@_attrs_define
class E2EeScopeParticipantProofs:
    """
    Attributes:
        proofs (list[E2EeInvitationParticipantProof | E2EeOrganizationParticipantProof]):
        source (E2EeParticipantSource | Unset):
        next_after (str | Unset):
    """

    proofs: list[E2EeInvitationParticipantProof | E2EeOrganizationParticipantProof]
    source: E2EeParticipantSource | Unset = UNSET
    next_after: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.e2_ee_invitation_participant_proof import (
            E2EeInvitationParticipantProof,
        )

        proofs = []
        for proofs_item_data in self.proofs:
            proofs_item: dict[str, Any]
            if isinstance(proofs_item_data, E2EeInvitationParticipantProof):
                proofs_item = proofs_item_data.to_dict()
            else:
                proofs_item = proofs_item_data.to_dict()

            proofs.append(proofs_item)

        source: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.to_dict()

        next_after = self.next_after

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "proofs": proofs,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source
        if next_after is not UNSET:
            field_dict["next_after"] = next_after

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_invitation_participant_proof import (
            E2EeInvitationParticipantProof,
        )
        from ..models.e2_ee_organization_participant_proof import (
            E2EeOrganizationParticipantProof,
        )
        from ..models.e2_ee_participant_source import E2EeParticipantSource

        d = dict(src_dict)
        proofs = []
        _proofs = d.pop("proofs")
        for proofs_item_data in _proofs:

            def _parse_proofs_item(
                data: object,
            ) -> E2EeInvitationParticipantProof | E2EeOrganizationParticipantProof:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_e2_ee_scope_participant_proof_type_0 = (
                        E2EeInvitationParticipantProof.from_dict(data)
                    )

                    return componentsschemas_e2_ee_scope_participant_proof_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_e2_ee_scope_participant_proof_type_1 = (
                    E2EeOrganizationParticipantProof.from_dict(data)
                )

                return componentsschemas_e2_ee_scope_participant_proof_type_1

            proofs_item = _parse_proofs_item(proofs_item_data)

            proofs.append(proofs_item)

        _source = d.pop("source", UNSET)
        source: E2EeParticipantSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = E2EeParticipantSource.from_dict(_source)

        next_after = d.pop("next_after", UNSET)

        e2_ee_scope_participant_proofs = cls(
            proofs=proofs,
            source=source,
            next_after=next_after,
        )

        return e2_ee_scope_participant_proofs
