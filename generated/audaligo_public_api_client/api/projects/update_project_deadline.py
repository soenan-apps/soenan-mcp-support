from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.project_envelope import ProjectEnvelope
from ...models.update_project_deadline_request import UpdateProjectDeadlineRequest
from ...models.update_project_deadline_sec_fetch_site import UpdateProjectDeadlineSecFetchSite
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    *,
    body: UpdateProjectDeadlineRequest,
    origin: str,
    sec_fetch_site: UpdateProjectDeadlineSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/projects/{project}/deadline".format(
            project=quote(str(project), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectEnvelope:
    if response.status_code == 200:
        response_200 = ProjectEnvelope.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProjectDeadlineRequest,
    origin: str,
    sec_fetch_site: UpdateProjectDeadlineSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ProjectEnvelope]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectDeadlineSecFetchSite | Unset):
        body (UpdateProjectDeadlineRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProjectDeadlineRequest,
    origin: str,
    sec_fetch_site: UpdateProjectDeadlineSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ProjectEnvelope | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectDeadlineSecFetchSite | Unset):
        body (UpdateProjectDeadlineRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectEnvelope
    """

    return sync_detailed(
        project=project,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProjectDeadlineRequest,
    origin: str,
    sec_fetch_site: UpdateProjectDeadlineSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ProjectEnvelope]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectDeadlineSecFetchSite | Unset):
        body (UpdateProjectDeadlineRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProjectDeadlineRequest,
    origin: str,
    sec_fetch_site: UpdateProjectDeadlineSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ProjectEnvelope | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectDeadlineSecFetchSite | Unset):
        body (UpdateProjectDeadlineRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
