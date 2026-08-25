from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.preview_read_descriptor_response import PreviewReadDescriptorResponse
from ...types import Response


def _get_kwargs(
    project: str,
    mix_version: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/versions/{mix_version}/preview/read-descriptor".format(
            project=quote(str(project), safe=""),
            mix_version=quote(str(mix_version), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | PreviewReadDescriptorResponse:
    if response.status_code == 200:
        response_200 = PreviewReadDescriptorResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | PreviewReadDescriptorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorEnvelope | PreviewReadDescriptorResponse]:
    """
    Args:
        project (str):
        mix_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | PreviewReadDescriptorResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        mix_version=mix_version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient,
) -> ErrorEnvelope | PreviewReadDescriptorResponse | None:
    """
    Args:
        project (str):
        mix_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | PreviewReadDescriptorResponse
    """

    return sync_detailed(
        project=project,
        mix_version=mix_version,
        client=client,
    ).parsed


async def asyncio_detailed(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorEnvelope | PreviewReadDescriptorResponse]:
    """
    Args:
        project (str):
        mix_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | PreviewReadDescriptorResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        mix_version=mix_version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient,
) -> ErrorEnvelope | PreviewReadDescriptorResponse | None:
    """
    Args:
        project (str):
        mix_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | PreviewReadDescriptorResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            mix_version=mix_version,
            client=client,
        )
    ).parsed
