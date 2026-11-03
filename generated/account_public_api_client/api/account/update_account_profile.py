from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_surface_view import AccountSurfaceView
from ...models.error_response import ErrorResponse
from ...models.update_account_profile_request import UpdateAccountProfileRequest
from ...models.update_account_profile_sec_fetch_site import (
    UpdateAccountProfileSecFetchSite,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: UpdateAccountProfileRequest,
    origin: str,
    sec_fetch_site: UpdateAccountProfileSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/account/profile",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountSurfaceView | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = AccountSurfaceView.from_dict(response.json())

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

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

    if response.status_code == 413:
        response_413 = ErrorResponse.from_dict(response.json())

        return response_413

    if response.status_code == 415:
        response_415 = ErrorResponse.from_dict(response.json())

        return response_415

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
) -> Response[AccountSurfaceView | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: UpdateAccountProfileRequest,
    origin: str,
    sec_fetch_site: UpdateAccountProfileSecFetchSite | Unset = UNSET,
) -> Response[AccountSurfaceView | ErrorResponse]:
    """Update the authenticated account display name.

    Args:
        origin (str):
        sec_fetch_site (UpdateAccountProfileSecFetchSite | Unset):
        body (UpdateAccountProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountSurfaceView | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: UpdateAccountProfileRequest,
    origin: str,
    sec_fetch_site: UpdateAccountProfileSecFetchSite | Unset = UNSET,
) -> AccountSurfaceView | ErrorResponse | None:
    """Update the authenticated account display name.

    Args:
        origin (str):
        sec_fetch_site (UpdateAccountProfileSecFetchSite | Unset):
        body (UpdateAccountProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountSurfaceView | ErrorResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: UpdateAccountProfileRequest,
    origin: str,
    sec_fetch_site: UpdateAccountProfileSecFetchSite | Unset = UNSET,
) -> Response[AccountSurfaceView | ErrorResponse]:
    """Update the authenticated account display name.

    Args:
        origin (str):
        sec_fetch_site (UpdateAccountProfileSecFetchSite | Unset):
        body (UpdateAccountProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountSurfaceView | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: UpdateAccountProfileRequest,
    origin: str,
    sec_fetch_site: UpdateAccountProfileSecFetchSite | Unset = UNSET,
) -> AccountSurfaceView | ErrorResponse | None:
    """Update the authenticated account display name.

    Args:
        origin (str):
        sec_fetch_site (UpdateAccountProfileSecFetchSite | Unset):
        body (UpdateAccountProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountSurfaceView | ErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
