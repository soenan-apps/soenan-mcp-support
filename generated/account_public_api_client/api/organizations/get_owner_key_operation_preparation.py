from http import HTTPStatus
from io import BytesIO
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import UNSET, File, Response


def _get_kwargs(
    operation_id: str,
    *,
    challenge: str,
    x_owner_key_operation_capability: str,
    x_owner_read_capabilities: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["X-Owner-Key-Operation-Capability"] = x_owner_key_operation_capability

    headers["X-Owner-Read-Capabilities"] = x_owner_read_capabilities

    params: dict[str, Any] = {}

    params["challenge"] = challenge

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/owner-key-operations/{operation_id}/preparation".format(
            operation_id=quote(str(operation_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | File | None:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

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
) -> Response[ErrorResponse | File]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_key_operation_capability: str,
    x_owner_read_capabilities: str,
) -> Response[ErrorResponse | File]:
    """
    Args:
        operation_id (str):
        challenge (str):
        x_owner_key_operation_capability (str):
        x_owner_read_capabilities (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | File]
    """

    kwargs = _get_kwargs(
        operation_id=operation_id,
        challenge=challenge,
        x_owner_key_operation_capability=x_owner_key_operation_capability,
        x_owner_read_capabilities=x_owner_read_capabilities,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_key_operation_capability: str,
    x_owner_read_capabilities: str,
) -> ErrorResponse | File | None:
    """
    Args:
        operation_id (str):
        challenge (str):
        x_owner_key_operation_capability (str):
        x_owner_read_capabilities (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | File
    """

    return sync_detailed(
        operation_id=operation_id,
        client=client,
        challenge=challenge,
        x_owner_key_operation_capability=x_owner_key_operation_capability,
        x_owner_read_capabilities=x_owner_read_capabilities,
    ).parsed


async def asyncio_detailed(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_key_operation_capability: str,
    x_owner_read_capabilities: str,
) -> Response[ErrorResponse | File]:
    """
    Args:
        operation_id (str):
        challenge (str):
        x_owner_key_operation_capability (str):
        x_owner_read_capabilities (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | File]
    """

    kwargs = _get_kwargs(
        operation_id=operation_id,
        challenge=challenge,
        x_owner_key_operation_capability=x_owner_key_operation_capability,
        x_owner_read_capabilities=x_owner_read_capabilities,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    challenge: str,
    x_owner_key_operation_capability: str,
    x_owner_read_capabilities: str,
) -> ErrorResponse | File | None:
    """
    Args:
        operation_id (str):
        challenge (str):
        x_owner_key_operation_capability (str):
        x_owner_read_capabilities (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | File
    """

    return (
        await asyncio_detailed(
            operation_id=operation_id,
            client=client,
            challenge=challenge,
            x_owner_key_operation_capability=x_owner_key_operation_capability,
            x_owner_read_capabilities=x_owner_read_capabilities,
        )
    ).parsed
