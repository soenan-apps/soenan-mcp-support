from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.bucket_capability_contract import BucketCapabilityContract
from ..models.bucket_capability_operation import BucketCapabilityOperation
from ..types import parse_datetime

if TYPE_CHECKING:
    from ..models.capability_headers import CapabilityHeaders


T = TypeVar("T", bound="BucketCapability")


@_attrs_define
class BucketCapability:
    """
    Attributes:
        contract (BucketCapabilityContract):
        v (int):
        operation (BucketCapabilityOperation):
        object_id (str):
        chunk_index (int):
        expires_at (datetime.datetime):
        content_length (int):
        url (str):
        headers (CapabilityHeaders):
    """

    contract: BucketCapabilityContract
    v: int
    operation: BucketCapabilityOperation
    object_id: str
    chunk_index: int
    expires_at: datetime.datetime
    content_length: int
    url: str
    headers: CapabilityHeaders

    def to_dict(self) -> dict[str, Any]:
        contract = self.contract.value

        v = self.v

        operation = self.operation.value

        object_id = self.object_id

        chunk_index = self.chunk_index

        expires_at = self.expires_at.isoformat()

        content_length = self.content_length

        url = self.url

        headers = self.headers.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "contract": contract,
                "v": v,
                "operation": operation,
                "objectId": object_id,
                "chunkIndex": chunk_index,
                "expiresAt": expires_at,
                "contentLength": content_length,
                "url": url,
                "headers": headers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.capability_headers import CapabilityHeaders

        d = dict(src_dict)
        contract = BucketCapabilityContract(d.pop("contract"))

        v = d.pop("v")

        operation = BucketCapabilityOperation(d.pop("operation"))

        object_id = d.pop("objectId")

        chunk_index = d.pop("chunkIndex")

        expires_at = parse_datetime(d.pop("expiresAt"))

        content_length = d.pop("contentLength")

        url = d.pop("url")

        headers = CapabilityHeaders.from_dict(d.pop("headers"))

        bucket_capability = cls(
            contract=contract,
            v=v,
            operation=operation,
            object_id=object_id,
            chunk_index=chunk_index,
            expires_at=expires_at,
            content_length=content_length,
            url=url,
            headers=headers,
        )

        return bucket_capability
