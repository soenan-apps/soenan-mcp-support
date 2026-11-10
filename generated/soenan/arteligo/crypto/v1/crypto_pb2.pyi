from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnrollmentAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENROLLMENT_ACTION_APPROVE_DEVICE: _ClassVar[EnrollmentAction]
    ENROLLMENT_ACTION_PREPARE_GENESIS: _ClassVar[EnrollmentAction]
    ENROLLMENT_ACTION_COMMIT_GENESIS: _ClassVar[EnrollmentAction]
    ENROLLMENT_ACTION_PREPARE_CODE: _ClassVar[EnrollmentAction]
    ENROLLMENT_ACTION_OPEN_CODE: _ClassVar[EnrollmentAction]
    ENROLLMENT_ACTION_PREPARE_DEVICE: _ClassVar[EnrollmentAction]
    ENROLLMENT_ACTION_EXPORT_CODE: _ClassVar[EnrollmentAction]

class DeviceStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DEVICE_STATUS_UNREGISTERED: _ClassVar[DeviceStatus]
    DEVICE_STATUS_PENDING: _ClassVar[DeviceStatus]
    DEVICE_STATUS_APPROVED: _ClassVar[DeviceStatus]
    DEVICE_STATUS_REVOKED: _ClassVar[DeviceStatus]

class IdentityOperationKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDENTITY_OPERATION_KIND_UNSPECIFIED: _ClassVar[IdentityOperationKind]
    IDENTITY_OPERATION_KIND_ENROLLMENT: _ClassVar[IdentityOperationKind]
    IDENTITY_OPERATION_KIND_ROOT_ROTATION: _ClassVar[IdentityOperationKind]
ENROLLMENT_ACTION_APPROVE_DEVICE: EnrollmentAction
ENROLLMENT_ACTION_PREPARE_GENESIS: EnrollmentAction
ENROLLMENT_ACTION_COMMIT_GENESIS: EnrollmentAction
ENROLLMENT_ACTION_PREPARE_CODE: EnrollmentAction
ENROLLMENT_ACTION_OPEN_CODE: EnrollmentAction
ENROLLMENT_ACTION_PREPARE_DEVICE: EnrollmentAction
ENROLLMENT_ACTION_EXPORT_CODE: EnrollmentAction
DEVICE_STATUS_UNREGISTERED: DeviceStatus
DEVICE_STATUS_PENDING: DeviceStatus
DEVICE_STATUS_APPROVED: DeviceStatus
DEVICE_STATUS_REVOKED: DeviceStatus
IDENTITY_OPERATION_KIND_UNSPECIFIED: IdentityOperationKind
IDENTITY_OPERATION_KIND_ENROLLMENT: IdentityOperationKind
IDENTITY_OPERATION_KIND_ROOT_ROTATION: IdentityOperationKind

class KeyRef(_message.Message):
    __slots__ = ("id", "generation")
    ID_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    generation: int
    def __init__(self, id: _Optional[str] = ..., generation: _Optional[int] = ...) -> None: ...

class SignedBytes(_message.Message):
    __slots__ = ("body", "signature", "signer_device_id")
    BODY_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    SIGNER_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    body: bytes
    signature: bytes
    signer_device_id: str
    def __init__(self, body: _Optional[bytes] = ..., signature: _Optional[bytes] = ..., signer_device_id: _Optional[str] = ...) -> None: ...

class HpkeEnvelope(_message.Message):
    __slots__ = ("encapsulated_key", "ciphertext")
    ENCAPSULATED_KEY_FIELD_NUMBER: _ClassVar[int]
    CIPHERTEXT_FIELD_NUMBER: _ClassVar[int]
    encapsulated_key: bytes
    ciphertext: bytes
    def __init__(self, encapsulated_key: _Optional[bytes] = ..., ciphertext: _Optional[bytes] = ...) -> None: ...

class AeadValue(_message.Message):
    __slots__ = ("nonce", "ciphertext")
    NONCE_FIELD_NUMBER: _ClassVar[int]
    CIPHERTEXT_FIELD_NUMBER: _ClassVar[int]
    nonce: bytes
    ciphertext: bytes
    def __init__(self, nonce: _Optional[bytes] = ..., ciphertext: _Optional[bytes] = ...) -> None: ...

