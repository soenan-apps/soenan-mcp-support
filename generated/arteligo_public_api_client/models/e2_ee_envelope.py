from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

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
        signed_command (E2EeSignedCommand | Unset):
    """

    scope_id: str
    key_epoch: int
    recipient_id: str
    recipient_kind: E2EeRecipientKind
    sender_device_id: str
    encapsulated_key: str
    ciphertext: str
    signed_command: E2EeSignedCommand | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        key_epoch = self.key_epoch

        recipient_id = self.recipient_id

        recipient_kind = self.recipient_kind.value

        sender_device_id = self.sender_device_id

        encapsulated_key = self.encapsulated_key

        ciphertext = self.ciphertext

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
            signed_command=signed_command,
        )

        return e2_ee_envelope
