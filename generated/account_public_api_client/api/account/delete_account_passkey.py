from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_account_passkey_sec_fetch_site import (
    DeleteAccountPasskeySecFetchSite,
)
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    passkey_id: UUID,
    *,
    origin: str,
    sec_fetch_site: DeleteAccountPasskeySecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/account/passkeys/{passkey_id}".format(
            passkey_id=quote(str(passkey_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorResponse | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    passkey_id: UUID,
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: DeleteAccountPasskeySecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Remove one Passkey owned by the authenticated Account identity.

    Args:
        passkey_id (UUID):
        origin (str):
        sec_fetch_site (DeleteAccountPasskeySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        passkey_id=passkey_id,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    passkey_id: UUID,
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: DeleteAccountPasskeySecFetchSite | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Remove one Passkey owned by the authenticated Account identity.

    Args:
        passkey_id (UUID):
        origin (str):
        sec_fetch_site (DeleteAccountPasskeySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        passkey_id=passkey_id,
        client=client,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    passkey_id: UUID,
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: DeleteAccountPasskeySecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Remove one Passkey owned by the authenticated Account identity.

    Args:
        passkey_id (UUID):
        origin (str):
        sec_fetch_site (DeleteAccountPasskeySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        passkey_id=passkey_id,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    passkey_id: UUID,
    *,
    client: AuthenticatedClient,
    origin: str,
    sec_fetch_site: DeleteAccountPasskeySecFetchSite | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Remove one Passkey owned by the authenticated Account identity.

    Args:
        passkey_id (UUID):
        origin (str):
        sec_fetch_site (DeleteAccountPasskeySecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            passkey_id=passkey_id,
            client=client,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
