from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_approve_invitation_sec_fetch_site import (
    E2EeApproveInvitationSecFetchSite,
)
from ...models.e2_ee_invitation_status import E2EeInvitationStatus
from ...models.e2_ee_signed_command import E2EeSignedCommand
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    request_id: str,
    *,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApproveInvitationSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/requests/{request_id}/approve".format(
            request_id=quote(str(request_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeInvitationStatus | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeInvitationStatus.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeInvitationStatus | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    request_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApproveInvitationSecFetchSite | Unset = UNSET,
) -> Response[E2EeInvitationStatus | ErrorEnvelope]:
    """
    Args:
        request_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApproveInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeInvitationStatus | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        request_id=request_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    request_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApproveInvitationSecFetchSite | Unset = UNSET,
) -> E2EeInvitationStatus | ErrorEnvelope | None:
    """
    Args:
        request_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApproveInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeInvitationStatus | ErrorEnvelope
    """

    return sync_detailed(
        request_id=request_id,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    request_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApproveInvitationSecFetchSite | Unset = UNSET,
) -> Response[E2EeInvitationStatus | ErrorEnvelope]:
    """
    Args:
        request_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApproveInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeInvitationStatus | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        request_id=request_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    request_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApproveInvitationSecFetchSite | Unset = UNSET,
) -> E2EeInvitationStatus | ErrorEnvelope | None:
    """
    Args:
        request_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApproveInvitationSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeInvitationStatus | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            request_id=request_id,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
