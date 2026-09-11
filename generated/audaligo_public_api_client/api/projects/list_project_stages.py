from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.project_stage_list_response import ProjectStageListResponse
from ...models.project_stage_status import ProjectStageStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    *,
    status: ProjectStageStatus | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["cursor"] = cursor

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/stages".format(
            project=quote(str(project), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectStageListResponse:
    if response.status_code == 200:
        response_200 = ProjectStageListResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectStageListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    *,
    client: AuthenticatedClient,
    status: ProjectStageStatus | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[ErrorEnvelope | ProjectStageListResponse]:
    """
    Args:
        project (str):
        status (ProjectStageStatus | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectStageListResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        status=status,
        cursor=cursor,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    *,
    client: AuthenticatedClient,
    status: ProjectStageStatus | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> ErrorEnvelope | ProjectStageListResponse | None:
    """
    Args:
        project (str):
        status (ProjectStageStatus | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectStageListResponse
    """

    return sync_detailed(
        project=project,
        client=client,
        status=status,
        cursor=cursor,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    project: str,
    *,
    client: AuthenticatedClient,
    status: ProjectStageStatus | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[ErrorEnvelope | ProjectStageListResponse]:
    """
    Args:
        project (str):
        status (ProjectStageStatus | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectStageListResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        status=status,
        cursor=cursor,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    *,
    client: AuthenticatedClient,
    status: ProjectStageStatus | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> ErrorEnvelope | ProjectStageListResponse | None:
    """
    Args:
        project (str):
        status (ProjectStageStatus | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectStageListResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            client=client,
            status=status,
            cursor=cursor,
            limit=limit,
        )
    ).parsed
