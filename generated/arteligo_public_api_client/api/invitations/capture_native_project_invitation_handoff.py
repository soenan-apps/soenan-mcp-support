from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.invitation_handoff_capture import InvitationHandoffCapture
from ...models.native_invitation_handoff import NativeInvitationHandoff
from ...types import Response


def _get_kwargs(
    *,
    body: InvitationHandoffCapture,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/project-invitations/handoff/native",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | NativeInvitationHandoff:
    if response.status_code == 200:
        response_200 = NativeInvitationHandoff.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | NativeInvitationHandoff]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: InvitationHandoffCapture,
) -> Response[ErrorEnvelope | NativeInvitationHandoff]:
    """Bind an invitation proof to the verified native Account subject and session; only the digest is
    persisted, never the returned binding.

    Args:
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | NativeInvitationHandoff]
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
    client: AuthenticatedClient,
    body: InvitationHandoffCapture,
) -> ErrorEnvelope | NativeInvitationHandoff | None:
    """Bind an invitation proof to the verified native Account subject and session; only the digest is
    persisted, never the returned binding.

    Args:
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | NativeInvitationHandoff
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: InvitationHandoffCapture,
) -> Response[ErrorEnvelope | NativeInvitationHandoff]:
    """Bind an invitation proof to the verified native Account subject and session; only the digest is
    persisted, never the returned binding.

    Args:
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | NativeInvitationHandoff]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: InvitationHandoffCapture,
) -> ErrorEnvelope | NativeInvitationHandoff | None:
    """Bind an invitation proof to the verified native Account subject and session; only the digest is
    persisted, never the returned binding.

    Args:
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | NativeInvitationHandoff
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
