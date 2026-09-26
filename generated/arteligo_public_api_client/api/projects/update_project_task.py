from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.project_task_response import ProjectTaskResponse
from ...models.update_project_task_request import UpdateProjectTaskRequest
from ...models.update_project_task_sec_fetch_site import UpdateProjectTaskSecFetchSite
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    task: str,
    *,
    body: UpdateProjectTaskRequest,
    origin: str,
    sec_fetch_site: UpdateProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/projects/{project}/tasks/{task}".format(
            project=quote(str(project), safe=""),
            task=quote(str(task), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectTaskResponse:
    if response.status_code == 200:
        response_200 = ProjectTaskResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectTaskResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    task: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectTaskRequest,
    origin: str,
    sec_fetch_site: UpdateProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectTaskResponse]:
    """
    Args:
        project (str):
        task (str):
        origin (str):
        sec_fetch_site (UpdateProjectTaskSecFetchSite | Unset):
        idempotency_key (str):
        body (UpdateProjectTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectTaskResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        task=task,
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
    task: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectTaskRequest,
    origin: str,
    sec_fetch_site: UpdateProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectTaskResponse | None:
    """
    Args:
        project (str):
        task (str):
        origin (str):
        sec_fetch_site (UpdateProjectTaskSecFetchSite | Unset):
        idempotency_key (str):
        body (UpdateProjectTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectTaskResponse
    """

    return sync_detailed(
        project=project,
        task=task,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    project: str,
    task: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectTaskRequest,
    origin: str,
    sec_fetch_site: UpdateProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectTaskResponse]:
    """
    Args:
        project (str):
        task (str):
        origin (str):
        sec_fetch_site (UpdateProjectTaskSecFetchSite | Unset):
        idempotency_key (str):
        body (UpdateProjectTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectTaskResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        task=task,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    task: str,
    *,
    client: AuthenticatedClient,
    body: UpdateProjectTaskRequest,
    origin: str,
    sec_fetch_site: UpdateProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectTaskResponse | None:
    """
    Args:
        project (str):
        task (str):
        origin (str):
        sec_fetch_site (UpdateProjectTaskSecFetchSite | Unset):
        idempotency_key (str):
        body (UpdateProjectTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectTaskResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            task=task,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            idempotency_key=idempotency_key,
        )
    ).parsed
