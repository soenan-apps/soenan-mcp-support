from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.commit_encrypted_project_file_sec_fetch_site import (
    CommitEncryptedProjectFileSecFetchSite,
)
from ...models.commit_project_file_request import CommitProjectFileRequest
from ...models.encrypted_project_file_response import EncryptedProjectFileResponse
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    file: str,
    *,
    body: CommitProjectFileRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CommitEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(audaligo_transfer_continuation, Unset):
        headers["Audaligo-Transfer-Continuation"] = audaligo_transfer_continuation

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/projects/{project}/files/{file}".format(
            project=quote(str(project), safe=""),
            file=quote(str(file), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> EncryptedProjectFileResponse | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = EncryptedProjectFileResponse.from_dict(response.json())

        return response_200

    if response.status_code == 201:
        response_201 = EncryptedProjectFileResponse.from_dict(response.json())

        return response_201

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[EncryptedProjectFileResponse | ErrorEnvelope]:
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
    body: CommitProjectFileRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CommitEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> Response[EncryptedProjectFileResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CommitEncryptedProjectFileSecFetchSite | Unset):
        body (CommitProjectFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EncryptedProjectFileResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        body=body,
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
    file: str,
    *,
    client: AuthenticatedClient,
    body: CommitProjectFileRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CommitEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> EncryptedProjectFileResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CommitEncryptedProjectFileSecFetchSite | Unset):
        body (CommitProjectFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EncryptedProjectFileResponse | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        file=file,
        client=client,
        body=body,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    body: CommitProjectFileRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CommitEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> Response[EncryptedProjectFileResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CommitEncryptedProjectFileSecFetchSite | Unset):
        body (CommitProjectFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EncryptedProjectFileResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        body=body,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    body: CommitProjectFileRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: CommitEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> EncryptedProjectFileResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (CommitEncryptedProjectFileSecFetchSite | Unset):
        body (CommitProjectFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EncryptedProjectFileResponse | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            file=file,
            client=client,
            body=body,
            origin=origin,
            audaligo_transfer_continuation=audaligo_transfer_continuation,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
