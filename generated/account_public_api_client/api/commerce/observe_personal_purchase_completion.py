from http import HTTPStatus
from io import BytesIO
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.commerce_attempt_completion_reference import (
    CommerceAttemptCompletionReference,
)
from ...models.commerce_contract_reconciliation_reference import (
    CommerceContractReconciliationReference,
)
from ...models.error_response import ErrorResponse
from ...models.observe_personal_purchase_completion_sec_fetch_site import (
    ObservePersonalPurchaseCompletionSecFetchSite,
)
from ...types import UNSET, File, Response, Unset


def _get_kwargs(
    *,
    body: CommerceAttemptCompletionReference | CommerceContractReconciliationReference,
    origin: str | Unset = UNSET,
    sec_fetch_site: ObservePersonalPurchaseCompletionSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/me/purchase-completion-stream",
    }

    if isinstance(body, CommerceAttemptCompletionReference):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

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

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

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
    *,
    client: AuthenticatedClient,
    body: CommerceAttemptCompletionReference | CommerceContractReconciliationReference,
    origin: str | Unset = UNSET,
    sec_fetch_site: ObservePersonalPurchaseCompletionSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | File]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (ObservePersonalPurchaseCompletionSecFetchSite | Unset):
        body (CommerceAttemptCompletionReference | CommerceContractReconciliationReference):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | File]
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
    body: CommerceAttemptCompletionReference | CommerceContractReconciliationReference,
    origin: str | Unset = UNSET,
    sec_fetch_site: ObservePersonalPurchaseCompletionSecFetchSite | Unset = UNSET,
) -> ErrorResponse | File | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (ObservePersonalPurchaseCompletionSecFetchSite | Unset):
        body (CommerceAttemptCompletionReference | CommerceContractReconciliationReference):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | File
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
    body: CommerceAttemptCompletionReference | CommerceContractReconciliationReference,
    origin: str | Unset = UNSET,
    sec_fetch_site: ObservePersonalPurchaseCompletionSecFetchSite | Unset = UNSET,
) -> Response[ErrorResponse | File]:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (ObservePersonalPurchaseCompletionSecFetchSite | Unset):
        body (CommerceAttemptCompletionReference | CommerceContractReconciliationReference):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | File]
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
    body: CommerceAttemptCompletionReference | CommerceContractReconciliationReference,
    origin: str | Unset = UNSET,
    sec_fetch_site: ObservePersonalPurchaseCompletionSecFetchSite | Unset = UNSET,
) -> ErrorResponse | File | None:
    """
    Args:
        origin (str | Unset):
        sec_fetch_site (ObservePersonalPurchaseCompletionSecFetchSite | Unset):
        body (CommerceAttemptCompletionReference | CommerceContractReconciliationReference):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | File
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