class PublicKey(_message.Message):
    __slots__ = ("key", "public_key")
    KEY_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    key: KeyRef
    public_key: bytes
    def __init__(self, key: _Optional[_Union[KeyRef, _Mapping]] = ..., public_key: _Optional[bytes] = ...) -> None: ...

class SecretKey(_message.Message):
    __slots__ = ("key", "secret_key")
    KEY_FIELD_NUMBER: _ClassVar[int]
    SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    key: KeyRef
    secret_key: bytes
    def __init__(self, key: _Optional[_Union[KeyRef, _Mapping]] = ..., secret_key: _Optional[bytes] = ...) -> None: ...

class Device(_message.Message):
    __slots__ = ("id", "signing_public_key", "receiver_public_key", "revoked")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIGNING_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    REVOKED_FIELD_NUMBER: _ClassVar[int]
    id: str
    signing_public_key: bytes
    receiver_public_key: bytes
    revoked: bool
    def __init__(self, id: _Optional[str] = ..., signing_public_key: _Optional[bytes] = ..., receiver_public_key: _Optional[bytes] = ..., revoked: bool = ...) -> None: ...

class IdentityStatement(_message.Message):
    __slots__ = ("subject", "revision", "previous_digest", "root_signing_public_key", "receiver", "devices", "bootstrap_digest", "account_attestation", "challenge", "addition_public_key", "genesis_binding", "enrollment_authorization", "addition_receiver_public_key")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_DIGEST_FIELD_NUMBER: _ClassVar[int]
    ROOT_SIGNING_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_DIGEST_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ATTESTATION_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    ADDITION_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    GENESIS_BINDING_FIELD_NUMBER: _ClassVar[int]
    ENROLLMENT_AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    ADDITION_RECEIVER_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    subject: str
    revision: int
    previous_digest: bytes
    root_signing_public_key: bytes
    receiver: PublicKey
    devices: _containers.RepeatedCompositeFieldContainer[Device]
    bootstrap_digest: bytes
    account_attestation: bytes
    challenge: bytes
    addition_public_key: bytes
    genesis_binding: bytes
    enrollment_authorization: SignedBytes
    addition_receiver_public_key: bytes
    def __init__(self, subject: _Optional[str] = ..., revision: _Optional[int] = ..., previous_digest: _Optional[bytes] = ..., root_signing_public_key: _Optional[bytes] = ..., receiver: _Optional[_Union[PublicKey, _Mapping]] = ..., devices: _Optional[_Iterable[_Union[Device, _Mapping]]] = ..., bootstrap_digest: _Optional[bytes] = ..., account_attestation: _Optional[bytes] = ..., challenge: _Optional[bytes] = ..., addition_public_key: _Optional[bytes] = ..., genesis_binding: _Optional[bytes] = ..., enrollment_authorization: _Optional[_Union[SignedBytes, _Mapping]] = ..., addition_receiver_public_key: _Optional[bytes] = ...) -> None: ...

class IdentityRecord(_message.Message):
    __slots__ = ("statement", "root_signature")
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    ROOT_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    statement: SignedBytes
    root_signature: bytes
    def __init__(self, statement: _Optional[_Union[SignedBytes, _Mapping]] = ..., root_signature: _Optional[bytes] = ...) -> None: ...

class KeyCertificateBody(_message.Message):
    __slots__ = ("public_key", "subject", "identity_revision")
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_REVISION_FIELD_NUMBER: _ClassVar[int]
    public_key: PublicKey
    subject: str
    identity_revision: int
    def __init__(self, public_key: _Optional[_Union[PublicKey, _Mapping]] = ..., subject: _Optional[str] = ..., identity_revision: _Optional[int] = ...) -> None: ...

