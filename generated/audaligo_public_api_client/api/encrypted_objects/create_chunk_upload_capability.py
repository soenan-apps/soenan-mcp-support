from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.capability_response import CapabilityResponse
from ...models.create_chunk_upload_capability_sec_fetch_site import (
    CreateChunkUploadCapabilitySecFetchSite,
)
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    upload: str,
    chunk: int,
    *,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CreateChunkUploadCapabilitySecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(audaligo_transfer_continuation, Unset):
        headers["Audaligo-Transfer-Continuation"] = audaligo_transfer_continuation

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects/{project}/uploads/{upload}/chunks/{chunk}/upload-capabilities".format(
            project=quote(str(project), safe=""),
            upload=quote(str(upload), safe=""),
            chunk=quote(str(chunk), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CapabilityResponse | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = CapabilityResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CapabilityResponse | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    upload: str,
    chunk: int,
    *,
    client: AuthenticatedClient,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CreateChunkUploadCapabilitySecFetchSite | Unset = UNSET,
) -> Response[CapabilityResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        upload (str):
        chunk (int):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CreateChunkUploadCapabilitySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CapabilityResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        upload=upload,
        chunk=chunk,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    upload: str,
    chunk: int,
    *,
    client: AuthenticatedClient,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CreateChunkUploadCapabilitySecFetchSite | Unset = UNSET,
) -> CapabilityResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        upload (str):
        chunk (int):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CreateChunkUploadCapabilitySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CapabilityResponse | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        upload=upload,
        chunk=chunk,
        client=client,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    upload: str,
    chunk: int,
    *,
    client: AuthenticatedClient,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CreateChunkUploadCapabilitySecFetchSite | Unset = UNSET,
) -> Response[CapabilityResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        upload (str):
        chunk (int):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CreateChunkUploadCapabilitySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CapabilityResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        upload=upload,
        chunk=chunk,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    upload: str,
    chunk: int,
    *,
    client: AuthenticatedClient,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CreateChunkUploadCapabilitySecFetchSite | Unset = UNSET,
) -> CapabilityResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        upload (str):
        chunk (int):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CreateChunkUploadCapabilitySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CapabilityResponse | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            upload=upload,
            chunk=chunk,
            client=client,
            origin=origin,
            audaligo_transfer_continuation=audaligo_transfer_continuation,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
