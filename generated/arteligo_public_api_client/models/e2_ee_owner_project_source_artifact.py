from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
    from ..models.e2_ee_owner_source_document import E2EeOwnerSourceDocument


T = TypeVar("T", bound="E2EeOwnerProjectSourceArtifact")


@_attrs_define
class E2EeOwnerProjectSourceArtifact:
    """
    Attributes:
        manifest_id (str):
        manifest_digest (str):
        document (E2EeOwnerSourceDocument): Exact canonical complete E2eeOwnerSourceProject bytes. Reuse these bytes
            unchanged on every later export.
        issuer_evidence (E2EeOwnerIssuerEvidence): Immutable public issuer proof graph for the selected binding.
            Includes only exact certificate references frozen by its signed issuer_admission and recursively by accepted
            Account witnesses, plus the corresponding public recovery checkpoints. This is not a current device directory
            and grants no content or key-distribution authority. Fetch on demand; retain references rather than embedding
            full certificate wrappers in private history.
    """

    manifest_id: str
    manifest_digest: str
    document: E2EeOwnerSourceDocument
    issuer_evidence: E2EeOwnerIssuerEvidence

    def to_dict(self) -> dict[str, Any]:
        manifest_id = self.manifest_id

        manifest_digest = self.manifest_digest

        document = self.document.to_dict()

        issuer_evidence = self.issuer_evidence.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "manifest_id": manifest_id,
                "manifest_digest": manifest_digest,
                "document": document,
                "issuer_evidence": issuer_evidence,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_issuer_evidence import E2EeOwnerIssuerEvidence
        from ..models.e2_ee_owner_source_document import E2EeOwnerSourceDocument

        d = dict(src_dict)
        manifest_id = d.pop("manifest_id")

        manifest_digest = d.pop("manifest_digest")

        document = E2EeOwnerSourceDocument.from_dict(d.pop("document"))

        issuer_evidence = E2EeOwnerIssuerEvidence.from_dict(d.pop("issuer_evidence"))

        e2_ee_owner_project_source_artifact = cls(
            manifest_id=manifest_id,
            manifest_digest=manifest_digest,
            document=document,
            issuer_evidence=issuer_evidence,
        )

        return e2_ee_owner_project_source_artifact