class KeyDeliveryBody(_message.Message):
    __slots__ = ("target", "recipient", "envelope", "subject", "distribution_revision")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    ENVELOPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_REVISION_FIELD_NUMBER: _ClassVar[int]
    target: KeyRef
    recipient: KeyRef
    envelope: HpkeEnvelope
    subject: str
    distribution_revision: int
    def __init__(self, target: _Optional[_Union[KeyRef, _Mapping]] = ..., recipient: _Optional[_Union[KeyRef, _Mapping]] = ..., envelope: _Optional[_Union[HpkeEnvelope, _Mapping]] = ..., subject: _Optional[str] = ..., distribution_revision: _Optional[int] = ...) -> None: ...

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
    protection_key: KeyRef
    sealed_dek: HpkeEnvelope
    value: AeadValue
    kind: str
    deleted: bool
    immutable: bool
    def __init__(self, id: _Optional[str] = ..., revision: _Optional[int] = ..., protection_key: _Optional[_Union[KeyRef, _Mapping]] = ..., sealed_dek: _Optional[_Union[HpkeEnvelope, _Mapping]] = ..., value: _Optional[_Union[AeadValue, _Mapping]] = ..., kind: _Optional[str] = ..., deleted: bool = ..., immutable: bool = ...) -> None: ...

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

class TrustAnchor(_message.Message):
    __slots__ = ("subject", "root_digest", "identity_revision", "identity_digest")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    ROOT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_REVISION_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_DIGEST_FIELD_NUMBER: _ClassVar[int]
    subject: str
    root_digest: bytes
    identity_revision: int
    identity_digest: bytes
    def __init__(self, subject: _Optional[str] = ..., root_digest: _Optional[bytes] = ..., identity_revision: _Optional[int] = ..., identity_digest: _Optional[bytes] = ...) -> None: ...

class CoreState(_message.Message):
    __slots__ = ("subject", "device_id", "device_signing_secret", "keys", "trust_anchors", "pending_root_secret", "pending_binding", "addition_secret", "account_jwks", "account_issuer", "account_audience", "prepared_operations", "device_signing_public", "device_receiver_secret", "device_receiver_public", "genesis_binding", "device_status", "identity_operations")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_SIGNING_SECRET_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    TRUST_ANCHORS_FIELD_NUMBER: _ClassVar[int]
    PENDING_ROOT_SECRET_FIELD_NUMBER: _ClassVar[int]
    PENDING_BINDING_FIELD_NUMBER: _ClassVar[int]
    ADDITION_SECRET_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_JWKS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ISSUER_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    PREPARED_OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_SIGNING_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    DEVICE_RECEIVER_SECRET_FIELD_NUMBER: _ClassVar[int]
    DEVICE_RECEIVER_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    GENESIS_BINDING_FIELD_NUMBER: _ClassVar[int]
    DEVICE_STATUS_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    subject: str
    device_id: str
    device_signing_secret: bytes
    keys: _containers.RepeatedCompositeFieldContainer[SecretKey]
    trust_anchors: _containers.RepeatedCompositeFieldContainer[TrustAnchor]
    pending_root_secret: bytes
    pending_binding: bytes
    addition_secret: bytes
    account_jwks: str
    account_issuer: str
    account_audience: str
    prepared_operations: _containers.RepeatedCompositeFieldContainer[PreparedOperation]
    device_signing_public: bytes
    device_receiver_secret: bytes
    device_receiver_public: bytes
    genesis_binding: bytes
    device_status: DeviceStatus
    identity_operations: _containers.RepeatedCompositeFieldContainer[IdentityOperation]
    def __init__(self, subject: _Optional[str] = ..., device_id: _Optional[str] = ..., device_signing_secret: _Optional[bytes] = ..., keys: _Optional[_Iterable[_Union[SecretKey, _Mapping]]] = ..., trust_anchors: _Optional[_Iterable[_Union[TrustAnchor, _Mapping]]] = ..., pending_root_secret: _Optional[bytes] = ..., pending_binding: _Optional[bytes] = ..., addition_secret: _Optional[bytes] = ..., account_jwks: _Optional[str] = ..., account_issuer: _Optional[str] = ..., account_audience: _Optional[str] = ..., prepared_operations: _Optional[_Iterable[_Union[PreparedOperation, _Mapping]]] = ..., device_signing_public: _Optional[bytes] = ..., device_receiver_secret: _Optional[bytes] = ..., device_receiver_public: _Optional[bytes] = ..., genesis_binding: _Optional[bytes] = ..., device_status: _Optional[_Union[DeviceStatus, str]] = ..., identity_operations: _Optional[_Iterable[_Union[IdentityOperation, _Mapping]]] = ...) -> None: ...

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
    values: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    key_deliveries: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    key_certificates: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    identity_statements: _containers.RepeatedCompositeFieldContainer[IdentityRecord]
    commit_receipts: _containers.RepeatedCompositeFieldContainer[CommitReceiptBody]
    identity_revision: int
    documents: _containers.RepeatedCompositeFieldContainer[SignedDocument]
    commitments: _containers.RepeatedCompositeFieldContainer[HashCommitment]
    proofs: _containers.RepeatedCompositeFieldContainer[PossessionProof]
    distribution_revision: int
    def __init__(self, values: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., key_deliveries: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., key_certificates: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., identity_statements: _Optional[_Iterable[_Union[IdentityRecord, _Mapping]]] = ..., commit_receipts: _Optional[_Iterable[_Union[CommitReceiptBody, _Mapping]]] = ..., identity_revision: _Optional[int] = ..., documents: _Optional[_Iterable[_Union[SignedDocument, _Mapping]]] = ..., commitments: _Optional[_Iterable[_Union[HashCommitment, _Mapping]]] = ..., proofs: _Optional[_Iterable[_Union[PossessionProof, _Mapping]]] = ..., distribution_revision: _Optional[int] = ...) -> None: ...

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
    protection_key: KeyRef
    plaintext: bytes
    kind: str
    deleted: bool
    immutable: bool
    author_device_id: str
    cursor: int
    author_subject: str
    def __init__(self, id: _Optional[str] = ..., revision: _Optional[int] = ..., protection_key: _Optional[_Union[KeyRef, _Mapping]] = ..., plaintext: _Optional[bytes] = ..., kind: _Optional[str] = ..., deleted: bool = ..., immutable: bool = ..., author_device_id: _Optional[str] = ..., cursor: _Optional[int] = ..., author_subject: _Optional[str] = ...) -> None: ...

