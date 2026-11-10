from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.commerce_attempt_completion_reference import (
    CommerceAttemptCompletionReference,
)
from ...models.commerce_contract_reconciliation_reference import (
    CommerceContractReconciliationReference,
)
from ...models.commerce_reconcile_purchase_request import (
    CommerceReconcilePurchaseRequest,
)
from ...models.error_response import ErrorResponse
from ...models.reconcile_group_purchase_sec_fetch_site import (
    ReconcileGroupPurchaseSecFetchSite,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    purchase_id: UUID,
    *,
    body: CommerceReconcilePurchaseRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: ReconcileGroupPurchaseSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/organizations/{organization_id}/contracts/{purchase_id}/reconciliations".format(
            organization_id=quote(str(organization_id), safe=""),
            purchase_id=quote(str(purchase_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    CommerceAttemptCompletionReference
    | CommerceContractReconciliationReference
    | ErrorResponse
    | None
):
    if response.status_code == 202:

        def _parse_response_202(
            data: object,
        ) -> (
            CommerceAttemptCompletionReference | CommerceContractReconciliationReference
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_commerce_completion_reference_type_0 = (
                    CommerceAttemptCompletionReference.from_dict(data)
                )

                return componentsschemas_commerce_completion_reference_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_commerce_completion_reference_type_1 = (
                CommerceContractReconciliationReference.from_dict(data)
            )

            return componentsschemas_commerce_completion_reference_type_1

        response_202 = _parse_response_202(response.json())

        return response_202

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
) -> Response[
    CommerceAttemptCompletionReference
    | CommerceContractReconciliationReference
    | ErrorResponse
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    purchase_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CommerceReconcilePurchaseRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: ReconcileGroupPurchaseSecFetchSite | Unset = UNSET,
) -> Response[
    CommerceAttemptCompletionReference
    | CommerceContractReconciliationReference
    | ErrorResponse
]:
    """
    Args:
        organization_id (str):
        purchase_id (UUID):
        origin (str | Unset):
        sec_fetch_site (ReconcileGroupPurchaseSecFetchSite | Unset):
        body (CommerceReconcilePurchaseRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommerceAttemptCompletionReference | CommerceContractReconciliationReference | ErrorResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        purchase_id=purchase_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    purchase_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CommerceReconcilePurchaseRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: ReconcileGroupPurchaseSecFetchSite | Unset = UNSET,
) -> (
    CommerceAttemptCompletionReference
    | CommerceContractReconciliationReference
    | ErrorResponse
    | None
):
    """
    Args:
        organization_id (str):
        purchase_id (UUID):
        origin (str | Unset):
        sec_fetch_site (ReconcileGroupPurchaseSecFetchSite | Unset):
        body (CommerceReconcilePurchaseRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommerceAttemptCompletionReference | CommerceContractReconciliationReference | ErrorResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        purchase_id=purchase_id,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    purchase_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CommerceReconcilePurchaseRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: ReconcileGroupPurchaseSecFetchSite | Unset = UNSET,
) -> Response[
    CommerceAttemptCompletionReference
    | CommerceContractReconciliationReference
    | ErrorResponse
]:
    """
    Args:
        organization_id (str):
        purchase_id (UUID):
        origin (str | Unset):
        sec_fetch_site (ReconcileGroupPurchaseSecFetchSite | Unset):
        body (CommerceReconcilePurchaseRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommerceAttemptCompletionReference | CommerceContractReconciliationReference | ErrorResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        purchase_id=purchase_id,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    purchase_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CommerceReconcilePurchaseRequest,
    origin: str | Unset = UNSET,
    sec_fetch_site: ReconcileGroupPurchaseSecFetchSite | Unset = UNSET,
) -> (
    CommerceAttemptCompletionReference
    | CommerceContractReconciliationReference
    | ErrorResponse
    | None
):
    """
    Args:
        organization_id (str):
        purchase_id (UUID):
        origin (str | Unset):
        sec_fetch_site (ReconcileGroupPurchaseSecFetchSite | Unset):
        body (CommerceReconcilePurchaseRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommerceAttemptCompletionReference | CommerceContractReconciliationReference | ErrorResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            purchase_id=purchase_id,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
