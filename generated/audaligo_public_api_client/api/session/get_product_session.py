from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.authenticated_product_session import AuthenticatedProductSession
from ...models.error_envelope import ErrorEnvelope
from ...models.terms_acceptance_required_product_session import TermsAcceptanceRequiredProductSession
from ...models.unauthenticated_product_session import UnauthenticatedProductSession
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/session",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
    | None
):
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_product_session_response_type_0 = AuthenticatedProductSession.from_dict(data)

                return componentsschemas_product_session_response_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_product_session_response_type_1 = TermsAcceptanceRequiredProductSession.from_dict(
                    data
                )

                return componentsschemas_product_session_response_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_product_session_response_type_2 = UnauthenticatedProductSession.from_dict(data)

            return componentsschemas_product_session_response_type_2

        response_200 = _parse_response_200(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ErrorEnvelope.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = ErrorEnvelope.from_dict(response.json())

        return response_401

    if response.status_code == 503:
        response_503 = ErrorEnvelope.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope
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
) -> Response[
    AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope
]:
    """
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> (
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
    | None
):
    """
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope
]:
    """
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> (
    AuthenticatedProductSession
    | TermsAcceptanceRequiredProductSession
    | UnauthenticatedProductSession
    | ErrorEnvelope
    | None
):
    """
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticatedProductSession | TermsAcceptanceRequiredProductSession | UnauthenticatedProductSession | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
