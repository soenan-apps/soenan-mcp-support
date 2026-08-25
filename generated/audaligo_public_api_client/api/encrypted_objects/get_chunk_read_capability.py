from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import Client
from ...models.capability_response import CapabilityResponse
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    object_: str,
    chunk: int,
    *,
    audaligo_transfer_continuation: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(audaligo_transfer_continuation, Unset):
        headers["Audaligo-Transfer-Continuation"] = audaligo_transfer_continuation

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/encrypted-objects/{object_}/chunks/{chunk}/read-capabilities".format(
            project=quote(str(project), safe=""),
            object_=quote(str(object_), safe=""),
            chunk=quote(str(chunk), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Client, response: httpx.Response
) -> CapabilityResponse | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = CapabilityResponse.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[CapabilityResponse | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    object_: str,
    chunk: int,
    *,
    client: Client,
    audaligo_transfer_continuation: str | Unset = UNSET,
) -> Response[CapabilityResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        object_ (str):
        chunk (int):
        audaligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CapabilityResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        object_=object_,
        chunk=chunk,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    object_: str,
    chunk: int,
    *,
    client: Client,
    audaligo_transfer_continuation: str | Unset = UNSET,
) -> CapabilityResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        object_ (str):
        chunk (int):
        audaligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CapabilityResponse | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        object_=object_,
        chunk=chunk,
        client=client,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
    ).parsed


async def asyncio_detailed(
    project: str,
    object_: str,
    chunk: int,
    *,
    client: Client,
    audaligo_transfer_continuation: str | Unset = UNSET,
) -> Response[CapabilityResponse | ErrorEnvelope]:
    """
    Args:
        project (str):
        object_ (str):
        chunk (int):
        audaligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CapabilityResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        object_=object_,
        chunk=chunk,
        audaligo_transfer_continuation=audaligo_transfer_continuation,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    object_: str,
    chunk: int,
    *,
    client: Client,
    audaligo_transfer_continuation: str | Unset = UNSET,
) -> CapabilityResponse | ErrorEnvelope | None:
    """
    Args:
        project (str):
        object_ (str):
        chunk (int):
        audaligo_transfer_continuation (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CapabilityResponse | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            object_=object_,
            chunk=chunk,
            client=client,
            audaligo_transfer_continuation=audaligo_transfer_continuation,
        )
    ).parsed
