from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_capability_headers import E2EeCapabilityHeaders


T = TypeVar("T", bound="E2EeCapability")


@_attrs_define
class E2EeCapability:
    """
    Attributes:
        method (str):
        url (str):
        headers (E2EeCapabilityHeaders):
        expires_at (int):
        content_length (int | Unset):
    """

    method: str
    url: str
    headers: E2EeCapabilityHeaders
    expires_at: int
    content_length: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        method = self.method

        url = self.url

        headers = self.headers.to_dict()

        expires_at = self.expires_at

        content_length = self.content_length

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "expires_at": expires_at,
            }
        )
        if content_length is not UNSET:
            field_dict["content_length"] = content_length

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_capability_headers import E2EeCapabilityHeaders

        d = dict(src_dict)
        method = d.pop("method")

        url = d.pop("url")

        headers = E2EeCapabilityHeaders.from_dict(d.pop("headers"))

        expires_at = d.pop("expires_at")

        content_length = d.pop("content_length", UNSET)

        e2_ee_capability = cls(
            method=method,
            url=url,
            headers=headers,
            expires_at=expires_at,
            content_length=content_length,
        )

        return e2_ee_capability
