from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.project_stage_response import ProjectStageResponse
from ...models.update_project_stage_request import UpdateProjectStageRequest
from ...models.update_project_stage_sec_fetch_site import UpdateProjectStageSecFetchSite
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    stage: str,
    *,
    body: UpdateProjectStageRequest,
    origin: str,
    sec_fetch_site: UpdateProjectStageSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/projects/{project}/stages/{stage}".format(
            project=quote(str(project), safe=""),
            stage=quote(str(stage), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectStageResponse:
    if response.status_code == 200:
        response_200 = ProjectStageResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectStageResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectStageRequest,
    origin: str,
    sec_fetch_site: UpdateProjectStageSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ProjectStageResponse]:
    """
    Args:
        project (str):
        stage (str):
        origin (str):
        sec_fetch_site (UpdateProjectStageSecFetchSite | Unset):
        body (UpdateProjectStageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectStageResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        stage=stage,
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
    stage: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectStageRequest,
    origin: str,
    sec_fetch_site: UpdateProjectStageSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ProjectStageResponse | None:
    """
    Args:
        project (str):
        stage (str):
        origin (str):
        sec_fetch_site (UpdateProjectStageSecFetchSite | Unset):
        body (UpdateProjectStageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectStageResponse
    """

    return sync_detailed(
        project=project,
        stage=stage,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectStageRequest,
    origin: str,
    sec_fetch_site: UpdateProjectStageSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ProjectStageResponse]:
    """
    Args:
        project (str):
        stage (str):
        origin (str):
        sec_fetch_site (UpdateProjectStageSecFetchSite | Unset):
        body (UpdateProjectStageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectStageResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        stage=stage,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectStageRequest,
    origin: str,
    sec_fetch_site: UpdateProjectStageSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ProjectStageResponse | None:
    """
    Args:
        project (str):
        stage (str):
        origin (str):
        sec_fetch_site (UpdateProjectStageSecFetchSite | Unset):
        body (UpdateProjectStageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectStageResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            stage=stage,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
