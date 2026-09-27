from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="WrappedDataKey")


@_attrs_define
class WrappedDataKey:
    """
    Attributes:
        nonce_b64_u (str):
        ciphertext_b64_u (str):
    """

    nonce_b64_u: str
    ciphertext_b64_u: str

    def to_dict(self) -> dict[str, Any]:
        nonce_b64_u = self.nonce_b64_u

        ciphertext_b64_u = self.ciphertext_b64_u

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "nonceB64u": nonce_b64_u,
                "ciphertextB64u": ciphertext_b64_u,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        nonce_b64_u = d.pop("nonceB64u")

        ciphertext_b64_u = d.pop("ciphertextB64u")

        wrapped_data_key = cls(
            nonce_b64_u=nonce_b64_u,
            ciphertext_b64_u=ciphertext_b64_u,
        )

        return wrapped_data_key
