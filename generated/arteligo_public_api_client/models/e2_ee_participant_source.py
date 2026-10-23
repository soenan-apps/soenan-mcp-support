from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeParticipantSource")


@_attrs_define
class E2EeParticipantSource:
    """
    Attributes:
        scope_id (str):
        links (list[E2EeEnvelope]):
        owner_statements (list[E2EeSignedCommand]):
        project_command (E2EeSignedCommand):
        org_command (E2EeSignedCommand):
    """

    scope_id: str
    links: list[E2EeEnvelope]
    owner_statements: list[E2EeSignedCommand]
    project_command: E2EeSignedCommand
    org_command: E2EeSignedCommand

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        links = []
        for links_item_data in self.links:
            links_item = links_item_data.to_dict()
            links.append(links_item)

        owner_statements = []
        for owner_statements_item_data in self.owner_statements:
            owner_statements_item = owner_statements_item_data.to_dict()
            owner_statements.append(owner_statements_item)

        project_command = self.project_command.to_dict()

        org_command = self.org_command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "links": links,
                "owner_statements": owner_statements,
                "project_command": project_command,
                "org_command": org_command,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        links = []
        _links = d.pop("links")
        for links_item_data in _links:
            links_item = E2EeEnvelope.from_dict(links_item_data)

            links.append(links_item)

        owner_statements = []
        _owner_statements = d.pop("owner_statements")
        for owner_statements_item_data in _owner_statements:
            owner_statements_item = E2EeSignedCommand.from_dict(
                owner_statements_item_data
            )

            owner_statements.append(owner_statements_item)

        project_command = E2EeSignedCommand.from_dict(d.pop("project_command"))

        org_command = E2EeSignedCommand.from_dict(d.pop("org_command"))

        e2_ee_participant_source = cls(
            scope_id=scope_id,
            links=links,
            owner_statements=owner_statements,
            project_command=project_command,
            org_command=org_command,
        )

        return e2_ee_participant_source
