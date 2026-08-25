from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.create_mix_version_sec_fetch_site import CreateMixVersionSecFetchSite
from ...models.error_envelope import ErrorEnvelope
from ...models.mix_version_request import MixVersionRequest
from ...models.version_envelope import VersionEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    *,
    body: MixVersionRequest,
    origin: str,
    sec_fetch_site: CreateMixVersionSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects/{project}/versions".format(
            project=quote(str(project), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | VersionEnvelope:
    if response.status_code == 201:
        response_201 = VersionEnvelope.from_dict(response.json())

        return response_201

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
    *,
    client: AuthenticatedClient | Client,
    body: MixVersionRequest,
    origin: str,
    sec_fetch_site: CreateMixVersionSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | VersionEnvelope]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateMixVersionSecFetchSite | Unset):
        idempotency_key (str):
        body (MixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | VersionEnvelope]
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
    client: AuthenticatedClient | Client,
    body: MixVersionRequest,
    origin: str,
    sec_fetch_site: CreateMixVersionSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | VersionEnvelope | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateMixVersionSecFetchSite | Unset):
        idempotency_key (str):
        body (MixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | VersionEnvelope
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
    client: AuthenticatedClient | Client,
    body: MixVersionRequest,
    origin: str,
    sec_fetch_site: CreateMixVersionSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | VersionEnvelope]:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateMixVersionSecFetchSite | Unset):
        idempotency_key (str):
        body (MixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | VersionEnvelope]
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
    client: AuthenticatedClient | Client,
    body: MixVersionRequest,
    origin: str,
    sec_fetch_site: CreateMixVersionSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | VersionEnvelope | None:
    """
    Args:
        project (str):
        origin (str):
        sec_fetch_site (CreateMixVersionSecFetchSite | Unset):
        idempotency_key (str):
        body (MixVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | VersionEnvelope
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