class OpenedValues(_message.Message):
    __slots__ = ("values", "state", "verified_documents")
    VALUES_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[OpenedValue]
    state: CoreState
    verified_documents: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    def __init__(self, values: _Optional[_Iterable[_Union[OpenedValue, _Mapping]]] = ..., state: _Optional[_Union[CoreState, _Mapping]] = ..., verified_documents: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ...) -> None: ...

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
    protection_key: KeyRef
    plaintext: bytes
    kind: str
    deleted: bool
    immutable: bool
    def __init__(self, id: _Optional[str] = ..., expected_revision: _Optional[int] = ..., protection_key: _Optional[_Union[KeyRef, _Mapping]] = ..., plaintext: _Optional[bytes] = ..., kind: _Optional[str] = ..., deleted: bool = ..., immutable: bool = ...) -> None: ...

class DeliveryMutation(_message.Message):
    __slots__ = ("target", "recipient", "include_history")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    target: KeyRef
    recipient: PublicKey
    include_history: bool
    def __init__(self, target: _Optional[_Union[KeyRef, _Mapping]] = ..., recipient: _Optional[_Union[PublicKey, _Mapping]] = ..., include_history: bool = ...) -> None: ...

class CryptoMutationInput(_message.Message):
    __slots__ = ("state", "bundle", "operation_id", "values", "deliveries", "create_protection_keys", "namespace_id", "application_binding", "documents")
    STATE_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    CREATE_PROTECTION_KEYS_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_BINDING_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    bundle: CryptoReadBundle
    operation_id: str
    values: _containers.RepeatedCompositeFieldContainer[ValueMutation]
    deliveries: _containers.RepeatedCompositeFieldContainer[DeliveryMutation]
    create_protection_keys: _containers.RepeatedCompositeFieldContainer[KeyRef]
    namespace_id: str
    application_binding: bytes
    documents: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., bundle: _Optional[_Union[CryptoReadBundle, _Mapping]] = ..., operation_id: _Optional[str] = ..., values: _Optional[_Iterable[_Union[ValueMutation, _Mapping]]] = ..., deliveries: _Optional[_Iterable[_Union[DeliveryMutation, _Mapping]]] = ..., create_protection_keys: _Optional[_Iterable[_Union[KeyRef, _Mapping]]] = ..., namespace_id: _Optional[str] = ..., application_binding: _Optional[bytes] = ..., documents: _Optional[_Iterable[bytes]] = ...) -> None: ...

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
    values: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    key_deliveries: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    key_certificates: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    namespace_id: str
    application_binding: bytes
    def __init__(self, operation_id: _Optional[str] = ..., expected_identity_revision: _Optional[int] = ..., expected_distribution_revision: _Optional[int] = ..., target_heads: _Optional[_Iterable[_Union[TargetHead, _Mapping]]] = ..., values: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., key_deliveries: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., key_certificates: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., namespace_id: _Optional[str] = ..., application_binding: _Optional[bytes] = ...) -> None: ...

