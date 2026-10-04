from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_invitations import E2EeInvitations
from ...models.error_envelope import ErrorEnvelope
from ...types import Response


def _get_kwargs(
    scope_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/projects/{scope_id}/invitations".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeInvitations | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeInvitations.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeInvitations | ErrorEnvelope]:
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
) -> Response[E2EeInvitations | ErrorEnvelope]:
    """
    Args:
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeInvitations | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scope_id: str,
    *,
    client: AuthenticatedClient,
) -> E2EeInvitations | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeInvitations | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[E2EeInvitations | ErrorEnvelope]:
    """
    Args:
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeInvitations | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
) -> E2EeInvitations | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeInvitations | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
        )
    ).parsed
