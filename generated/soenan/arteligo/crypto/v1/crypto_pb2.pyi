from soenan.account.crypto.v1 import crypto_pb2 as _crypto_pb2
from soenan.account.identity.v1 import identity_pb2 as _identity_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CipherValueBody(_message.Message):
    __slots__ = ("id", "revision", "protection_key", "sealed_dek", "value", "kind", "deleted", "immutable")
    ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_KEY_FIELD_NUMBER: _ClassVar[int]
    SEALED_DEK_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    IMMUTABLE_FIELD_NUMBER: _ClassVar[int]
    id: str
    revision: int
    protection_key: _crypto_pb2.KeyRef
    sealed_dek: _crypto_pb2.HpkeEnvelope
    value: _crypto_pb2.AeadValue
    kind: str
    deleted: bool
    immutable: bool
    def __init__(self, id: _Optional[str] = ..., revision: _Optional[int] = ..., protection_key: _Optional[_Union[_crypto_pb2.KeyRef, _Mapping]] = ..., sealed_dek: _Optional[_Union[_crypto_pb2.HpkeEnvelope, _Mapping]] = ..., value: _Optional[_Union[_crypto_pb2.AeadValue, _Mapping]] = ..., kind: _Optional[str] = ..., deleted: bool = ..., immutable: bool = ...) -> None: ...

class CommitReceiptBody(_message.Message):
    __slots__ = ("operation_id", "mutation_digest", "identity_revision", "distribution_revision", "heads", "accepted_document_digests")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    MUTATION_DIGEST_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_REVISION_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_REVISION_FIELD_NUMBER: _ClassVar[int]
    HEADS_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_DOCUMENT_DIGESTS_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    mutation_digest: bytes
    identity_revision: int
    distribution_revision: int
    heads: _containers.RepeatedCompositeFieldContainer[TargetHead]
    accepted_document_digests: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, operation_id: _Optional[str] = ..., mutation_digest: _Optional[bytes] = ..., identity_revision: _Optional[int] = ..., distribution_revision: _Optional[int] = ..., heads: _Optional[_Iterable[_Union[TargetHead, _Mapping]]] = ..., accepted_document_digests: _Optional[_Iterable[bytes]] = ...) -> None: ...

class TargetHead(_message.Message):
    __slots__ = ("id", "expected_revision", "revision")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_REVISION_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    id: str
    expected_revision: int
    revision: int
    def __init__(self, id: _Optional[str] = ..., expected_revision: _Optional[int] = ..., revision: _Optional[int] = ...) -> None: ...

class CryptoReadBundle(_message.Message):
    __slots__ = ("values", "key_deliveries", "key_certificates", "identity_statements", "commit_receipts", "identity_revision", "documents", "commitments", "proofs", "distribution_revision")
    VALUES_FIELD_NUMBER: _ClassVar[int]
    KEY_DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    KEY_CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_STATEMENTS_FIELD_NUMBER: _ClassVar[int]
    COMMIT_RECEIPTS_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_REVISION_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENTS_FIELD_NUMBER: _ClassVar[int]
    PROOFS_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_REVISION_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    key_deliveries: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    key_certificates: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    identity_statements: _containers.RepeatedCompositeFieldContainer[_identity_pb2.IdentityRecord]
    commit_receipts: _containers.RepeatedCompositeFieldContainer[CommitReceiptBody]
    identity_revision: int
    documents: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedDocument]
    commitments: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.HashCommitment]
    proofs: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.PossessionProof]
    distribution_revision: int
    def __init__(self, values: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ..., key_deliveries: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ..., key_certificates: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ..., identity_statements: _Optional[_Iterable[_Union[_identity_pb2.IdentityRecord, _Mapping]]] = ..., commit_receipts: _Optional[_Iterable[_Union[CommitReceiptBody, _Mapping]]] = ..., identity_revision: _Optional[int] = ..., documents: _Optional[_Iterable[_Union[_crypto_pb2.SignedDocument, _Mapping]]] = ..., commitments: _Optional[_Iterable[_Union[_crypto_pb2.HashCommitment, _Mapping]]] = ..., proofs: _Optional[_Iterable[_Union[_crypto_pb2.PossessionProof, _Mapping]]] = ..., distribution_revision: _Optional[int] = ...) -> None: ...