class PreparedMutation(_message.Message):
    __slots__ = ("command", "state", "signed_documents")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SIGNED_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    command: SignedBytes
    state: CoreState
    signed_documents: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    def __init__(self, command: _Optional[_Union[SignedBytes, _Mapping]] = ..., state: _Optional[_Union[CoreState, _Mapping]] = ..., signed_documents: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ...) -> None: ...

class DeviceEnrollment(_message.Message):
    __slots__ = ("state", "bundle", "operation_id", "device", "code_challenge", "code_signature", "code_public_key", "sealed_bootstrap", "action", "account_assertion", "now_seconds", "addition_code", "pairing_request")
    STATE_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    CODE_CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    CODE_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    CODE_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    SEALED_BOOTSTRAP_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ASSERTION_FIELD_NUMBER: _ClassVar[int]
    NOW_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ADDITION_CODE_FIELD_NUMBER: _ClassVar[int]
    PAIRING_REQUEST_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    bundle: CryptoReadBundle
    operation_id: str
    device: Device
    code_challenge: bytes
    code_signature: bytes
    code_public_key: bytes
    sealed_bootstrap: bytes
    action: EnrollmentAction
    account_assertion: str
    now_seconds: int
    addition_code: bytes
    pairing_request: SignedBytes
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., bundle: _Optional[_Union[CryptoReadBundle, _Mapping]] = ..., operation_id: _Optional[str] = ..., device: _Optional[_Union[Device, _Mapping]] = ..., code_challenge: _Optional[bytes] = ..., code_signature: _Optional[bytes] = ..., code_public_key: _Optional[bytes] = ..., sealed_bootstrap: _Optional[bytes] = ..., action: _Optional[_Union[EnrollmentAction, str]] = ..., account_assertion: _Optional[str] = ..., now_seconds: _Optional[int] = ..., addition_code: _Optional[bytes] = ..., pairing_request: _Optional[_Union[SignedBytes, _Mapping]] = ...) -> None: ...

class EnrollmentBody(_message.Message):
    __slots__ = ("operation_id", "expected_identity_revision", "device", "code_challenge", "code_signature", "code_public_key", "sealed_bootstrap", "action", "subject")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_IDENTITY_REVISION_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    CODE_CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    CODE_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    CODE_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    SEALED_BOOTSTRAP_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    expected_identity_revision: int
    device: Device
    code_challenge: bytes
    code_signature: bytes
    code_public_key: bytes
    sealed_bootstrap: bytes
    action: EnrollmentAction
    subject: str
    def __init__(self, operation_id: _Optional[str] = ..., expected_identity_revision: _Optional[int] = ..., device: _Optional[_Union[Device, _Mapping]] = ..., code_challenge: _Optional[bytes] = ..., code_signature: _Optional[bytes] = ..., code_public_key: _Optional[bytes] = ..., sealed_bootstrap: _Optional[bytes] = ..., action: _Optional[_Union[EnrollmentAction, str]] = ..., subject: _Optional[str] = ...) -> None: ...

class IdentityRotation(_message.Message):
    __slots__ = ("state", "bundle", "operation_id", "active_devices", "revoke_device_ids", "replace_addition_key")
    STATE_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_DEVICES_FIELD_NUMBER: _ClassVar[int]
    REVOKE_DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    REPLACE_ADDITION_KEY_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    bundle: CryptoReadBundle
    operation_id: str
    active_devices: _containers.RepeatedCompositeFieldContainer[Device]
    revoke_device_ids: _containers.RepeatedScalarFieldContainer[str]
    replace_addition_key: bool
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., bundle: _Optional[_Union[CryptoReadBundle, _Mapping]] = ..., operation_id: _Optional[str] = ..., active_devices: _Optional[_Iterable[_Union[Device, _Mapping]]] = ..., revoke_device_ids: _Optional[_Iterable[str]] = ..., replace_addition_key: bool = ...) -> None: ...

