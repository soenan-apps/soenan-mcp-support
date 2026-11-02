from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CryptoProtoMessage")


@_attrs_define
class CryptoProtoMessage:
    """
    Attributes:
        bytes_ (str):
    """

    bytes_: str

    def to_dict(self) -> dict[str, Any]:
        bytes_ = self.bytes_

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "bytes": bytes_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bytes_ = d.pop("bytes")

        crypto_proto_message = cls(
            bytes_=bytes_,
        )

        return crypto_proto_message
