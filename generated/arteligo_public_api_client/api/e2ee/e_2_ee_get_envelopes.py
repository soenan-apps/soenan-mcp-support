from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_envelopes import E2EeEnvelopes
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    scope_id: str,
    *,
    epoch: int | Unset = UNSET,
    recipient_id: str | Unset = UNSET,
    recipient_kind: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["epoch"] = epoch

    params["recipient_id"] = recipient_id

    params["recipient_kind"] = recipient_kind

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/scopes/{scope_id}/envelopes".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeEnvelopes | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeEnvelopes.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeEnvelopes | ErrorEnvelope]:
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
    epoch: int | Unset = UNSET,
    recipient_id: str | Unset = UNSET,
    recipient_kind: str | Unset = UNSET,
) -> Response[E2EeEnvelopes | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        epoch (int | Unset):
        recipient_id (str | Unset):
        recipient_kind (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeEnvelopes | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        epoch=epoch,
        recipient_id=recipient_id,
        recipient_kind=recipient_kind,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    epoch: int | Unset = UNSET,
    recipient_id: str | Unset = UNSET,
    recipient_kind: str | Unset = UNSET,
) -> E2EeEnvelopes | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        epoch (int | Unset):
        recipient_id (str | Unset):
        recipient_kind (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeEnvelopes | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
        epoch=epoch,
        recipient_id=recipient_id,
        recipient_kind=recipient_kind,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    epoch: int | Unset = UNSET,
    recipient_id: str | Unset = UNSET,
    recipient_kind: str | Unset = UNSET,
) -> Response[E2EeEnvelopes | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        epoch (int | Unset):
        recipient_id (str | Unset):
        recipient_kind (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeEnvelopes | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        epoch=epoch,
        recipient_id=recipient_id,
        recipient_kind=recipient_kind,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    epoch: int | Unset = UNSET,
    recipient_id: str | Unset = UNSET,
    recipient_kind: str | Unset = UNSET,
) -> E2EeEnvelopes | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        epoch (int | Unset):
        recipient_id (str | Unset):
        recipient_kind (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeEnvelopes | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
            epoch=epoch,
            recipient_id=recipient_id,
            recipient_kind=recipient_kind,
        )
    ).parsed