class RotationBody(_message.Message):
    __slots__ = ("operation_id", "expected_identity_revision", "identity", "deliveries", "bootstrap", "revoked_device_ids", "key_certificates", "replace_addition_key")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_IDENTITY_REVISION_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_FIELD_NUMBER: _ClassVar[int]
    REVOKED_DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    KEY_CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    REPLACE_ADDITION_KEY_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    expected_identity_revision: int
    identity: IdentityRecord
    deliveries: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    bootstrap: bytes
    revoked_device_ids: _containers.RepeatedScalarFieldContainer[str]
    key_certificates: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    replace_addition_key: bool
    def __init__(self, operation_id: _Optional[str] = ..., expected_identity_revision: _Optional[int] = ..., identity: _Optional[_Union[IdentityRecord, _Mapping]] = ..., deliveries: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., bootstrap: _Optional[bytes] = ..., revoked_device_ids: _Optional[_Iterable[str]] = ..., key_certificates: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., replace_addition_key: bool = ...) -> None: ...

class PreparedIdentityChange(_message.Message):
    __slots__ = ("command", "state", "binding_bytes", "binding_nonce", "identity", "addition_code", "bootstrap", "key_certificates", "deliveries", "device")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    BINDING_BYTES_FIELD_NUMBER: _ClassVar[int]
    BINDING_NONCE_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    ADDITION_CODE_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_FIELD_NUMBER: _ClassVar[int]
    KEY_CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    command: SignedBytes
    state: CoreState
    binding_bytes: bytes
    binding_nonce: bytes
    identity: IdentityRecord
    addition_code: bytes
    bootstrap: bytes
    key_certificates: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    deliveries: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    device: Device
    def __init__(self, command: _Optional[_Union[SignedBytes, _Mapping]] = ..., state: _Optional[_Union[CoreState, _Mapping]] = ..., binding_bytes: _Optional[bytes] = ..., binding_nonce: _Optional[bytes] = ..., identity: _Optional[_Union[IdentityRecord, _Mapping]] = ..., addition_code: _Optional[bytes] = ..., bootstrap: _Optional[bytes] = ..., key_certificates: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., deliveries: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., device: _Optional[_Union[Device, _Mapping]] = ...) -> None: ...

class RejectPreparedOperationInput(_message.Message):
    __slots__ = ("state", "command")
    STATE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    command: SignedBytes
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., command: _Optional[_Union[SignedBytes, _Mapping]] = ...) -> None: ...

class RejectedPreparedOperation(_message.Message):
    __slots__ = ("state", "removed")
    STATE_FIELD_NUMBER: _ClassVar[int]
    REMOVED_FIELD_NUMBER: _ClassVar[int]
    state: CoreState
    removed: bool
    def __init__(self, state: _Optional[_Union[CoreState, _Mapping]] = ..., removed: bool = ...) -> None: ...

class CoreRequest(_message.Message):
    __slots__ = ("open", "prepare", "enroll", "rotate", "reject_prepared_operation")
    OPEN_FIELD_NUMBER: _ClassVar[int]
    PREPARE_FIELD_NUMBER: _ClassVar[int]
    ENROLL_FIELD_NUMBER: _ClassVar[int]
    ROTATE_FIELD_NUMBER: _ClassVar[int]
    REJECT_PREPARED_OPERATION_FIELD_NUMBER: _ClassVar[int]
    open: OpenInput
    prepare: CryptoMutationInput
    enroll: DeviceEnrollment
    rotate: IdentityRotation
    reject_prepared_operation: RejectPreparedOperationInput
    def __init__(self, open: _Optional[_Union[OpenInput, _Mapping]] = ..., prepare: _Optional[_Union[CryptoMutationInput, _Mapping]] = ..., enroll: _Optional[_Union[DeviceEnrollment, _Mapping]] = ..., rotate: _Optional[_Union[IdentityRotation, _Mapping]] = ..., reject_prepared_operation: _Optional[_Union[RejectPreparedOperationInput, _Mapping]] = ...) -> None: ...

