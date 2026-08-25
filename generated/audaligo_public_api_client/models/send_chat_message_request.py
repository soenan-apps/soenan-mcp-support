from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SendChatMessageRequest")


@_attrs_define
class SendChatMessageRequest:
    """
    Attributes:
        client_operation_id (str):
        message_id (str):
        body (str):
    """

    client_operation_id: str
    message_id: str
    body: str

    def to_dict(self) -> dict[str, Any]:
        client_operation_id = self.client_operation_id

        message_id = self.message_id

        body = self.body

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clientOperationId": client_operation_id,
                "messageId": message_id,
                "body": body,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_operation_id = d.pop("clientOperationId")

        message_id = d.pop("messageId")

        body = d.pop("body")

        send_chat_message_request = cls(
            client_operation_id=client_operation_id,
            message_id=message_id,
            body=body,
        )

        return send_chat_message_request
