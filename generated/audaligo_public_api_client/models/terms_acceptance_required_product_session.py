from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.terms_acceptance_required_product_session_kind import TermsAcceptanceRequiredProductSessionKind

if TYPE_CHECKING:
    from ..models.product_session_metadata import ProductSessionMetadata
    from ..models.product_session_user import ProductSessionUser
    from ..models.terms_version import TermsVersion


T = TypeVar("T", bound="TermsAcceptanceRequiredProductSession")


@_attrs_define
class TermsAcceptanceRequiredProductSession:
    """
    Attributes:
        kind (TermsAcceptanceRequiredProductSessionKind):
        authenticated (bool):
        user (ProductSessionUser):
        session (ProductSessionMetadata):
        required_terms (TermsVersion):
    """

    kind: TermsAcceptanceRequiredProductSessionKind
    authenticated: bool
    user: ProductSessionUser
    session: ProductSessionMetadata
    required_terms: TermsVersion

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        authenticated = self.authenticated

        user = self.user.to_dict()

        session = self.session.to_dict()

        required_terms = self.required_terms.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "authenticated": authenticated,
                "user": user,
                "session": session,
                "requiredTerms": required_terms,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.product_session_metadata import ProductSessionMetadata
        from ..models.product_session_user import ProductSessionUser
        from ..models.terms_version import TermsVersion

        d = dict(src_dict)
        kind = TermsAcceptanceRequiredProductSessionKind(d.pop("kind"))

        authenticated = d.pop("authenticated")

        user = ProductSessionUser.from_dict(d.pop("user"))

        session = ProductSessionMetadata.from_dict(d.pop("session"))

        required_terms = TermsVersion.from_dict(d.pop("requiredTerms"))

        terms_acceptance_required_product_session = cls(
            kind=kind,
            authenticated=authenticated,
            user=user,
            session=session,
            required_terms=required_terms,
        )

        return terms_acceptance_required_product_session
