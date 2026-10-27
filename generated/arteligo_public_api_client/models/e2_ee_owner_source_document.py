from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="E2EeOwnerSourceDocument")


@_attrs_define
class E2EeOwnerSourceDocument:
    """Exact canonical complete E2eeOwnerSourceProject bytes. Reuse these bytes unchanged on every later export.

    Attributes:
        document_bytes (str):
    """

    document_bytes: str

    def to_dict(self) -> dict[str, Any]:
        document_bytes = self.document_bytes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "document_bytes": document_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_bytes = d.pop("document_bytes")

        e2_ee_owner_source_document = cls(
            document_bytes=document_bytes,
        )

        return e2_ee_owner_source_document
