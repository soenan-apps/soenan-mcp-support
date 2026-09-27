from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.invitation_handoff_status import InvitationHandoffStatus
from ...types import Response


def _get_kwargs(
    invitation: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/project-invitations/handoff/{invitation}".format(
            invitation=quote(str(invitation), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | InvitationHandoffStatus:
    if response.status_code == 200:
        response_200 = InvitationHandoffStatus.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | InvitationHandoffStatus]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorEnvelope | InvitationHandoffStatus]:
    """Resolves only the HttpOnly binding cookie named for the path invitation. A missing or expired
    binding is not a successful capture.

    Args:
        invitation (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationHandoffStatus]
    """

    kwargs = _get_kwargs(
        invitation=invitation,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorEnvelope | InvitationHandoffStatus | None:
    """Resolves only the HttpOnly binding cookie named for the path invitation. A missing or expired
    binding is not a successful capture.

    Args:
        invitation (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationHandoffStatus
    """

    return sync_detailed(
        invitation=invitation,
        client=client,
    ).parsed


async def asyncio_detailed(
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorEnvelope | InvitationHandoffStatus]:
    """Resolves only the HttpOnly binding cookie named for the path invitation. A missing or expired
    binding is not a successful capture.

    Args:
        invitation (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationHandoffStatus]
    """

    kwargs = _get_kwargs(
        invitation=invitation,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorEnvelope | InvitationHandoffStatus | None:
    """Resolves only the HttpOnly binding cookie named for the path invitation. A missing or expired
    binding is not a successful capture.

    Args:
        invitation (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationHandoffStatus
    """

    return (
        await asyncio_detailed(
            invitation=invitation,
            client=client,
        )
    ).parsed
