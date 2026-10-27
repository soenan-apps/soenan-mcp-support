from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.organization_close_conflict_error import OrganizationCloseConflictError

if TYPE_CHECKING:
    from ..models.organization_close_entitlement_pending import (
        OrganizationCloseEntitlementPending,
    )
    from ..models.organization_close_simple_blocker import (
        OrganizationCloseSimpleBlocker,
    )
    from ..models.organization_close_subscription_cancellation_scheduled import (
        OrganizationCloseSubscriptionCancellationScheduled,
    )


T = TypeVar("T", bound="OrganizationCloseConflict")


@_attrs_define
class OrganizationCloseConflict:
    """
    Attributes:
        error (OrganizationCloseConflictError):
        blockers (list[OrganizationCloseEntitlementPending | OrganizationCloseSimpleBlocker |
            OrganizationCloseSubscriptionCancellationScheduled]):
    """

    error: OrganizationCloseConflictError
    blockers: list[
        OrganizationCloseEntitlementPending
        | OrganizationCloseSimpleBlocker
        | OrganizationCloseSubscriptionCancellationScheduled
    ]

    def to_dict(self) -> dict[str, Any]:
        from ..models.organization_close_simple_blocker import (
            OrganizationCloseSimpleBlocker,
        )
        from ..models.organization_close_subscription_cancellation_scheduled import (
            OrganizationCloseSubscriptionCancellationScheduled,
        )

        error = self.error.value

        blockers = []
        for blockers_item_data in self.blockers:
            blockers_item: dict[str, Any]
            if isinstance(blockers_item_data, OrganizationCloseSimpleBlocker):
                blockers_item = blockers_item_data.to_dict()
            elif isinstance(
                blockers_item_data, OrganizationCloseSubscriptionCancellationScheduled
            ):
                blockers_item = blockers_item_data.to_dict()
            else:
                blockers_item = blockers_item_data.to_dict()

            blockers.append(blockers_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "error": error,
                "blockers": blockers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organization_close_entitlement_pending import (
            OrganizationCloseEntitlementPending,
        )
        from ..models.organization_close_simple_blocker import (
            OrganizationCloseSimpleBlocker,
        )
        from ..models.organization_close_subscription_cancellation_scheduled import (
            OrganizationCloseSubscriptionCancellationScheduled,
        )

        d = dict(src_dict)
        error = OrganizationCloseConflictError(d.pop("error"))

        blockers = []
        _blockers = d.pop("blockers")
        for blockers_item_data in _blockers:

            def _parse_blockers_item(
                data: object,
            ) -> (
                OrganizationCloseEntitlementPending
                | OrganizationCloseSimpleBlocker
                | OrganizationCloseSubscriptionCancellationScheduled
            ):
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_organization_close_blocker_type_0 = (
                        OrganizationCloseSimpleBlocker.from_dict(data)
                    )

                    return componentsschemas_organization_close_blocker_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_organization_close_blocker_type_1 = (
                        OrganizationCloseSubscriptionCancellationScheduled.from_dict(
                            data
                        )
                    )

                    return componentsschemas_organization_close_blocker_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_organization_close_blocker_type_2 = (
                    OrganizationCloseEntitlementPending.from_dict(data)
                )

                return componentsschemas_organization_close_blocker_type_2

            blockers_item = _parse_blockers_item(blockers_item_data)

            blockers.append(blockers_item)

        organization_close_conflict = cls(
            error=error,
            blockers=blockers,
        )

        return organization_close_conflict
