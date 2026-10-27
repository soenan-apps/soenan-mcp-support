from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_owner_authority import E2EeOwnerAuthority
from ...models.e2_ee_signed_command import E2EeSignedCommand
from ...models.error_envelope import ErrorEnvelope
from ...types import Response


def _get_kwargs(
    organization_id: str,
    *,
    body: E2EeSignedCommand,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/organizations/{organization_id}/owner-access/invalidate".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeOwnerAuthority | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeOwnerAuthority.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeOwnerAuthority | ErrorEnvelope]:
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
    body: E2EeSignedCommand,
) -> Response[E2EeOwnerAuthority | ErrorEnvelope]:
    """
    Args:
        organization_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeOwnerAuthority | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
) -> E2EeOwnerAuthority | ErrorEnvelope | None:
    """
    Args:
        organization_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeOwnerAuthority | ErrorEnvelope
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
) -> Response[E2EeOwnerAuthority | ErrorEnvelope]:
    """
    Args:
        organization_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeOwnerAuthority | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
) -> E2EeOwnerAuthority | ErrorEnvelope | None:
    """
    Args:
        organization_id (str):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeOwnerAuthority | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            body=body,
        )
    ).parsed
