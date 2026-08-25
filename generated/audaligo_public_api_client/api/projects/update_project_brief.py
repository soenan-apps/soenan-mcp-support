from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.project_brief_envelope import ProjectBriefEnvelope
from ...models.project_brief_request import ProjectBriefRequest
from ...models.update_project_brief_sec_fetch_site import UpdateProjectBriefSecFetchSite
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    *,
    body: ProjectBriefRequest,
    origin: str,
    sec_fetch_site: UpdateProjectBriefSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/projects/{project}/brief".format(
            project=quote(str(project), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectBriefEnvelope:
    if response.status_code == 200:
        response_200 = ProjectBriefEnvelope.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectBriefEnvelope]:
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
    body: ProjectBriefRequest,
    origin: str,
    sec_fetch_site: UpdateProjectBriefSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ProjectBriefEnvelope]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectBriefSecFetchSite | Unset):
        body (ProjectBriefRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectBriefEnvelope]
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
    body: ProjectBriefRequest,
    origin: str,
    sec_fetch_site: UpdateProjectBriefSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ProjectBriefEnvelope | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectBriefSecFetchSite | Unset):
        body (ProjectBriefRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectBriefEnvelope
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
    body: ProjectBriefRequest,
    origin: str,
    sec_fetch_site: UpdateProjectBriefSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ProjectBriefEnvelope]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectBriefSecFetchSite | Unset):
        body (ProjectBriefRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectBriefEnvelope]
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
    body: ProjectBriefRequest,
    origin: str,
    sec_fetch_site: UpdateProjectBriefSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ProjectBriefEnvelope | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (UpdateProjectBriefSecFetchSite | Unset):
        body (ProjectBriefRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectBriefEnvelope
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
