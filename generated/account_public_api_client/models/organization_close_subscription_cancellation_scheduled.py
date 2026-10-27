from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.organization_close_subscription_cancellation_scheduled_kind import (
    OrganizationCloseSubscriptionCancellationScheduledKind,
)

T = TypeVar("T", bound="OrganizationCloseSubscriptionCancellationScheduled")


@_attrs_define
class OrganizationCloseSubscriptionCancellationScheduled:
    """
    Attributes:
        kind (OrganizationCloseSubscriptionCancellationScheduledKind):
        effective_at (datetime.datetime):
    """

    kind: OrganizationCloseSubscriptionCancellationScheduledKind
    effective_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        effective_at = self.effective_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "effectiveAt": effective_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = OrganizationCloseSubscriptionCancellationScheduledKind(d.pop("kind"))

        effective_at = isoparse(d.pop("effectiveAt"))

        organization_close_subscription_cancellation_scheduled = cls(
            kind=kind,
            effective_at=effective_at,
        )

        return organization_close_subscription_cancellation_scheduled
