from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_recovery_roots import E2EeRecoveryRoots
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    scope_id: str,
    *,
    recovery_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["recovery_id"] = recovery_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/scopes/{scope_id}/recovery-roots".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeRecoveryRoots | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeRecoveryRoots.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeRecoveryRoots | ErrorEnvelope]:
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
    recovery_id: str | Unset = UNSET,
) -> Response[E2EeRecoveryRoots | ErrorEnvelope]:
    """Public recovery-root certificates for current and historical scope authors. Requires current read
    access and never returns encrypted recovery bundles.

    Args:
        scope_id (str):
        recovery_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeRecoveryRoots | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        recovery_id=recovery_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    recovery_id: str | Unset = UNSET,
) -> E2EeRecoveryRoots | ErrorEnvelope | None:
    """Public recovery-root certificates for current and historical scope authors. Requires current read
    access and never returns encrypted recovery bundles.

    Args:
        scope_id (str):
        recovery_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeRecoveryRoots | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
        recovery_id=recovery_id,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    recovery_id: str | Unset = UNSET,
) -> Response[E2EeRecoveryRoots | ErrorEnvelope]:
    """Public recovery-root certificates for current and historical scope authors. Requires current read
    access and never returns encrypted recovery bundles.

    Args:
        scope_id (str):
        recovery_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeRecoveryRoots | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        recovery_id=recovery_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    recovery_id: str | Unset = UNSET,
) -> E2EeRecoveryRoots | ErrorEnvelope | None:
    """Public recovery-root certificates for current and historical scope authors. Requires current read
    access and never returns encrypted recovery bundles.

    Args:
        scope_id (str):
        recovery_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeRecoveryRoots | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
            recovery_id=recovery_id,
        )
    ).parsed
