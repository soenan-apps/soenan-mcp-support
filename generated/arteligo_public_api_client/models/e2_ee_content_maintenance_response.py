from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_content_maintenance_status import E2EeContentMaintenanceStatus


T = TypeVar("T", bound="E2EeContentMaintenanceResponse")


@_attrs_define
class E2EeContentMaintenanceResponse:
    """
    Attributes:
        migration (E2EeContentMaintenanceStatus | None):
    """

    migration: E2EeContentMaintenanceStatus | None

    def to_dict(self) -> dict[str, Any]:
        from ..models.e2_ee_content_maintenance_status import (
            E2EeContentMaintenanceStatus,
        )

        migration: dict[str, Any] | None
        if isinstance(self.migration, E2EeContentMaintenanceStatus):
            migration = self.migration.to_dict()
        else:
            migration = self.migration

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "migration": migration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_content_maintenance_status import (
            E2EeContentMaintenanceStatus,
        )

        d = dict(src_dict)

        def _parse_migration(data: object) -> E2EeContentMaintenanceStatus | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                migration_type_1 = E2EeContentMaintenanceStatus.from_dict(data)

                return migration_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(E2EeContentMaintenanceStatus | None, data)

        migration = _parse_migration(d.pop("migration"))

        e2_ee_content_maintenance_response = cls(
            migration=migration,
        )

        return e2_ee_content_maintenance_response
