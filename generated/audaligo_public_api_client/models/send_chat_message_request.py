from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.comment_project_reference import CommentProjectReference
    from ..models.comment_reply_project_reference import CommentReplyProjectReference
    from ..models.file_project_reference import FileProjectReference
    from ..models.stage_project_reference import StageProjectReference


T = TypeVar("T", bound="SendChatMessageRequest")


@_attrs_define
class SendChatMessageRequest:
    """
    Attributes:
        client_operation_id (str):
        message_id (str):
        body (str):
        references (list[CommentProjectReference | CommentReplyProjectReference | FileProjectReference |
            StageProjectReference]):
    """

    client_operation_id: str
    message_id: str
    body: str
    references: list[
        CommentProjectReference
        | CommentReplyProjectReference
        | FileProjectReference
        | StageProjectReference
    ]

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

        client_operation_id = self.client_operation_id

        message_id = self.message_id

        body = self.body

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

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clientOperationId": client_operation_id,
                "messageId": message_id,
                "body": body,
                "references": references,
            }
        )

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
        client_operation_id = d.pop("clientOperationId")

        message_id = d.pop("messageId")

        body = d.pop("body")

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

        send_chat_message_request = cls(
            client_operation_id=client_operation_id,
            message_id=message_id,
            body=body,
            references=references,
        )

        return send_chat_message_request