class CoreResponse(_message.Message):
    __slots__ = ("opened", "prepared", "identity_change", "error", "rejected_prepared_operation")
    OPENED_FIELD_NUMBER: _ClassVar[int]
    PREPARED_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_CHANGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    REJECTED_PREPARED_OPERATION_FIELD_NUMBER: _ClassVar[int]
    opened: OpenedValues
    prepared: PreparedMutation
    identity_change: PreparedIdentityChange
    error: str
    rejected_prepared_operation: RejectedPreparedOperation
    def __init__(self, opened: _Optional[_Union[OpenedValues, _Mapping]] = ..., prepared: _Optional[_Union[PreparedMutation, _Mapping]] = ..., identity_change: _Optional[_Union[PreparedIdentityChange, _Mapping]] = ..., error: _Optional[str] = ..., rejected_prepared_operation: _Optional[_Union[RejectedPreparedOperation, _Mapping]] = ...) -> None: ...

class GenesisPublicBinding(_message.Message):
    __slots__ = ("subject", "root_signing_public_key", "receiver", "addition_public_key", "challenge", "addition_receiver_public_key")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    ROOT_SIGNING_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    ADDITION_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    ADDITION_RECEIVER_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    subject: str
    root_signing_public_key: bytes
    receiver: PublicKey
    addition_public_key: bytes
    challenge: bytes
    addition_receiver_public_key: bytes
    def __init__(self, subject: _Optional[str] = ..., root_signing_public_key: _Optional[bytes] = ..., receiver: _Optional[_Union[PublicKey, _Mapping]] = ..., addition_public_key: _Optional[bytes] = ..., challenge: _Optional[bytes] = ..., addition_receiver_public_key: _Optional[bytes] = ...) -> None: ...

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

class SignedDocument(_message.Message):
    __slots__ = ("signed", "expected_digest", "expected_root_digest")
    SIGNED_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_DIGEST_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_ROOT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    signed: SignedBytes
    expected_digest: bytes
    expected_root_digest: bytes
    def __init__(self, signed: _Optional[_Union[SignedBytes, _Mapping]] = ..., expected_digest: _Optional[bytes] = ..., expected_root_digest: _Optional[bytes] = ...) -> None: ...

class HashCommitment(_message.Message):
    __slots__ = ("plaintext", "expected_digest")
    PLAINTEXT_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_DIGEST_FIELD_NUMBER: _ClassVar[int]
    plaintext: bytes
    expected_digest: bytes
    def __init__(self, plaintext: _Optional[bytes] = ..., expected_digest: _Optional[bytes] = ...) -> None: ...

class LocalSeal(_message.Message):
    __slots__ = ("key", "plaintext", "aad")
    KEY_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_FIELD_NUMBER: _ClassVar[int]
    AAD_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    plaintext: bytes
    aad: bytes
    def __init__(self, key: _Optional[bytes] = ..., plaintext: _Optional[bytes] = ..., aad: _Optional[bytes] = ...) -> None: ...

class LocalOpen(_message.Message):
    __slots__ = ("key", "value", "aad")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    AAD_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    value: AeadValue
    aad: bytes
    def __init__(self, key: _Optional[bytes] = ..., value: _Optional[_Union[AeadValue, _Mapping]] = ..., aad: _Optional[bytes] = ...) -> None: ...

class PreparedOperation(_message.Message):
    __slots__ = ("operation_id", "input_digest", "command", "signed_documents")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    SIGNED_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    input_digest: bytes
    command: SignedBytes
    signed_documents: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    def __init__(self, operation_id: _Optional[str] = ..., input_digest: _Optional[bytes] = ..., command: _Optional[_Union[SignedBytes, _Mapping]] = ..., signed_documents: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ...) -> None: ...

class ProofInput(_message.Message):
    __slots__ = ("secret", "challenge")
    SECRET_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    secret: bytes
    challenge: bytes
    def __init__(self, secret: _Optional[bytes] = ..., challenge: _Optional[bytes] = ...) -> None: ...

class PossessionProof(_message.Message):
    __slots__ = ("public_key", "challenge", "signature")
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    public_key: bytes
    challenge: bytes
    signature: bytes
    def __init__(self, public_key: _Optional[bytes] = ..., challenge: _Optional[bytes] = ..., signature: _Optional[bytes] = ...) -> None: ...

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

