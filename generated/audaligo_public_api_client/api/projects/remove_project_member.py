from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.remove_project_member_sec_fetch_site import (
    RemoveProjectMemberSecFetchSite,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    membership_id: str,
    *,
    origin: str,
    sec_fetch_site: RemoveProjectMemberSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/projects/{project}/members/{membership_id}".format(
            project=quote(str(project), safe=""),
            membership_id=quote(str(membership_id), safe=""),
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
    project: str,
    membership_id: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RemoveProjectMemberSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """Only the project owner can remove an invitation-origin member. Repeated removal is idempotent.
    Membership history is retained.

    Args:
        project (str):
        membership_id (str):
        origin (str):
        sec_fetch_site (RemoveProjectMemberSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        membership_id=membership_id,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    membership_id: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RemoveProjectMemberSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """Only the project owner can remove an invitation-origin member. Repeated removal is idempotent.
    Membership history is retained.

    Args:
        project (str):
        membership_id (str):
        origin (str):
        sec_fetch_site (RemoveProjectMemberSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        membership_id=membership_id,
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    membership_id: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RemoveProjectMemberSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """Only the project owner can remove an invitation-origin member. Repeated removal is idempotent.
    Membership history is retained.

    Args:
        project (str):
        membership_id (str):
        origin (str):
        sec_fetch_site (RemoveProjectMemberSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        membership_id=membership_id,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    membership_id: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: RemoveProjectMemberSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """Only the project owner can remove an invitation-origin member. Repeated removal is idempotent.
    Membership history is retained.

    Args:
        project (str):
        membership_id (str):
        origin (str):
        sec_fetch_site (RemoveProjectMemberSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            membership_id=membership_id,
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
