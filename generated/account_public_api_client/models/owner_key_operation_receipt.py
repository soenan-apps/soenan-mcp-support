from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.owner_authority_head import OwnerAuthorityHead
    from ..models.owner_key_root_receipt import OwnerKeyRootReceipt


T = TypeVar("T", bound="OwnerKeyOperationReceipt")


@_attrs_define
class OwnerKeyOperationReceipt:
    """
    Attributes:
        operation_id (str):
        actor_subject (str):
        preparation_digest (str):
        request_digest (str):
        root_transition (OwnerKeyRootReceipt):
        root_invalidation_heads (list[OwnerAuthorityHead]):
    """

    operation_id: str
    actor_subject: str
    preparation_digest: str
    request_digest: str
    root_transition: OwnerKeyRootReceipt
    root_invalidation_heads: list[OwnerAuthorityHead]

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        actor_subject = self.actor_subject

        preparation_digest = self.preparation_digest

        request_digest = self.request_digest

        root_transition = self.root_transition.to_dict()

        root_invalidation_heads = []
        for root_invalidation_heads_item_data in self.root_invalidation_heads:
            root_invalidation_heads_item = root_invalidation_heads_item_data.to_dict()
            root_invalidation_heads.append(root_invalidation_heads_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "actor_subject": actor_subject,
                "preparation_digest": preparation_digest,
                "request_digest": request_digest,
                "root_transition": root_transition,
                "root_invalidation_heads": root_invalidation_heads,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_authority_head import OwnerAuthorityHead
        from ..models.owner_key_root_receipt import OwnerKeyRootReceipt

        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        actor_subject = d.pop("actor_subject")

        preparation_digest = d.pop("preparation_digest")

        request_digest = d.pop("request_digest")

        root_transition = OwnerKeyRootReceipt.from_dict(d.pop("root_transition"))

        root_invalidation_heads = []
        _root_invalidation_heads = d.pop("root_invalidation_heads")
        for root_invalidation_heads_item_data in _root_invalidation_heads:
            root_invalidation_heads_item = OwnerAuthorityHead.from_dict(
                root_invalidation_heads_item_data
            )

            root_invalidation_heads.append(root_invalidation_heads_item)

        owner_key_operation_receipt = cls(
            operation_id=operation_id,
            actor_subject=actor_subject,
            preparation_digest=preparation_digest,
            request_digest=request_digest,
            root_transition=root_transition,
            root_invalidation_heads=root_invalidation_heads,
        )

        return owner_key_operation_receipt
