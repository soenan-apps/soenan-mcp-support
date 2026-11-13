from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from typing import Literal

from ._crypto import E2eeError
from ._local_broker import MemoryGrant
from ._oauth import ProfileVault


@dataclass(frozen=True)
class LocalMcpApproval:
    account_origin: str
    arteligo_origin: str
    subject: str
    environment_authorization_id: str
    projects: tuple[str, ...]
    access: Literal["read-only", "update"]
    input_directory: str | None
    output_directory: str | None
    expires_at: int

    @classmethod
    def approve(
        cls,
        vault: ProfileVault,
        *,
        projects: frozenset[str],
        access: Literal["read-only", "update"],
        input_directory: str | None,
        output_directory: str | None,
        expires_at: int,
    ) -> LocalMcpApproval:
        authorization = vault.environment_authorization()
        if authorization is None:
            raise E2eeError("environment_authorization_required")
        if not time.time() < expires_at <= authorization.expires_at:
            raise E2eeError("invalid_local_approval_expiry")
        approval = cls(
            vault.account_origin,
            vault.arteligo_origin,
            authorization.subject,
            authorization.authorization_id,
            tuple(sorted(projects)),
            access,
            input_directory,
            output_directory,
            expires_at,
        )
        approval.worker_grant(vault)
        with vault.store.credential(
            cls._key(
                approval.account_origin, approval.arteligo_origin, approval.subject
            )
        ) as item:
            previous = item.read()
            if previous is not None:
                saved = cls._parse(previous)
                if (
                    saved.account_origin != approval.account_origin
                    or saved.arteligo_origin != approval.arteligo_origin
                    or saved.subject != approval.subject
                ):
                    raise E2eeError("local_mcp_approval_binding_mismatch")
                if (
                    saved.environment_authorization_id
                    == approval.environment_authorization_id
                ):
                    if (
                        not set(approval.projects) <= set(saved.projects)
                        or (saved.access == "read-only" and approval.access == "update")
                        or approval.expires_at > saved.expires_at
                        or approval.input_directory not in (None, saved.input_directory)
                        or approval.output_directory
                        not in (None, saved.output_directory)
                    ):
                        raise E2eeError("local_mcp_approval_expansion")
            item.replace(json.dumps(asdict(approval), separators=(",", ":")))
        return approval

    @classmethod
    def load(cls, vault: ProfileVault) -> LocalMcpApproval:
        authorization = vault.environment_authorization()
        if authorization is None:
            raise E2eeError("environment_authorization_required")
        key = cls._key(
            vault.account_origin, vault.arteligo_origin, authorization.subject
        )
        with vault.store.credential(key) as item:
            raw = item.read()
        if raw is None:
            raise E2eeError("local_mcp_approval_required")
        approval = cls._parse(raw)
        approval.worker_grant(vault)
        return approval

    @classmethod
    def _parse(cls, raw: str) -> LocalMcpApproval:
        try:
            value = json.loads(raw)
            if not isinstance(value, dict) or set(value) != set(
                cls.__dataclass_fields__
            ):
                raise ValueError
            if (
                any(
                    not isinstance(value[name], str) or not value[name]
                    for name in (
                        "account_origin",
                        "arteligo_origin",
                        "subject",
                        "environment_authorization_id",
                    )
                )
                or not isinstance(value["projects"], list)
                or not value["projects"]
                or any(
                    not isinstance(project, str) or not project
                    for project in value["projects"]
                )
                or len(set(value["projects"])) != len(value["projects"])
                or value["access"] not in {"read-only", "update"}
                or type(value["expires_at"]) is not int
                or not math.isfinite(value["expires_at"])
                or any(
                    path is not None
                    and (
                        not isinstance(path, str)
                        or not os.path.isabs(path)
                        or "\0" in path
                    )
                    for path in (value["input_directory"], value["output_directory"])
                )
            ):
                raise ValueError
            value["projects"] = tuple(value["projects"])
            approval = cls(**value)
        except (ValueError, TypeError, KeyError, OverflowError):
            raise E2eeError("invalid_local_mcp_approval") from None
        return approval

    @staticmethod
    def _key(account: str, arteligo: str, subject: str) -> str:
        binding = json.dumps([account, arteligo, subject], separators=(",", ":"))
        return "local-mcp-approval:" + hashlib.sha256(binding.encode()).hexdigest()

    def worker_grant(self, vault: ProfileVault) -> MemoryGrant:
        authorization = vault.environment_authorization()
        if authorization is None or (
            self.account_origin != vault.account_origin
            or self.arteligo_origin != vault.arteligo_origin
            or self.subject != authorization.subject
            or self.environment_authorization_id != authorization.authorization_id
        ):
            raise E2eeError("local_mcp_approval_binding_mismatch")
        if "arteligo:app" not in authorization.scope.split():
            raise E2eeError("local_mcp_approval_scope_denied")
        if self.expires_at > authorization.expires_at:
            raise E2eeError("local_mcp_approval_expansion")
        remaining = int(min(self.expires_at, authorization.expires_at) - time.time())
        if remaining <= 0:
            raise E2eeError("local_mcp_approval_expired")
        grant = MemoryGrant(frozenset(self.projects), self.access, min(3600, remaining))
        grant.expires_at = min(
            grant.expires_at, self.expires_at, authorization.expires_at
        )
        return grant
