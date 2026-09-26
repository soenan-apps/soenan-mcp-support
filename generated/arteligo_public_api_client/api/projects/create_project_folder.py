from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.create_project_folder_request import CreateProjectFolderRequest
from ...models.create_project_folder_sec_fetch_site import (
    CreateProjectFolderSecFetchSite,
)
from ...models.error_envelope import ErrorEnvelope
from ...models.project_entry_response import ProjectEntryResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    *,
    body: CreateProjectFolderRequest,
    origin: str,
    sec_fetch_site: CreateProjectFolderSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects/{project}/folders".format(
            project=quote(str(project), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectEntryResponse:
    if response.status_code == 201:
        response_201 = ProjectEntryResponse.from_dict(response.json())

        return response_201

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectEntryResponse]:
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
    body: CreateProjectFolderRequest,
    origin: str,
    sec_fetch_site: CreateProjectFolderSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectEntryResponse]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateProjectFolderSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectEntryResponse]
    """

    kwargs = _get_kwargs(
        project=project,
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
    *,
    client: AuthenticatedClient,
    body: CreateProjectFolderRequest,
    origin: str,
    sec_fetch_site: CreateProjectFolderSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectEntryResponse | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateProjectFolderSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectEntryResponse
    """

    return sync_detailed(
        project=project,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    project: str,
    *,
    client: AuthenticatedClient,
    body: CreateProjectFolderRequest,
    origin: str,
    sec_fetch_site: CreateProjectFolderSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectEntryResponse]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateProjectFolderSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectEntryResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    *,
    client: AuthenticatedClient,
    body: CreateProjectFolderRequest,
    origin: str,
    sec_fetch_site: CreateProjectFolderSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectEntryResponse | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateProjectFolderSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectEntryResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            idempotency_key=idempotency_key,
        )
    ).parsed
