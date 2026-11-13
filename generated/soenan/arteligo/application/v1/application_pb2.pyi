from soenan.arteligo.crypto.v1 import crypto_pb2 as _crypto_pb2
from soenan.account.crypto.v1 import crypto_pb2 as _crypto_pb2_1
from soenan.arteligo.domain.v1 import domain_pb2 as _domain_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadCryptoRequest(_message.Message):
    __slots__ = ("value_ids", "protection_keys", "project_id", "device_id", "kind", "cursor", "limit", "view", "value_id", "live_only", "id_prefix", "snapshot_cursor", "immutable_only", "comment_cursor", "history_cursor", "comment_limit", "history_limit", "comment_anchor_id")
    VALUE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_KEYS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    VIEW_FIELD_NUMBER: _ClassVar[int]
    VALUE_ID_FIELD_NUMBER: _ClassVar[int]
    LIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    ID_PREFIX_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    IMMUTABLE_ONLY_FIELD_NUMBER: _ClassVar[int]
    COMMENT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    HISTORY_CURSOR_FIELD_NUMBER: _ClassVar[int]
    COMMENT_LIMIT_FIELD_NUMBER: _ClassVar[int]
    HISTORY_LIMIT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_ANCHOR_ID_FIELD_NUMBER: _ClassVar[int]
    value_ids: _containers.RepeatedScalarFieldContainer[str]
    protection_keys: _containers.RepeatedCompositeFieldContainer[_crypto_pb2_1.KeyRef]
    project_id: str
    device_id: str
    kind: str
    cursor: str
    limit: int
    view: str
    value_id: str
    live_only: bool
    id_prefix: str
    snapshot_cursor: int
    immutable_only: bool
    comment_cursor: _domain_pb2.CommentCursor
    history_cursor: str
    comment_limit: int
    history_limit: int
    comment_anchor_id: str
    def __init__(self, value_ids: _Optional[_Iterable[str]] = ..., protection_keys: _Optional[_Iterable[_Union[_crypto_pb2_1.KeyRef, _Mapping]]] = ..., project_id: _Optional[str] = ..., device_id: _Optional[str] = ..., kind: _Optional[str] = ..., cursor: _Optional[str] = ..., limit: _Optional[int] = ..., view: _Optional[str] = ..., value_id: _Optional[str] = ..., live_only: bool = ..., id_prefix: _Optional[str] = ..., snapshot_cursor: _Optional[int] = ..., immutable_only: bool = ..., comment_cursor: _Optional[_Union[_domain_pb2.CommentCursor, _Mapping]] = ..., history_cursor: _Optional[str] = ..., comment_limit: _Optional[int] = ..., history_limit: _Optional[int] = ..., comment_anchor_id: _Optional[str] = ...) -> None: ...

class CommitCryptoRequest(_message.Message):
    __slots__ = ("command", "project_id", "signer_public_key")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNER_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    command: _crypto_pb2_1.SignedBytes
    project_id: str
    signer_public_key: bytes
    def __init__(self, command: _Optional[_Union[_crypto_pb2_1.SignedBytes, _Mapping]] = ..., project_id: _Optional[str] = ..., signer_public_key: _Optional[bytes] = ...) -> None: ...

class CommitCryptoResponse(_message.Message):
    __slots__ = ("receipt", "bundle")
    RECEIPT_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    receipt: _crypto_pb2.CommitReceiptBody
    bundle: _crypto_pb2.CryptoReadBundle
    def __init__(self, receipt: _Optional[_Union[_crypto_pb2.CommitReceiptBody, _Mapping]] = ..., bundle: _Optional[_Union[_crypto_pb2.CryptoReadBundle, _Mapping]] = ...) -> None: ...

class RecordHead(_message.Message):
    __slots__ = ("id", "revision", "kind", "deleted", "immutable", "author_device_id", "cursor")
    ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    IMMUTABLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    revision: int
    kind: str
    deleted: bool
    immutable: bool
    author_device_id: str
    cursor: str
    def __init__(self, id: _Optional[str] = ..., revision: _Optional[int] = ..., kind: _Optional[str] = ..., deleted: bool = ..., immutable: bool = ..., author_device_id: _Optional[str] = ..., cursor: _Optional[str] = ...) -> None: ...

