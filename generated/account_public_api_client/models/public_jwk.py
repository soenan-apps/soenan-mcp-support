from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.public_jwk_alg import PublicJWKAlg
from ..models.public_jwk_kty import PublicJWKKty
from ..models.public_jwk_use import PublicJWKUse

T = TypeVar("T", bound="PublicJWK")


@_attrs_define
class PublicJWK:
    """
    Attributes:
        kty (PublicJWKKty):
        use (PublicJWKUse):
        alg (PublicJWKAlg):
        kid (str):
        n (str):
        e (str):
    """

    kty: PublicJWKKty
    use: PublicJWKUse
    alg: PublicJWKAlg
    kid: str
    n: str
    e: str

    def to_dict(self) -> dict[str, Any]:
        kty = self.kty.value

        use = self.use.value

        alg = self.alg.value

        kid = self.kid

        n = self.n

        e = self.e

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kty": kty,
                "use": use,
                "alg": alg,
                "kid": kid,
                "n": n,
                "e": e,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kty = PublicJWKKty(d.pop("kty"))

        use = PublicJWKUse(d.pop("use"))

        alg = PublicJWKAlg(d.pop("alg"))

        kid = d.pop("kid")

        n = d.pop("n")

        e = d.pop("e")

        public_jwk = cls(
            kty=kty,
            use=use,
            alg=alg,
            kid=kid,
            n=n,
            e=e,
        )

        return public_jwk
