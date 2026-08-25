from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.chat_catch_up_page import ChatCatchUpPage
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response


def _get_kwargs(
    project: str,
    *,
    after: int,
    limit: int,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["after"] = after

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/{project}/chat/events".format(
            project=quote(str(project), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ChatCatchUpPage | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = ChatCatchUpPage.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ChatCatchUpPage | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    after: int,
    limit: int,
) -> Response[ChatCatchUpPage | ErrorEnvelope]:
    """
    Args:
        project (str):
        after (int):
        limit (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCatchUpPage | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        after=after,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    after: int,
    limit: int,
) -> ChatCatchUpPage | ErrorEnvelope | None:
    """
    Args:
        project (str):
        after (int):
        limit (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCatchUpPage | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        client=client,
        after=after,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    after: int,
    limit: int,
) -> Response[ChatCatchUpPage | ErrorEnvelope]:
    """
    Args:
        project (str):
        after (int):
        limit (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCatchUpPage | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        after=after,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    after: int,
    limit: int,
) -> ChatCatchUpPage | ErrorEnvelope | None:
    """
    Args:
        project (str):
        after (int):
        limit (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCatchUpPage | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            client=client,
            after=after,
            limit=limit,
        )
    ).parsed
