from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.invitation_created import InvitationCreated
from ...models.regenerate_invitation_request import RegenerateInvitationRequest
from ...models.regenerate_project_invitation_sec_fetch_site import (
    RegenerateProjectInvitationSecFetchSite,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    invitation: str,
    *,
    body: RegenerateInvitationRequest,
    origin: str,
    sec_fetch_site: RegenerateProjectInvitationSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects/{project}/invitations/{invitation}/regenerate".format(
            project=quote(str(project), safe=""),
            invitation=quote(str(invitation), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | InvitationCreated:
    if response.status_code == 200:
        response_200 = InvitationCreated.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | InvitationCreated]:
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
    body: RegenerateInvitationRequest,
    origin: str,
    sec_fetch_site: RegenerateProjectInvitationSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | InvitationCreated]:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RegenerateProjectInvitationSecFetchSite | Unset):
        idempotency_key (str):
        body (RegenerateInvitationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationCreated]
    """

    kwargs = _get_kwargs(
        project=project,
        invitation=invitation,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
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
    body: RegenerateInvitationRequest,
    origin: str,
    sec_fetch_site: RegenerateProjectInvitationSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | InvitationCreated | None:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RegenerateProjectInvitationSecFetchSite | Unset):
        idempotency_key (str):
        body (RegenerateInvitationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationCreated
    """

    return sync_detailed(
        project=project,
        invitation=invitation,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    project: str,
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    body: RegenerateInvitationRequest,
    origin: str,
    sec_fetch_site: RegenerateProjectInvitationSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | InvitationCreated]:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RegenerateProjectInvitationSecFetchSite | Unset):
        idempotency_key (str):
        body (RegenerateInvitationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | InvitationCreated]
    """

    kwargs = _get_kwargs(
        project=project,
        invitation=invitation,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    invitation: str,
    *,
    client: AuthenticatedClient | Client,
    body: RegenerateInvitationRequest,
    origin: str,
    sec_fetch_site: RegenerateProjectInvitationSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | InvitationCreated | None:
    """
    Args:
        project (str):
        invitation (str):
        origin (str):
        sec_fetch_site (RegenerateProjectInvitationSecFetchSite | Unset):
        idempotency_key (str):
        body (RegenerateInvitationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | InvitationCreated
    """

    return (
        await asyncio_detailed(
            project=project,
            invitation=invitation,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            idempotency_key=idempotency_key,
        )
    ).parsed
