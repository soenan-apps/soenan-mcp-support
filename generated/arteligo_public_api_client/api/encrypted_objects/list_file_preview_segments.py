from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.file_preview_segment_page import FilePreviewSegmentPage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    file: str,
    *,
    preview_id: str,
    from_seconds: float,
    to_seconds: float,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["previewId"] = preview_id

    params["fromSeconds"] = from_seconds

    params["toSeconds"] = to_seconds

    params["cursor"] = cursor

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/files/{file}/preview/segments".format(
            project=quote(str(project), safe=""),
            file=quote(str(file), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | FilePreviewSegmentPage:
    if response.status_code == 200:
        response_200 = FilePreviewSegmentPage.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | FilePreviewSegmentPage]:
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
    preview_id: str,
    from_seconds: float,
    to_seconds: float,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> Response[ErrorEnvelope | FilePreviewSegmentPage]:
    """
    Args:
        project (str):
        file (str):
        preview_id (str):
        from_seconds (float):
        to_seconds (float):
        cursor (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | FilePreviewSegmentPage]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        preview_id=preview_id,
        from_seconds=from_seconds,
        to_seconds=to_seconds,
        cursor=cursor,
        limit=limit,
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
    preview_id: str,
    from_seconds: float,
    to_seconds: float,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> ErrorEnvelope | FilePreviewSegmentPage | None:
    """
    Args:
        project (str):
        file (str):
        preview_id (str):
        from_seconds (float):
        to_seconds (float):
        cursor (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | FilePreviewSegmentPage
    """

    return sync_detailed(
        project=project,
        file=file,
        client=client,
        preview_id=preview_id,
        from_seconds=from_seconds,
        to_seconds=to_seconds,
        cursor=cursor,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    preview_id: str,
    from_seconds: float,
    to_seconds: float,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> Response[ErrorEnvelope | FilePreviewSegmentPage]:
    """
    Args:
        project (str):
        file (str):
        preview_id (str):
        from_seconds (float):
        to_seconds (float):
        cursor (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | FilePreviewSegmentPage]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        preview_id=preview_id,
        from_seconds=from_seconds,
        to_seconds=to_seconds,
        cursor=cursor,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    preview_id: str,
    from_seconds: float,
    to_seconds: float,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> ErrorEnvelope | FilePreviewSegmentPage | None:
    """
    Args:
        project (str):
        file (str):
        preview_id (str):
        from_seconds (float):
        to_seconds (float):
        cursor (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | FilePreviewSegmentPage
    """

    return (
        await asyncio_detailed(
            project=project,
            file=file,
            client=client,
            preview_id=preview_id,
            from_seconds=from_seconds,
            to_seconds=to_seconds,
            cursor=cursor,
            limit=limit,
        )
    ).parsed
