from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.create_project_request import CreateProjectRequest
from ...models.create_project_sec_fetch_site import CreateProjectSecFetchSite
from ...models.error_envelope import ErrorEnvelope
from ...models.project_envelope import ProjectEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CreateProjectRequest,
    origin: str,
    sec_fetch_site: CreateProjectSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ProjectEnvelope:
    if response.status_code == 201:
        response_201 = ProjectEnvelope.from_dict(response.json())

        return response_201

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ProjectEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateProjectRequest,
    origin: str,
    sec_fetch_site: CreateProjectSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectEnvelope]:
    """
    Args:
        origin (str):
        sec_fetch_site (CreateProjectSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectEnvelope]
    """

    kwargs = _get_kwargs(
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
    *,
    client: AuthenticatedClient | Client,
    body: CreateProjectRequest,
    origin: str,
    sec_fetch_site: CreateProjectSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectEnvelope | None:
    """
    Args:
        origin (str):
        sec_fetch_site (CreateProjectSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectEnvelope
    """

    return sync_detailed(
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateProjectRequest,
    origin: str,
    sec_fetch_site: CreateProjectSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ProjectEnvelope]:
    """
    Args:
        origin (str):
        sec_fetch_site (CreateProjectSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ProjectEnvelope]
    """

    kwargs = _get_kwargs(
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateProjectRequest,
    origin: str,
    sec_fetch_site: CreateProjectSecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ProjectEnvelope | None:
    """
    Args:
        origin (str):
        sec_fetch_site (CreateProjectSecFetchSite | Unset):
        idempotency_key (str):
        body (CreateProjectRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ProjectEnvelope
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            idempotency_key=idempotency_key,
        )
    ).parsed
