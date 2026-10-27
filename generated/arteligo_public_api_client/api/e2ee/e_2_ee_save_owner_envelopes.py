from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_signed_command import E2EeSignedCommand
from ...models.error_envelope import ErrorEnvelope
from ...types import Response


def _get_kwargs(
    scope_id: str,
    *,
    body: E2EeSignedCommand,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/scopes/{scope_id}/owner-envelopes".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorEnvelope:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
) -> Response[Any | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
) -> Any | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
) -> Response[Any | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
) -> Any | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
            body=body,
        )
    ).parsed
