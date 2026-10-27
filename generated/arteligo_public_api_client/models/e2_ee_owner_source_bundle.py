from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
    from ..models.e2_ee_owner_source_document import E2EeOwnerSourceDocument
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerSourceBundle")


@_attrs_define
class E2EeOwnerSourceBundle:
    """
    Attributes:
        signed_command (E2EeSignedCommand):
        manifest_digest (str):
        documents (list[E2EeOwnerSourceDocument]):
        issuer_evidence (E2EeOwnerIssuerEvidence): Immutable public issuer proof graph for the selected binding.
            Includes only exact certificate references frozen by its signed issuer_admission and recursively by accepted
            Account witnesses, plus the corresponding public recovery checkpoints. This is not a current device directory
            and grants no content or key-distribution authority. Fetch on demand; retain references rather than embedding
            full certificate wrappers in private history.
    """

    signed_command: E2EeSignedCommand
    manifest_digest: str
    documents: list[E2EeOwnerSourceDocument]
    issuer_evidence: E2EeOwnerIssuerEvidence

    def to_dict(self) -> dict[str, Any]:
        signed_command = self.signed_command.to_dict()

        manifest_digest = self.manifest_digest

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        issuer_evidence = self.issuer_evidence.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "signed_command": signed_command,
                "manifest_digest": manifest_digest,
                "documents": documents,
                "issuer_evidence": issuer_evidence,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
        from ..models.e2_ee_owner_source_document import E2EeOwnerSourceDocument
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        manifest_digest = d.pop("manifest_digest")

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = E2EeOwnerSourceDocument.from_dict(documents_item_data)

            documents.append(documents_item)

        issuer_evidence = E2EeOwnerIssuerEvidence.from_dict(d.pop("issuer_evidence"))

        e2_ee_owner_source_bundle = cls(
            signed_command=signed_command,
            manifest_digest=manifest_digest,
            documents=documents,
            issuer_evidence=issuer_evidence,
        )

        return e2_ee_owner_source_bundle
