from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_owner_generation import E2EeOwnerGeneration
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response


def _get_kwargs(
    scope_id: str,
    *,
    epoch: int,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["epoch"] = epoch

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/scopes/{scope_id}/owner-generation".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeOwnerGeneration | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeOwnerGeneration.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeOwnerGeneration | ErrorEnvelope]:
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
    epoch: int,
) -> Response[E2EeOwnerGeneration | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        epoch (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeOwnerGeneration | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        epoch=epoch,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    epoch: int,
) -> E2EeOwnerGeneration | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        epoch (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeOwnerGeneration | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
        epoch=epoch,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    epoch: int,
) -> Response[E2EeOwnerGeneration | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        epoch (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeOwnerGeneration | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        epoch=epoch,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    epoch: int,
) -> E2EeOwnerGeneration | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        epoch (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeOwnerGeneration | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
            epoch=epoch,
        )
    ).parsed
