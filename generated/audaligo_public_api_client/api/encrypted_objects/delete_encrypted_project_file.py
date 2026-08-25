from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.delete_encrypted_project_file_sec_fetch_site import DeleteEncryptedProjectFileSecFetchSite
from ...models.encrypted_project_file_deletion_response import EncryptedProjectFileDeletionResponse
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    file: str,
    *,
    origin: str,
    sec_fetch_site: DeleteEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/projects/{project}/files/{file}".format(
            project=quote(str(project), safe=""),
            file=quote(str(file), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> EncryptedProjectFileDeletionResponse | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = EncryptedProjectFileDeletionResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[EncryptedProjectFileDeletionResponse | ErrorEnvelope]:
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
    origin: str,
    sec_fetch_site: DeleteEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> Response[EncryptedProjectFileDeletionResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        sec_fetch_site (DeleteEncryptedProjectFileSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EncryptedProjectFileDeletionResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        origin=origin,
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
    origin: str,
    sec_fetch_site: DeleteEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> EncryptedProjectFileDeletionResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        sec_fetch_site (DeleteEncryptedProjectFileSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EncryptedProjectFileDeletionResponse | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        file=file,
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: DeleteEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> Response[EncryptedProjectFileDeletionResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        sec_fetch_site (DeleteEncryptedProjectFileSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EncryptedProjectFileDeletionResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        file=file,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    file: str,
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: DeleteEncryptedProjectFileSecFetchSite | Unset = UNSET,
) -> EncryptedProjectFileDeletionResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        file (str):
        origin (str):
        sec_fetch_site (DeleteEncryptedProjectFileSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EncryptedProjectFileDeletionResponse | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            file=file,
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
