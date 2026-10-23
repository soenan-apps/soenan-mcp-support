from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_source_document import E2EeOwnerSourceDocument
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerSourceSubmission")


@_attrs_define
class E2EeOwnerSourceSubmission:
    """
    Attributes:
        signed_command (E2EeSignedCommand):
        documents (list[E2EeOwnerSourceDocument]):
    """

    signed_command: E2EeSignedCommand
    documents: list[E2EeOwnerSourceDocument]

    def to_dict(self) -> dict[str, Any]:
        signed_command = self.signed_command.to_dict()

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "signed_command": signed_command,
                "documents": documents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_source_document import E2EeOwnerSourceDocument
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = E2EeOwnerSourceDocument.from_dict(documents_item_data)

            documents.append(documents_item)

        e2_ee_owner_source_submission = cls(
            signed_command=signed_command,
            documents=documents,
        )

        return e2_ee_owner_source_submission
