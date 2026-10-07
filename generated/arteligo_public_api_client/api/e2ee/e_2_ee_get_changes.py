from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_changes_page import E2EeChangesPage
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    scope_id: str,
    *,
    after: int | Unset = 0,
    limit: int | Unset = 256,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["after"] = after

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/scopes/{scope_id}/changes".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeChangesPage | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeChangesPage.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeChangesPage | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    after: int | Unset = 0,
    limit: int | Unset = 256,
) -> Response[E2EeChangesPage | ErrorEnvelope]:
    """Invalidation metadata without content or signatures. Observation cursors are not verified record
    revisions. Complete transactions are returned; the first transaction may exceed the requested soft
    limit, up to 256 changes. A cursor outside the retained range returns revision_conflict.

    Args:
        scope_id (str):
        after (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeChangesPage | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        after=after,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    after: int | Unset = 0,
    limit: int | Unset = 256,
) -> E2EeChangesPage | ErrorEnvelope | None:
    """Invalidation metadata without content or signatures. Observation cursors are not verified record
    revisions. Complete transactions are returned; the first transaction may exceed the requested soft
    limit, up to 256 changes. A cursor outside the retained range returns revision_conflict.

    Args:
        scope_id (str):
        after (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeChangesPage | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
        after=after,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    after: int | Unset = 0,
    limit: int | Unset = 256,
) -> Response[E2EeChangesPage | ErrorEnvelope]:
    """Invalidation metadata without content or signatures. Observation cursors are not verified record
    revisions. Complete transactions are returned; the first transaction may exceed the requested soft
    limit, up to 256 changes. A cursor outside the retained range returns revision_conflict.

    Args:
        scope_id (str):
        after (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeChangesPage | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        after=after,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    after: int | Unset = 0,
    limit: int | Unset = 256,
) -> E2EeChangesPage | ErrorEnvelope | None:
    """Invalidation metadata without content or signatures. Observation cursors are not verified record
    revisions. Complete transactions are returned; the first transaction may exceed the requested soft
    limit, up to 256 changes. A cursor outside the retained range returns revision_conflict.

    Args:
        scope_id (str):
        after (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeChangesPage | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
            after=after,
            limit=limit,
        )
    ).parsed
