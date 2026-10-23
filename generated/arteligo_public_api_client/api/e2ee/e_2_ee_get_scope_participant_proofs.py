from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_scope_participant_proofs import E2EeScopeParticipantProofs
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    scope_id: str,
    *,
    account_subject: str | Unset = UNSET,
    after_request_id: str | Unset = UNSET,
    source_scope_id: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["account_subject"] = account_subject

    params["after_request_id"] = after_request_id

    params["source_scope_id"] = source_scope_id

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/scopes/{scope_id}/participant-proofs".format(
            scope_id=quote(str(scope_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeScopeParticipantProofs | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeScopeParticipantProofs.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeScopeParticipantProofs | ErrorEnvelope]:
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
    account_subject: str | Unset = UNSET,
    after_request_id: str | Unset = UNSET,
    source_scope_id: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> Response[E2EeScopeParticipantProofs | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        account_subject (str | Unset):
        after_request_id (str | Unset):
        source_scope_id (str | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeScopeParticipantProofs | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        account_subject=account_subject,
        after_request_id=after_request_id,
        source_scope_id=source_scope_id,
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
    account_subject: str | Unset = UNSET,
    after_request_id: str | Unset = UNSET,
    source_scope_id: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> E2EeScopeParticipantProofs | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        account_subject (str | Unset):
        after_request_id (str | Unset):
        source_scope_id (str | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeScopeParticipantProofs | ErrorEnvelope
    """

    return sync_detailed(
        scope_id=scope_id,
        client=client,
        account_subject=account_subject,
        after_request_id=after_request_id,
        source_scope_id=source_scope_id,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    account_subject: str | Unset = UNSET,
    after_request_id: str | Unset = UNSET,
    source_scope_id: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> Response[E2EeScopeParticipantProofs | ErrorEnvelope]:
    """
    Args:
        scope_id (str):
        account_subject (str | Unset):
        after_request_id (str | Unset):
        source_scope_id (str | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeScopeParticipantProofs | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        scope_id=scope_id,
        account_subject=account_subject,
        after_request_id=after_request_id,
        source_scope_id=source_scope_id,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scope_id: str,
    *,
    client: AuthenticatedClient,
    account_subject: str | Unset = UNSET,
    after_request_id: str | Unset = UNSET,
    source_scope_id: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> E2EeScopeParticipantProofs | ErrorEnvelope | None:
    """
    Args:
        scope_id (str):
        account_subject (str | Unset):
        after_request_id (str | Unset):
        source_scope_id (str | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeScopeParticipantProofs | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            scope_id=scope_id,
            client=client,
            account_subject=account_subject,
            after_request_id=after_request_id,
            source_scope_id=source_scope_id,
            limit=limit,
        )
    ).parsed
