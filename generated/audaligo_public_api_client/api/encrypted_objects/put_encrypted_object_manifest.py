from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import Client
from ...models.error_envelope import ErrorEnvelope
from ...models.object_state_response import ObjectStateResponse
from ...models.put_encrypted_object_manifest_sec_fetch_site import (
    PutEncryptedObjectManifestSecFetchSite,
)
from ...models.put_manifest_request import PutManifestRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    upload: str,
    *,
    body: PutManifestRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: PutEncryptedObjectManifestSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(audaligo_transfer_continuation, Unset):
        headers["Audaligo-Transfer-Continuation"] = audaligo_transfer_continuation

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/projects/{project}/uploads/{upload}/manifest".format(
            project=quote(str(project), safe=""),
            upload=quote(str(upload), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Client, response: httpx.Response
) -> ErrorEnvelope | ObjectStateResponse:
    if response.status_code == 200:
        response_200 = ObjectStateResponse.from_dict(response.json())

        return response_200

    if response.status_code == 201:
        response_201 = ObjectStateResponse.from_dict(response.json())

        return response_201

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[ErrorEnvelope | ObjectStateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    upload: str,
    *,
    client: Client,
    body: PutManifestRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: PutEncryptedObjectManifestSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ObjectStateResponse]:
    """
    Args:
        project (str):
        upload (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (PutEncryptedObjectManifestSecFetchSite | Unset):
        body (PutManifestRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ObjectStateResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        upload=upload,
        body=body,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    upload: str,
    *,
    client: Client,
    body: PutManifestRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: PutEncryptedObjectManifestSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ObjectStateResponse | None:
    """
    Args:
        project (str):
        upload (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (PutEncryptedObjectManifestSecFetchSite | Unset):
        body (PutManifestRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ObjectStateResponse
    """

    return sync_detailed(
        project=project,
        upload=upload,
        client=client,
        body=body,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    upload: str,
    *,
    client: Client,
    body: PutManifestRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: PutEncryptedObjectManifestSecFetchSite | Unset = UNSET,
) -> Response[ErrorEnvelope | ObjectStateResponse]:
    """
    Args:
        project (str):
        upload (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (PutEncryptedObjectManifestSecFetchSite | Unset):
        body (PutManifestRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ObjectStateResponse]
    """

    kwargs = _get_kwargs(
        project=project,
        upload=upload,
        body=body,
        origin=origin,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    upload: str,
    *,
    client: Client,
    body: PutManifestRequest,
    origin: str,
    audaligo_transfer_continuation: str | Unset = UNSET,
    sec_fetch_site: PutEncryptedObjectManifestSecFetchSite | Unset = UNSET,
) -> ErrorEnvelope | ObjectStateResponse | None:
    """
    Args:
        project (str):
        upload (str):
        origin (str):
        audaligo_transfer_continuation (str | Unset):
        sec_fetch_site (PutEncryptedObjectManifestSecFetchSite | Unset):
        body (PutManifestRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ObjectStateResponse
    """

    return (
        await asyncio_detailed(
            project=project,
            upload=upload,
            client=client,
            body=body,
            origin=origin,
            audaligo_transfer_continuation=audaligo_transfer_continuation,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
