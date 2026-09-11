from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.delete_project_task_sec_fetch_site import DeleteProjectTaskSecFetchSite
from ...models.error_envelope import ErrorEnvelope
from ...models.project_task_deletion_response import ProjectTaskDeletionResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    task: str,
    *,
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    headers["Idempotency-Key"] = idempotency_key

    params: dict[str, Any] = {}

    params["expectedRevision"] = expected_revision

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/projects/{project}/tasks/{task}".format(
            project=quote(str(project), safe=""),
            task=quote(str(task), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectTaskDeletionResponse:
    if response.status_code == 200:
        response_200 = ProjectTaskDeletionResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectTaskDeletionResponse]:
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
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectTaskDeletionResponse]:
    """
    Args:
        project (str):
        task (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectTaskSecFetchSite | Unset):
        idempotency_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectTaskDeletionResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        task=task,
        expected_revision=expected_revision,
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
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectTaskDeletionResponse | None:
    """
    Args:
        project (str):
        task (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectTaskSecFetchSite | Unset):
        idempotency_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectTaskDeletionResponse
    """

    return sync_detailed(
        project=project,
        task=task,
        client=client,
        expected_revision=expected_revision,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    project: str,
    task: str,
    *,
    client: AuthenticatedClient,
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectTaskDeletionResponse]:
    """
    Args:
        project (str):
        task (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectTaskSecFetchSite | Unset):
        idempotency_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectTaskDeletionResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        task=task,
        expected_revision=expected_revision,
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
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectTaskSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectTaskDeletionResponse | None:
    """
    Args:
        project (str):
        task (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectTaskSecFetchSite | Unset):
        idempotency_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectTaskDeletionResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            task=task,
            client=client,
            expected_revision=expected_revision,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            idempotency_key=idempotency_key,
        )
    ).parsed
