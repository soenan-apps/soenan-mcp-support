from __future__ import annotations

from collections.abc import Mapping
import hashlib
import re
import secrets
from typing import Any

from ._crypto import E2eeError, decode, wipe


_COMMITTED_ID = re.compile(r"prj_([0-9a-f]{64})_[0-9a-f]{32}\Z")
_RANDOM_ID = re.compile(r"prj_[0-9a-f]{32}\Z")


def _creator_commitment(signing_public_key: str) -> str:
    key = decode(signing_public_key)
    try:
        if len(key) != 32:
            raise E2eeError("invalid_device")
        digest = hashlib.sha256(b"arteligo-project-creator-v1\n")
        digest.update(key)
        return digest.hexdigest()
    finally:
        wipe(key)


def new_project_id(signing_public_key: str) -> str:
    return f"prj_{_creator_commitment(signing_public_key)}_{secrets.token_hex(16)}"


def has_committed_creator(project_id: str) -> bool:
    return _COMMITTED_ID.fullmatch(project_id) is not None


def is_canonical_project_id(project_id: object) -> bool:
    return isinstance(project_id, str) and (
        _RANDOM_ID.fullmatch(project_id) is not None or has_committed_creator(project_id)
    )


def committed_creator(project_id: str, signing_public_key: str) -> bool:
    match = _COMMITTED_ID.fullmatch(project_id)
    return match is not None and secrets.compare_digest(
        match.group(1), _creator_commitment(signing_public_key),
    )


def creation_recovery_id(body: Mapping[str, Any], signer: str) -> str:
    envelopes = body.get("envelopes")
    if not isinstance(envelopes, list):
        raise E2eeError("owner_project_source_mismatch")
    roots = [value for value in envelopes
             if isinstance(value, dict) and value.get("recipient_kind") == "recovery"]
    if not roots:
        raise E2eeError("owner_identity_verification_required")
    if len(roots) != 1:
        raise E2eeError("owner_project_source_mismatch")
    root = roots[0]
    identifier = root.get("recipient_id")
    if (not isinstance(identifier, str) or not identifier
            or root.get("scope_id") != body.get("project_id")
            or root.get("key_epoch") != 1 or root.get("sender_device_id") != signer):
        raise E2eeError("owner_project_source_mismatch")
    return identifier