class OpenInput(_message.Message):
    __slots__ = ("state", "bundle", "release_operation_ids")
    STATE_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    RELEASE_OPERATION_IDS_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    bundle: CryptoReadBundle
    release_operation_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., bundle: _Optional[_Union[CryptoReadBundle, _Mapping]] = ..., release_operation_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class OpenedValue(_message.Message):
    __slots__ = ("id", "revision", "protection_key", "plaintext", "kind", "deleted", "immutable", "author_device_id", "cursor", "author_subject")
    ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_KEY_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    IMMUTABLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_SUBJECT_FIELD_NUMBER: _ClassVar[int]
    id: str
    revision: int
    protection_key: _crypto_pb2.KeyRef
    plaintext: bytes
    kind: str
    deleted: bool
    immutable: bool
    author_device_id: str
    cursor: int
    author_subject: str
    def __init__(self, id: _Optional[str] = ..., revision: _Optional[int] = ..., protection_key: _Optional[_Union[_crypto_pb2.KeyRef, _Mapping]] = ..., plaintext: _Optional[bytes] = ..., kind: _Optional[str] = ..., deleted: bool = ..., immutable: bool = ..., author_device_id: _Optional[str] = ..., cursor: _Optional[int] = ..., author_subject: _Optional[str] = ...) -> None: ...

class OpenedValues(_message.Message):
    __slots__ = ("values", "state", "verified_documents")
    VALUES_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[OpenedValue]
    state: CoreState
    verified_documents: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    def __init__(self, values: _Optional[_Iterable[_Union[OpenedValue, _Mapping]]] = ..., state: _Optional[_Union[CoreState, _Mapping]] = ..., verified_documents: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ...) -> None: ...

class SignDocumentsInput(_message.Message):
    __slots__ = ("state", "bundle", "documents")
    STATE_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    bundle: CryptoReadBundle
    documents: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., bundle: _Optional[_Union[CryptoReadBundle, _Mapping]] = ..., documents: _Optional[_Iterable[bytes]] = ...) -> None: ...

class SignedDocumentsResult(_message.Message):
    __slots__ = ("state", "documents")
    STATE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    documents: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., documents: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ...) -> None: ...

class ValueMutation(_message.Message):
    __slots__ = ("id", "expected_revision", "protection_key", "plaintext", "kind", "deleted", "immutable")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_REVISION_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_KEY_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    IMMUTABLE_FIELD_NUMBER: _ClassVar[int]
    id: str
    expected_revision: int
    protection_key: _crypto_pb2.KeyRef
    plaintext: bytes
    kind: str
    deleted: bool
    immutable: bool
    def __init__(self, id: _Optional[str] = ..., expected_revision: _Optional[int] = ..., protection_key: _Optional[_Union[_crypto_pb2.KeyRef, _Mapping]] = ..., plaintext: _Optional[bytes] = ..., kind: _Optional[str] = ..., deleted: bool = ..., immutable: bool = ...) -> None: ...

class DeliveryMutation(_message.Message):
    __slots__ = ("target", "recipient", "include_history")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    target: _crypto_pb2.KeyRef
    recipient: _crypto_pb2.PublicKey
    include_history: bool
    def __init__(self, target: _Optional[_Union[_crypto_pb2.KeyRef, _Mapping]] = ..., recipient: _Optional[_Union[_crypto_pb2.PublicKey, _Mapping]] = ..., include_history: bool = ...) -> None: ...

class CryptoMutationInput(_message.Message):
    __slots__ = ("state", "bundle", "operation_id", "values", "deliveries", "create_protection_keys", "namespace_id", "application_binding")
    STATE_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    CREATE_PROTECTION_KEYS_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_BINDING_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    bundle: CryptoReadBundle
    operation_id: str
    values: _containers.RepeatedCompositeFieldContainer[ValueMutation]
    deliveries: _containers.RepeatedCompositeFieldContainer[DeliveryMutation]
    create_protection_keys: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.KeyRef]
    namespace_id: str
    application_binding: bytes
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., bundle: _Optional[_Union[CryptoReadBundle, _Mapping]] = ..., operation_id: _Optional[str] = ..., values: _Optional[_Iterable[_Union[ValueMutation, _Mapping]]] = ..., deliveries: _Optional[_Iterable[_Union[DeliveryMutation, _Mapping]]] = ..., create_protection_keys: _Optional[_Iterable[_Union[_crypto_pb2.KeyRef, _Mapping]]] = ..., namespace_id: _Optional[str] = ..., application_binding: _Optional[bytes] = ...) -> None: ...

