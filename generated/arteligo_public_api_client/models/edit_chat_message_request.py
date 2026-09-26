from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="EditChatMessageRequest")


@_attrs_define
class EditChatMessageRequest:
    """
    Attributes:
        client_operation_id (str):
        expected_revision (int):
        body (str):
    """

    client_operation_id: str
    expected_revision: int
    body: str

    def to_dict(self) -> dict[str, Any]:
        client_operation_id = self.client_operation_id

        expected_revision = self.expected_revision

        body = self.body

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clientOperationId": client_operation_id,
                "expectedRevision": expected_revision,
                "body": body,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        client_operation_id = d.pop("clientOperationId")

        expected_revision = d.pop("expectedRevision")

        body = d.pop("body")

        edit_chat_message_request = cls(
            client_operation_id=client_operation_id,
            expected_revision=expected_revision,
            body=body,
        )

        return edit_chat_message_request
