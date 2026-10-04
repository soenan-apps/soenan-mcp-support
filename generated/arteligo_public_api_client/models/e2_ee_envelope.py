from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_recipient_kind import E2EeRecipientKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeEnvelope")


@_attrs_define
class E2EeEnvelope:
    """
    Attributes:
        scope_id (str):
        key_epoch (int):
        recipient_id (str):
        recipient_kind (E2EeRecipientKind):
        sender_device_id (str):
        encapsulated_key (str):
        ciphertext (str):
        organization_epoch (int | None | Unset): Organization key epoch bound into the signed command and HPKE context.
            Required for new organization recipients and forbidden for other recipients. Legacy stored envelopes may omit
            this field and retain their original authenticated context.
        signed_command (E2EeSignedCommand | Unset):
    """

    scope_id: str
    key_epoch: int
    recipient_id: str
    recipient_kind: E2EeRecipientKind
    sender_device_id: str
    encapsulated_key: str
    ciphertext: str
    organization_epoch: int | None | Unset = UNSET
    signed_command: E2EeSignedCommand | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        key_epoch = self.key_epoch

        recipient_id = self.recipient_id

        recipient_kind = self.recipient_kind.value

        sender_device_id = self.sender_device_id

        encapsulated_key = self.encapsulated_key

        ciphertext = self.ciphertext

        organization_epoch: int | None | Unset
        if isinstance(self.organization_epoch, Unset):
            organization_epoch = UNSET
        else:
            organization_epoch = self.organization_epoch

        signed_command: dict[str, Any] | Unset = UNSET
        if not isinstance(self.signed_command, Unset):
            signed_command = self.signed_command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "key_epoch": key_epoch,
                "recipient_id": recipient_id,
                "recipient_kind": recipient_kind,
                "sender_device_id": sender_device_id,
                "encapsulated_key": encapsulated_key,
                "ciphertext": ciphertext,
            }
        )
        if organization_epoch is not UNSET:
            field_dict["organization_epoch"] = organization_epoch
        if signed_command is not UNSET:
            field_dict["signed_command"] = signed_command

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        key_epoch = d.pop("key_epoch")

        recipient_id = d.pop("recipient_id")

        recipient_kind = E2EeRecipientKind(d.pop("recipient_kind"))

        sender_device_id = d.pop("sender_device_id")

        encapsulated_key = d.pop("encapsulated_key")

        ciphertext = d.pop("ciphertext")

        def _parse_organization_epoch(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        organization_epoch = _parse_organization_epoch(
            d.pop("organization_epoch", UNSET)
        )

        _signed_command = d.pop("signed_command", UNSET)
        signed_command: E2EeSignedCommand | Unset
        if isinstance(_signed_command, Unset):
            signed_command = UNSET
        else:
            signed_command = E2EeSignedCommand.from_dict(_signed_command)

        e2_ee_envelope = cls(
            scope_id=scope_id,
            key_epoch=key_epoch,
            recipient_id=recipient_id,
            recipient_kind=recipient_kind,
            sender_device_id=sender_device_id,
            encapsulated_key=encapsulated_key,
            ciphertext=ciphertext,
            organization_epoch=organization_epoch,
            signed_command=signed_command,
        )

        return e2_ee_envelope
