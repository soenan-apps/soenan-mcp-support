from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_invitation_info import E2EeInvitationInfo
from ...models.error_envelope import ErrorEnvelope
from ...types import Response


def _get_kwargs(
    invitation_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/invitations/{invitation_id}".format(
            invitation_id=quote(str(invitation_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeInvitationInfo | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeInvitationInfo.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeInvitationInfo | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    invitation_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[E2EeInvitationInfo | ErrorEnvelope]:
    """
    Args:
        invitation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeInvitationInfo | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        invitation_id=invitation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    invitation_id: str,
    *,
    client: AuthenticatedClient,
) -> E2EeInvitationInfo | ErrorEnvelope | None:
    """
    Args:
        invitation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeInvitationInfo | ErrorEnvelope
    """

    return sync_detailed(
        invitation_id=invitation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    invitation_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[E2EeInvitationInfo | ErrorEnvelope]:
    """
    Args:
        invitation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeInvitationInfo | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        invitation_id=invitation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    invitation_id: str,
    *,
    client: AuthenticatedClient,
) -> E2EeInvitationInfo | ErrorEnvelope | None:
    """
    Args:
        invitation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeInvitationInfo | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            invitation_id=invitation_id,
            client=client,
        )
    ).parsed
