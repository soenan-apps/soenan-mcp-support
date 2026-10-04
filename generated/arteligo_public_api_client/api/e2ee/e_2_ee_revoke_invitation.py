from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_revoke_invitation_sec_fetch_site import (
    E2EeRevokeInvitationSecFetchSite,
)
from ...models.e2_ee_signed_command import E2EeSignedCommand
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    invitation_id: str,
    *,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeRevokeInvitationSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/invitations/{invitation_id}/revoke".format(
            invitation_id=quote(str(invitation_id), safe=""),
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
    invitation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeRevokeInvitationSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """
    Args:
        invitation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeRevokeInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        invitation_id=invitation_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    invitation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeRevokeInvitationSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """
    Args:
        invitation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeRevokeInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return sync_detailed(
        invitation_id=invitation_id,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    invitation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeRevokeInvitationSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """
    Args:
        invitation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeRevokeInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        invitation_id=invitation_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    invitation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeRevokeInvitationSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """
    Args:
        invitation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeRevokeInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            invitation_id=invitation_id,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
