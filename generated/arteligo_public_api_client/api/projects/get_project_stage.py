from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.project_stage_response import ProjectStageResponse
from ...types import Response


def _get_kwargs(
    project: str,
    stage: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/stages/{stage}".format(
            project=quote(str(project), safe=""),
            stage=quote(str(stage), safe=""),
        ),
    }

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
) -> Response[ErrorEnvelope | ProjectStageResponse]:
    """
    Args:
        project (str):
        stage (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectStageResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        stage=stage,
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
) -> ErrorEnvelope | ProjectStageResponse | None:
    """
    Args:
        project (str):
        stage (str):

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
    ).parsed


async def asyncio_detailed(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorEnvelope | ProjectStageResponse]:
    """
    Args:
        project (str):
        stage (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectStageResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        stage=stage,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
) -> ErrorEnvelope | ProjectStageResponse | None:
    """
    Args:
        project (str):
        stage (str):

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
        )
    ).parsed
