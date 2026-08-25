from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.delete_mix_version_sec_fetch_site import DeleteMixVersionSecFetchSite
from ...models.error_envelope import ErrorEnvelope
from ...models.version_deletion_envelope import VersionDeletionEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    mix_version: str,
    *,
    origin: str,
    sec_fetch_site: DeleteMixVersionSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/projects/{project}/versions/{mix_version}".format(
            project=quote(str(project), safe=""),
            mix_version=quote(str(mix_version), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | VersionDeletionEnvelope:
    if response.status_code == 200:
        response_200 = VersionDeletionEnvelope.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | VersionDeletionEnvelope]:
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
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: DeleteMixVersionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | VersionDeletionEnvelope]:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (DeleteMixVersionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | VersionDeletionEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        mix_version=mix_version,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: DeleteMixVersionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | VersionDeletionEnvelope | None:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (DeleteMixVersionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | VersionDeletionEnvelope
    """

    return sync_detailed(
        project=project,
        mix_version=mix_version,
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: DeleteMixVersionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | VersionDeletionEnvelope]:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (DeleteMixVersionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | VersionDeletionEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        mix_version=mix_version,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient | Client,
    origin: str,
    sec_fetch_site: DeleteMixVersionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | VersionDeletionEnvelope | None:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (DeleteMixVersionSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | VersionDeletionEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            mix_version=mix_version,
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
