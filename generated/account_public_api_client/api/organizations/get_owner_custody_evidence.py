from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.owner_custody_evidence_response import OwnerCustodyEvidenceResponse
from ...types import UNSET, Response


def _get_kwargs(
    account_subject: str,
    evidence_digest: str,
    *,
    challenge: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["challenge"] = challenge

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/owner-authority/custody-evidence/{account_subject}/{evidence_digest}".format(
            account_subject=quote(str(account_subject), safe=""),
            evidence_digest=quote(str(evidence_digest), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | OwnerCustodyEvidenceResponse | None:
    if response.status_code == 200:
        response_200 = OwnerCustodyEvidenceResponse.from_dict(response.json())

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
) -> Response[ErrorResponse | OwnerCustodyEvidenceResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_subject: str,
    evidence_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> Response[ErrorResponse | OwnerCustodyEvidenceResponse]:
    """Resolve one exact immutable public custody acceptance fact.

     Returns only the historical acceptance witness for the exact subject and signed-command digest. No
    organization, session or read capability is required. The challenge authenticates this direct
    Account response, not event freshness. A witness remains historical after device revocation or root
    replacement and never establishes current authority or permission.

    Args:
        account_subject (str):
        evidence_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerCustodyEvidenceResponse]
    """

    kwargs = _get_kwargs(
        account_subject=account_subject,
        evidence_digest=evidence_digest,
        challenge=challenge,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_subject: str,
    evidence_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> ErrorResponse | OwnerCustodyEvidenceResponse | None:
    """Resolve one exact immutable public custody acceptance fact.

     Returns only the historical acceptance witness for the exact subject and signed-command digest. No
    organization, session or read capability is required. The challenge authenticates this direct
    Account response, not event freshness. A witness remains historical after device revocation or root
    replacement and never establishes current authority or permission.

    Args:
        account_subject (str):
        evidence_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerCustodyEvidenceResponse
    """

    return sync_detailed(
        account_subject=account_subject,
        evidence_digest=evidence_digest,
        client=client,
        challenge=challenge,
    ).parsed


async def asyncio_detailed(
    account_subject: str,
    evidence_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> Response[ErrorResponse | OwnerCustodyEvidenceResponse]:
    """Resolve one exact immutable public custody acceptance fact.

     Returns only the historical acceptance witness for the exact subject and signed-command digest. No
    organization, session or read capability is required. The challenge authenticates this direct
    Account response, not event freshness. A witness remains historical after device revocation or root
    replacement and never establishes current authority or permission.

    Args:
        account_subject (str):
        evidence_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerCustodyEvidenceResponse]
    """

    kwargs = _get_kwargs(
        account_subject=account_subject,
        evidence_digest=evidence_digest,
        challenge=challenge,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_subject: str,
    evidence_digest: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
) -> ErrorResponse | OwnerCustodyEvidenceResponse | None:
    """Resolve one exact immutable public custody acceptance fact.

     Returns only the historical acceptance witness for the exact subject and signed-command digest. No
    organization, session or read capability is required. The challenge authenticates this direct
    Account response, not event freshness. A witness remains historical after device revocation or root
    replacement and never establishes current authority or permission.

    Args:
        account_subject (str):
        evidence_digest (str):
        challenge (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerCustodyEvidenceResponse
    """

    return (
        await asyncio_detailed(
            account_subject=account_subject,
            evidence_digest=evidence_digest,
            client=client,
            challenge=challenge,
        )
    ).parsed
