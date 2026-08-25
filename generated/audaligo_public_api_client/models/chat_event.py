from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.chat_event_type import ChatEventType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatEvent")


@_attrs_define
class ChatEvent:
    """
    Attributes:
        type_ (ChatEventType):
        project_id (str):
        sequence (int):
        message_id (str):
        author_membership_id (str):
        actor_membership_id (str):
        client_operation_id (str):
        revision (int):
        committed_at (datetime.datetime):
        body (None | str | Unset):
    """

    type_: ChatEventType
    project_id: str
    sequence: int
    message_id: str
    author_membership_id: str
    actor_membership_id: str
    client_operation_id: str
    revision: int
    committed_at: datetime.datetime
    body: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        project_id = self.project_id

        sequence = self.sequence

        message_id = self.message_id

        author_membership_id = self.author_membership_id

        actor_membership_id = self.actor_membership_id

        client_operation_id = self.client_operation_id

        revision = self.revision

        committed_at = self.committed_at.isoformat()

        body: None | str | Unset
        if isinstance(self.body, Unset):
            body = UNSET
        else:
            body = self.body

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "projectId": project_id,
                "sequence": sequence,
                "messageId": message_id,
                "authorMembershipId": author_membership_id,
                "actorMembershipId": actor_membership_id,
                "clientOperationId": client_operation_id,
                "revision": revision,
                "committedAt": committed_at,
            }
        )
        if body is not UNSET:
            field_dict["body"] = body

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = ChatEventType(d.pop("type"))

        project_id = d.pop("projectId")

        sequence = d.pop("sequence")

        message_id = d.pop("messageId")

        author_membership_id = d.pop("authorMembershipId")

        actor_membership_id = d.pop("actorMembershipId")

        client_operation_id = d.pop("clientOperationId")

        revision = d.pop("revision")

        committed_at = datetime.datetime.fromisoformat(d.pop("committedAt"))

        def _parse_body(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        body = _parse_body(d.pop("body", UNSET))

        chat_event = cls(
            type_=type_,
            project_id=project_id,
            sequence=sequence,
            message_id=message_id,
            author_membership_id=author_membership_id,
            actor_membership_id=actor_membership_id,
            client_operation_id=client_operation_id,
            revision=revision,
            committed_at=committed_at,
            body=body,
        )

        return chat_event
