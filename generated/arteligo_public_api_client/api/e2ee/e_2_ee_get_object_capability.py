from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_capability import E2EeCapability
from ...models.error_envelope import ErrorEnvelope
from ...types import Response


def _get_kwargs(
    scope_id: str,
    object_id: str,
    index: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/projects/{scope_id}/objects/{object_id}/chunks/{index}".format(
            scope_id=quote(str(scope_id), safe=""),
            object_id=quote(str(object_id), safe=""),
            index=quote(str(index), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeCapability | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeCapability.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeCapability | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    scope_id: str,
    object_id: str,
    index: int,
    *,
    client: AuthenticatedClient,
) -> Response[E2EeCapability | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        object_id (str):
        index (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeCapability | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        object_id=object_id,
        index=index,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scope_id: str,
    object_id: str,
    index: int,
    *,
    client: AuthenticatedClient,
) -> E2EeCapability | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        object_id (str):
        index (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeCapability | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        object_id=object_id,
        index=index,
        client=client,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    object_id: str,
    index: int,
    *,
    client: AuthenticatedClient,
) -> Response[E2EeCapability | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        object_id (str):
        index (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeCapability | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        object_id=object_id,
        index=index,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    object_id: str,
    index: int,
    *,
    client: AuthenticatedClient,
) -> E2EeCapability | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        object_id (str):
        index (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeCapability | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            object_id=object_id,
            index=index,
            client=client,
        )
    ).parsed