class MutationBody(_message.Message):
    __slots__ = ("operation_id", "expected_identity_revision", "expected_distribution_revision", "target_heads", "values", "key_deliveries", "key_certificates", "namespace_id", "application_binding")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_IDENTITY_REVISION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_DISTRIBUTION_REVISION_FIELD_NUMBER: _ClassVar[int]
    TARGET_HEADS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    KEY_DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    KEY_CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_BINDING_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    expected_identity_revision: int
    expected_distribution_revision: int
    target_heads: _containers.RepeatedCompositeFieldContainer[TargetHead]
    values: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    key_deliveries: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    key_certificates: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SignedBytes]
    namespace_id: str
    application_binding: bytes
    def __init__(self, operation_id: _Optional[str] = ..., expected_identity_revision: _Optional[int] = ..., expected_distribution_revision: _Optional[int] = ..., target_heads: _Optional[_Iterable[_Union[TargetHead, _Mapping]]] = ..., values: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ..., key_deliveries: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ..., key_certificates: _Optional[_Iterable[_Union[_crypto_pb2.SignedBytes, _Mapping]]] = ..., namespace_id: _Optional[str] = ..., application_binding: _Optional[bytes] = ...) -> None: ...

class PreparedMutation(_message.Message):
    __slots__ = ("command", "state")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    command: _crypto_pb2.SignedBytes
    state: CoreState
    def __init__(self, command: _Optional[_Union[_crypto_pb2.SignedBytes, _Mapping]] = ..., state: _Optional[_Union[CoreState, _Mapping]] = ...) -> None: ...

class RejectPreparedOperationInput(_message.Message):
    __slots__ = ("state", "command")
    STATE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    command: _crypto_pb2.SignedBytes
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., command: _Optional[_Union[_crypto_pb2.SignedBytes, _Mapping]] = ...) -> None: ...

class RejectedPreparedOperation(_message.Message):
    __slots__ = ("state", "removed")
    STATE_FIELD_NUMBER: _ClassVar[int]
    REMOVED_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    removed: bool
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., removed: bool = ...) -> None: ...

class CoreRequest(_message.Message):
    __slots__ = ("open", "prepare", "reject_prepared_operation", "sign_documents")
    OPEN_FIELD_NUMBER: _ClassVar[int]
    PREPARE_FIELD_NUMBER: _ClassVar[int]
    REJECT_PREPARED_OPERATION_FIELD_NUMBER: _ClassVar[int]
    SIGN_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    open: OpenInput
    prepare: CryptoMutationInput
    reject_prepared_operation: RejectPreparedOperationInput
    sign_documents: SignDocumentsInput
    def __init__(self, open: _Optional[_Union[OpenInput, _Mapping]] = ..., prepare: _Optional[_Union[CryptoMutationInput, _Mapping]] = ..., reject_prepared_operation: _Optional[_Union[RejectPreparedOperationInput, _Mapping]] = ..., sign_documents: _Optional[_Union[SignDocumentsInput, _Mapping]] = ...) -> None: ...

class CoreResponse(_message.Message):
    __slots__ = ("opened", "prepared", "error", "rejected_prepared_operation", "signed_documents")
    OPENED_FIELD_NUMBER: _ClassVar[int]
    PREPARED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    REJECTED_PREPARED_OPERATION_FIELD_NUMBER: _ClassVar[int]
    SIGNED_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    opened: OpenedValues
    prepared: PreparedMutation
    error: str
    rejected_prepared_operation: RejectedPreparedOperation
    signed_documents: SignedDocumentsResult
    def __init__(self, opened: _Optional[_Union[OpenedValues, _Mapping]] = ..., prepared: _Optional[_Union[PreparedMutation, _Mapping]] = ..., error: _Optional[str] = ..., rejected_prepared_operation: _Optional[_Union[RejectedPreparedOperation, _Mapping]] = ..., signed_documents: _Optional[_Union[SignedDocumentsResult, _Mapping]] = ...) -> None: ...

class StreamState(_message.Message):
    __slots__ = ("key", "nonce_prefix", "binding", "next_index", "finished")
    KEY_FIELD_NUMBER: _ClassVar[int]
    NONCE_PREFIX_FIELD_NUMBER: _ClassVar[int]
    BINDING_FIELD_NUMBER: _ClassVar[int]
    NEXT_INDEX_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    nonce_prefix: bytes
    binding: bytes
    next_index: int
    finished: bool
    def __init__(self, key: _Optional[bytes] = ..., nonce_prefix: _Optional[bytes] = ..., binding: _Optional[bytes] = ..., next_index: _Optional[int] = ..., finished: bool = ...) -> None: ...

