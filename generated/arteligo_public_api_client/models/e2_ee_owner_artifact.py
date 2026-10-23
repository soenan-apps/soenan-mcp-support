from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerArtifact")


@_attrs_define
class E2EeOwnerArtifact:
    """
    Attributes:
        signed_command (E2EeSignedCommand):
        manifest_digest (str | Unset):
        preparation_digest (str | Unset):
        state (str | Unset):
    """

    signed_command: E2EeSignedCommand
    manifest_digest: str | Unset = UNSET
    preparation_digest: str | Unset = UNSET
    state: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        signed_command = self.signed_command.to_dict()

        manifest_digest = self.manifest_digest

        preparation_digest = self.preparation_digest

        state = self.state

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "signed_command": signed_command,
            }
        )
        if manifest_digest is not UNSET:
            field_dict["manifest_digest"] = manifest_digest
        if preparation_digest is not UNSET:
            field_dict["preparation_digest"] = preparation_digest
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        manifest_digest = d.pop("manifest_digest", UNSET)

        preparation_digest = d.pop("preparation_digest", UNSET)

        state = d.pop("state", UNSET)

        e2_ee_owner_artifact = cls(
            signed_command=signed_command,
            manifest_digest=manifest_digest,
            preparation_digest=preparation_digest,
            state=state,
        )

        return e2_ee_owner_artifact