class ReadCryptoResponse(_message.Message):
    __slots__ = ("bundle", "heads", "cursor", "has_more", "configuration", "snapshot_cursor", "comments", "latest_comment_sequence", "next_comment_cursor", "next_history_cursor", "has_more_comments", "has_more_history", "project")
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    HEADS_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    LATEST_COMMENT_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    NEXT_COMMENT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    NEXT_HISTORY_CURSOR_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_COMMENTS_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    bundle: _crypto_pb2.CryptoReadBundle
    heads: _containers.RepeatedCompositeFieldContainer[RecordHead]
    cursor: str
    has_more: bool
    configuration: CryptoConfiguration
    snapshot_cursor: int
    comments: _containers.RepeatedCompositeFieldContainer[CommentViewItem]
    latest_comment_sequence: int
    next_comment_cursor: _domain_pb2.CommentCursor
    next_history_cursor: str
    has_more_comments: bool
    has_more_history: bool
    project: ProjectCatalogEntry
    def __init__(self, bundle: _Optional[_Union[_crypto_pb2.CryptoReadBundle, _Mapping]] = ..., heads: _Optional[_Iterable[_Union[RecordHead, _Mapping]]] = ..., cursor: _Optional[str] = ..., has_more: bool = ..., configuration: _Optional[_Union[CryptoConfiguration, _Mapping]] = ..., snapshot_cursor: _Optional[int] = ..., comments: _Optional[_Iterable[_Union[CommentViewItem, _Mapping]]] = ..., latest_comment_sequence: _Optional[int] = ..., next_comment_cursor: _Optional[_Union[_domain_pb2.CommentCursor, _Mapping]] = ..., next_history_cursor: _Optional[str] = ..., has_more_comments: bool = ..., has_more_history: bool = ..., project: _Optional[_Union[ProjectCatalogEntry, _Mapping]] = ...) -> None: ...

class ContentChangeHint(_message.Message):
    __slots__ = ("heads",)
    HEADS_FIELD_NUMBER: _ClassVar[int]
    heads: _containers.RepeatedCompositeFieldContainer[RecordHead]
    def __init__(self, heads: _Optional[_Iterable[_Union[RecordHead, _Mapping]]] = ...) -> None: ...

class ProjectCreateRequest(_message.Message):
    __slots__ = ("project_id", "mutation", "group_id", "shared", "protection_key")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MUTATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SHARED_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_KEY_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    mutation: CommitCryptoRequest
    group_id: str
    shared: bool
    protection_key: _crypto_pb2_1.KeyRef
    def __init__(self, project_id: _Optional[str] = ..., mutation: _Optional[_Union[CommitCryptoRequest, _Mapping]] = ..., group_id: _Optional[str] = ..., shared: bool = ..., protection_key: _Optional[_Union[_crypto_pb2_1.KeyRef, _Mapping]] = ...) -> None: ...

class InvitationRequest(_message.Message):
    __slots__ = ("project_id", "invitation_id", "descriptor")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    invitation_id: str
    descriptor: _crypto_pb2_1.SignedBytes
    def __init__(self, project_id: _Optional[str] = ..., invitation_id: _Optional[str] = ..., descriptor: _Optional[_Union[_crypto_pb2_1.SignedBytes, _Mapping]] = ...) -> None: ...

class InvitationApproval(_message.Message):
    __slots__ = ("project_id", "invitation_id", "subject", "mutation")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    MUTATION_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    invitation_id: str
    subject: str
    mutation: CommitCryptoRequest
    def __init__(self, project_id: _Optional[str] = ..., invitation_id: _Optional[str] = ..., subject: _Optional[str] = ..., mutation: _Optional[_Union[CommitCryptoRequest, _Mapping]] = ...) -> None: ...

class OwnerDeliveryRequest(_message.Message):
    __slots__ = ("project_id", "subject", "mutation")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    MUTATION_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    subject: str
    mutation: CommitCryptoRequest
    def __init__(self, project_id: _Optional[str] = ..., subject: _Optional[str] = ..., mutation: _Optional[_Union[CommitCryptoRequest, _Mapping]] = ...) -> None: ...

