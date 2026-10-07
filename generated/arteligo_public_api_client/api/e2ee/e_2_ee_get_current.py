from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_current_page import E2EeCurrentPage
from ...models.e2_ee_record_kind import E2EeRecordKind
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    scope_id: str,
    *,
    kind: E2EeRecordKind | Unset = UNSET,
    after_record_id: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_kind: str | Unset = UNSET
    if not isinstance(kind, Unset):
        json_kind = kind.value

    params["kind"] = json_kind

    params["after_record_id"] = after_record_id

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/scopes/{scope_id}/current".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeCurrentPage | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeCurrentPage.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeCurrentPage | ErrorEnvelope]:
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
    kind: E2EeRecordKind | Unset = UNSET,
    after_record_id: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> Response[E2EeCurrentPage | ErrorEnvelope]:
    """Bounded current records ordered by opaque record ID. Optional kind is a public record category, not
    a name or folder search. The complete encoded response is limited to 8 MiB. Continue using
    next_record_id when has_more.

    Args:
        scope_id (str):
        kind (E2EeRecordKind | Unset):
        after_record_id (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeCurrentPage | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        kind=kind,
        after_record_id=after_record_id,
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
    kind: E2EeRecordKind | Unset = UNSET,
    after_record_id: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> E2EeCurrentPage | ErrorEnvelope | None:
    """Bounded current records ordered by opaque record ID. Optional kind is a public record category, not
    a name or folder search. The complete encoded response is limited to 8 MiB. Continue using
    next_record_id when has_more.

    Args:
        scope_id (str):
        kind (E2EeRecordKind | Unset):
        after_record_id (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeCurrentPage | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
        kind=kind,
        after_record_id=after_record_id,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    kind: E2EeRecordKind | Unset = UNSET,
    after_record_id: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> Response[E2EeCurrentPage | ErrorEnvelope]:
    """Bounded current records ordered by opaque record ID. Optional kind is a public record category, not
    a name or folder search. The complete encoded response is limited to 8 MiB. Continue using
    next_record_id when has_more.

    Args:
        scope_id (str):
        kind (E2EeRecordKind | Unset):
        after_record_id (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeCurrentPage | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        kind=kind,
        after_record_id=after_record_id,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    kind: E2EeRecordKind | Unset = UNSET,
    after_record_id: str | Unset = UNSET,
    limit: int | Unset = 256,
) -> E2EeCurrentPage | ErrorEnvelope | None:
    """Bounded current records ordered by opaque record ID. Optional kind is a public record category, not
    a name or folder search. The complete encoded response is limited to 8 MiB. Continue using
    next_record_id when has_more.

    Args:
        scope_id (str):
        kind (E2EeRecordKind | Unset):
        after_record_id (str | Unset):
        limit (int | Unset):  Default: 256.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeCurrentPage | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
            kind=kind,
            after_record_id=after_record_id,
            limit=limit,
        )
    ).parsed
