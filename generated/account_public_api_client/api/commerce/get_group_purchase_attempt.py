from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.commerce_purchase_attempt import CommercePurchaseAttempt
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    organization_id: str,
    attempt_id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/organizations/{organization_id}/purchase-attempts/{attempt_id}".format(
            organization_id=quote(str(organization_id), safe=""),
            attempt_id=quote(str(attempt_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CommercePurchaseAttempt | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = CommercePurchaseAttempt.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CommercePurchaseAttempt | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    attempt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[CommercePurchaseAttempt | ErrorResponse]:
    """
    Args:
        organization_id (str):
        attempt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommercePurchaseAttempt | ErrorResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        attempt_id=attempt_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    attempt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> CommercePurchaseAttempt | ErrorResponse | None:
    """
    Args:
        organization_id (str):
        attempt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommercePurchaseAttempt | ErrorResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        attempt_id=attempt_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    attempt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[CommercePurchaseAttempt | ErrorResponse]:
    """
    Args:
        organization_id (str):
        attempt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommercePurchaseAttempt | ErrorResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        attempt_id=attempt_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    attempt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> CommercePurchaseAttempt | ErrorResponse | None:
    """
    Args:
        organization_id (str):
        attempt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommercePurchaseAttempt | ErrorResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            attempt_id=attempt_id,
            client=client,
        )
    ).parsed
