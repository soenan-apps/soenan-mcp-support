from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.authenticated_product_session import AuthenticatedProductSession
from ...models.error_envelope import ErrorEnvelope
from ...models.switch_product_session_organization_request import (
    SwitchProductSessionOrganizationRequest,
)
from ...models.switch_product_session_organization_sec_fetch_site import (
    SwitchProductSessionOrganizationSecFetchSite,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SwitchProductSessionOrganizationRequest,
    origin: str,
    sec_fetch_site: SwitchProductSessionOrganizationSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/session/active-organization",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AuthenticatedProductSession | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = AuthenticatedProductSession.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AuthenticatedProductSession | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SwitchProductSessionOrganizationRequest,
    origin: str,
    sec_fetch_site: SwitchProductSessionOrganizationSecFetchSite | Unset = UNSET,
) -> Response[AuthenticatedProductSession | ErrorEnvelope]:
    """
    Args:
        origin (str):
        sec_fetch_site (SwitchProductSessionOrganizationSecFetchSite | Unset):
        body (SwitchProductSessionOrganizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticatedProductSession | ErrorEnvelope]
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
    client: AuthenticatedClient | Client,
    body: SwitchProductSessionOrganizationRequest,
    origin: str,
    sec_fetch_site: SwitchProductSessionOrganizationSecFetchSite | Unset = UNSET,
) -> AuthenticatedProductSession | ErrorEnvelope | None:
    """
    Args:
        origin (str):
        sec_fetch_site (SwitchProductSessionOrganizationSecFetchSite | Unset):
        body (SwitchProductSessionOrganizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticatedProductSession | ErrorEnvelope
    """

    return sync_detailed(
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SwitchProductSessionOrganizationRequest,
    origin: str,
    sec_fetch_site: SwitchProductSessionOrganizationSecFetchSite | Unset = UNSET,
) -> Response[AuthenticatedProductSession | ErrorEnvelope]:
    """
    Args:
        origin (str):
        sec_fetch_site (SwitchProductSessionOrganizationSecFetchSite | Unset):
        body (SwitchProductSessionOrganizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticatedProductSession | ErrorEnvelope]
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
    client: AuthenticatedClient | Client,
    body: SwitchProductSessionOrganizationRequest,
    origin: str,
    sec_fetch_site: SwitchProductSessionOrganizationSecFetchSite | Unset = UNSET,
) -> AuthenticatedProductSession | ErrorEnvelope | None:
    """
    Args:
        origin (str):
        sec_fetch_site (SwitchProductSessionOrganizationSecFetchSite | Unset):
        body (SwitchProductSessionOrganizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticatedProductSession | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