class LocalSealed(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    value: AeadValue
    def __init__(self, key: _Optional[bytes] = ..., value: _Optional[_Union[AeadValue, _Mapping]] = ...) -> None: ...

class RandomInput(_message.Message):
    __slots__ = ("length",)
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    length: int
    def __init__(self, length: _Optional[int] = ...) -> None: ...

class CoreUtilityRequest(_message.Message):
    __slots__ = ("seal_stream", "open_stream", "seal_local", "open_local", "prove", "random")
    SEAL_STREAM_FIELD_NUMBER: _ClassVar[int]
    OPEN_STREAM_FIELD_NUMBER: _ClassVar[int]
    SEAL_LOCAL_FIELD_NUMBER: _ClassVar[int]
    OPEN_LOCAL_FIELD_NUMBER: _ClassVar[int]
    PROVE_FIELD_NUMBER: _ClassVar[int]
    RANDOM_FIELD_NUMBER: _ClassVar[int]
    seal_stream: StreamSeal
    open_stream: StreamOpen
    seal_local: LocalSeal
    open_local: LocalOpen
    prove: ProofInput
    random: RandomInput
    def __init__(self, seal_stream: _Optional[_Union[StreamSeal, _Mapping]] = ..., open_stream: _Optional[_Union[StreamOpen, _Mapping]] = ..., seal_local: _Optional[_Union[LocalSeal, _Mapping]] = ..., open_local: _Optional[_Union[LocalOpen, _Mapping]] = ..., prove: _Optional[_Union[ProofInput, _Mapping]] = ..., random: _Optional[_Union[RandomInput, _Mapping]] = ...) -> None: ...

class CoreUtilityResponse(_message.Message):
    __slots__ = ("stream_sealed", "stream_opened", "local_sealed", "local_plaintext", "proof", "random_bytes", "error")
    STREAM_SEALED_FIELD_NUMBER: _ClassVar[int]
    STREAM_OPENED_FIELD_NUMBER: _ClassVar[int]
    LOCAL_SEALED_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PLAINTEXT_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    RANDOM_BYTES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    stream_sealed: StreamSealed
    stream_opened: StreamOpened
    local_sealed: LocalSealed
    local_plaintext: bytes
    proof: PossessionProof
    random_bytes: bytes
    error: str
    def __init__(self, stream_sealed: _Optional[_Union[StreamSealed, _Mapping]] = ..., stream_opened: _Optional[_Union[StreamOpened, _Mapping]] = ..., local_sealed: _Optional[_Union[LocalSealed, _Mapping]] = ..., local_plaintext: _Optional[bytes] = ..., proof: _Optional[_Union[PossessionProof, _Mapping]] = ..., random_bytes: _Optional[bytes] = ..., error: _Optional[str] = ...) -> None: ...

class IdentityOperation(_message.Message):
    __slots__ = ("operation_id", "action", "input_digest", "command", "identity", "bootstrap", "binding_bytes", "binding_nonce", "key_certificates", "deliveries", "device", "addition_code", "kind")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_FIELD_NUMBER: _ClassVar[int]
    BINDING_BYTES_FIELD_NUMBER: _ClassVar[int]
    BINDING_NONCE_FIELD_NUMBER: _ClassVar[int]
    KEY_CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    ADDITION_CODE_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    action: EnrollmentAction
    input_digest: bytes
    command: SignedBytes
    identity: IdentityRecord
    bootstrap: bytes
    binding_bytes: bytes
    binding_nonce: bytes
    key_certificates: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    deliveries: _containers.RepeatedCompositeFieldContainer[SignedBytes]
    device: Device
    addition_code: bytes
    kind: IdentityOperationKind
    def __init__(self, operation_id: _Optional[str] = ..., action: _Optional[_Union[EnrollmentAction, str]] = ..., input_digest: _Optional[bytes] = ..., command: _Optional[_Union[SignedBytes, _Mapping]] = ..., identity: _Optional[_Union[IdentityRecord, _Mapping]] = ..., bootstrap: _Optional[bytes] = ..., binding_bytes: _Optional[bytes] = ..., binding_nonce: _Optional[bytes] = ..., key_certificates: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., deliveries: _Optional[_Iterable[_Union[SignedBytes, _Mapping]]] = ..., device: _Optional[_Union[Device, _Mapping]] = ..., addition_code: _Optional[bytes] = ..., kind: _Optional[_Union[IdentityOperationKind, str]] = ...) -> None: ...
