from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.invitation_status import InvitationStatus
from ...models.revoke_project_invitation_sec_fetch_site import RevokeProjectInvitationSecFetchSite
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    invitation: str,
    *,
    origin: str,
    sec_fetch_site: RevokeProjectInvitationSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects/{project}/invitations/{invitation}/revoke".format(
            project=quote(str(project), safe=""),
            invitation=quote(str(invitation), safe=""),
        ),
    }

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
    project: str,
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RevokeProjectInvitationSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | InvitationStatus]:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RevokeProjectInvitationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationStatus]
    """

    kwargs = _get_kwargs(
        project=project,
        invitation=invitation,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RevokeProjectInvitationSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | InvitationStatus | None:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RevokeProjectInvitationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationStatus
    """

    return sync_detailed(
        project=project,
        invitation=invitation,
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RevokeProjectInvitationSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | InvitationStatus]:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RevokeProjectInvitationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationStatus]
    """

    kwargs = _get_kwargs(
        project=project,
        invitation=invitation,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RevokeProjectInvitationSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | InvitationStatus | None:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RevokeProjectInvitationSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationStatus
    """

    return (
        await asyncio_detailed(
            project=project,
            invitation=invitation,
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
