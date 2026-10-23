from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.prepare_account_totp_sec_fetch_site import PrepareAccountTOTPSecFetchSite
from ...models.totp_setup import TOTPSetup
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    origin: str,
    sec_fetch_site: PrepareAccountTOTPSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/account/totp/prepare",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | TOTPSetup | None:
    if response.status_code == 200:
        response_200 = TOTPSetup.from_dict(response.json())

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
) -> Response[ErrorResponse | TOTPSetup]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: PrepareAccountTOTPSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | TOTPSetup]:
    """Prepare a server-bound replacement Authenticator after fresh root authentication.

    Args:
        origin (str):
        sec_fetch_site (PrepareAccountTOTPSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | TOTPSetup]
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
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: PrepareAccountTOTPSecFetchSite | Unset = UNSET,
) -> ErrorResponse | TOTPSetup | None:
    """Prepare a server-bound replacement Authenticator after fresh root authentication.

    Args:
        origin (str):
        sec_fetch_site (PrepareAccountTOTPSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | TOTPSetup
    """

    return sync_detailed(
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: PrepareAccountTOTPSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | TOTPSetup]:
    """Prepare a server-bound replacement Authenticator after fresh root authentication.

    Args:
        origin (str):
        sec_fetch_site (PrepareAccountTOTPSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | TOTPSetup]
    """

    kwargs = _get_kwargs(
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: PrepareAccountTOTPSecFetchSite | Unset = UNSET,
) -> ErrorResponse | TOTPSetup | None:
    """Prepare a server-bound replacement Authenticator after fresh root authentication.

    Args:
        origin (str):
        sec_fetch_site (PrepareAccountTOTPSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | TOTPSetup
    """

    return (
        await asyncio_detailed(
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
