from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.update_mix_version_request import UpdateMixVersionRequest
from ...models.update_mix_version_sec_fetch_site import UpdateMixVersionSecFetchSite
from ...models.version_envelope import VersionEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    mix_version: str,
    *,
    body: UpdateMixVersionRequest,
    origin: str,
    sec_fetch_site: UpdateMixVersionSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/projects/{project}/versions/{mix_version}".format(
            project=quote(str(project), safe=""),
            mix_version=quote(str(mix_version), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | VersionEnvelope:
    if response.status_code == 200:
        response_200 = VersionEnvelope.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | VersionEnvelope]:
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
    body: UpdateMixVersionRequest,
    origin: str,
    sec_fetch_site: UpdateMixVersionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | VersionEnvelope]:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (UpdateMixVersionSecFetchSite | Unset):
        body (UpdateMixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | VersionEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        mix_version=mix_version,
        body=body,
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
    body: UpdateMixVersionRequest,
    origin: str,
    sec_fetch_site: UpdateMixVersionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | VersionEnvelope | None:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (UpdateMixVersionSecFetchSite | Unset):
        body (UpdateMixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | VersionEnvelope
    """

    return sync_detailed(
        project=project,
        mix_version=mix_version,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    mix_version: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMixVersionRequest,
    origin: str,
    sec_fetch_site: UpdateMixVersionSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | VersionEnvelope]:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (UpdateMixVersionSecFetchSite | Unset):
        body (UpdateMixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | VersionEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        mix_version=mix_version,
        body=body,
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
    body: UpdateMixVersionRequest,
    origin: str,
    sec_fetch_site: UpdateMixVersionSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | VersionEnvelope | None:
    """
    Args:
        project (str):
        mix_version (str):
        origin (str):
        sec_fetch_site (UpdateMixVersionSecFetchSite | Unset):
        body (UpdateMixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | VersionEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            mix_version=mix_version,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
