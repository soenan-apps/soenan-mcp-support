from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.accept_product_terms_sec_fetch_site import AcceptProductTermsSecFetchSite
from ...models.authenticated_product_session import AuthenticatedProductSession
from ...models.error_envelope import ErrorEnvelope
from ...models.terms_acceptance_request import TermsAcceptanceRequest
from ...models.terms_acceptance_required_product_session import (
    TermsAcceptanceRequiredProductSession,
)
from ...models.unauthenticated_product_session import UnauthenticatedProductSession
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: TermsAcceptanceRequest,
    origin: str,
    sec_fetch_site: AcceptProductTermsSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/session/terms-acceptance",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
):
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> (
            AuthenticatedProductSession
            | TermsAcceptanceRequiredProductSession
            | UnauthenticatedProductSession
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_product_session_response_type_0 = (
                    AuthenticatedProductSession.from_dict(data)
                )

                return componentsschemas_product_session_response_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_product_session_response_type_1 = (
                    TermsAcceptanceRequiredProductSession.from_dict(data)
                )

                return componentsschemas_product_session_response_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_product_session_response_type_2 = (
                UnauthenticatedProductSession.from_dict(data)
            )

            return componentsschemas_product_session_response_type_2

        response_200 = _parse_response_200(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TermsAcceptanceRequest,
    origin: str,
    sec_fetch_site: AcceptProductTermsSecFetchSite | Unset = UNSET,
) -> Response[
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
]:
    """
    Args:
        origin (str):
        sec_fetch_site (AcceptProductTermsSecFetchSite | Unset):
        body (TermsAcceptanceRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope]
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
    body: TermsAcceptanceRequest,
    origin: str,
    sec_fetch_site: AcceptProductTermsSecFetchSite | Unset = UNSET,
) -> (
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
    | None
):
    """
    Args:
        origin (str):
        sec_fetch_site (AcceptProductTermsSecFetchSite | Unset):
        body (TermsAcceptanceRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope
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
    body: TermsAcceptanceRequest,
    origin: str,
    sec_fetch_site: AcceptProductTermsSecFetchSite | Unset = UNSET,
) -> Response[
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
]:
    """
    Args:
        origin (str):
        sec_fetch_site (AcceptProductTermsSecFetchSite | Unset):
        body (TermsAcceptanceRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope]
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
    body: TermsAcceptanceRequest,
    origin: str,
    sec_fetch_site: AcceptProductTermsSecFetchSite | Unset = UNSET,
) -> (
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
    | None
):
    """
    Args:
        origin (str):
        sec_fetch_site (AcceptProductTermsSecFetchSite | Unset):
        body (TermsAcceptanceRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
