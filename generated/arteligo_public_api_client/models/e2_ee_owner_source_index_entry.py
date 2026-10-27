from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="E2EeOwnerSourceIndexEntry")


@_attrs_define
class E2EeOwnerSourceIndexEntry:
    """
    Attributes:
        project_key (str):
        document_digest (str):
    """

    project_key: str
    document_digest: str

    def to_dict(self) -> dict[str, Any]:
        project_key = self.project_key

        document_digest = self.document_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_key": project_key,
                "document_digest": document_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_key = d.pop("project_key")

        document_digest = d.pop("document_digest")

        e2_ee_owner_source_index_entry = cls(
            project_key=project_key,
            document_digest=document_digest,
        )

        return e2_ee_owner_source_index_entry
