from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.complete_passkey_authentication_sec_fetch_site import (
    CompletePasskeyAuthenticationSecFetchSite,
)
from ...models.error_response import ErrorResponse
from ...models.passkey_authentication_completion import PasskeyAuthenticationCompletion
from ...models.passkey_authentication_request import PasskeyAuthenticationRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PasskeyAuthenticationRequest,
    origin: str,
    sec_fetch_site: CompletePasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/auth/passkey/verify",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | PasskeyAuthenticationCompletion | None:
    if response.status_code == 200:
        response_200 = PasskeyAuthenticationCompletion.from_dict(response.json())

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
) -> Response[ErrorResponse | PasskeyAuthenticationCompletion]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PasskeyAuthenticationRequest,
    origin: str,
    sec_fetch_site: CompletePasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | PasskeyAuthenticationCompletion]:
    """Verify a Passkey assertion and create an Account JWT root session.

    Args:
        origin (str):
        sec_fetch_site (CompletePasskeyAuthenticationSecFetchSite | Unset):
        body (PasskeyAuthenticationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | PasskeyAuthenticationCompletion]
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
    client: AuthenticatedClient | Client,
    body: PasskeyAuthenticationRequest,
    origin: str,
    sec_fetch_site: CompletePasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> ErrorResponse | PasskeyAuthenticationCompletion | None:
    """Verify a Passkey assertion and create an Account JWT root session.

    Args:
        origin (str):
        sec_fetch_site (CompletePasskeyAuthenticationSecFetchSite | Unset):
        body (PasskeyAuthenticationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | PasskeyAuthenticationCompletion
    """

    return sync_detailed(
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PasskeyAuthenticationRequest,
    origin: str,
    sec_fetch_site: CompletePasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | PasskeyAuthenticationCompletion]:
    """Verify a Passkey assertion and create an Account JWT root session.

    Args:
        origin (str):
        sec_fetch_site (CompletePasskeyAuthenticationSecFetchSite | Unset):
        body (PasskeyAuthenticationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | PasskeyAuthenticationCompletion]
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
    client: AuthenticatedClient | Client,
    body: PasskeyAuthenticationRequest,
    origin: str,
    sec_fetch_site: CompletePasskeyAuthenticationSecFetchSite | Unset = UNSET,
) -> ErrorResponse | PasskeyAuthenticationCompletion | None:
    """Verify a Passkey assertion and create an Account JWT root session.

    Args:
        origin (str):
        sec_fetch_site (CompletePasskeyAuthenticationSecFetchSite | Unset):
        body (PasskeyAuthenticationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | PasskeyAuthenticationCompletion
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
