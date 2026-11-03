from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.owner_transfer_readiness import OwnerTransferReadiness
from ...types import UNSET, Response


def _get_kwargs(
    organization_id: str,
    *,
    target_subject: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["targetSubject"] = target_subject

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/organizations/{organization_id}/ownership/readiness".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | OwnerTransferReadiness | None:
    if response.status_code == 200:
        response_200 = OwnerTransferReadiness.from_dict(response.json())

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

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | OwnerTransferReadiness]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    target_subject: str,
) -> Response[ErrorResponse | OwnerTransferReadiness]:
    """
    Args:
        organization_id (str):
        target_subject (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerTransferReadiness]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        target_subject=target_subject,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    target_subject: str,
) -> ErrorResponse | OwnerTransferReadiness | None:
    """
    Args:
        organization_id (str):
        target_subject (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerTransferReadiness
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        target_subject=target_subject,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    target_subject: str,
) -> Response[ErrorResponse | OwnerTransferReadiness]:
    """
    Args:
        organization_id (str):
        target_subject (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerTransferReadiness]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        target_subject=target_subject,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    target_subject: str,
) -> ErrorResponse | OwnerTransferReadiness | None:
    """
    Args:
        organization_id (str):
        target_subject (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerTransferReadiness
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            target_subject=target_subject,
        )
    ).parsed
