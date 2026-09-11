from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.file_preview_response import FilePreviewResponse
from ...types import Response


def _get_kwargs(
    project: str,
    file: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/files/{file}/preview".format(
            project=quote(str(project), safe=""),
            file=quote(str(file), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | FilePreviewResponse:
    if response.status_code == 200:
        response_200 = FilePreviewResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | FilePreviewResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorEnvelope | FilePreviewResponse]:
    """
    Args:
        project (str):
        file (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | FilePreviewResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
) -> ErrorEnvelope | FilePreviewResponse | None:
    """
    Args:
        project (str):
        file (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | FilePreviewResponse
    """

    return sync_detailed(
        project=project,
        file=file,
        client=client,
    ).parsed


async def asyncio_detailed(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorEnvelope | FilePreviewResponse]:
    """
    Args:
        project (str):
        file (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | FilePreviewResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
) -> ErrorEnvelope | FilePreviewResponse | None:
    """
    Args:
        project (str):
        file (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | FilePreviewResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            file=file,
            client=client,
        )
    ).parsed
