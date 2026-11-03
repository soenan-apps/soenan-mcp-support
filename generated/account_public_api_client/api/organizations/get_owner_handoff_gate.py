from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.owner_handoff_gate_response import OwnerHandoffGateResponse
from ...types import UNSET, Response


def _get_kwargs(
    gate_id: str,
    *,
    challenge: str,
    x_owner_read_capability: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["X-Owner-Read-Capability"] = x_owner_read_capability

    params: dict[str, Any] = {}

    params["challenge"] = challenge

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/owner-handoff/gates/{gate_id}".format(
            gate_id=quote(str(gate_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | OwnerHandoffGateResponse | None:
    if response.status_code == 200:
        response_200 = OwnerHandoffGateResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | OwnerHandoffGateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    gate_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_read_capability: str,
) -> Response[ErrorResponse | OwnerHandoffGateResponse]:
    """
    Args:
        gate_id (str):
        challenge (str):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerHandoffGateResponse]
    """

    kwargs = _get_kwargs(
        gate_id=gate_id,
        challenge=challenge,
        x_owner_read_capability=x_owner_read_capability,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    gate_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_read_capability: str,
) -> ErrorResponse | OwnerHandoffGateResponse | None:
    """
    Args:
        gate_id (str):
        challenge (str):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerHandoffGateResponse
    """

    return sync_detailed(
        gate_id=gate_id,
        client=client,
        challenge=challenge,
        x_owner_read_capability=x_owner_read_capability,
    ).parsed


async def asyncio_detailed(
    gate_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_read_capability: str,
) -> Response[ErrorResponse | OwnerHandoffGateResponse]:
    """
    Args:
        gate_id (str):
        challenge (str):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OwnerHandoffGateResponse]
    """

    kwargs = _get_kwargs(
        gate_id=gate_id,
        challenge=challenge,
        x_owner_read_capability=x_owner_read_capability,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    gate_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_read_capability: str,
) -> ErrorResponse | OwnerHandoffGateResponse | None:
    """
    Args:
        gate_id (str):
        challenge (str):
        x_owner_read_capability (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OwnerHandoffGateResponse
    """

    return (
        await asyncio_detailed(
            gate_id=gate_id,
            client=client,
            challenge=challenge,
            x_owner_read_capability=x_owner_read_capability,
        )
    ).parsed