class RecordMutationBinding(_message.Message):
    __slots__ = ("heads", "preconditions", "deleted_objects", "object_ids", "thread_id", "project_policy", "invitation", "membership", "files", "comments", "object_effects")
    HEADS_FIELD_NUMBER: _ClassVar[int]
    PRECONDITIONS_FIELD_NUMBER: _ClassVar[int]
    DELETED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_POLICY_FIELD_NUMBER: _ClassVar[int]
    INVITATION_FIELD_NUMBER: _ClassVar[int]
    MEMBERSHIP_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_EFFECTS_FIELD_NUMBER: _ClassVar[int]
    heads: _containers.RepeatedCompositeFieldContainer[RecordHead]
    preconditions: _containers.RepeatedCompositeFieldContainer[RecordPrecondition]
    deleted_objects: _containers.RepeatedScalarFieldContainer[str]
    object_ids: _containers.RepeatedScalarFieldContainer[str]
    thread_id: str
    project_policy: ProjectPolicyBinding
    invitation: InvitationBinding
    membership: MembershipBinding
    files: _containers.RepeatedCompositeFieldContainer[FileRevisionBinding]
    comments: _containers.RepeatedCompositeFieldContainer[CommentRevisionBinding]
    object_effects: _containers.RepeatedCompositeFieldContainer[ObjectEffect]
    def __init__(self, heads: _Optional[_Iterable[_Union[RecordHead, _Mapping]]] = ..., preconditions: _Optional[_Iterable[_Union[RecordPrecondition, _Mapping]]] = ..., deleted_objects: _Optional[_Iterable[str]] = ..., object_ids: _Optional[_Iterable[str]] = ..., thread_id: _Optional[str] = ..., project_policy: _Optional[_Union[ProjectPolicyBinding, _Mapping]] = ..., invitation: _Optional[_Union[InvitationBinding, _Mapping]] = ..., membership: _Optional[_Union[MembershipBinding, _Mapping]] = ..., files: _Optional[_Iterable[_Union[FileRevisionBinding, _Mapping]]] = ..., comments: _Optional[_Iterable[_Union[CommentRevisionBinding, _Mapping]]] = ..., object_effects: _Optional[_Iterable[_Union[ObjectEffect, _Mapping]]] = ...) -> None: ...

class ProjectPolicyBinding(_message.Message):
    __slots__ = ("project_id", "group_id", "shared", "current_protection_key", "expected_distribution_revision", "prepare_owner_deliveries", "lifecycle")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SHARED_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PROTECTION_KEY_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_DISTRIBUTION_REVISION_FIELD_NUMBER: _ClassVar[int]
    PREPARE_OWNER_DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    group_id: str
    shared: bool
    current_protection_key: _crypto_pb2_1.KeyRef
    expected_distribution_revision: int
    prepare_owner_deliveries: bool
    lifecycle: str
    def __init__(self, project_id: _Optional[str] = ..., group_id: _Optional[str] = ..., shared: bool = ..., current_protection_key: _Optional[_Union[_crypto_pb2_1.KeyRef, _Mapping]] = ..., expected_distribution_revision: _Optional[int] = ..., prepare_owner_deliveries: bool = ..., lifecycle: _Optional[str] = ...) -> None: ...

class InvitationBinding(_message.Message):
    __slots__ = ("invitation_id", "expires_at", "secret_digest", "inviter_root_digest", "descriptor_digest")
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    SECRET_DIGEST_FIELD_NUMBER: _ClassVar[int]
    INVITER_ROOT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_DIGEST_FIELD_NUMBER: _ClassVar[int]
    invitation_id: str
    expires_at: int
    secret_digest: bytes
    inviter_root_digest: bytes
    descriptor_digest: bytes
    def __init__(self, invitation_id: _Optional[str] = ..., expires_at: _Optional[int] = ..., secret_digest: _Optional[bytes] = ..., inviter_root_digest: _Optional[bytes] = ..., descriptor_digest: _Optional[bytes] = ...) -> None: ...

class MembershipBinding(_message.Message):
    __slots__ = ("subject", "expected_revision", "role", "revoked", "owner_candidate")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_REVISION_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    REVOKED_FIELD_NUMBER: _ClassVar[int]
    OWNER_CANDIDATE_FIELD_NUMBER: _ClassVar[int]
    subject: str
    expected_revision: int
    role: str
    revoked: bool
    owner_candidate: bool
    def __init__(self, subject: _Optional[str] = ..., expected_revision: _Optional[int] = ..., role: _Optional[str] = ..., revoked: bool = ..., owner_candidate: bool = ...) -> None: ...

class FileRevisionBinding(_message.Message):
    __slots__ = ("file_id", "revision", "metadata_value_id", "metadata_revision", "original_object_id", "preview_object_id", "thread_id")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    METADATA_VALUE_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_REVISION_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    revision: int
    metadata_value_id: str
    metadata_revision: int
    original_object_id: str
    preview_object_id: str
    thread_id: str
    def __init__(self, file_id: _Optional[str] = ..., revision: _Optional[int] = ..., metadata_value_id: _Optional[str] = ..., metadata_revision: _Optional[int] = ..., original_object_id: _Optional[str] = ..., preview_object_id: _Optional[str] = ..., thread_id: _Optional[str] = ...) -> None: ...

