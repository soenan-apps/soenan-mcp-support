# Generated from CryptoService and OpenAPI; do not modify.
from base64 import b64decode, b64encode
from collections.abc import Callable

from arteligo_public_api_client.api.default import (
    approve_crypto_invitation as _approve_crypto_invitation,
)
from arteligo_public_api_client.api.default import attest_crypto as _attest_crypto
from arteligo_public_api_client.api.default import commit_crypto as _commit_crypto
from arteligo_public_api_client.api.default import (
    create_crypto_file_upload_capability as _create_crypto_file_upload_capability,
)
from arteligo_public_api_client.api.default import (
    create_crypto_invitation as _create_crypto_invitation,
)
from arteligo_public_api_client.api.default import (
    create_crypto_project as _create_crypto_project,
)
from arteligo_public_api_client.api.default import enroll_crypto as _enroll_crypto
from arteligo_public_api_client.api.default import genesis_crypto as _genesis_crypto
from arteligo_public_api_client.api.default import (
    get_crypto_project_audience as _get_crypto_project_audience,
)
from arteligo_public_api_client.api.default import (
    get_crypto_settings as _get_crypto_settings,
)
from arteligo_public_api_client.api.default import (
    list_crypto_projects as _list_crypto_projects,
)
from arteligo_public_api_client.api.default import (
    prepare_crypto_group_member as _prepare_crypto_group_member,
)
from arteligo_public_api_client.api.default import (
    prepare_crypto_owner_delivery as _prepare_crypto_owner_delivery,
)
from arteligo_public_api_client.api.default import read_crypto as _read_crypto
from arteligo_public_api_client.api.default import read_crypto_file as _read_crypto_file
from arteligo_public_api_client.api.default import (
    read_crypto_invitations as _read_crypto_invitations,
)
from arteligo_public_api_client.api.default import (
    request_crypto_invitation as _request_crypto_invitation,
)
from arteligo_public_api_client.api.default import (
    revoke_crypto_invitation as _revoke_crypto_invitation,
)
from arteligo_public_api_client.api.default import rotate_crypto as _rotate_crypto
from arteligo_public_api_client.client import AuthenticatedClient
from arteligo_public_api_client.models.crypto_proto_message import CryptoProtoMessage
from arteligo_public_api_client.models.error_envelope import ErrorEnvelope
from arteligo_public_api_client.types import Response
from google.protobuf.message import DecodeError
from soenan.arteligo.application.v1 import application_pb2 as app

from ._crypto import E2eeError

EnvelopeCall = Callable[
    [AuthenticatedClient], Response[CryptoProtoMessage | ErrorEnvelope]
]
EnvelopeExecutor = Callable[[EnvelopeCall], CryptoProtoMessage]


class CryptoServiceClient:
    def __init__(self, exchange: EnvelopeExecutor):
        self._exchange = exchange

    def approve_crypto_invitation(
        self, request: app.InvitationApproval
    ) -> app.CommitCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _approve_crypto_invitation.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.CommitCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def attest_crypto(
        self, request: app.NonceAttestationRequest
    ) -> app.NonceAttestationResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _attest_crypto.sync_detailed(client=client, body=body)
        )
        try:
            return app.NonceAttestationResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def commit_crypto(
        self, request: app.CommitCryptoRequest
    ) -> app.CommitCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _commit_crypto.sync_detailed(client=client, body=body)
        )
        try:
            return app.CommitCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def create_crypto_file_upload_capability(
        self, request: app.FileOperationRequest
    ) -> app.FileOperationResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _create_crypto_file_upload_capability.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.FileOperationResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def create_crypto_invitation(
        self, request: app.InvitationRequest
    ) -> app.InvitationReadResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _create_crypto_invitation.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.InvitationReadResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def create_crypto_project(
        self, request: app.ProjectCreateRequest
    ) -> app.CommitCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _create_crypto_project.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.CommitCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def enroll_crypto(
        self, request: app.IdentityChangeRequest
    ) -> app.CommitCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _enroll_crypto.sync_detailed(client=client, body=body)
        )
        try:
            return app.CommitCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def genesis_crypto(self, request: app.GenesisRequest) -> app.CommitCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _genesis_crypto.sync_detailed(client=client, body=body)
        )
        try:
            return app.CommitCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def get_crypto_project_audience(
        self, request: app.ProjectAudienceRequest
    ) -> app.ProjectAudienceResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _get_crypto_project_audience.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.ProjectAudienceResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def get_crypto_settings(
        self, request: app.CryptoSettingsRequest
    ) -> app.CryptoSettingsResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _get_crypto_settings.sync_detailed(client=client, body=body)
        )
        try:
            return app.CryptoSettingsResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def list_crypto_projects(
        self, request: app.ProjectCatalogRequest
    ) -> app.ProjectCatalogResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _list_crypto_projects.sync_detailed(client=client, body=body)
        )
        try:
            return app.ProjectCatalogResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def prepare_crypto_group_member(
        self, request: app.GroupMemberPreparationRequest
    ) -> app.GroupMemberPreparationResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _prepare_crypto_group_member.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.GroupMemberPreparationResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def prepare_crypto_owner_delivery(
        self, request: app.OwnerDeliveryRequest
    ) -> app.CommitCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _prepare_crypto_owner_delivery.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.CommitCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def read_crypto(self, request: app.ReadCryptoRequest) -> app.ReadCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _read_crypto.sync_detailed(client=client, body=body)
        )
        try:
            return app.ReadCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def read_crypto_file(
        self, request: app.FileOperationRequest
    ) -> app.FileOperationResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _read_crypto_file.sync_detailed(client=client, body=body)
        )
        try:
            return app.FileOperationResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def read_crypto_invitations(
        self, request: app.InvitationReadRequest
    ) -> app.InvitationReadResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _read_crypto_invitations.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.InvitationReadResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def request_crypto_invitation(
        self, request: app.InvitationJoinRequest
    ) -> app.InvitationReadResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _request_crypto_invitation.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.InvitationReadResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def revoke_crypto_invitation(
        self, request: app.InvitationRequest
    ) -> app.InvitationReadResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _revoke_crypto_invitation.sync_detailed(
                client=client, body=body
            )
        )
        try:
            return app.InvitationReadResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None

    def rotate_crypto(
        self, request: app.IdentityChangeRequest
    ) -> app.CommitCryptoResponse:
        body = CryptoProtoMessage(
            bytes_=b64encode(request.SerializeToString()).decode("ascii")
        )
        envelope = self._exchange(
            lambda client: _rotate_crypto.sync_detailed(client=client, body=body)
        )
        try:
            return app.CommitCryptoResponse.FromString(
                b64decode(envelope.bytes_, validate=True)
            )
        except (DecodeError, ValueError):
            raise E2eeError("invalid_response") from None
