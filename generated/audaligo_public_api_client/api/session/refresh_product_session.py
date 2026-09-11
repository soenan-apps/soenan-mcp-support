from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.refresh_product_session_sec_fetch_site import (
    RefreshProductSessionSecFetchSite,
)
from ...models.refresh_session_response import RefreshSessionResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    origin: str,
    sec_fetch_site: RefreshProductSessionSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/auth/refresh",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | RefreshSessionResponse:
    if response.status_code == 200:
        response_200 = RefreshSessionResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | RefreshSessionResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RefreshProductSessionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | RefreshSessionResponse]:
    """
    Args:
        origin (str):
        sec_fetch_site (RefreshProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | RefreshSessionResponse]
    """

    kwargs = _get_kwargs(
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RefreshProductSessionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | RefreshSessionResponse | None:
    """
    Args:
        origin (str):
        sec_fetch_site (RefreshProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | RefreshSessionResponse
    """

    return sync_detailed(
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RefreshProductSessionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | RefreshSessionResponse]:
    """
    Args:
        origin (str):
        sec_fetch_site (RefreshProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | RefreshSessionResponse]
    """

    kwargs = _get_kwargs(
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RefreshProductSessionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | RefreshSessionResponse | None:
    """
    Args:
        origin (str):
        sec_fetch_site (RefreshProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | RefreshSessionResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
