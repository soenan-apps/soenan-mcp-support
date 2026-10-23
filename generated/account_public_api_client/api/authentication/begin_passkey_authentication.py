from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.begin_passkey_authentication_sec_fetch_site import (
    BeginPasskeyAuthenticationSecFetchSite,
)
from ...models.error_response import ErrorResponse
from ...models.passkey_authentication_options import PasskeyAuthenticationOptions
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    origin: str,
    sec_fetch_site: BeginPasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/auth/passkey/options",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | PasskeyAuthenticationOptions | None:
    if response.status_code == 200:
        response_200 = PasskeyAuthenticationOptions.from_dict(response.json())

        return response_200

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = ErrorResponse.from_dict(response.json())

        return response_429

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | PasskeyAuthenticationOptions]:
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
    sec_fetch_site: BeginPasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | PasskeyAuthenticationOptions]:
    """Start a discoverable Passkey authentication ceremony.

    Args:
        origin (str):
        sec_fetch_site (BeginPasskeyAuthenticationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | PasskeyAuthenticationOptions]
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
    sec_fetch_site: BeginPasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> ErrorResponse | PasskeyAuthenticationOptions | None:
    """Start a discoverable Passkey authentication ceremony.

    Args:
        origin (str):
        sec_fetch_site (BeginPasskeyAuthenticationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | PasskeyAuthenticationOptions
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
    sec_fetch_site: BeginPasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | PasskeyAuthenticationOptions]:
    """Start a discoverable Passkey authentication ceremony.

    Args:
        origin (str):
        sec_fetch_site (BeginPasskeyAuthenticationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | PasskeyAuthenticationOptions]
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
    sec_fetch_site: BeginPasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> ErrorResponse | PasskeyAuthenticationOptions | None:
    """Start a discoverable Passkey authentication ceremony.

    Args:
        origin (str):
        sec_fetch_site (BeginPasskeyAuthenticationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | PasskeyAuthenticationOptions
    """

    return (
        await asyncio_detailed(
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
