from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.clear_project_invitation_handoff_sec_fetch_site import (
    ClearProjectInvitationHandoffSecFetchSite,
)
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    invitation: str,
    *,
    origin: str,
    sec_fetch_site: ClearProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/project-invitations/handoff/{invitation}".format(
            invitation=quote(str(invitation), safe=""),
        ),
    }

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
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: ClearProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """Clears only the binding cookie named for the path invitation; other outstanding invitation cookies
    survive.

    Args:
        invitation (str):
        origin (str):
        sec_fetch_site (ClearProjectInvitationHandoffSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        invitation=invitation,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: ClearProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """Clears only the binding cookie named for the path invitation; other outstanding invitation cookies
    survive.

    Args:
        invitation (str):
        origin (str):
        sec_fetch_site (ClearProjectInvitationHandoffSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return sync_detailed(
        invitation=invitation,
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: ClearProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """Clears only the binding cookie named for the path invitation; other outstanding invitation cookies
    survive.

    Args:
        invitation (str):
        origin (str):
        sec_fetch_site (ClearProjectInvitationHandoffSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        invitation=invitation,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: ClearProjectInvitationHandoffSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """Clears only the binding cookie named for the path invitation; other outstanding invitation cookies
    survive.

    Args:
        invitation (str):
        origin (str):
        sec_fetch_site (ClearProjectInvitationHandoffSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            invitation=invitation,
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
