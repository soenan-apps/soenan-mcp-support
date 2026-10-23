from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_authority_head import OwnerAuthorityHead
    from ..models.owner_source_selection import OwnerSourceSelection


T = TypeVar("T", bound="OwnerAuthorityResponse")


@_attrs_define
class OwnerAuthorityResponse:
    """
    Attributes:
        challenge (str):
        head (OwnerAuthorityHead):
        source_selection (None | OwnerSourceSelection): Null establishes that no committed content-transfer selection
            exists at this head's cutoff. It is retained through no-content, keyless, key-registration and rotation-required
            heads. Historical lookups never use a later selection.
        predecessor_head (OwnerAuthorityHead | Unset):
    """

    challenge: str
    head: OwnerAuthorityHead
    source_selection: None | OwnerSourceSelection
    predecessor_head: OwnerAuthorityHead | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.owner_source_selection import OwnerSourceSelection

        challenge = self.challenge

        head = self.head.to_dict()

        source_selection: dict[str, Any] | None
        if isinstance(self.source_selection, OwnerSourceSelection):
            source_selection = self.source_selection.to_dict()
        else:
            source_selection = self.source_selection

        predecessor_head: dict[str, Any] | Unset = UNSET
        if not isinstance(self.predecessor_head, Unset):
            predecessor_head = self.predecessor_head.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "head": head,
                "source_selection": source_selection,
            }
        )
        if predecessor_head is not UNSET:
            field_dict["predecessor_head"] = predecessor_head

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_authority_head import OwnerAuthorityHead
        from ..models.owner_source_selection import OwnerSourceSelection

        d = dict(src_dict)
        challenge = d.pop("challenge")

        head = OwnerAuthorityHead.from_dict(d.pop("head"))

        def _parse_source_selection(data: object) -> None | OwnerSourceSelection:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_selection_type_1 = OwnerSourceSelection.from_dict(data)

                return source_selection_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OwnerSourceSelection, data)

        source_selection = _parse_source_selection(d.pop("source_selection"))

        _predecessor_head = d.pop("predecessor_head", UNSET)
        predecessor_head: OwnerAuthorityHead | Unset
        if isinstance(_predecessor_head, Unset):
            predecessor_head = UNSET
        else:
            predecessor_head = OwnerAuthorityHead.from_dict(_predecessor_head)

        owner_authority_response = cls(
            challenge=challenge,
            head=head,
            source_selection=source_selection,
            predecessor_head=predecessor_head,
        )

        return owner_authority_response
