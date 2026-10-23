from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.owner_certificate_signature_projection_response import (
    OwnerCertificateSignatureProjectionResponse,
)
from ...types import UNSET, Response


def _get_kwargs(
    account_subject: str,
    certificate_digest: str,
    *,
    challenge: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["challenge"] = challenge

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/owner-authority/certificate-projections/{account_subject}/{certificate_digest}".format(
            account_subject=quote(str(account_subject), safe=""),
            certificate_digest=quote(str(certificate_digest), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | OwnerCertificateSignatureProjectionResponse | None:
    if response.status_code == 200:
        response_200 = OwnerCertificateSignatureProjectionResponse.from_dict(
            response.json()
        )

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | OwnerCertificateSignatureProjectionResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_subject: str,
    certificate_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> Response[ErrorResponse | OwnerCertificateSignatureProjectionResponse]:
    """Resolve the verified safe subset of one exact original witnessed certificate.

     Attests only the original signature computation under the returned public key and the fixed signed
    fields. It does not assign that key to a person, establish an independent root anchor, or grant
    current authority. The original immutable custody witness must be resolved separately. Unknown
    projections return not found and reads never derive or backfill them.

    Args:
        account_subject (str):
        certificate_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerCertificateSignatureProjectionResponse]
    """

    kwargs = _get_kwargs(
        account_subject=account_subject,
        certificate_digest=certificate_digest,
        challenge=challenge,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_subject: str,
    certificate_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> ErrorResponse | OwnerCertificateSignatureProjectionResponse | None:
    """Resolve the verified safe subset of one exact original witnessed certificate.

     Attests only the original signature computation under the returned public key and the fixed signed
    fields. It does not assign that key to a person, establish an independent root anchor, or grant
    current authority. The original immutable custody witness must be resolved separately. Unknown
    projections return not found and reads never derive or backfill them.

    Args:
        account_subject (str):
        certificate_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerCertificateSignatureProjectionResponse
    """

    return sync_detailed(
        account_subject=account_subject,
        certificate_digest=certificate_digest,
        client=client,
        challenge=challenge,
    ).parsed


async def asyncio_detailed(
    account_subject: str,
    certificate_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> Response[ErrorResponse | OwnerCertificateSignatureProjectionResponse]:
    """Resolve the verified safe subset of one exact original witnessed certificate.

     Attests only the original signature computation under the returned public key and the fixed signed
    fields. It does not assign that key to a person, establish an independent root anchor, or grant
    current authority. The original immutable custody witness must be resolved separately. Unknown
    projections return not found and reads never derive or backfill them.

    Args:
        account_subject (str):
        certificate_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerCertificateSignatureProjectionResponse]
    """

    kwargs = _get_kwargs(
        account_subject=account_subject,
        certificate_digest=certificate_digest,
        challenge=challenge,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_subject: str,
    certificate_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> ErrorResponse | OwnerCertificateSignatureProjectionResponse | None:
    """Resolve the verified safe subset of one exact original witnessed certificate.

     Attests only the original signature computation under the returned public key and the fixed signed
    fields. It does not assign that key to a person, establish an independent root anchor, or grant
    current authority. The original immutable custody witness must be resolved separately. Unknown
    projections return not found and reads never derive or backfill them.

    Args:
        account_subject (str):
        certificate_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerCertificateSignatureProjectionResponse
    """

    return (
        await asyncio_detailed(
            account_subject=account_subject,
            certificate_digest=certificate_digest,
            client=client,
            challenge=challenge,
        )
    ).parsed
