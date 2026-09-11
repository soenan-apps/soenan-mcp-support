from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.chat_event_type import ChatEventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.comment_project_reference import CommentProjectReference
    from ..models.comment_reply_project_reference import CommentReplyProjectReference
    from ..models.file_project_reference import FileProjectReference
    from ..models.stage_project_reference import StageProjectReference


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
        references (list[CommentProjectReference | CommentReplyProjectReference | FileProjectReference |
            StageProjectReference]):
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
    references: list[
        CommentProjectReference
        | CommentReplyProjectReference
        | FileProjectReference
        | StageProjectReference
    ]
    committed_at: datetime.datetime
    body: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.comment_project_reference import (
            CommentProjectReference,
        )
        from ..models.file_project_reference import (
            FileProjectReference,
        )
        from ..models.stage_project_reference import (
            StageProjectReference,
        )

        type_ = self.type_.value

        project_id = self.project_id

        sequence = self.sequence

        message_id = self.message_id

        author_membership_id = self.author_membership_id

        actor_membership_id = self.actor_membership_id

        client_operation_id = self.client_operation_id

        revision = self.revision

        references = []
        for references_item_data in self.references:
            references_item: dict[str, Any]
            if (
                isinstance(references_item_data, FileProjectReference)
                or isinstance(references_item_data, StageProjectReference)
                or isinstance(references_item_data, CommentProjectReference)
            ):
                references_item = references_item_data.to_dict()
            else:
                references_item = references_item_data.to_dict()

            references.append(references_item)

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
                "references": references,
                "committedAt": committed_at,
            }
        )
        if body is not UNSET:
            field_dict["body"] = body

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.comment_project_reference import (
            CommentProjectReference,
        )
        from ..models.comment_reply_project_reference import (
            CommentReplyProjectReference,
        )
        from ..models.file_project_reference import (
            FileProjectReference,
        )
        from ..models.stage_project_reference import (
            StageProjectReference,
        )

        d = dict(src_dict)
        type_ = ChatEventType(d.pop("type"))

        project_id = d.pop("projectId")

        sequence = d.pop("sequence")

        message_id = d.pop("messageId")

        author_membership_id = d.pop("authorMembershipId")

        actor_membership_id = d.pop("actorMembershipId")

        client_operation_id = d.pop("clientOperationId")

        revision = d.pop("revision")

        references = []
        _references = d.pop("references")
        for references_item_data in _references:

            def _parse_references_item(
                data: object,
            ) -> (
                CommentProjectReference
                | CommentReplyProjectReference
                | FileProjectReference
                | StageProjectReference
            ):
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_project_reference_type_0 = (
                        FileProjectReference.from_dict(data)
                    )

                    return componentsschemas_project_reference_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_project_reference_type_1 = (
                        StageProjectReference.from_dict(data)
                    )

                    return componentsschemas_project_reference_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_project_reference_type_2 = (
                        CommentProjectReference.from_dict(data)
                    )

                    return componentsschemas_project_reference_type_2
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_project_reference_type_3 = (
                    CommentReplyProjectReference.from_dict(data)
                )

                return componentsschemas_project_reference_type_3

            references_item = _parse_references_item(references_item_data)

            references.append(references_item)

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
            references=references,
            committed_at=committed_at,
            body=body,
        )

        return chat_event
