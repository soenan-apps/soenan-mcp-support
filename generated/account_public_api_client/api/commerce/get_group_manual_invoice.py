from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.manual_invoice_customer_detail import ManualInvoiceCustomerDetail
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    invoice_id: UUID,
    *,
    receipt_offset: int | Unset = 0,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["receiptOffset"] = receipt_offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/organizations/{organization_id}/manual-invoices/{invoice_id}".format(
            organization_id=quote(str(organization_id), safe=""),
            invoice_id=quote(str(invoice_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | ManualInvoiceCustomerDetail | None:
    if response.status_code == 200:
        response_200 = ManualInvoiceCustomerDetail.from_dict(response.json())

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

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | ManualInvoiceCustomerDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    invoice_id: UUID,
    *,
    client: AuthenticatedClient,
    receipt_offset: int | Unset = 0,
) -> Response[ErrorResponse | ManualInvoiceCustomerDetail]:
    """
    Args:
        organization_id (str):
        invoice_id (UUID):
        receipt_offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | ManualInvoiceCustomerDetail]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        invoice_id=invoice_id,
        receipt_offset=receipt_offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    invoice_id: UUID,
    *,
    client: AuthenticatedClient,
    receipt_offset: int | Unset = 0,
) -> ErrorResponse | ManualInvoiceCustomerDetail | None:
    """
    Args:
        organization_id (str):
        invoice_id (UUID):
        receipt_offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | ManualInvoiceCustomerDetail
    """

    return sync_detailed(
        organization_id=organization_id,
        invoice_id=invoice_id,
        client=client,
        receipt_offset=receipt_offset,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    invoice_id: UUID,
    *,
    client: AuthenticatedClient,
    receipt_offset: int | Unset = 0,
) -> Response[ErrorResponse | ManualInvoiceCustomerDetail]:
    """
    Args:
        organization_id (str):
        invoice_id (UUID):
        receipt_offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | ManualInvoiceCustomerDetail]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        invoice_id=invoice_id,
        receipt_offset=receipt_offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    invoice_id: UUID,
    *,
    client: AuthenticatedClient,
    receipt_offset: int | Unset = 0,
) -> ErrorResponse | ManualInvoiceCustomerDetail | None:
    """
    Args:
        organization_id (str):
        invoice_id (UUID):
        receipt_offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | ManualInvoiceCustomerDetail
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            invoice_id=invoice_id,
            client=client,
            receipt_offset=receipt_offset,
        )
    ).parsed
