from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.complete_file_preview_upload_sec_fetch_site import (
    CompleteFilePreviewUploadSecFetchSite,
)
from ...models.error_envelope import ErrorEnvelope
from ...models.object_state_response import ObjectStateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    file: str,
    *,
    origin: str | Unset = UNSET,
    sec_fetch_site: CompleteFilePreviewUploadSecFetchSite | Unset = UNSET,
    arteligo_transfer_continuation: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    if not isinstance(arteligo_transfer_continuation, Unset):
        headers["Arteligo-Transfer-Continuation"] = arteligo_transfer_continuation

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects/{project}/files/{file}/preview-upload/completion".format(
            project=quote(str(project), safe=""),
            file=quote(str(file), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ObjectStateResponse:
    if response.status_code == 200:
        response_200 = ObjectStateResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ObjectStateResponse]:
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
    origin: str | Unset = UNSET,
    sec_fetch_site: CompleteFilePreviewUploadSecFetchSite | Unset = UNSET,
    arteligo_transfer_continuation: str | Unset = UNSET,
) -> Response[ErrorEnvelope | ObjectStateResponse]:
    """
    Args:
        project (str):
        file (str):
        origin (str | Unset):
        sec_fetch_site (CompleteFilePreviewUploadSecFetchSite | Unset):
        arteligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ObjectStateResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        arteligo_transfer_continuation=arteligo_transfer_continuation,
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
    origin: str | Unset = UNSET,
    sec_fetch_site: CompleteFilePreviewUploadSecFetchSite | Unset = UNSET,
    arteligo_transfer_continuation: str | Unset = UNSET,
) -> ErrorEnvelope | ObjectStateResponse | None:
    """
    Args:
        project (str):
        file (str):
        origin (str | Unset):
        sec_fetch_site (CompleteFilePreviewUploadSecFetchSite | Unset):
        arteligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ObjectStateResponse
    """

    return sync_detailed(
        project=project,
        file=file,
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        arteligo_transfer_continuation=arteligo_transfer_continuation,
    ).parsed


async def asyncio_detailed(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    origin: str | Unset = UNSET,
    sec_fetch_site: CompleteFilePreviewUploadSecFetchSite | Unset = UNSET,
    arteligo_transfer_continuation: str | Unset = UNSET,
) -> Response[ErrorEnvelope | ObjectStateResponse]:
    """
    Args:
        project (str):
        file (str):
        origin (str | Unset):
        sec_fetch_site (CompleteFilePreviewUploadSecFetchSite | Unset):
        arteligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ObjectStateResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        arteligo_transfer_continuation=arteligo_transfer_continuation,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    origin: str | Unset = UNSET,
    sec_fetch_site: CompleteFilePreviewUploadSecFetchSite | Unset = UNSET,
    arteligo_transfer_continuation: str | Unset = UNSET,
) -> ErrorEnvelope | ObjectStateResponse | None:
    """
    Args:
        project (str):
        file (str):
        origin (str | Unset):
        sec_fetch_site (CompleteFilePreviewUploadSecFetchSite | Unset):
        arteligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ObjectStateResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            file=file,
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            arteligo_transfer_continuation=arteligo_transfer_continuation,
        )
    ).parsed