class CommentRevisionBinding(_message.Message):
    __slots__ = ("thread_id", "comment_id", "revision", "value_id", "value_revision", "origin", "thread_head", "body_head", "resolution", "text_revisions", "anchor_id", "sequence", "reply_sequence", "operation", "parent_comment_id")
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    VALUE_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_REVISION_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    THREAD_HEAD_FIELD_NUMBER: _ClassVar[int]
    BODY_HEAD_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    TEXT_REVISIONS_FIELD_NUMBER: _ClassVar[int]
    ANCHOR_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REPLY_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    PARENT_COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    thread_id: str
    comment_id: str
    revision: int
    value_id: str
    value_revision: int
    origin: _crypto_pb2.TargetHead
    thread_head: _crypto_pb2.TargetHead
    body_head: _crypto_pb2.TargetHead
    resolution: _crypto_pb2.TargetHead
    text_revisions: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.TargetHead]
    anchor_id: str
    sequence: int
    reply_sequence: int
    operation: str
    parent_comment_id: str
    def __init__(self, thread_id: _Optional[str] = ..., comment_id: _Optional[str] = ..., revision: _Optional[int] = ..., value_id: _Optional[str] = ..., value_revision: _Optional[int] = ..., origin: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., thread_head: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., body_head: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., resolution: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., text_revisions: _Optional[_Iterable[_Union[_crypto_pb2.TargetHead, _Mapping]]] = ..., anchor_id: _Optional[str] = ..., sequence: _Optional[int] = ..., reply_sequence: _Optional[int] = ..., operation: _Optional[str] = ..., parent_comment_id: _Optional[str] = ...) -> None: ...

class FileView(_message.Message):
    __slots__ = ("metadata", "file_revision", "protection_key", "snapshot", "file_id")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    FILE_REVISION_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_KEY_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    metadata: _domain_pb2.FileMetadata
    file_revision: int
    protection_key: _crypto_pb2_1.KeyRef
    snapshot: ReadCryptoResponse
    file_id: str
    def __init__(self, metadata: _Optional[_Union[_domain_pb2.FileMetadata, _Mapping]] = ..., file_revision: _Optional[int] = ..., protection_key: _Optional[_Union[_crypto_pb2_1.KeyRef, _Mapping]] = ..., snapshot: _Optional[_Union[ReadCryptoResponse, _Mapping]] = ..., file_id: _Optional[str] = ...) -> None: ...

