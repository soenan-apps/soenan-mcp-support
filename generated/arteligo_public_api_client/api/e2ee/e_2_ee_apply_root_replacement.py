from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_apply_root_replacement_sec_fetch_site import (
    E2EeApplyRootReplacementSecFetchSite,
)
from ...models.e2_ee_root_replacement_apply import E2EeRootReplacementApply
from ...models.e2_ee_root_replacement_result import E2EeRootReplacementResult
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, File, Response, Unset


def _get_kwargs(
    operation_id: str,
    *,
    body: E2EeRootReplacementApply | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApplyRootReplacementSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/root-replacements/{operation_id}/apply".format(
            operation_id=quote(str(operation_id), safe=""),
        ),
    }

    if isinstance(body, E2EeRootReplacementApply):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, File):
        _kwargs["content"] = body.payload

        headers["Content-Type"] = "application/x-ndjson"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeRootReplacementResult | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeRootReplacementResult.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeRootReplacementResult | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    operation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementApply | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApplyRootReplacementSecFetchSite | Unset = UNSET,
) -> Response[E2EeRootReplacementResult | ErrorEnvelope]:
    """
    Args:
        operation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApplyRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementApply):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeRootReplacementResult | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        operation_id=operation_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    operation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementApply | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApplyRootReplacementSecFetchSite | Unset = UNSET,
) -> E2EeRootReplacementResult | ErrorEnvelope | None:
    """
    Args:
        operation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApplyRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementApply):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeRootReplacementResult | ErrorEnvelope
    """

    return sync_detailed(
        operation_id=operation_id,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    operation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementApply | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApplyRootReplacementSecFetchSite | Unset = UNSET,
) -> Response[E2EeRootReplacementResult | ErrorEnvelope]:
    """
    Args:
        operation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApplyRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementApply):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeRootReplacementResult | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        operation_id=operation_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    operation_id: str,
    *,
    client: AuthenticatedClient,
    body: E2EeRootReplacementApply | File | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeApplyRootReplacementSecFetchSite | Unset = UNSET,
) -> E2EeRootReplacementResult | ErrorEnvelope | None:
    """
    Args:
        operation_id (str):
        origin (str | Unset):
        sec_fetch_site (E2EeApplyRootReplacementSecFetchSite | Unset):
        body (E2EeRootReplacementApply):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeRootReplacementResult | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            operation_id=operation_id,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
