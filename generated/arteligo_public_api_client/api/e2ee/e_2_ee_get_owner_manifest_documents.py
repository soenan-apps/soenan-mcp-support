from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.e2_ee_owner_source_bundle import E2EeOwnerSourceBundle
from ...models.error_envelope import ErrorEnvelope
from ...types import Response


def _get_kwargs(
    organization_id: str,
    manifest_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/e2ee/organizations/{organization_id}/owner-access/manifests/{manifest_id}/documents".format(
            organization_id=quote(str(organization_id), safe=""),
            manifest_id=quote(str(manifest_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> E2EeOwnerSourceBundle | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = E2EeOwnerSourceBundle.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[E2EeOwnerSourceBundle | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[E2EeOwnerSourceBundle | ErrorEnvelope]:
    """
    Args:
        organization_id (str):
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeOwnerSourceBundle | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        manifest_id=manifest_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> E2EeOwnerSourceBundle | ErrorEnvelope | None:
    """
    Args:
        organization_id (str):
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeOwnerSourceBundle | ErrorEnvelope
    """

    return sync_detailed(
        organization_id=organization_id,
        manifest_id=manifest_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[E2EeOwnerSourceBundle | ErrorEnvelope]:
    """
    Args:
        organization_id (str):
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[E2EeOwnerSourceBundle | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        manifest_id=manifest_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> E2EeOwnerSourceBundle | ErrorEnvelope | None:
    """
    Args:
        organization_id (str):
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        E2EeOwnerSourceBundle | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            manifest_id=manifest_id,
            client=client,
        )
    ).parsed