class ProjectCatalogRequest(_message.Message):
    __slots__ = ("device_id", "cursor", "limit")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    cursor: str
    limit: int
    def __init__(self, device_id: _Optional[str] = ..., cursor: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class ProjectCatalogEntry(_message.Message):
    __slots__ = ("project_id", "group_id", "shared", "role", "protection_key", "distribution_revision", "lifecycle", "storage_used_bytes", "access_source", "key_distribution_revision")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SHARED_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_KEY_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_REVISION_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_USED_BYTES_FIELD_NUMBER: _ClassVar[int]
    ACCESS_SOURCE_FIELD_NUMBER: _ClassVar[int]
    KEY_DISTRIBUTION_REVISION_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    group_id: str
    shared: bool
    role: str
    protection_key: _crypto_pb2_1.KeyRef
    distribution_revision: int
    lifecycle: str
    storage_used_bytes: int
    access_source: str
    key_distribution_revision: int
    def __init__(self, project_id: _Optional[str] = ..., group_id: _Optional[str] = ..., shared: bool = ..., role: _Optional[str] = ..., protection_key: _Optional[_Union[_crypto_pb2_1.KeyRef, _Mapping]] = ..., distribution_revision: _Optional[int] = ..., lifecycle: _Optional[str] = ..., storage_used_bytes: _Optional[int] = ..., access_source: _Optional[str] = ..., key_distribution_revision: _Optional[int] = ...) -> None: ...

class CatalogGroup(_message.Message):
    __slots__ = ("group_id", "current_owner", "owner_candidate")
    class CurrentOwner(_message.Message):
        __slots__ = ("prepared_candidate_count", "incomplete_candidate_count")
        PREPARED_CANDIDATE_COUNT_FIELD_NUMBER: _ClassVar[int]
        INCOMPLETE_CANDIDATE_COUNT_FIELD_NUMBER: _ClassVar[int]
        prepared_candidate_count: int
        incomplete_candidate_count: int
        def __init__(self, prepared_candidate_count: _Optional[int] = ..., incomplete_candidate_count: _Optional[int] = ...) -> None: ...
    class OwnerCandidate(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_OWNER_FIELD_NUMBER: _ClassVar[int]
    OWNER_CANDIDATE_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    current_owner: CatalogGroup.CurrentOwner
    owner_candidate: CatalogGroup.OwnerCandidate
    def __init__(self, group_id: _Optional[str] = ..., current_owner: _Optional[_Union[CatalogGroup.CurrentOwner, _Mapping]] = ..., owner_candidate: _Optional[_Union[CatalogGroup.OwnerCandidate, _Mapping]] = ...) -> None: ...

class ProjectCatalogResponse(_message.Message):
    __slots__ = ("projects", "cursor", "has_more", "bundle", "groups")
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[ProjectCatalogEntry]
    cursor: str
    has_more: bool
    bundle: _crypto_pb2.CryptoReadBundle
    groups: _containers.RepeatedCompositeFieldContainer[CatalogGroup]
    def __init__(self, projects: _Optional[_Iterable[_Union[ProjectCatalogEntry, _Mapping]]] = ..., cursor: _Optional[str] = ..., has_more: bool = ..., bundle: _Optional[_Union[_crypto_pb2.CryptoReadBundle, _Mapping]] = ..., groups: _Optional[_Iterable[_Union[CatalogGroup, _Mapping]]] = ...) -> None: ...

class InvitationJoinRequest(_message.Message):
    __slots__ = ("project_id", "invitation_id", "request")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    invitation_id: str
    request: _crypto_pb2_1.SignedBytes
    def __init__(self, project_id: _Optional[str] = ..., invitation_id: _Optional[str] = ..., request: _Optional[_Union[_crypto_pb2_1.SignedBytes, _Mapping]] = ...) -> None: ...

class GroupReceiverRequest(_message.Message):
    __slots__ = ("group_id", "subject")
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    subject: str
    def __init__(self, group_id: _Optional[str] = ..., subject: _Optional[str] = ...) -> None: ...

class RecordPrecondition(_message.Message):
    __slots__ = ("id", "expected_revision", "require_live")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_REVISION_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_LIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    expected_revision: int
    require_live: bool
    def __init__(self, id: _Optional[str] = ..., expected_revision: _Optional[int] = ..., require_live: bool = ...) -> None: ...

class ObjectEffect(_message.Message):
    __slots__ = ("action", "object_id", "file_id", "artifact_kind", "locator", "draft_id", "expected_draft_revision", "expected_file_revision", "expected_preview_id", "source_object_id", "processing_id", "job_id", "exact_source_binding")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_KIND_FIELD_NUMBER: _ClassVar[int]
    LOCATOR_FIELD_NUMBER: _ClassVar[int]
    DRAFT_ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_DRAFT_REVISION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_FILE_REVISION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_PREVIEW_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    EXACT_SOURCE_BINDING_FIELD_NUMBER: _ClassVar[int]
    action: str
    object_id: str
    file_id: str
    artifact_kind: str
    locator: _domain_pb2.ObjectDescriptor
    draft_id: str
    expected_draft_revision: int
    expected_file_revision: int
    expected_preview_id: str
    source_object_id: str
    processing_id: str
    job_id: str
    exact_source_binding: bytes
    def __init__(self, action: _Optional[str] = ..., object_id: _Optional[str] = ..., file_id: _Optional[str] = ..., artifact_kind: _Optional[str] = ..., locator: _Optional[_Union[_domain_pb2.ObjectDescriptor, _Mapping]] = ..., draft_id: _Optional[str] = ..., expected_draft_revision: _Optional[int] = ..., expected_file_revision: _Optional[int] = ..., expected_preview_id: _Optional[str] = ..., source_object_id: _Optional[str] = ..., processing_id: _Optional[str] = ..., job_id: _Optional[str] = ..., exact_source_binding: _Optional[bytes] = ...) -> None: ...

class CryptoConfiguration(_message.Message):
    __slots__ = ("account_jwks", "account_issuer", "account_audience")
    ACCOUNT_JWKS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ISSUER_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    account_jwks: str
    account_issuer: str
    account_audience: str
    def __init__(self, account_jwks: _Optional[str] = ..., account_issuer: _Optional[str] = ..., account_audience: _Optional[str] = ...) -> None: ...

class ProjectAudienceRequest(_message.Message):
    __slots__ = ("group_id", "project_id", "device_id")
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    project_id: str
    device_id: str
    def __init__(self, group_id: _Optional[str] = ..., project_id: _Optional[str] = ..., device_id: _Optional[str] = ...) -> None: ...

class ProjectAudienceMember(_message.Message):
    __slots__ = ("subject", "role", "revision", "owner_candidate", "receiver")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    OWNER_CANDIDATE_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    subject: str
    role: str
    revision: int
    owner_candidate: bool
    receiver: _crypto_pb2_1.PublicKey
    def __init__(self, subject: _Optional[str] = ..., role: _Optional[str] = ..., revision: _Optional[int] = ..., owner_candidate: bool = ..., receiver: _Optional[_Union[_crypto_pb2_1.PublicKey, _Mapping]] = ...) -> None: ...

class ProjectRosterMember(_message.Message):
    __slots__ = ("subject", "role", "state", "origin_kind", "revision", "display_name")
    class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROLE_UNSPECIFIED: _ClassVar[ProjectRosterMember.Role]
        ROLE_OWNER: _ClassVar[ProjectRosterMember.Role]
        ROLE_EDITOR: _ClassVar[ProjectRosterMember.Role]
        ROLE_VIEWER: _ClassVar[ProjectRosterMember.Role]
    ROLE_UNSPECIFIED: ProjectRosterMember.Role
    ROLE_OWNER: ProjectRosterMember.Role
    ROLE_EDITOR: ProjectRosterMember.Role
    ROLE_VIEWER: ProjectRosterMember.Role
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATE_UNSPECIFIED: _ClassVar[ProjectRosterMember.State]
        STATE_ACTIVE: _ClassVar[ProjectRosterMember.State]
        STATE_REMOVED: _ClassVar[ProjectRosterMember.State]
    STATE_UNSPECIFIED: ProjectRosterMember.State
    STATE_ACTIVE: ProjectRosterMember.State
    STATE_REMOVED: ProjectRosterMember.State
    class OriginKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ORIGIN_KIND_UNSPECIFIED: _ClassVar[ProjectRosterMember.OriginKind]
        ORIGIN_KIND_PROJECT_CREATION: _ClassVar[ProjectRosterMember.OriginKind]
        ORIGIN_KIND_INVITATION: _ClassVar[ProjectRosterMember.OriginKind]
        ORIGIN_KIND_ORGANIZATION_PARTICIPATION: _ClassVar[ProjectRosterMember.OriginKind]
    ORIGIN_KIND_UNSPECIFIED: ProjectRosterMember.OriginKind
    ORIGIN_KIND_PROJECT_CREATION: ProjectRosterMember.OriginKind
    ORIGIN_KIND_INVITATION: ProjectRosterMember.OriginKind
    ORIGIN_KIND_ORGANIZATION_PARTICIPATION: ProjectRosterMember.OriginKind
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_KIND_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    subject: str
    role: ProjectRosterMember.Role
    state: ProjectRosterMember.State
    origin_kind: ProjectRosterMember.OriginKind
    revision: int
    display_name: str
    def __init__(self, subject: _Optional[str] = ..., role: _Optional[_Union[ProjectRosterMember.Role, str]] = ..., state: _Optional[_Union[ProjectRosterMember.State, str]] = ..., origin_kind: _Optional[_Union[ProjectRosterMember.OriginKind, str]] = ..., revision: _Optional[int] = ..., display_name: _Optional[str] = ...) -> None: ...

class ProjectAudienceResponse(_message.Message):
    __slots__ = ("members", "bundle", "projects", "group_revision", "catalog_digest", "project_members")
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    GROUP_REVISION_FIELD_NUMBER: _ClassVar[int]
    CATALOG_DIGEST_FIELD_NUMBER: _ClassVar[int]
    PROJECT_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[ProjectAudienceMember]
    bundle: _crypto_pb2.CryptoReadBundle
    projects: _containers.RepeatedCompositeFieldContainer[ProjectCatalogEntry]
    group_revision: int
    catalog_digest: bytes
    project_members: _containers.RepeatedCompositeFieldContainer[ProjectRosterMember]
    def __init__(self, members: _Optional[_Iterable[_Union[ProjectAudienceMember, _Mapping]]] = ..., bundle: _Optional[_Union[_crypto_pb2.CryptoReadBundle, _Mapping]] = ..., projects: _Optional[_Iterable[_Union[ProjectCatalogEntry, _Mapping]]] = ..., group_revision: _Optional[int] = ..., catalog_digest: _Optional[bytes] = ..., project_members: _Optional[_Iterable[_Union[ProjectRosterMember, _Mapping]]] = ...) -> None: ...

class InvitationDescriptor(_message.Message):
    __slots__ = ("invitation_id", "project_id", "role", "expires_at", "secret_digest", "inviter_root_digest", "proof_public_key")
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    SECRET_DIGEST_FIELD_NUMBER: _ClassVar[int]
    INVITER_ROOT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    PROOF_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    invitation_id: str
    project_id: str
    role: str
    expires_at: int
    secret_digest: bytes
    inviter_root_digest: bytes
    proof_public_key: bytes
    def __init__(self, invitation_id: _Optional[str] = ..., project_id: _Optional[str] = ..., role: _Optional[str] = ..., expires_at: _Optional[int] = ..., secret_digest: _Optional[bytes] = ..., inviter_root_digest: _Optional[bytes] = ..., proof_public_key: _Optional[bytes] = ...) -> None: ...

class InvitationJoinBinding(_message.Message):
    __slots__ = ("invitation_id", "subject", "descriptor_digest", "proof", "challenge_bytes", "receiver_digest")
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_DIGEST_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_DIGEST_FIELD_NUMBER: _ClassVar[int]
    invitation_id: str
    subject: str
    descriptor_digest: bytes
    proof: _crypto_pb2_1.PossessionProof
    challenge_bytes: bytes
    receiver_digest: bytes
    def __init__(self, invitation_id: _Optional[str] = ..., subject: _Optional[str] = ..., descriptor_digest: _Optional[bytes] = ..., proof: _Optional[_Union[_crypto_pb2_1.PossessionProof, _Mapping]] = ..., challenge_bytes: _Optional[bytes] = ..., receiver_digest: _Optional[bytes] = ...) -> None: ...

class InvitationStatus(_message.Message):
    __slots__ = ("invitation_id", "project_id", "state", "descriptor", "requests", "current_owner_subject", "applicants")
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_OWNER_SUBJECT_FIELD_NUMBER: _ClassVar[int]
    APPLICANTS_FIELD_NUMBER: _ClassVar[int]
    invitation_id: str
    project_id: str
    state: str
    descriptor: _crypto_pb2_1.SignedBytes
    requests: _containers.RepeatedCompositeFieldContainer[_crypto_pb2_1.SignedBytes]
    current_owner_subject: str
    applicants: _containers.RepeatedCompositeFieldContainer[ProjectAudienceMember]
    def __init__(self, invitation_id: _Optional[str] = ..., project_id: _Optional[str] = ..., state: _Optional[str] = ..., descriptor: _Optional[_Union[_crypto_pb2_1.SignedBytes, _Mapping]] = ..., requests: _Optional[_Iterable[_Union[_crypto_pb2_1.SignedBytes, _Mapping]]] = ..., current_owner_subject: _Optional[str] = ..., applicants: _Optional[_Iterable[_Union[ProjectAudienceMember, _Mapping]]] = ...) -> None: ...

class InvitationReadRequest(_message.Message):
    __slots__ = ("project_id", "invitation_id", "device_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    invitation_id: str
    device_id: str
    def __init__(self, project_id: _Optional[str] = ..., invitation_id: _Optional[str] = ..., device_id: _Optional[str] = ...) -> None: ...

class InvitationReadResponse(_message.Message):
    __slots__ = ("invitations", "bundle")
    INVITATIONS_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    invitations: _containers.RepeatedCompositeFieldContainer[InvitationStatus]
    bundle: _crypto_pb2.CryptoReadBundle
    def __init__(self, invitations: _Optional[_Iterable[_Union[InvitationStatus, _Mapping]]] = ..., bundle: _Optional[_Union[_crypto_pb2.CryptoReadBundle, _Mapping]] = ...) -> None: ...

class FileOperationRequest(_message.Message):
    __slots__ = ("project_id", "device_id", "object_id", "chunk_index", "content_length", "sha256", "action")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    CONTENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SHA256_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    device_id: str
    object_id: str
    chunk_index: int
    content_length: int
    sha256: bytes
    action: str
    def __init__(self, project_id: _Optional[str] = ..., device_id: _Optional[str] = ..., object_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., content_length: _Optional[int] = ..., sha256: _Optional[bytes] = ..., action: _Optional[str] = ...) -> None: ...

class FileOperationResponse(_message.Message):
    __slots__ = ("url", "content_length", "headers", "missing_indices", "state", "expires_at", "operation", "object_id", "chunk_index", "contract", "version")
    URL_FIELD_NUMBER: _ClassVar[int]
    CONTENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    MISSING_INDICES_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    url: str
    content_length: int
    headers: _containers.RepeatedCompositeFieldContainer[HttpHeader]
    missing_indices: _containers.RepeatedScalarFieldContainer[int]
    state: str
    expires_at: str
    operation: str
    object_id: str
    chunk_index: int
    contract: str
    version: int
    def __init__(self, url: _Optional[str] = ..., content_length: _Optional[int] = ..., headers: _Optional[_Iterable[_Union[HttpHeader, _Mapping]]] = ..., missing_indices: _Optional[_Iterable[int]] = ..., state: _Optional[str] = ..., expires_at: _Optional[str] = ..., operation: _Optional[str] = ..., object_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., contract: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class HttpHeader(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class InvitationLink(_message.Message):
    __slots__ = ("invitation_id", "project_id", "secret", "inviter_root_digest", "descriptor_digest")
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    INVITER_ROOT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_DIGEST_FIELD_NUMBER: _ClassVar[int]
    invitation_id: str
    project_id: str
    secret: bytes
    inviter_root_digest: bytes
    descriptor_digest: bytes
    def __init__(self, invitation_id: _Optional[str] = ..., project_id: _Optional[str] = ..., secret: _Optional[bytes] = ..., inviter_root_digest: _Optional[bytes] = ..., descriptor_digest: _Optional[bytes] = ...) -> None: ...

class GroupMemberPreparationRequest(_message.Message):
    __slots__ = ("group_id", "subject", "mutations", "expected_group_revision", "catalog_digest", "device_id")
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_GROUP_REVISION_FIELD_NUMBER: _ClassVar[int]
    CATALOG_DIGEST_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    subject: str
    mutations: _containers.RepeatedCompositeFieldContainer[CommitCryptoRequest]
    expected_group_revision: int
    catalog_digest: bytes
    device_id: str
    def __init__(self, group_id: _Optional[str] = ..., subject: _Optional[str] = ..., mutations: _Optional[_Iterable[_Union[CommitCryptoRequest, _Mapping]]] = ..., expected_group_revision: _Optional[int] = ..., catalog_digest: _Optional[bytes] = ..., device_id: _Optional[str] = ...) -> None: ...

class GroupMemberPreparationResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CommitCryptoResponse]
    def __init__(self, results: _Optional[_Iterable[_Union[CommitCryptoResponse, _Mapping]]] = ...) -> None: ...

class InvitationJoinChallenge(_message.Message):
    __slots__ = ("invitation_id", "subject", "descriptor_digest", "receiver_digest")
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_DIGEST_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_DIGEST_FIELD_NUMBER: _ClassVar[int]
    invitation_id: str
    subject: str
    descriptor_digest: bytes
    receiver_digest: bytes
    def __init__(self, invitation_id: _Optional[str] = ..., subject: _Optional[str] = ..., descriptor_digest: _Optional[bytes] = ..., receiver_digest: _Optional[bytes] = ...) -> None: ...

class CommentViewItem(_message.Message):
    __slots__ = ("thread_id", "comment_id", "origin", "thread_head", "body_head", "resolution", "text_revisions", "sequence", "reply_sequence", "anchor_id", "parent_comment_id", "revision")
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    THREAD_HEAD_FIELD_NUMBER: _ClassVar[int]
    BODY_HEAD_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    TEXT_REVISIONS_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REPLY_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ANCHOR_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    thread_id: str
    comment_id: str
    origin: _crypto_pb2.TargetHead
    thread_head: _crypto_pb2.TargetHead
    body_head: _crypto_pb2.TargetHead
    resolution: _crypto_pb2.TargetHead
    text_revisions: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.TargetHead]
    sequence: int
    reply_sequence: int
    anchor_id: str
    parent_comment_id: str
    revision: int
    def __init__(self, thread_id: _Optional[str] = ..., comment_id: _Optional[str] = ..., origin: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., thread_head: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., body_head: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., resolution: _Optional[_Union[_crypto_pb2.TargetHead, _Mapping]] = ..., text_revisions: _Optional[_Iterable[_Union[_crypto_pb2.TargetHead, _Mapping]]] = ..., sequence: _Optional[int] = ..., reply_sequence: _Optional[int] = ..., anchor_id: _Optional[str] = ..., parent_comment_id: _Optional[str] = ..., revision: _Optional[int] = ...) -> None: ...