class StreamSeal(_message.Message):
    __slots__ = ("state", "plaintext", "final_frame", "binding")
    STATE_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_FIELD_NUMBER: _ClassVar[int]
    FINAL_FRAME_FIELD_NUMBER: _ClassVar[int]
    BINDING_FIELD_NUMBER: _ClassVar[int]
    state: StreamState
    plaintext: bytes
    final_frame: bool
    binding: bytes
    def __init__(self, state: _Optional[_Union[StreamState, _Mapping]] = ..., plaintext: _Optional[bytes] = ..., final_frame: bool = ..., binding: _Optional[bytes] = ...) -> None: ...

class StreamFrame(_message.Message):
    __slots__ = ("index", "final_frame", "plaintext_length", "ciphertext", "sha256")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    FINAL_FRAME_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    CIPHERTEXT_FIELD_NUMBER: _ClassVar[int]
    SHA256_FIELD_NUMBER: _ClassVar[int]
    index: int
    final_frame: bool
    plaintext_length: int
    ciphertext: bytes
    sha256: bytes
    def __init__(self, index: _Optional[int] = ..., final_frame: bool = ..., plaintext_length: _Optional[int] = ..., ciphertext: _Optional[bytes] = ..., sha256: _Optional[bytes] = ...) -> None: ...

class PreparedOperation(_message.Message):
    __slots__ = ("operation_id", "input_digest", "command")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    input_digest: bytes
    command: _crypto_pb2.SignedBytes
    def __init__(self, operation_id: _Optional[str] = ..., input_digest: _Optional[bytes] = ..., command: _Optional[_Union[_crypto_pb2.SignedBytes, _Mapping]] = ...) -> None: ...

class StreamOpen(_message.Message):
    __slots__ = ("state", "frame", "binding")
    STATE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    BINDING_FIELD_NUMBER: _ClassVar[int]
    state: StreamState
    frame: StreamFrame
    binding: bytes
    def __init__(self, state: _Optional[_Union[StreamState, _Mapping]] = ..., frame: _Optional[_Union[StreamFrame, _Mapping]] = ..., binding: _Optional[bytes] = ...) -> None: ...

class StreamSealed(_message.Message):
    __slots__ = ("state", "frame")
    STATE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    state: StreamState
    frame: StreamFrame
    def __init__(self, state: _Optional[_Union[StreamState, _Mapping]] = ..., frame: _Optional[_Union[StreamFrame, _Mapping]] = ...) -> None: ...

class StreamOpened(_message.Message):
    __slots__ = ("state", "plaintext")
    STATE_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_FIELD_NUMBER: _ClassVar[int]
    state: StreamState
    plaintext: bytes
    def __init__(self, state: _Optional[_Union[StreamState, _Mapping]] = ..., plaintext: _Optional[bytes] = ...) -> None: ...

class CoreUtilityRequest(_message.Message):
    __slots__ = ("seal_stream", "open_stream")
    SEAL_STREAM_FIELD_NUMBER: _ClassVar[int]
    OPEN_STREAM_FIELD_NUMBER: _ClassVar[int]
    seal_stream: StreamSeal
    open_stream: StreamOpen
    def __init__(self, seal_stream: _Optional[_Union[StreamSeal, _Mapping]] = ..., open_stream: _Optional[_Union[StreamOpen, _Mapping]] = ...) -> None: ...

class CoreUtilityResponse(_message.Message):
    __slots__ = ("stream_sealed", "stream_opened", "error")
    STREAM_SEALED_FIELD_NUMBER: _ClassVar[int]
    STREAM_OPENED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    stream_sealed: StreamSealed
    stream_opened: StreamOpened
    error: str
    def __init__(self, stream_sealed: _Optional[_Union[StreamSealed, _Mapping]] = ..., stream_opened: _Optional[_Union[StreamOpened, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class ProductState(_message.Message):
    __slots__ = ("keys", "prepared_operations")
    KEYS_FIELD_NUMBER: _ClassVar[int]
    PREPARED_OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_crypto_pb2.SecretKey]
    prepared_operations: _containers.RepeatedCompositeFieldContainer[PreparedOperation]
    def __init__(self, keys: _Optional[_Iterable[_Union[_crypto_pb2.SecretKey, _Mapping]]] = ..., prepared_operations: _Optional[_Iterable[_Union[PreparedOperation, _Mapping]]] = ...) -> None: ...

class CoreState(_message.Message):
    __slots__ = ("identity", "product")
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    identity: _identity_pb2.IdentityState
    product: ProductState
    def __init__(self, identity: _Optional[_Union[_identity_pb2.IdentityState, _Mapping]] = ..., product: _Optional[_Union[ProductState, _Mapping]] = ...) -> None: ...
