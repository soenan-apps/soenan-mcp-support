from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...models.capture_project_invitation_handoff_sec_fetch_site import (
    CaptureProjectInvitationHandoffSecFetchSite,
)
from ...models.error_envelope import ErrorEnvelope
from ...models.invitation_handoff_capture import InvitationHandoffCapture
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: InvitationHandoffCapture,
    origin: str | Unset = UNSET,
    sec_fetch_site: CaptureProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/project-invitations/handoff",
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
    *,
    client: AuthenticatedClient | Client,
    body: InvitationHandoffCapture,
    origin: str | Unset = UNSET,
    sec_fetch_site: CaptureProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """Browser prebootstrap sends the share-link fragment before loading Flutter. WWW verifies the active
    invitation, persists only token and random-binding digests, and issues an invitation-specific
    30-minute HttpOnly SameSite=Lax host-only binding across the full Account redirect.

    Args:
        origin (str | Unset):
        sec_fetch_site (CaptureProjectInvitationHandoffSecFetchSite | Unset):
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
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
    body: InvitationHandoffCapture,
    origin: str | Unset = UNSET,
    sec_fetch_site: CaptureProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """Browser prebootstrap sends the share-link fragment before loading Flutter. WWW verifies the active
    invitation, persists only token and random-binding digests, and issues an invitation-specific
    30-minute HttpOnly SameSite=Lax host-only binding across the full Account redirect.

    Args:
        origin (str | Unset):
        sec_fetch_site (CaptureProjectInvitationHandoffSecFetchSite | Unset):
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
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
    body: InvitationHandoffCapture,
    origin: str | Unset = UNSET,
    sec_fetch_site: CaptureProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """Browser prebootstrap sends the share-link fragment before loading Flutter. WWW verifies the active
    invitation, persists only token and random-binding digests, and issues an invitation-specific
    30-minute HttpOnly SameSite=Lax host-only binding across the full Account redirect.

    Args:
        origin (str | Unset):
        sec_fetch_site (CaptureProjectInvitationHandoffSecFetchSite | Unset):
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
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
    body: InvitationHandoffCapture,
    origin: str | Unset = UNSET,
    sec_fetch_site: CaptureProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """Browser prebootstrap sends the share-link fragment before loading Flutter. WWW verifies the active
    invitation, persists only token and random-binding digests, and issues an invitation-specific
    30-minute HttpOnly SameSite=Lax host-only binding across the full Account redirect.

    Args:
        origin (str | Unset):
        sec_fetch_site (CaptureProjectInvitationHandoffSecFetchSite | Unset):
        body (InvitationHandoffCapture):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
