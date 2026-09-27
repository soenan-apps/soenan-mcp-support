from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.accept_project_invitation_handoff_sec_fetch_site import (
    AcceptProjectInvitationHandoffSecFetchSite,
)
from ...models.error_envelope import ErrorEnvelope
from ...models.invitation_handoff_accept import InvitationHandoffAccept
from ...models.invitation_status import InvitationStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: InvitationHandoffAccept,
    origin: str | Unset = UNSET,
    sec_fetch_site: AcceptProjectInvitationHandoffSecFetchSite | Unset = UNSET,
    x_arteligo_invitation_handoff: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    if not isinstance(x_arteligo_invitation_handoff, Unset):
        headers["X-Arteligo-Invitation-Handoff"] = x_arteligo_invitation_handoff

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/project-invitations/handoff/accept",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | InvitationStatus:
    if response.status_code == 200:
        response_200 = InvitationStatus.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | InvitationStatus]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: InvitationHandoffAccept,
    origin: str | Unset = UNSET,
    sec_fetch_site: AcceptProjectInvitationHandoffSecFetchSite | Unset = UNSET,
    x_arteligo_invitation_handoff: str | Unset = UNSET,
) -> Response[ErrorEnvelope | InvitationStatus]:
    """Requires either the Web session and HttpOnly invitation binding, or a native Account Bearer and its
    same-subject/session handoff header. Mixing transports is rejected.

    Args:
        origin (str | Unset):
        sec_fetch_site (AcceptProjectInvitationHandoffSecFetchSite | Unset):
        x_arteligo_invitation_handoff (str | Unset):
        body (InvitationHandoffAccept):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationStatus]
    """

    kwargs = _get_kwargs(
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        x_arteligo_invitation_handoff=x_arteligo_invitation_handoff,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: InvitationHandoffAccept,
    origin: str | Unset = UNSET,
    sec_fetch_site: AcceptProjectInvitationHandoffSecFetchSite | Unset = UNSET,
    x_arteligo_invitation_handoff: str | Unset = UNSET,
) -> ErrorEnvelope | InvitationStatus | None:
    """Requires either the Web session and HttpOnly invitation binding, or a native Account Bearer and its
    same-subject/session handoff header. Mixing transports is rejected.

    Args:
        origin (str | Unset):
        sec_fetch_site (AcceptProjectInvitationHandoffSecFetchSite | Unset):
        x_arteligo_invitation_handoff (str | Unset):
        body (InvitationHandoffAccept):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationStatus
    """

    return sync_detailed(
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        x_arteligo_invitation_handoff=x_arteligo_invitation_handoff,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: InvitationHandoffAccept,
    origin: str | Unset = UNSET,
    sec_fetch_site: AcceptProjectInvitationHandoffSecFetchSite | Unset = UNSET,
    x_arteligo_invitation_handoff: str | Unset = UNSET,
) -> Response[ErrorEnvelope | InvitationStatus]:
    """Requires either the Web session and HttpOnly invitation binding, or a native Account Bearer and its
    same-subject/session handoff header. Mixing transports is rejected.

    Args:
        origin (str | Unset):
        sec_fetch_site (AcceptProjectInvitationHandoffSecFetchSite | Unset):
        x_arteligo_invitation_handoff (str | Unset):
        body (InvitationHandoffAccept):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationStatus]
    """

    kwargs = _get_kwargs(
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        x_arteligo_invitation_handoff=x_arteligo_invitation_handoff,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: InvitationHandoffAccept,
    origin: str | Unset = UNSET,
    sec_fetch_site: AcceptProjectInvitationHandoffSecFetchSite | Unset = UNSET,
    x_arteligo_invitation_handoff: str | Unset = UNSET,
) -> ErrorEnvelope | InvitationStatus | None:
    """Requires either the Web session and HttpOnly invitation binding, or a native Account Bearer and its
    same-subject/session handoff header. Mixing transports is rejected.

    Args:
        origin (str | Unset):
        sec_fetch_site (AcceptProjectInvitationHandoffSecFetchSite | Unset):
        x_arteligo_invitation_handoff (str | Unset):
        body (InvitationHandoffAccept):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationStatus
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            x_arteligo_invitation_handoff=x_arteligo_invitation_handoff,
        )
    ).parsed
