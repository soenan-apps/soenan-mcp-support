from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.authenticated_product_session_kind import AuthenticatedProductSessionKind

if TYPE_CHECKING:
    from ..models.product_session_metadata import ProductSessionMetadata
    from ..models.product_session_organization import ProductSessionOrganization
    from ..models.product_session_user import ProductSessionUser


T = TypeVar("T", bound="AuthenticatedProductSession")


@_attrs_define
class AuthenticatedProductSession:
    """
    Attributes:
        kind (AuthenticatedProductSessionKind):
        authenticated (bool):
        user (ProductSessionUser):
        active_organization (ProductSessionOrganization):
        joined_organizations (list[ProductSessionOrganization]):
        session (ProductSessionMetadata):
    """

    kind: AuthenticatedProductSessionKind
    authenticated: bool
    user: ProductSessionUser
    active_organization: ProductSessionOrganization
    joined_organizations: list[ProductSessionOrganization]
    session: ProductSessionMetadata

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        authenticated = self.authenticated

        user = self.user.to_dict()

        active_organization = self.active_organization.to_dict()

        joined_organizations = []
        for joined_organizations_item_data in self.joined_organizations:
            joined_organizations_item = joined_organizations_item_data.to_dict()
            joined_organizations.append(joined_organizations_item)

        session = self.session.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "authenticated": authenticated,
                "user": user,
                "activeOrganization": active_organization,
                "joinedOrganizations": joined_organizations,
                "session": session,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.product_session_metadata import ProductSessionMetadata
        from ..models.product_session_organization import ProductSessionOrganization
        from ..models.product_session_user import ProductSessionUser

        d = dict(src_dict)
        kind = AuthenticatedProductSessionKind(d.pop("kind"))

        authenticated = d.pop("authenticated")

        user = ProductSessionUser.from_dict(d.pop("user"))

        active_organization = ProductSessionOrganization.from_dict(d.pop("activeOrganization"))

        joined_organizations = []
        _joined_organizations = d.pop("joinedOrganizations")
        for joined_organizations_item_data in _joined_organizations:
            joined_organizations_item = ProductSessionOrganization.from_dict(joined_organizations_item_data)

            joined_organizations.append(joined_organizations_item)

        session = ProductSessionMetadata.from_dict(d.pop("session"))

        authenticated_product_session = cls(
            kind=kind,
            authenticated=authenticated,
            user=user,
            active_organization=active_organization,
            joined_organizations=joined_organizations,
            session=session,
        )

        return authenticated_product_session
