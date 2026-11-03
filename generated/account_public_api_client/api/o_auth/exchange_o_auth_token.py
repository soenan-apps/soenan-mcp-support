from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.o_auth_error_response import OAuthErrorResponse
from ...models.o_auth_token_request import OAuthTokenRequest
from ...models.o_auth_token_response import OAuthTokenResponse
from ...types import Response


def _get_kwargs(
    *,
    body: OAuthTokenRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/token",
    }

    _kwargs["data"] = body.to_dict()

    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | OAuthErrorResponse | OAuthTokenResponse | None:
    if response.status_code == 200:
        response_200 = OAuthTokenResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = OAuthErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 415:
        response_415 = ErrorResponse.from_dict(response.json())

        return response_415

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | OAuthErrorResponse | OAuthTokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OAuthTokenRequest,
) -> Response[ErrorResponse | OAuthErrorResponse | OAuthTokenResponse]:
    """Exchange an authorization code or rotate a refresh proof.

    Args:
        body (OAuthTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OAuthErrorResponse | OAuthTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: OAuthTokenRequest,
) -> ErrorResponse | OAuthErrorResponse | OAuthTokenResponse | None:
    """Exchange an authorization code or rotate a refresh proof.

    Args:
        body (OAuthTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OAuthErrorResponse | OAuthTokenResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OAuthTokenRequest,
) -> Response[ErrorResponse | OAuthErrorResponse | OAuthTokenResponse]:
    """Exchange an authorization code or rotate a refresh proof.

    Args:
        body (OAuthTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OAuthErrorResponse | OAuthTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: OAuthTokenRequest,
) -> ErrorResponse | OAuthErrorResponse | OAuthTokenResponse | None:
    """Exchange an authorization code or rotate a refresh proof.

    Args:
        body (OAuthTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OAuthErrorResponse | OAuthTokenResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
