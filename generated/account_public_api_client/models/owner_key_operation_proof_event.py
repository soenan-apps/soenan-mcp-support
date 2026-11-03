from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.owner_key_operation_event import OwnerKeyOperationEvent


T = TypeVar("T", bound="OwnerKeyOperationProofEvent")


@_attrs_define
class OwnerKeyOperationProofEvent:
    """
    Attributes:
        challenge (str):
        event (OwnerKeyOperationEvent): Exactly one typed part accompanies sequence. SHA-256 covers uint64 big-endian
            byte length followed by the exact Account canonical JSON event bytes before complete. The complete part is
            excluded. Private frames carry these exact bytes as canonical_json.
        event_bytes (str): Base64url of the exact Account canonical JSON event bytes. Must decode to event before
            adoption.
    """

    challenge: str
    event: OwnerKeyOperationEvent
    event_bytes: str

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        event = self.event.to_dict()

        event_bytes = self.event_bytes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "event": event,
                "event_bytes": event_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_key_operation_event import OwnerKeyOperationEvent

        d = dict(src_dict)
        challenge = d.pop("challenge")

        event = OwnerKeyOperationEvent.from_dict(d.pop("event"))

        event_bytes = d.pop("event_bytes")

        owner_key_operation_proof_event = cls(
            challenge=challenge,
            event=event,
            event_bytes=event_bytes,
        )

        return owner_key_operation_proof_event
