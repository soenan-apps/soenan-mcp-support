from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_bootstrap_sec_fetch_site import E2EeBootstrapSecFetchSite
from ...models.e2_ee_device import E2EeDevice
from ...models.e2_ee_signed_command import E2EeSignedCommand
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeBootstrapSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/bootstrap",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeDevice | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeDevice.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeDevice | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeBootstrapSecFetchSite | Unset = UNSET,
) -> Response[E2EeDevice | ErrorEnvelope]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeBootstrapSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeDevice | ErrorEnvelope]
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
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeBootstrapSecFetchSite | Unset = UNSET,
) -> E2EeDevice | ErrorEnvelope | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeBootstrapSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeDevice | ErrorEnvelope
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
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeBootstrapSecFetchSite | Unset = UNSET,
) -> Response[E2EeDevice | ErrorEnvelope]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeBootstrapSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeDevice | ErrorEnvelope]
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
    body: E2EeSignedCommand,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeBootstrapSecFetchSite | Unset = UNSET,
) -> E2EeDevice | ErrorEnvelope | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeBootstrapSecFetchSite | Unset):
        body (E2EeSignedCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeDevice | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
