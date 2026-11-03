from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OwnerKeyOperationPrepared")


@_attrs_define
class OwnerKeyOperationPrepared:
    """
    Attributes:
        operation_id (str):
        actor_subject (str):
        environment (str):
        local_state_digest (str):
        manifest_digest (str):
        state_digest (str):
        authorization_not_after_unix (int):
        proof_read_capability (str):
    """

    operation_id: str
    actor_subject: str
    environment: str
    local_state_digest: str
    manifest_digest: str
    state_digest: str
    authorization_not_after_unix: int
    proof_read_capability: str

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        actor_subject = self.actor_subject

        environment = self.environment

        local_state_digest = self.local_state_digest

        manifest_digest = self.manifest_digest

        state_digest = self.state_digest

        authorization_not_after_unix = self.authorization_not_after_unix

        proof_read_capability = self.proof_read_capability

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "actor_subject": actor_subject,
                "environment": environment,
                "local_state_digest": local_state_digest,
                "manifest_digest": manifest_digest,
                "state_digest": state_digest,
                "authorization_not_after_unix": authorization_not_after_unix,
                "proof_read_capability": proof_read_capability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        actor_subject = d.pop("actor_subject")

        environment = d.pop("environment")

        local_state_digest = d.pop("local_state_digest")

        manifest_digest = d.pop("manifest_digest")

        state_digest = d.pop("state_digest")

        authorization_not_after_unix = d.pop("authorization_not_after_unix")

        proof_read_capability = d.pop("proof_read_capability")

        owner_key_operation_prepared = cls(
            operation_id=operation_id,
            actor_subject=actor_subject,
            environment=environment,
            local_state_digest=local_state_digest,
            manifest_digest=manifest_digest,
            state_digest=state_digest,
            authorization_not_after_unix=authorization_not_after_unix,
            proof_read_capability=proof_read_capability,
        )

        return owner_key_operation_prepared
