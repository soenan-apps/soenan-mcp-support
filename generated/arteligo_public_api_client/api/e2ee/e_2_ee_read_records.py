from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_read_records_sec_fetch_site import E2EeReadRecordsSecFetchSite
from ...models.e2_ee_read_request import E2EeReadRequest
from ...models.e2_ee_read_response import E2EeReadResponse
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: E2EeReadRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeReadRecordsSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/e2ee/records/read",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeReadResponse | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeReadResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeReadResponse | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: E2EeReadRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeReadRecordsSecFetchSite | Unset = UNSET,
) -> Response[E2EeReadResponse | ErrorEnvelope]:
    """Read up to 256 opaque record IDs across at most 32 distinct scopes. This unsigned JSON POST is a
    read operation. Scope authorization failures are isolated in the corresponding result. The complete
    encoded response is limited to 8 MiB; remaining_record_ids explicitly identifies deferred reads.
    Names, paths, parent relationships, and search predicates are not interpreted by this API.

    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeReadRecordsSecFetchSite | Unset):
        body (E2EeReadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeReadResponse | ErrorEnvelope]
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
    body: E2EeReadRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeReadRecordsSecFetchSite | Unset = UNSET,
) -> E2EeReadResponse | ErrorEnvelope | None:
    """Read up to 256 opaque record IDs across at most 32 distinct scopes. This unsigned JSON POST is a
    read operation. Scope authorization failures are isolated in the corresponding result. The complete
    encoded response is limited to 8 MiB; remaining_record_ids explicitly identifies deferred reads.
    Names, paths, parent relationships, and search predicates are not interpreted by this API.

    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeReadRecordsSecFetchSite | Unset):
        body (E2EeReadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeReadResponse | ErrorEnvelope
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
    body: E2EeReadRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeReadRecordsSecFetchSite | Unset = UNSET,
) -> Response[E2EeReadResponse | ErrorEnvelope]:
    """Read up to 256 opaque record IDs across at most 32 distinct scopes. This unsigned JSON POST is a
    read operation. Scope authorization failures are isolated in the corresponding result. The complete
    encoded response is limited to 8 MiB; remaining_record_ids explicitly identifies deferred reads.
    Names, paths, parent relationships, and search predicates are not interpreted by this API.

    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeReadRecordsSecFetchSite | Unset):
        body (E2EeReadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeReadResponse | ErrorEnvelope]
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
    body: E2EeReadRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: E2EeReadRecordsSecFetchSite | Unset = UNSET,
) -> E2EeReadResponse | ErrorEnvelope | None:
    """Read up to 256 opaque record IDs across at most 32 distinct scopes. This unsigned JSON POST is a
    read operation. Scope authorization failures are isolated in the corresponding result. The complete
    encoded response is limited to 8 MiB; remaining_record_ids explicitly identifies deferred reads.
    Names, paths, parent relationships, and search predicates are not interpreted by this API.

    Args:
        origin (str | Unset):
        sec_fetch_site (E2EeReadRecordsSecFetchSite | Unset):
        body (E2EeReadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeReadResponse | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
