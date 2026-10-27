from http import HTTPStatus
from io import BytesIO
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_prepare_root_replacement_sec_fetch_site import (
    E2EePrepareRootReplacementSecFetchSite,
)
from ...models.e2_ee_root_replacement_prepare import E2EeRootReplacementPrepare
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, File, Response, Unset


def _get_kwargs(
    *,
    body: E2EeRootReplacementPrepare | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EePrepareRootReplacementSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/root-replacements/prepare",
    }

    if isinstance(body, E2EeRootReplacementPrepare):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, File):
        _kwargs["content"] = body.payload

        headers["Content-Type"] = "application/x-ndjson"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | File:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | File]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementPrepare | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EePrepareRootReplacementSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | File]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EePrepareRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementPrepare):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | File]
    """

    kwargs = _get_kwargs(
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementPrepare | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EePrepareRootReplacementSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | File | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EePrepareRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementPrepare):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | File
    """

    return sync_detailed(
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementPrepare | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EePrepareRootReplacementSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | File]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EePrepareRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementPrepare):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | File]
    """

    kwargs = _get_kwargs(
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementPrepare | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EePrepareRootReplacementSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | File | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EePrepareRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementPrepare):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | File
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
