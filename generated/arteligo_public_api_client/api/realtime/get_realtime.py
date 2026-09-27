from http import HTTPStatus
from io import BytesIO
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, File, Response, Unset


def _get_kwargs(
    *,
    project_id: str | Unset = UNSET,
    after: int | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(origin, Unset):
        headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = sec_fetch_site

    params: dict[str, Any] = {}

    params["projectId"] = project_id

    params["after"] = after

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/realtime",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | File | None:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.text))

        return response_200

    if response.status_code == 400:
        response_400 = ErrorEnvelope.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = ErrorEnvelope.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ErrorEnvelope.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = ErrorEnvelope.from_dict(response.json())

        return response_429

    if response.status_code == 503:
        response_503 = ErrorEnvelope.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | File]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    project_id: str | Unset = UNSET,
    after: int | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: str | Unset = UNSET,
) -> Response[ErrorEnvelope | File]:
    """Opens the project-change stream when projectId and after are both absent. Opens one project chat
    hint stream when both are present. Supplying only one parameter is invalid. HTTP remains the durable
    catch-up authority. Every data-bearing SSE record uses the event name declared by x-sse-event-name
    and a RealtimeServerMessage JSON value; transport-only keep-alives do not carry data.

    Args:
        project_id (str | Unset):
        after (int | Unset):
        origin (str | Unset):
        sec_fetch_site (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | File]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        after=after,
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
    project_id: str | Unset = UNSET,
    after: int | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: str | Unset = UNSET,
) -> ErrorEnvelope | File | None:
    """Opens the project-change stream when projectId and after are both absent. Opens one project chat
    hint stream when both are present. Supplying only one parameter is invalid. HTTP remains the durable
    catch-up authority. Every data-bearing SSE record uses the event name declared by x-sse-event-name
    and a RealtimeServerMessage JSON value; transport-only keep-alives do not carry data.

    Args:
        project_id (str | Unset):
        after (int | Unset):
        origin (str | Unset):
        sec_fetch_site (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | File
    """

    return sync_detailed(
        client=client,
        project_id=project_id,
        after=after,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    project_id: str | Unset = UNSET,
    after: int | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: str | Unset = UNSET,
) -> Response[ErrorEnvelope | File]:
    """Opens the project-change stream when projectId and after are both absent. Opens one project chat
    hint stream when both are present. Supplying only one parameter is invalid. HTTP remains the durable
    catch-up authority. Every data-bearing SSE record uses the event name declared by x-sse-event-name
    and a RealtimeServerMessage JSON value; transport-only keep-alives do not carry data.

    Args:
        project_id (str | Unset):
        after (int | Unset):
        origin (str | Unset):
        sec_fetch_site (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | File]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        after=after,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    project_id: str | Unset = UNSET,
    after: int | Unset = UNSET,
    origin: str | Unset = UNSET,
    sec_fetch_site: str | Unset = UNSET,
) -> ErrorEnvelope | File | None:
    """Opens the project-change stream when projectId and after are both absent. Opens one project chat
    hint stream when both are present. Supplying only one parameter is invalid. HTTP remains the durable
    catch-up authority. Every data-bearing SSE record uses the event name declared by x-sse-event-name
    and a RealtimeServerMessage JSON value; transport-only keep-alives do not carry data.

    Args:
        project_id (str | Unset):
        after (int | Unset):
        origin (str | Unset):
        sec_fetch_site (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | File
    """

    return (
        await asyncio_detailed(
            client=client,
            project_id=project_id,
            after=after,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
