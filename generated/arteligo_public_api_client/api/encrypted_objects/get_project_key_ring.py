from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.project_key_ring_response import ProjectKeyRingResponse
from ...types import Response


def _get_kwargs(
    project: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/keyring".format(
            project=quote(str(project), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectKeyRingResponse:
    if response.status_code == 200:
        response_200 = ProjectKeyRingResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectKeyRingResponse]:
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
) -> Response[ErrorEnvelope | ProjectKeyRingResponse]:
    """
    Args:
        project (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectKeyRingResponse]
    """

    kwargs = _get_kwargs(
        project=project,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    *,
    client: AuthenticatedClient,
) -> ErrorEnvelope | ProjectKeyRingResponse | None:
    """
    Args:
        project (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectKeyRingResponse
    """

    return sync_detailed(
        project=project,
        client=client,
    ).parsed


async def asyncio_detailed(
    project: str,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorEnvelope | ProjectKeyRingResponse]:
    """
    Args:
        project (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectKeyRingResponse]
    """

    kwargs = _get_kwargs(
        project=project,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    *,
    client: AuthenticatedClient,
) -> ErrorEnvelope | ProjectKeyRingResponse | None:
    """
    Args:
        project (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectKeyRingResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            client=client,
        )
    ).parsed
