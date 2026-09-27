from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.logout_product_session_response import LogoutProductSessionResponse
from ...models.logout_product_session_sec_fetch_site import (
    LogoutProductSessionSecFetchSite,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    origin: str | Unset = UNSET,
    sec_fetch_site: LogoutProductSessionSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/auth/logout",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | LogoutProductSessionResponse:
    if response.status_code == 200:
        response_200 = LogoutProductSessionResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | LogoutProductSessionResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    origin: str | Unset = UNSET,
    sec_fetch_site: LogoutProductSessionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | LogoutProductSessionResponse]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (LogoutProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | LogoutProductSessionResponse]
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
    origin: str | Unset = UNSET,
    sec_fetch_site: LogoutProductSessionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | LogoutProductSessionResponse | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (LogoutProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | LogoutProductSessionResponse
    """

    return sync_detailed(
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    origin: str | Unset = UNSET,
    sec_fetch_site: LogoutProductSessionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | LogoutProductSessionResponse]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (LogoutProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | LogoutProductSessionResponse]
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
    origin: str | Unset = UNSET,
    sec_fetch_site: LogoutProductSessionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | LogoutProductSessionResponse | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (LogoutProductSessionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | LogoutProductSessionResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
