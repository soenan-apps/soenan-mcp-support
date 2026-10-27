from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.owner_custody_response import OwnerCustodyResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    account_subject: str,
    *,
    challenge: str,
    evidence_digest: str | Unset = UNSET,
    x_owner_read_capability: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["X-Owner-Read-Capability"] = x_owner_read_capability

    params: dict[str, Any] = {}

    params["challenge"] = challenge

    params["evidence_digest"] = evidence_digest

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/owner-authority/{organization_id}/custody/{account_subject}".format(
            organization_id=quote(str(organization_id), safe=""),
            account_subject=quote(str(account_subject), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | OwnerCustodyResponse | None:
    if response.status_code == 200:
        response_200 = OwnerCustodyResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | OwnerCustodyResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    account_subject: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    evidence_digest: str | Unset = UNSET,
    x_owner_read_capability: str,
) -> Response[ErrorResponse | OwnerCustodyResponse]:
    """
    Args:
        organization_id (str):
        account_subject (str):
        challenge (str):
        evidence_digest (str | Unset):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerCustodyResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        account_subject=account_subject,
        challenge=challenge,
        evidence_digest=evidence_digest,
        x_owner_read_capability=x_owner_read_capability,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    account_subject: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    evidence_digest: str | Unset = UNSET,
    x_owner_read_capability: str,
) -> ErrorResponse | OwnerCustodyResponse | None:
    """
    Args:
        organization_id (str):
        account_subject (str):
        challenge (str):
        evidence_digest (str | Unset):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerCustodyResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        account_subject=account_subject,
        client=client,
        challenge=challenge,
        evidence_digest=evidence_digest,
        x_owner_read_capability=x_owner_read_capability,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    account_subject: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    evidence_digest: str | Unset = UNSET,
    x_owner_read_capability: str,
) -> Response[ErrorResponse | OwnerCustodyResponse]:
    """
    Args:
        organization_id (str):
        account_subject (str):
        challenge (str):
        evidence_digest (str | Unset):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerCustodyResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        account_subject=account_subject,
        challenge=challenge,
        evidence_digest=evidence_digest,
        x_owner_read_capability=x_owner_read_capability,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    account_subject: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    evidence_digest: str | Unset = UNSET,
    x_owner_read_capability: str,
) -> ErrorResponse | OwnerCustodyResponse | None:
    """
    Args:
        organization_id (str):
        account_subject (str):
        challenge (str):
        evidence_digest (str | Unset):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerCustodyResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            account_subject=account_subject,
            client=client,
            challenge=challenge,
            evidence_digest=evidence_digest,
            x_owner_read_capability=x_owner_read_capability,
        )
    ).parsed
